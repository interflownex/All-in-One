from __future__ import annotations

import base64
import os
from pathlib import Path, PurePosixPath
import secrets
import tempfile

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class DocumentConfigurationError(RuntimeError):
    pass


class DocumentNotFoundError(FileNotFoundError):
    pass


class PrivateDocumentStore:
    """Encrypted-at-rest private document vault for candidate evidence files."""

    KEY_ENVIRONMENT = "ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY"
    ROOT_ENVIRONMENT = "ALL_IN_ONE_PRIVATE_DOCUMENT_DIR"
    URI_PREFIX = "private://jobs/"

    def __init__(self) -> None:
        configured_root = os.getenv(self.ROOT_ENVIRONMENT)
        storage_root = os.getenv("ALL_IN_ONE_STORAGE_DIR")
        if configured_root:
            self.root = Path(configured_root)
        elif storage_root:
            self.root = Path(storage_root) / "private_documents"
        else:
            self.root = Path(tempfile.mkdtemp(prefix="all-in-one-private-documents-"))
        self.root.mkdir(parents=True, exist_ok=True)
        self.key = self._load_key()

    def _load_key(self) -> bytes:
        configured = os.getenv(self.KEY_ENVIRONMENT)
        if configured:
            try:
                key = base64.urlsafe_b64decode(configured.encode("ascii"))
            except (ValueError, UnicodeEncodeError) as exc:
                raise DocumentConfigurationError("Chave de documentos deve ser base64 URL-safe.") from exc
            if len(key) != 32:
                raise DocumentConfigurationError("Chave de documentos deve conter 32 bytes.")
            return key
        if os.getenv("ALL_IN_ONE_ENV", "development").casefold() == "production":
            raise DocumentConfigurationError("Chave de criptografia documental obrigatoria em producao.")

        key_path = self.root / ".development-document-key"
        if key_path.exists():
            return base64.urlsafe_b64decode(key_path.read_text(encoding="ascii").strip().encode("ascii"))
        key = AESGCM.generate_key(bit_length=256)
        key_path.write_text(base64.urlsafe_b64encode(key).decode("ascii"), encoding="ascii")
        try:
            key_path.chmod(0o600)
        except OSError:
            pass
        return key

    def save(self, digest: str, contents: bytes) -> dict[str, str]:
        relative = PurePosixPath("ctps") / digest[:2] / f"{digest}.pdf.aesgcm"
        target = self.root.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            nonce = secrets.token_bytes(12)
            ciphertext = AESGCM(self.key).encrypt(nonce, contents, digest.encode("ascii"))
            temporary = target.with_suffix(f"{target.suffix}.tmp")
            temporary.write_bytes(nonce + ciphertext)
            temporary.replace(target)
        return {
            "storage_key": f"{self.URI_PREFIX}{relative.as_posix()}",
            "storage_encryption": "AES-256-GCM",
        }

    def read(self, storage_key: str, digest: str) -> bytes:
        if not storage_key.startswith(self.URI_PREFIX):
            raise DocumentNotFoundError("Referencia de documento privado invalida.")
        relative = PurePosixPath(storage_key.removeprefix(self.URI_PREFIX))
        if relative.is_absolute() or ".." in relative.parts:
            raise DocumentNotFoundError("Referencia de documento privado invalida.")
        target = self.root.joinpath(*relative.parts)
        if not target.is_file():
            raise DocumentNotFoundError("Documento privado nao encontrado.")
        sealed = target.read_bytes()
        if len(sealed) <= 12:
            raise DocumentNotFoundError("Documento privado corrompido.")
        try:
            return AESGCM(self.key).decrypt(sealed[:12], sealed[12:], digest.encode("ascii"))
        except InvalidTag as exc:
            raise DocumentNotFoundError("Documento privado nao pode ser autenticado.") from exc

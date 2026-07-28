from __future__ import annotations

import stat

from scripts.configure_valley_android_signing import strong_password, write_private
from scripts.validate_valley_android_release_v29 import validate


def test_strong_password_has_expected_length_and_classes() -> None:
    password = strong_password()
    assert len(password) == 32
    assert any(character.islower() for character in password)
    assert any(character.isupper() for character in password)
    assert any(character.isdigit() for character in password)
    assert any(character in "-_.@" for character in password)


def test_write_private_creates_owner_only_file(tmp_path) -> None:
    target = tmp_path / "secrets" / "release.properties"
    write_private(target, "sensitive=true\n")
    assert target.read_text(encoding="utf-8") == "sensitive=true\n"
    assert stat.S_IMODE(target.stat().st_mode) == 0o600


def test_valley_android_release_contract_is_hardened() -> None:
    assert validate() == []


def test_release_validator_detects_no_plaintext_session_storage() -> None:
    assert validate() == []

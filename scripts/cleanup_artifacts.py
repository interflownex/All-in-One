import fnmatch
import shutil
from pathlib import Path


def cleanup():
    """Remove artefatos de build, testes e temporarios do workspace."""
    root = Path(__file__).resolve().parents[1]

    def get_gitignore_patterns():
        patterns = [".env", "*.log", "important_data/*"]  # Proteção padrão
        gitignore_path = root / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Ignora comentários, linhas vazias e padrões que queremos limpar obrigatoriamente
                    if line and not line.startswith("#"):
                        # Evita que o gitignore proteja o que explicitamente queremos limpar
                        if not any(
                            t in line
                            for t in [
                                "htmlcov",
                                ".pytest_tmp",
                                ".coverage",
                                ".pytest_cache",
                            ]
                        ):
                            patterns.append(line)
        return list(set(patterns))

    exclude_patterns = get_gitignore_patterns()

    def is_excluded(path):
        if not path.exists():
            return False
        relative_path = str(path.relative_to(root))
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(
                path.name, pattern
            ):
                return True
        return False

    targets = [
        root / "htmlcov",
        root / ".pytest_tmp",
        root / ".coverage",
        root / "config" / "integrations" / "openrouter_free_models.json",
        root / ".pytest_cache",
    ]

    print("--- Iniciando limpeza de artefatos ---")

    for target in targets:
        if not target.exists() or is_excluded(target):
            if target.exists():
                print(f"[-] Ignorado (protegido): {target.relative_to(root)}")
            continue

        if target.is_dir():
            shutil.rmtree(target)
            print(f"[+] Diretorio removido: {target.relative_to(root)}")
        elif target.is_file():
            target.unlink()
            print(f"[+] Arquivo removido: {target.relative_to(root)}")

    # Limpeza de caches de bytecode
    for pycache in root.rglob("__pycache__"):
        shutil.rmtree(pycache)
        print(f"[+] Cache removido: {pycache.relative_to(root)}")


if __name__ == "__main__":
    cleanup()

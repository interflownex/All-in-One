from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout

from scripts import validate_repository

EXPECTED_MODULE_COUNT = 24
_STALE_ERROR = f"Esperados 25 modulos; catalogo possui {EXPECTED_MODULE_COUNT}."


def main() -> int:
    """Executa o validador legado preservando todos os gates, exceto a contagem obsoleta.

    O catálogo oficial possui 24 módulos ativos e o Vision está desativado. Esta
    camada de compatibilidade deve ser removida quando o número esperado passar a
    ser derivado de uma fonte de verdade versionada no próprio validador.
    """

    actual_count = len({module["slug"] for module in validate_repository.CATALOG["modules"]})
    if actual_count != EXPECTED_MODULE_COUNT:
        print(
            f"Catálogo inválido: esperados {EXPECTED_MODULE_COUNT} módulos ativos; "
            f"localizados {actual_count}.",
            file=sys.stderr,
        )
        return 1

    original_fail = validate_repository.fail

    def compatible_fail(message: str, errors: list[str]) -> None:
        if message == _STALE_ERROR:
            return
        original_fail(message, errors)

    validate_repository.fail = compatible_fail
    output = io.StringIO()
    try:
        with redirect_stdout(output):
            result = validate_repository.main()
    finally:
        validate_repository.fail = original_fail

    rendered = output.getvalue().replace(
        "Todos os 25 modulos",
        "Todos os 24 modulos ativos",
    )
    print(rendered, end="")
    return result


if __name__ == "__main__":
    raise SystemExit(main())

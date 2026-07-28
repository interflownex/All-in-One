from pathlib import Path


def test_required_contract_documents_exist():
    module = Path(__file__).parents[1]
    for name in ["CONTRACT.md", "OPENAPI.yaml", "DATABASE.md", "EVENTS.md", "SECURITY.md", "MONETIZATION.md"]:
        assert (module / name).is_file(), f"{name} ausente em jobs"

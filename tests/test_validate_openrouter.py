import json
import os
import unittest
from unittest.mock import mock_open, patch

from scripts.validate_openrouter import update_provider_matrix


class TestOpenRouterValidation(unittest.TestCase):
    def test_update_provider_matrix_persistence(self):
        """Valida se a matriz de provedores e atualizada corretamente em disco."""
        matrix_path = os.path.join("config", "integrations", "provider_matrix.json")
        mock_data = {
            "integrations": [
                {
                    "key": "ai_agent_superdesign",
                    "primary_model": "old-model",
                    "available_free_models": [],
                }
            ]
        }

        # Mock do sistema de arquivos para evitar IO real
        with (
            patch("os.path.exists", return_value=True),
            patch(
                "builtins.open", mock_open(read_data=json.dumps(mock_data))
            ) as mocked_file,
        ):
            free_ids = ["model-a", "model-b"]
            update_provider_matrix(free_ids, new_primary_model="model-b")

            # Verifica se o arquivo foi aberto para escrita com o encoding correto
            mocked_file.assert_called_with(matrix_path, "w", encoding="utf-8")

            # Captura e valida o conteudo escrito
            written_content = "".join(
                call.args[0] for call in mocked_file().write.call_args_list
            )
            result = json.loads(written_content)

            integration = next(
                i for i in result["integrations"] if i["key"] == "ai_agent_superdesign"
            )
            self.assertEqual(integration["primary_model"], "model-b")
            self.assertEqual(
                integration["available_free_models"], ["model-a", "model-b"]
            )


if __name__ == "__main__":
    unittest.main()

import json
import os
import sys

import requests


def update_provider_matrix(free_model_ids, new_primary_model=None):
    """Atualiza o provider_matrix.json com a lista de modelos gratuitos detectada."""
    matrix_path = os.path.join("config", "integrations", "provider_matrix.json")
    if not os.path.exists(matrix_path):
        return
    try:
        with open(matrix_path, encoding="utf-8") as f:
            matrix = json.load(f)
        for item in matrix.get("integrations", []):
            if item.get("key") == "ai_agent_superdesign":
                item["available_free_models"] = sorted(free_model_ids)
                if new_primary_model:
                    print(f"[+] Atualizando primary_model para: {new_primary_model}")
                    item["primary_model"] = new_primary_model
                break
        with open(matrix_path, "w", encoding="utf-8") as f:
            json.dump(matrix, f, indent=2, ensure_ascii=False)
        print(f"[+] Matriz de provedores atualizada em {matrix_path}")
    except Exception as e:
        print(f"[-] Erro ao atualizar matriz: {e}")


def get_model_latency(model_id, headers, base_url):
    """Mede a latencia de um modelo com um prompt minimo para fins de benchmark."""
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
    }
    try:
        resp = requests.post(
            f"{base_url}/chat/completions", headers=headers, json=payload, timeout=10
        )
        return resp.elapsed.total_seconds() if resp.status_code == 200 else 999.0
    except Exception:
        return 999.0


def validate_openrouter_config():
    """
    Valida a configuracao do OpenRouter para o agente Superdesign.
    Verifica a presenca da API Key e a resposta do endpoint de autenticacao.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = "https://openrouter.ai/api/v1"

    # Carrega modelo alvo da matriz de provedores
    matrix_path = os.path.join("config", "integrations", "provider_matrix.json")
    target_model = "openrouter/auto"  # Fallback nao Google enquanto integracoes Google estiverem desativadas.
    if os.path.exists(matrix_path):
        try:
            with open(matrix_path, encoding="utf-8") as f:
                matrix = json.load(f)
                for item in matrix.get("integrations", []):
                    if item.get("key") == "ai_agent_superdesign":
                        target_model = item.get("primary_model", target_model)
                        break
        except Exception as e:
            print(f"[!] Aviso: Erro ao ler modelo da matriz, usando default: {e}")

    print("--- Validacao OpenRouter (Superdesign) ---")

    if not api_key:
        print("[-] ERRO: Variavel de ambiente OPENROUTER_API_KEY nao encontrada.")
        print(
            "    Certifique-se de configurar seu .env ou exportar a chave no terminal."
        )
        sys.exit(1)

    print(f"[+] Variavel OPENROUTER_API_KEY detectada (tamanho: {len(api_key)})")
    print(f"[+] Endpoint: {base_url}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8100",  # Requisito do OpenRouter para ranking
        "X-Title": "All-in-One Validator",
    }

    try:
        # O endpoint /auth/key retorna metadados sobre a chave em uso
        response = requests.get(f"{base_url}/auth/key", headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("[+] Autenticacao bem-sucedida!")
            print(
                f"[+] Detalhes da Chave: {json.dumps(data.get('data', {}), indent=2)}"
            )

            # Verifica se a chave tem acesso a modelos
            models_resp = requests.get(
                f"{base_url}/models", headers=headers, timeout=10
            )
            if models_resp.status_code == 200:
                all_models = models_resp.json().get("data", [])
                print(
                    f"[+] Conexao de listagem de modelos OK ({len(all_models)} modelos totais)"
                )

                # Filtra modelos onde o custo de prompt e completion e zero
                free_models = [
                    m
                    for m in all_models
                    if float(m.get("pricing", {}).get("prompt", "1")) == 0
                    and float(m.get("pricing", {}).get("completion", "1")) == 0
                ]
                print(f"[+] Modelos gratuitos disponiveis ({len(free_models)}):")
                for m in free_models:
                    print(f"    - {m.get('id')}")

                # Verificacao de disponibilidade gratuita com logica de fallback
                active_model = target_model
                is_primary_free = any(m.get("id") == target_model for m in free_models)

                if is_primary_free:
                    print(
                        f"[+] Verificacao: {target_model} permanece na lista GRATUITA."
                    )
                elif free_models:
                    print(
                        "[*] Avaliando latencia dos modelos gratuitos disponiveis para fallback..."
                    )
                    # Benchmark nos primeiros 3 modelos para encontrar o mais rapido sem demorar muito
                    candidates = free_models[:3]
                    benchmarks = []
                    for m in candidates:
                        m_id = m.get("id")
                        lat = get_model_latency(m_id, headers, base_url)
                        benchmarks.append((lat, m_id))
                        print(f"    - {m_id}: {lat:.2f}s")

                    # Filtra modelos com latencia superior a 5 segundos
                    benchmarks = [b for b in benchmarks if b[0] <= 5.0]

                    if not benchmarks:
                        print(
                            "[-] ERRO: Nenhum modelo gratuito com latencia aceitavel (<= 5s) encontrado."
                        )
                        sys.exit(1)

                    benchmarks.sort()  # Ordena por latencia (menor primeiro)
                    active_model = benchmarks[0][1]
                    print(
                        f"[!] Alerta: {target_model} NAO e mais gratuito. Fallback para o mais rapido: {active_model}"
                    )
                else:
                    print("[-] ERRO: Nenhum modelo gratuito disponivel no OpenRouter.")
                    sys.exit(1)

                # Exportacao para JSON formatado
                output_path = os.path.join(
                    "config", "integrations", "openrouter_free_models.json"
                )
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(free_models, f, indent=2, ensure_ascii=False)
                print(f"[+] Lista de modelos gratuitos exportada para: {output_path}")

                # Atualizacao automatica da matriz de provedores
                update_provider_matrix(
                    [m.get("id") for m in free_models],
                    new_primary_model=active_model if not is_primary_free else None,
                )

            # Teste de Prompt Real
            print(f"[+] Testando prompt 'Hello World' com o modelo: {active_model}...")

            chat_payload = {
                "model": active_model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello World. Responda apenas com 'Conexao OK' se voce recebeu esta mensagem.",
                    }
                ],
            }

            chat_resp = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=chat_payload,
                timeout=30,
            )

            if chat_resp.status_code == 200:
                result = chat_resp.json()
                content = result["choices"][0]["message"]["content"]
                latency = chat_resp.elapsed.total_seconds()
                print(f"[+] Resposta do modelo ({latency:.2f}s): {content.strip()}")

                # Se usamos um fallback, falhamos o script no fim para alertar o CI
                if not is_primary_free:
                    print(
                        f"[!] Falhando auditoria: O modelo primario {target_model} precisa ser revisado."
                    )
                    sys.exit(1)
            else:
                print(f"[-] Erro ao testar chat: {chat_resp.status_code}")
                print(f"[-] Detalhes: {chat_resp.text}")

        else:
            print(f"[-] Erro de Autenticacao: Status {response.status_code}")
            print(f"[-] Resposta: {response.text}")
            sys.exit(1)

    except Exception as e:
        print(f"[-] Falha na conexao de rede: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    validate_openrouter_config()

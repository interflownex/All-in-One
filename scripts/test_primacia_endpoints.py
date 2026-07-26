#!/usr/bin/env python3
"""Testa endpoints de primícia em todos os módulos.

Executa verificações básicas:
  - GET /{module}/feature-status
  - GET /{module}/health  
  - GET /{module}/status
  - POST /{module}/delegations (com flag desligada)
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Any
import json

# Setup para importar módulos
workspace = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workspace / "modules"))

MODULES = [
    "identity", "business", "permissions", "finance", "marketplace",
    "delivery", "riders", "services", "mobility", "jobs",
    "erp", "wms", "tms", "crm", "bpm",
    "document", "hr", "health", "legal", "property",
    "bi", "ai_core", "api_hub",
]

def test_module_endpoints(module_name: str) -> dict[str, Any]:
    """Testa endpoints de um módulo."""
    try:
        # Importa o app do módulo
        module = __import__(f"{module_name}.main", fromlist=["app"])
        app = module.app
        
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        results = {
            "module": module_name,
            "feature_status": None,
            "health": None,
            "status": None,
            "delegations_403": None,  # Sem flag habilitada
            "errors": [],
        }
        
        # Teste 1: Feature status
        try:
            resp = client.get("/feature-status")
            results["feature_status"] = {
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
            }
            if resp.status_code == 200:
                data = resp.json()
                results["feature_status"]["flag"] = data.get("flag", "unknown")
                results["feature_status"]["enabled"] = data.get("enabled", False)
        except Exception as e:
            results["errors"].append(f"feature_status: {str(e)}")
        
        # Teste 2: Health
        try:
            resp = client.get("/health")
            results["health"] = {
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
            }
        except Exception as e:
            results["errors"].append(f"health: {str(e)}")
        
        # Teste 3: Status
        try:
            resp = client.get("/status")
            results["status"] = {
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
            }
        except Exception as e:
            results["errors"].append(f"status: {str(e)}")
        
        # Teste 4: Delegations (sem flag, deve retornar 402 ou 404)
        try:
            resp = client.post(
                "/delegations",
                json={
                    "grantee_id": "test-user",
                    "purpose": "test",
                },
            )
            # Esperamos 402 (feature not enabled) ou 404 (not found)
            results["delegations_403"] = {
                "status_code": resp.status_code,
                "success": resp.status_code in {402, 404},
            }
        except Exception as e:
            results["errors"].append(f"delegations: {str(e)}")
        
        return results
    
    except Exception as e:
        return {
            "module": module_name,
            "error": str(e),
            "type": type(e).__name__,
        }

def main():
    """Executa testes em todos os módulos."""
    print(f"\n{'='*100}")
    print(f"{'TESTAR ENDPOINTS DE PRIMÍCIA - TODOS OS MÓDULOS':^100}")
    print(f"{'='*100}\n")
    
    results_by_module = {}
    summary = {
        "total": len(MODULES),
        "tested": 0,
        "with_errors": 0,
        "endpoints_ok": 0,
    }
    
    for module_name in sorted(MODULES):
        print(f"Testando {module_name}...", end=" ", flush=True)
        results = test_module_endpoints(module_name)
        results_by_module[module_name] = results
        
        if "error" in results:
            print(f"❌ ERRO: {results['error']}")
            summary["with_errors"] += 1
        else:
            summary["tested"] += 1
            
            # Conta endpoints bem-sucedidos
            ok_count = 0
            if results.get("feature_status", {}).get("success"):
                ok_count += 1
            if results.get("health", {}).get("success"):
                ok_count += 1
            if results.get("status", {}).get("success"):
                ok_count += 1
            if results.get("delegations_403", {}).get("success"):
                ok_count += 1
            
            if ok_count == 4:
                print("✅ 4/4 endpoints")
                summary["endpoints_ok"] += 1
            else:
                print(f"⚠️  {ok_count}/4 endpoints")
    
    print(f"\n{'='*100}")
    print(f"Resumo:")
    print(f"  Total de módulos: {summary['total']}")
    print(f"  Testados com sucesso: {summary['tested']}")
    print(f"  Com erro de importação: {summary['with_errors']}")
    print(f"  Módulos com todos os 4 endpoints: {summary['endpoints_ok']}")
    print(f"{'='*100}\n")
    
    # Detalha erros
    erros = [
        (m, r) for m, r in results_by_module.items()
        if "error" in r or r.get("errors")
    ]
    
    if erros:
        print("DETALHES DOS ERROS:\n")
        for module_name, result in erros:
            print(f"  {module_name}:")
            if "error" in result:
                print(f"    Erro de importação: {result['error']}")
            if result.get("errors"):
                for err in result["errors"]:
                    print(f"    {err}")

if __name__ == "__main__":
    main()

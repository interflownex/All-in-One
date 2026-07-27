# Resumo Bandit v2.8

**Código de saída:** `1`
**Achados:** `114`

| ID | Severidade | Confiança | Arquivo | Linha | Achado |
|---|---|---|---|---:|---|
| B608 | MEDIUM | MEDIUM | `modules/shared/dynamic_forms_postgres_store.py` | 149 | Possible SQL injection vector through string-based query construction. |
| B608 | MEDIUM | MEDIUM | `modules/shared/dynamic_forms_postgres_store.py` | 175 | Possible SQL injection vector through string-based query construction. |
| B608 | MEDIUM | MEDIUM | `modules/shared/dynamic_forms_postgres_store.py` | 599 | Possible SQL injection vector through string-based query construction. |
| B404 | LOW | HIGH | `modules/shared/runtime.py` | 5 | Consider possible security implications associated with the subprocess module. |
| B607 | LOW | HIGH | `modules/shared/runtime.py` | 54 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `modules/shared/runtime.py` | 54 | subprocess call - check for execution of untrusted input. |
| B110 | LOW | HIGH | `modules/shared/runtime.py` | 69 | Try, Except, Pass detected. |
| B105 | LOW | MEDIUM | `modules/shared/runtime.py` | 81 | Possible hardcoded password: 'jwt-secret' |
| B112 | LOW | HIGH | `modules/shared/valley_catalog.py` | 311 | Try, Except, Continue detected. |
| B404 | LOW | HIGH | `scripts/audit_valley_apk.py` | 9 | Consider possible security implications associated with the subprocess module. |
| B607 | LOW | HIGH | `scripts/audit_valley_apk.py` | 79 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/audit_valley_apk.py` | 79 | subprocess call - check for execution of untrusted input. |
| B607 | LOW | HIGH | `scripts/audit_valley_apk.py` | 99 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/audit_valley_apk.py` | 99 | subprocess call - check for execution of untrusted input. |
| B603 | LOW | HIGH | `scripts/audit_valley_apk.py` | 112 | subprocess call - check for execution of untrusted input. |
| B607 | LOW | HIGH | `scripts/audit_valley_apk.py` | 151 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/audit_valley_apk.py` | 151 | subprocess call - check for execution of untrusted input. |
| B603 | LOW | HIGH | `scripts/audit_valley_apk.py` | 169 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/automate_ui_generation.py` | 2 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/automate_ui_generation.py` | 27 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/check_artifact_registry.py` | 1 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/check_artifact_registry.py` | 60 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/check_firebase_auth_remote.py` | 7 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/check_firebase_auth_remote.py` | 18 | subprocess call - check for execution of untrusted input. |
| B310 | MEDIUM | HIGH | `scripts/check_firebase_auth_remote.py` | 37 | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. |
| B404 | LOW | HIGH | `scripts/check_generated_artifacts.py` | 5 | Consider possible security implications associated with the subprocess module. |
| B607 | LOW | HIGH | `scripts/check_generated_artifacts.py` | 18 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/check_generated_artifacts.py` | 18 | subprocess call - check for execution of untrusted input. |
| B607 | LOW | HIGH | `scripts/check_generated_artifacts.py` | 33 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/check_generated_artifacts.py` | 33 | subprocess call - check for execution of untrusted input. |
| B603 | LOW | HIGH | `scripts/check_generated_artifacts.py` | 45 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/check_git_sync.py` | 8 | Consider possible security implications associated with the subprocess module. |
| B607 | LOW | HIGH | `scripts/check_git_sync.py` | 16 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/check_git_sync.py` | 16 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/configure_apigee_api_hub.py` | 9 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/configure_apigee_api_hub.py` | 46 | subprocess call - check for execution of untrusted input. |
| B105 | LOW | MEDIUM | `scripts/configure_apigee_api_hub.py` | 340 | Possible hardcoded password: 'False' |
| B105 | LOW | MEDIUM | `scripts/configure_apigee_api_hub.py` | 360 | Possible hardcoded password: 'True' |
| B404 | LOW | HIGH | `scripts/configure_data_agent_kit.py` | 10 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/configure_data_agent_kit.py` | 111 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/configure_docker_dx.py` | 10 | Consider possible security implications associated with the subprocess module. |
| B607 | LOW | HIGH | `scripts/configure_docker_dx.py` | 94 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/configure_docker_dx.py` | 94 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/configure_valley_android_signing.py` | 11 | Consider possible security implications associated with the subprocess module. |
| B607 | LOW | HIGH | `scripts/configure_valley_android_signing.py` | 59 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/configure_valley_android_signing.py` | 59 | subprocess call - check for execution of untrusted input. |
| B607 | LOW | HIGH | `scripts/configure_valley_android_signing.py` | 115 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/configure_valley_android_signing.py` | 115 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/deploy_mobile_artifacts.py` | 7 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/deploy_mobile_artifacts.py` | 35 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/docker_gcp_push.py` | 1 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/docker_gcp_push.py` | 38 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/gcp_storage_hygiene.py` | 13 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/gcp_storage_hygiene.py` | 34 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/gemini_agent_watchdog.py` | 11 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/gemini_agent_watchdog.py` | 28 | subprocess call - check for execution of untrusted input. |
| B101 | LOW | HIGH | `scripts/generate_abnt_memo_pdf.py` | 147 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B405 | LOW | HIGH | `scripts/generate_data_audit_inventory.py` | 13 | Using xml.etree.ElementTree to parse untrusted XML data is known to be vulnerable to XML attacks. Replace xml.etree.ElementTree with the equivalent defusedxml package, or make sure defusedxml.defuse_stdlib() is called. |
| B314 | MEDIUM | HIGH | `scripts/generate_data_audit_inventory.py` | 1384 | Using xml.etree.ElementTree.parse to parse untrusted XML data is known to be vulnerable to XML attacks. Replace xml.etree.ElementTree.parse with its defusedxml equivalent function or make sure defusedxml.defuse_stdlib() is called |
| B404 | LOW | HIGH | `scripts/google_cloud_control.py` | 7 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/google_cloud_control.py` | 48 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/harden_firebase_android_api_key.py` | 7 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/harden_firebase_android_api_key.py` | 19 | subprocess call - check for execution of untrusted input. |
| B310 | MEDIUM | HIGH | `scripts/harden_firebase_android_api_key.py` | 47 | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. |
| B404 | LOW | HIGH | `scripts/multi_agent_sync_guard.py` | 7 | Consider possible security implications associated with the subprocess module. |
| B607 | LOW | HIGH | `scripts/multi_agent_sync_guard.py` | 20 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/multi_agent_sync_guard.py` | 20 | subprocess call - check for execution of untrusted input. |
| B603 | LOW | HIGH | `scripts/multi_agent_sync_guard.py` | 278 | subprocess call - check for execution of untrusted input. |
| B310 | MEDIUM | HIGH | `scripts/send_apk_artifact.py` | 68 | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. |
| B310 | MEDIUM | HIGH | `scripts/send_ready_artifact_to_telegram.py` | 29 | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. |
| B310 | MEDIUM | HIGH | `scripts/send_ready_artifact_to_telegram.py` | 50 | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. |
| B404 | LOW | HIGH | `scripts/setup_cloud_secrets.py` | 1 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/setup_cloud_secrets.py` | 19 | subprocess call - check for execution of untrusted input. |
| B603 | LOW | HIGH | `scripts/setup_cloud_secrets.py` | 33 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/validate_compose_health.py` | 9 | Consider possible security implications associated with the subprocess module. |
| B603 | LOW | HIGH | `scripts/validate_compose_health.py` | 73 | subprocess call - check for execution of untrusted input. |
| B603 | LOW | HIGH | `scripts/validate_compose_health.py` | 129 | subprocess call - check for execution of untrusted input. |
| B603 | LOW | HIGH | `scripts/validate_compose_health.py` | 131 | subprocess call - check for execution of untrusted input. |
| B603 | LOW | HIGH | `scripts/validate_compose_health.py` | 208 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/validate_firebase_auth.py` | 7 | Consider possible security implications associated with the subprocess module. |
| B607 | LOW | HIGH | `scripts/validate_firebase_auth.py` | 74 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/validate_firebase_auth.py` | 74 | subprocess call - check for execution of untrusted input. |
| B404 | LOW | HIGH | `scripts/validate_stitch_mcp_config.py` | 8 | Consider possible security implications associated with the subprocess module. |
| B607 | LOW | HIGH | `scripts/validate_stitch_mcp_config.py` | 135 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/validate_stitch_mcp_config.py` | 135 | subprocess call - check for execution of untrusted input. |
| B607 | LOW | HIGH | `scripts/validate_stitch_mcp_config.py` | 171 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/validate_stitch_mcp_config.py` | 171 | subprocess call - check for execution of untrusted input. |
| B607 | LOW | HIGH | `scripts/validate_stitch_mcp_config.py` | 204 | Starting a process with a partial executable path |
| B603 | LOW | HIGH | `scripts/validate_stitch_mcp_config.py` | 204 | subprocess call - check for execution of untrusted input. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 25 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 28 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 31 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 41 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 48 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 49 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 54 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 57 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 60 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 66 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 72 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 74 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 75 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 78 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 88 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 91 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 94 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 97 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 100 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 102 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 103 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 111 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 119 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 126 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |
| B101 | LOW | HIGH | `scripts/validate_web_frontend.py` | 127 | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. |

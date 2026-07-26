# Diagnóstico Bandit

## modules/shared/dynamic_forms_postgres_store.py:149
- teste: B608 hardcoded_sql_expressions
- severidade: MEDIUM
- confiança: MEDIUM
- motivo: Possible SQL injection vector through string-based query construction.

## modules/shared/dynamic_forms_postgres_store.py:175
- teste: B608 hardcoded_sql_expressions
- severidade: MEDIUM
- confiança: MEDIUM
- motivo: Possible SQL injection vector through string-based query construction.

## modules/shared/dynamic_forms_postgres_store.py:599
- teste: B608 hardcoded_sql_expressions
- severidade: MEDIUM
- confiança: MEDIUM
- motivo: Possible SQL injection vector through string-based query construction.

## scripts/check_firebase_auth_remote.py:37
- teste: B310 blacklist
- severidade: MEDIUM
- confiança: HIGH
- motivo: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

## scripts/generate_data_audit_inventory.py:1384
- teste: B314 blacklist
- severidade: MEDIUM
- confiança: HIGH
- motivo: Using xml.etree.ElementTree.parse to parse untrusted XML data is known to be vulnerable to XML attacks. Replace xml.etree.ElementTree.parse with its defusedxml equivalent function or make sure defusedxml.defuse_stdlib() is called

## scripts/harden_firebase_android_api_key.py:47
- teste: B310 blacklist
- severidade: MEDIUM
- confiança: HIGH
- motivo: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

## scripts/send_apk_artifact.py:68
- teste: B310 blacklist
- severidade: MEDIUM
- confiança: HIGH
- motivo: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

## scripts/send_ready_artifact_to_telegram.py:29
- teste: B310 blacklist
- severidade: MEDIUM
- confiança: HIGH
- motivo: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

## scripts/send_ready_artifact_to_telegram.py:50
- teste: B310 blacklist
- severidade: MEDIUM
- confiança: HIGH
- motivo: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

Total de achados: 9

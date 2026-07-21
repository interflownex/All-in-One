# Permissões, Segurança e Privacidade

Foram triados 304 campos potencialmente pessoais, sensíveis, financeiros, restritos ou pseudônimos vinculáveis. A política versionada registra categoria, padrão que motivou a triagem, criptografia, mascaramento e retenção. A classificação automática exige homologação pelo proprietário do domínio e revisão jurídica/privacidade quando aplicável.

RBAC/ABAC deve ser provado endpoint a endpoint; controle apenas no frontend não é aceito. Campos sem regra automática continuam explicitamente sem classificação e com lacuna de retenção.

EVIDÊNCIAS: `config/data_audit/field_classification_policy.json`, `artifacts/politica_classificacao_campos.json`, `artifacts/dicionario_de_dados.csv`, `modules/permissions/`, `modules/identity/`.

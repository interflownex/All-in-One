# Permissões, Segurança e Privacidade

Foram triados 520 campos potencialmente pessoais, sensíveis, financeiros, restritos ou pseudônimos vinculáveis. A política versionada registra categoria, padrão que motivou a triagem, criptografia, mascaramento e retenção. A classificação automática exige homologação pelo proprietário do domínio e revisão jurídica/privacidade quando aplicável.

Foram catalogadas 794 operações backend: 600 operações CRUD sobre 120 entidades e 194 transições. 129 possuem ao menos um arquivo de teste candidato localizado; isso não equivale a prova positiva/negativa completa por endpoint.

A rota genérica de leitura por ID deixa 0 entidades não sensíveis fora do módulo `permissions` sem verificação de owner, tenant ou papel depois da autenticação. Essa condição é P0 por risco de IDOR e isolamento horizontal. RBAC/ABAC deve ser provado endpoint a endpoint; controle apenas no frontend não é aceito. Campos sem regra automática continuam explicitamente sem classificação e com lacuna de retenção.

EVIDÊNCIAS: `config/data_audit/field_classification_policy.json`, `artifacts/politica_classificacao_campos.json`, `artifacts/dicionario_de_dados.csv`, `modules/permissions/`, `modules/identity/`.

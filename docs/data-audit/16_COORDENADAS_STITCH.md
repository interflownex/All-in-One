# Coordenadas para Templates Stitch

## Cobertura gerada

Foram geradas 263 coordenadas a partir de rotas e superfícies reais. Cada registro contém módulo, entidade, título, tipo, rota, persona pendente, campos, ação primária, endpoint lógico, permissões, estados, responsividade, acessibilidade e evidência.

As coordenadas estão em `artifacts/coordenadas_stitch.csv` e `artifacts/coordenadas_stitch.json`. O status de binding permanece parcial porque o `SmartCRUD` genérico não implementa todos os campos específicos.

## TEMPLATE adicional: Catálogo de dados

- Módulo: Administração interna
- Persona: auditor e proprietário de domínio
- Rota: `/admin/data-audit` (proposta)
- Dados: dicionário, lacunas, cobertura e evidências
- Ações: filtrar, abrir evidência, atribuir lacuna e homologar classificação
- Estados: loading, vazio, erro, conflito, sem permissão e sucesso
- Responsividade: desktop, tablet e mobile
- Acessibilidade: teclado, foco, labels e contraste

Nenhuma rota proposta é apresentada como existente. EVIDÊNCIAS: `apps/all-in-one/src/App.tsx`, `artifacts/coordenadas_stitch.json`, `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:2545`.

# Plano de Ação Estruturado para o Codex

**Versão:** 2.6  
**Data da entrega:** 26/07/2026  
**Hora da entrega:** 14:01:53  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Commit de referência:** `c2c8eaccc1581ed674821feaaa3336c03a5b763c`  
**Issue de orquestração:** `#43`  
**Ciclo principal:** 8 horas  
**Tolerância operacional:** até 4 horas  
**Nova coleta obrigatória:** após 12 horas

## 1. Missão

Executar o primeiro ciclo operacional completo sob as regras permanentes de Estudar, Pesquisa Avançada, versionamento, data, hora e atualização do arquivo `tarefas.md`.

O objetivo deste ciclo não é iniciar o maior número possível de frentes. O objetivo é reduzir risco de integração, validar entregas já existentes e devolver um repositório rastreável para os próximos agentes.

## 2. Fontes de verdade

Antes de editar, consultar:

- `AGENTS.md`;
- `tarefas.md` versão 1.1;
- `docs/Pendências Do desenvolvedor.md` versão 2.6;
- `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v2.6_2026-07-26.md`;
- issue `#43`;
- PRs `#34`, `#36`, `#37`, `#38` e `#40`;
- issues `#24`, `#39` e `#41`;
- `config/module_catalog.json`;
- `modules/business/module_settings.py`;
- `scripts/audit_confirmation_v7.py`;
- `config/autonomy/telegram_delivery_policy.json`;
- manifestos `.gemini/skills/.datacloud_skills_manifest` e `.github/skills/.datacloud_skills_manifest`.

## 3. Regras obrigatórias

1. executar `git status --short --branch`;
2. atualizar referências remotas permitidas;
3. executar preflight multiagente;
4. adquirir lock da atividade;
5. criar branch de trabalho quando estiver na `main`;
6. não descartar alterações de outro agente;
7. não executar push direto na `main`;
8. não versionar segredos;
9. executar testes relacionados;
10. registrar logs, artefatos e evidências;
11. abrir ou atualizar pull request;
12. usar Squash and Merge somente após revisão e checks;
13. atualizar a issue `#43`;
14. atualizar o relatório, o plano e `tarefas.md` ao final.

## 4. Resultado esperado após 8 horas

Entregar o máximo possível, nesta ordem:

1. checks executados no estado atual ou falhas transformadas em issues;
2. decisão documentada para cada PR aberto e desatualizado;
3. sobreposição entre `#34` e `#37` resolvida;
4. commit `44be12a` e pacote de skills auditados;
5. ambiente público identificado corretamente ou bloqueio documentado;
6. executor Telegram iniciado e testado;
7. artefatos do APK Admin e PDV Desktop validados ou rejeitados com evidência;
8. relatórios, issue e `tarefas.md` atualizados.

## 5. Plano de execução de 8 horas

### Bloco 1: 0h a 1h, estado e gates

**Atividades**

- confirmar branch e lock;
- executar `python3 scripts/audit_confirmation_v7.py`;
- executar `python3 scripts/validate_repository.py`;
- executar os testes diretamente relacionados a módulos, auditoria e governança;
- identificar workflows aplicáveis ao commit atual;
- registrar checks ausentes ou falhos.

**Critério de aceite**

Resultado reproduzível associado ao commit ou falhas registradas com comando, saída e causa.

### Bloco 2: 1h a 2h30, triagem dos PRs

**Atividades**

- atualizar referências dos PRs `#34`, `#36`, `#37`, `#38` e `#40`;
- comparar cada head com a `main` atual;
- gerar matriz de arquivos sobrepostos entre `#34` e `#37`;
- decidir para cada PR: atualizar, dividir, converter em rascunho ou encerrar como substituído;
- impedir merge enquanto a base estiver desatualizada ou `mergeable` estiver falso.

**Critério de aceite**

Cada PR deve possuir uma decisão explícita, justificativa, responsável e próximo passo.

### Bloco 3: 2h30 a 3h30, auditoria do pacote de skills

**Atividades**

- revisar o commit `44be12a9751d336f0c8094f79c893eb69008eaf4`;
- listar arquivos adicionados, removidos, alterados e restaurados;
- comparar `.gemini/skills` com `.github/skills`;
- validar checksums dos manifestos;
- identificar alteração de conteúdo, modo de arquivo ou pacote gerado;
- confirmar se houve perda acidental ou apenas atualização controlada;
- abrir issue específica se a origem e o processo não forem reproduzíveis.

**Critério de aceite**

Relatório com escopo, causa, impacto, segurança, arquivos afetados e recomendação de manutenção ou reversão.

### Bloco 4: 3h30 a 4h30, ambiente público e Render

**Atividades**

- identificar a fonte do título `tmp-valley` em `brasildesconto.com.br`;
- verificar DNS, artefato publicado e configuração de ambiente;
- validar `render.yaml`, entrypoint, dependências e secrets externos;
- obter URL real do API Hub;
- registrar logs de build e inicialização;
- testar `/health`;
- confirmar CORS para os domínios oficiais.

**Critério de aceite**

Ambiente com identidade correta, URL e saúde comprovadas, ou bloqueio externo documentado com causa e ação necessária.

### Bloco 5: 4h30 a 6h, Telegram executável

**Atividades**

- localizar o script de envio existente e preservar compatibilidade;
- criar serviço ou CLI para `activity_started` e `activity_completed`;
- criar gerador dos quatro relatórios diários;
- validar campos obrigatórios da política;
- implementar retry com limite e timeout;
- criar mocks para Telegram sem usar credencial real nos testes;
- garantir que token e chat ID venham apenas de secrets;
- registrar logs sem dados sensíveis.

**Critério de aceite**

Testes reproduzíveis comprovam geração dos três tipos de payload, retry controlado e ausência de segredo no repositório.

### Bloco 6: 6h a 7h30, validação de artefatos

#### APK Admin, PR #36

- atualizar a branch contra a `main`;
- executar testes unitários;
- gerar APK debug;
- instalar em emulador ou dispositivo homologado;
- validar HTTPS, bloqueio de conteúdo misto, navegação externa e arquivos locais;
- confirmar a URL do painel.

#### PDV Desktop, PR #38

- atualizar a branch contra a `main`;
- executar testes de armazenamento, caixa, estoque e idempotência;
- gerar instalador ou executável portátil no ambiente Windows autorizado;
- validar operação sem internet;
- verificar backup, restauração e token remoto criptografado;
- confirmar que o modo offline não duplica vendas após sincronização.

**Critério de aceite**

Artefatos identificados por hash, versão, commit, plataforma e resultado de smoke test.

### Bloco 7: 7h30 a 8h, rastreabilidade e passagem

**Atividades**

- atualizar a issue `#43`;
- criar issues para falhas abertas;
- atualizar `docs/Pendências Do desenvolvedor.md`;
- atualizar os dois relatórios v2.6;
- atualizar `tarefas.md` para a próxima versão;
- registrar PRs, commits, testes, artefatos, URLs e bloqueios;
- liberar lock multiagente.

**Critério de aceite**

A próxima IA consegue continuar sem nova explicação e sabe exatamente o que está concluído, parcial, bloqueado e pendente.

## 6. Tolerância de até 4 horas

Usar a tolerância apenas para concluir atividades do ciclo, nesta ordem:

1. corrigir conflito ou regressão causada pela atualização dos PRs;
2. estabilizar checks diretamente afetados;
3. terminar auditoria de skills;
4. homologar ambiente público e `/health`;
5. finalizar executor Telegram;
6. concluir build e smoke test de APK Admin e PDV Desktop;
7. atualizar evidências.

Não iniciar nova frente grande durante a tolerância.

## 7. Atualização obrigatória após 12 horas

Registrar:

- atividade;
- descrição técnica;
- status;
- percentual concluído;
- falha detectada;
- causa;
- ação realizada;
- possibilidade de resolução;
- responsável ou dependência externa;
- evidência;
- pendências restantes;
- próximos passos;
- versão do `tarefas.md`.

## 8. Condições de parada

Parar e registrar bloqueio quando houver:

- credencial legítima ausente;
- billing, IAM ou aceite jurídico obrigatório;
- lock de outro agente;
- risco de sobrescrever trabalho;
- necessidade de alterar marca oficial sem autorização;
- artefato de produção sem ambiente seguro de teste;
- conflito entre dois PRs sem fonte de verdade definida;
- ação reservada ao proprietário do projeto.

## 9. Formato da entrega

A entrega do Codex deve conter:

- resumo simples para o gestor;
- relatório técnico em Markdown;
- atualização da issue `#43`;
- branch e pull request;
- testes e evidências;
- arquivo `tarefas.md` atualizado e versionado;
- integração final por Squash and Merge, quando todos os critérios forem atendidos.

# Plano de Execução do Mapa Mestre de Dados e Conformidade

**Projeto:** All in One + Valley  
**Classificação:** Pendências / Técnico / Equipe Técnica  
**Público-alvo:** Equipe Técnica, Arquitetura, Segurança, DPO, Jurídico, Fiscal, Contábil, Produto e profissionais regulados  
**Status:** obrigatório e versionado  
**Data-base:** 2026-08-04  
**Escopo-alvo:** 702 tabelas lógicas, 24 módulos de produto, 7 domínios transversais e gates G0-G23  
**Fonte conceitual:** Mapa Mestre Regulatório v1.2.0  

> Este documento transforma o Mapa Mestre em uma sequência executável. Ele não autoriza automaticamente tratamentos de dados, operação financeira regulada, ato médico, ato jurídico, emissão fiscal produtiva ou ativação de feature flag. Cada atividade continua subordinada aos gates, ao papel regulatório confirmado e às aprovações profissionais aplicáveis.

## 1. Regra mandatória de encaixe no backlog

Antes de criar qualquer issue, branch ou migration, a IA desenvolvedora deve:

1. consultar a `main`, issues abertas, PRs abertas, commits recentes, checks, Dependabot e política de merge;
2. localizar atividade existente com o mesmo owner, domínio, objetivo e critério de aceite;
3. acrescentar a nova obrigação à atividade existente quando houver coerência;
4. criar uma nova issue apenas quando não existir owner ou escopo compatível;
5. registrar dependências, bloqueios, gates, evidências e rollback;
6. impedir duplicidade de implementação, segundo banco autoritativo ou segundo serviço para o mesmo domínio;
7. manter feature flags desligadas até homologação formal;
8. integrar exclusivamente por Squash and Merge, com todos os gates verdes no mesmo head SHA e `expected_head_sha`.

### 1.1 Fontes existentes preservadas

| Fonte existente | Função no plano | Inserção obrigatória |
|---|---|---|
| Issue #39 | guarda-chuva dos 24 módulos | capacidades de dados, contratos, tabelas e gates de cada módulo |
| Issue #51 | orquestração Marketplace → Stock → Finance → Delivery → Rider | fases transacionais e dependências de negócio |
| Issue #95 | homologação financeira produtiva | BCB/PSP, webhooks, ledger, split, escrow, fraude, reconciliação e bloqueio de entrega |
| Issue #134 | MCP Gateway | sandbox, escopos, auditoria, ferramentas somente leitura e governança de conectores |
| `tarefas.md` | histórico operacional | evidência final das ondas integradas, sem substituir as issues executoras |
| `docs/MANDATORY_EXECUTION_TOOLING.md` | política de ferramentas | GitHub, gates, Cloudflare, MCP, Dependabot e bloqueios externos |

## 2. Princípios de execução

- **Owner único:** cada informação possui um microsserviço proprietário.
- **Campo catalogado antes da migration:** nenhuma coluna entra no repositório sem contrato no `compliance.field_registry`.
- **Amplitude sem coleta excessiva:** modelar capacidade ampla, ativar somente campos necessários e juridicamente fundamentados.
- **Documentos e mídia fora do relacional:** conteúdo em object storage cifrado; banco guarda metadados, checksum, classificação, retenção e referência.
- **Imutabilidade probatória:** oferta, aceite, ledger, fiscal, prontuário, assinatura e auditoria são aditados ou revertidos, nunca sobrescritos.
- **Regra versionada:** tributo, Pix, TISS, FHIR, eSocial, moderação, preço e retenção possuem fonte, versão, vigência e teste.
- **Sem segredo no Git:** certificados, tokens, chaves, PAN, CVV e credenciais permanecem em KMS, HSM, Secret Manager ou PSP.
- **Revisão humana:** decisão clínica, jurídica, fiscal ou automatizada de alto impacto exige aprovação habilitada quando aplicável.
- **Nenhum go-live por existência de código:** somente evidência do ambiente correto encerra uma etapa.

## 3. Trilha de execução cronológica

O cronograma usa cinco fases e dez sprints como ordem lógica. Sprint não é promessa de prazo. Uma fase só avança após o gate de prontidão G23.

### Fase 0 — Fundação transversal obrigatória

**Executar antes de qualquer expansão de schema.**

#### Atividades sequenciais

- [ ] congelar inventário da `main` e reconciliar migrations, schemas, tabelas, campos, índices, endpoints, MongoDB, Redis, SQLite e object stores;
- [ ] criar fonte executável `compliance.field_registry`;
- [ ] criar catálogos de domínio, finalidade, base legal, retenção, criptografia, máscara, acesso, compartilhamento e linhagem;
- [ ] implementar bundles B0-B14 como contratos reutilizáveis;
- [ ] criar validador que bloqueia migration com coluna não registrada;
- [ ] criar matriz `norma -> obrigação -> tabela -> campo -> owner -> API/evento -> evidência -> teste`;
- [ ] implementar RLS/ABAC e testes negativos entre tenants;
- [ ] criar workflows de direitos do titular, incidente, legal hold, anonimização e descarte;
- [ ] ativar gates G0-G4, G10-G14 e G23 em modo bloqueante;
- [ ] executar RIPD por domínio de alto risco antes da coleta real.

#### Saída obrigatória

- catálogo executável;
- schema contracts versionados;
- CI impedindo coluna órfã;
- nenhuma perda de dados no rollback;
- owners e consumidores registrados.

### Fase 1 — Sprints 1-2: identidade, empresas e fundação transacional

**Issues âncora:** #39 e nova issue de fundação regulatória.  
**Dependência:** Fase 0 concluída.

#### Módulos

`identity`, `business`, `permissions`, catálogo base, `riders`, `delivery` básico e contas financeiras técnicas.

#### Atividades

- [ ] tokenizar CPF/CNPJ e demais identificadores; separar token, hash de busca e últimos dígitos;
- [ ] implantar KYC/KYB com claims temporários, reason codes, revisão humana e alternativa não biométrica;
- [ ] cadastrar contrato social, estatuto, alterações, QSA, beneficiário final, representantes, procurações, licenças, alvarás e certidões;
- [ ] implantar cofre documental, versionamento, validade, malware scan, assinatura e legal hold;
- [ ] estabelecer RBAC, ABAC, alçadas, delegação, segregação de funções e revisão de acesso;
- [ ] criar cadastro de Rider/veículo sem ativar fluxo produtivo bloqueado por #95;
- [ ] criar contas, journals e entradas de ledger em partidas dobradas, sem saldo mutável como fonte de verdade;
- [ ] manter biometria condicional e isolada por chaves;
- [ ] vincular todos os campos pessoais a finalidade, base legal e retenção.

#### Gates de saída

G0-G4, G6, G12-G14 e G23.

### Fase 2 — Sprints 3-4: Marketplace, Stock, Finance e One Services

**Issues âncora:** #51, #95 e #39.  
**Regra de bloqueio:** checkout, Delivery e Rider permanecem produtivamente desligados até #95 comprovar pagamento e reconciliação.

#### Marketplace e consumidor

- [ ] catálogo, variantes, atributos e mídia 1:N configurável;
- [ ] perfis logísticos com peso, dimensões, cubagem, fragilidade, temperatura e risco;
- [ ] snapshots imutáveis de oferta, fornecedor, preço total, frete, prazo, termos e publicidade;
- [ ] descontos progressivos versionados, margem mínima e transparência ao consumidor;
- [ ] arrependimento, cancelamento, devolução, garantia, recall, SAC, protocolo e disputa;
- [ ] direitos autorais, consentimento de pessoas identificáveis, moderação e acessibilidade de mídia.

#### Stock

- [ ] depósitos, zonas, bins, lotes, seriais, validade e movimentações;
- [ ] reservas, confirmações, liberações e expirações idempotentes;
- [ ] eventos de leitura barcode/EAN/GTIN vinculados a dispositivo, operador e local;
- [ ] sincronização de fornecedor, qualidade, recall e reconciliação de estoque;
- [ ] impedir sobrescrita direta de saldo físico sem movimento causal.

#### Finance — encaixe obrigatório em #95

- [ ] modelo operacional regulatório e papel perante BCB/PSP;
- [ ] adaptador PSP independente de fornecedor;
- [ ] Pix, cartão tokenizado, boleto e Open Finance conforme produto autorizado;
- [ ] webhooks autenticados, minimizados, idempotentes e processados por outbox/worker;
- [ ] autorização, captura, cancelamento, estorno, chargeback e liquidação separados;
- [ ] split, escrow, payout, reconciliação e bloqueio automático de divergência;
- [ ] KYC/KYB, fraude, PEP, sanções e PLD/FTP somente conforme papel validado;
- [ ] nenhuma credencial ou dado bruto de cartão no sistema;
- [ ] checkout continua desligado até homologação completa.

#### One Services

- [ ] prestadores, licenças, área, agenda, orçamento e contrato;
- [ ] evidências de visita e conclusão;
- [ ] escrow vinculado por referência, garantia, cancelamento e disputa;
- [ ] proibir promessa de resultado e preservar responsabilidade profissional.

#### Gates de saída

G5-G7, G12, G15-G16, G21 e G23.

### Fase 3 — Sprints 5-6: ERP, fiscal, WMS, Jobs e documentos

**Issue âncora:** #39; criar issues executoras por domínio após decomposição da Fase 0.

#### ERP e fiscal

- [ ] motor de regras fiscais versionadas com fonte oficial, checksum, fórmula DSL, vigência e vetores de teste;
- [ ] NF-e, NFC-e, NFS-e, CT-e, MDF-e, eventos e artefatos fiscais;
- [ ] CBS, IBS, IS, ICMS, FCP, DIFAL, ST, IPI, PIS, COFINS, ISS e demais tributos somente por regra versionada;
- [ ] XML, DANFE, protocolos, cancelamentos e inutilizações reconciliados com contabilidade;
- [ ] aprovação fiscal/contábil antes de produção;
- [ ] operação de PDV offline com sessão cifrada, sequência local, lote idempotente e conflito explícito;
- [ ] contingência fiscal sem autorização silenciosa ou resolução destrutiva.

#### WMS

- [ ] recebimento, putaway, picking, packing, inventário, ajustes e quality hold;
- [ ] temperatura, lote, serial, validade e rastreabilidade;
- [ ] integração causal com pedidos e documentos fiscais.

#### Jobs e HR inicial

- [ ] currículo versionado, candidatura, avaliação, entrevista e acesso auditado;
- [ ] CTPS e documentos trabalhistas em cofre, não em logs;
- [ ] descarte após processo seletivo e consentimento específico para banco de talentos;
- [ ] métricas de igualdade separadas da decisão individual e protegidas contra discriminação;
- [ ] eSocial versionado e segregação de saúde ocupacional.

#### GED/ECM e assinatura

- [ ] documentos, versões, OCR, redaction, assinatura, acesso, download, retenção e descarte;
- [ ] cadeia de validação ICP-Brasil quando aplicável;
- [ ] certificados A1/PFX apenas em KMS/HSM/Secret Manager; banco guarda metadados.

#### Gates de saída

G0-G4, G7, G13, G16, G20-G21 e G23.

### Fase 4 — Sprints 7-8: IA, reconciliação, saúde, jurídico e mobilidade

**Issues âncora:** #39, #51 e #134 quando houver conectores MCP.

#### IA e Helena

- [ ] modelo, prompt, finalidade, entrada, saída, explicação, viés e revisão humana versionados;
- [ ] `secondary_training_allowed=false` por padrão;
- [ ] memória conversacional com TTL, sumarização, isolamento, categorias proibidas e expurgo;
- [ ] impedir uso de conteúdo médico, jurídico ou corporativo para treinamento secundário sem base própria;
- [ ] recurso e revisão para decisões automatizadas de alto impacto.

#### Health

- [ ] pacientes, profissionais, licenças, instalações, agenda e relação assistencial;
- [ ] prontuário cifrado, aditamentos, assinatura, acesso por relação e break-glass auditado;
- [ ] telemedicina, diagnósticos, prescrições, exames, imagens e cuidados;
- [ ] TISS/TUSS versionado, glosa e faturamento segregado;
- [ ] Health Connect, dispositivos e laboratórios com consentimento, proveniência e descarte de payload bruto;
- [ ] FHIR com release, profile, terminologia, mapping, cursor e validação clínica.

#### Legal

- [ ] clientes, matérias, equipe, conflito, procuração, processo, prazo, documento e evidência;
- [ ] sigilo por matéria e barreiras éticas;
- [ ] cadeia de custódia, legal hold, honorários e comunicação privilegiada;
- [ ] minutas de IA sempre marcadas e submetidas à revisão humana habilitada;
- [ ] publicidade jurídica informativa, objetiva e sem promessa de resultado.

#### Mobilidade e TMS

- [ ] rotas, tarifas, tickets, acessibilidade, incidentes e itens perdidos;
- [ ] snapshots neutros de provedor externo de rota; Mapbox é implementação, não owner do domínio;
- [ ] geolocalização mínima, precisão delimitada, retenção curta e isolamento por finalidade;
- [ ] impacto urbano, restrições municipais e vigências versionadas.

#### Gates de saída

G8-G12, G17-G19, G22-G23.

### Fase 5 — Sprints 9-10: Property, HR/LMS, BI e API Hub

**Issues âncora:** #39 e #134 para sandbox/conectores.

#### Property

- [ ] imóveis, proprietários, matrícula, IPTU, endereço, características e finalidade;
- [ ] termos comerciais versionados: venda, aluguel, condomínio, garantia, caução e corretagem;
- [ ] mídia 1:N com fotos, vídeos 4K, tour 360°, plantas e vistorias;
- [ ] contratos, moradores, privacidade, assembleia, votos, atas e documentos do condomínio;
- [ ] CRECI e poderes quando aplicável;
- [ ] impedir exposição pública de endereço preciso ou dados de moradores sem finalidade.

#### HR/LMS

- [ ] empregado, dependente, contrato, remuneração, folha, ponto, benefícios e desligamento;
- [ ] banco de tempo de aprendizagem em ledger imutável;
- [ ] saúde ocupacional segregada;
- [ ] treinamentos, certificados e obrigações regulatórias.

#### BI

- [ ] métricas por definição versionada, fonte e owner;
- [ ] pseudonimização, agregação mínima, orçamento de privacidade e controle de exportação;
- [ ] impedir dashboards de dados sensíveis sem finalidade e acesso comprovados;
- [ ] livro de decisões, linhagem e reprodutibilidade.

#### API Hub e MCP

- [ ] encaixar produção do gateway em #134;
- [ ] sandbox somente com dados sintéticos, expiração e limpeza comprovada;
- [ ] escopos por ferramenta, OAuth/OIDC, rate limit, logs redigidos e auditoria;
- [ ] conectores com credenciais em cofre, egress controlado e contrato de compartilhamento;
- [ ] ferramentas mutáveis continuam proibidas até autorização explícita.

#### Gates de saída

G0-G5, G9-G10, G18, G22-G23.

## 4. Gates obrigatórios G0-G23

| Gate | Controle bloqueante |
|---|---|
| G0 | toda tabela e campo registrados no catálogo executável |
| G1 | finalidade, base legal, sensibilidade e retenção por campo |
| G2 | RLS/ABAC e isolamento entre tenants/usuários |
| G3 | criptografia, tokenização, máscara e cofre de segredos |
| G4 | retenção, legal hold, anonimização, expurgo e prova de descarte |
| G5 | oferta, preço, termos, cancelamento, garantia, SAC e CDC |
| G6 | ledger balanceado, idempotência, Pix/PSP e reconciliação |
| G7 | fonte fiscal oficial, checksum, vigência, teste e aprovação |
| G8 | prontuário, acesso assistencial, break-glass, TISS e saúde |
| G9 | sigilo jurídico, matéria, conflito e revisão humana |
| G10 | linhagem de IA, explicação, viés, recurso e revisão |
| G11 | incidente, avaliação, comunicação, evidência e prazo aplicável |
| G12 | logs Marco Civil separados por papel jurídico |
| G13 | KYC explicável, alternativa não biométrica e recurso |
| G14 | certificado e chave privada fora do banco/repositório |
| G15 | perfil logístico e motor de frete coerentes |
| G16 | artefatos fiscais reconciliados com contabilidade |
| G17 | conectores de saúde com consentimento e proveniência |
| G18 | memória de IA isolada e expirada |
| G19 | FHIR: release, profile, terminologia, mapping e cursor validados |
| G20 | PDV offline: sessão, sequência, conflito e contingência testados |
| G21 | barcode: dispositivo, operador, produto, lote/serial e movimento causal |
| G22 | provedor externo de rota, termos, precisão, retenção e isolamento |
| G23 | prontidão da fase, sign-offs, rollback e evidência do ambiente correto |

## 5. Definição de pronto por atividade

Uma atividade só pode ser marcada como concluída quando possuir:

- issue executora e owner;
- ADR ou decisão arquitetural quando houver fronteira entre serviços;
- contrato de tabela/campo no catálogo;
- migration reversível e teste em banco limpo;
- API/evento versionado e idempotente;
- autorização e isolamento testados;
- classificação LGPD e retenção aprovadas;
- testes unitários, integração, contrato e jornada negativa;
- telemetria sem conteúdo sensível;
- documentação, evidência e rollback;
- feature flag e plano de ativação;
- gates verdes no mesmo SHA;
- PR revisada e integrada somente por Squash and Merge.

## 6. Ordem imediata de execução

1. abrir issue-mãe transversal para este plano;
2. vincular #39, #51, #95 e #134;
3. criar a issue executora da Fase 0;
4. inventariar o estado real da `main` e produzir delta `atual x alvo`;
5. implementar primeiro o catálogo executável e o validador de migrations;
6. decompor as 702 tabelas em lotes pequenos por owner, sem criar todas fisicamente antecipadamente;
7. começar Fase 1 somente após G0-G4 mínimos;
8. manter #95 como bloqueio do fluxo financeiro, Delivery e Rider;
9. criar issues de domínio apenas quando não houver atividade existente coerente;
10. registrar cada integração em `tarefas.md` após merge e evidência.

## 7. Proibições

- push direto na `main`;
- migration massiva contendo múltiplos domínios sem rollback isolado;
- criação antecipada de tabela sem produto, finalidade ou owner;
- cópia de CPF, prontuário, processo jurídico ou dado financeiro entre serviços;
- JSONB livre para dados pessoais não catalogados;
- ativação de pagamento, fiscal, saúde ou jurídico por mera presença de código;
- alteração automática de regra oficial em produção sem diff, teste e aprovação;
- armazenamento de segredo, chave privada ou URL assinada permanente;
- marcar fase concluída com gate vermelho, ausente, cancelado ou pendente;
- declarar conformidade total sem evidência operacional e validação profissional.

## 8. Status inicial

- plano versionado: em PR;
- issue-mãe transversal: a criar nesta rodada;
- issue da Fase 0: a criar nesta rodada;
- encaixe em #39, #51, #95 e #134: a registrar nesta rodada;
- migrations regulatórias: não iniciadas;
- feature flags produtivas: permanecem desligadas quando ainda não homologadas;
- conteúdo anterior: preservado integralmente.

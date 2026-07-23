# Pendências do Desenvolvedor

**Versão:** 2.0  
**Data da verificação:** 22/07/2026  
**Repositório verificado:** `interflownex/All-in-One`  
**Branch de referência:** `main`  
**Objetivo:** consolidar pendências reais, remover duplicidades e separar bloqueios externos, validações e ações técnicas.

## 1. Regra de classificação

- **Crítica:** bloqueia publicação, segurança, integridade financeira, autenticação ou operação real.
- **Alta:** impede homologação completa ou integração externa de um módulo importante.
- **Média:** não bloqueia a base local, mas reduz confiabilidade, rastreabilidade ou qualidade operacional.
- **Secundária:** melhoria planejada que não impede o funcionamento atual.
- Nenhum item é considerado concluído apenas porque existe código ou PR fechado. A conclusão exige evidência executável ou validação no ambiente correspondente.
- Itens duplicados foram consolidados em uma única pendência com escopo ampliado.

## 2. Resumo da verificação

O repositório está ativo, com integrações recentes envolvendo ambiente de desenvolvimento, padronização dos shells Valley, infraestrutura, auditoria de dados, UI/UX, cadastro empresarial inteligente e gestão automática/manual de módulos.

Não existem issues abertas funcionando como backlog oficial. Atualmente, as pendências estão distribuídas principalmente em `STATUS.md`, `docs/ROADMAP.md`, `docs/EXECUTION_PLAN.md`, documentos especializados e descrições de pull requests já encerrados. Isso cria risco de perda de rastreabilidade e de declaração prematura de conclusão.

## 3. Pendências críticas

### 3.1 Publicar e homologar o ambiente externo definitivo

**Categoria:** Crítica  
**Necessidade:** concluir a publicação real no Cloudflare Pages ou no ambiente definitivo aprovado, configurar as credenciais operacionais fora do repositório e validar o domínio público final.  
**Inclui:**

- disponibilizar `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID` por cofre ou secrets;
- realizar, pelo titular, os aceites jurídicos exigidos pelo provedor;
- validar DNS, HTTPS, cache, fallback SPA e headers de segurança;
- registrar a URL pública oficial e substituir referências temporárias.

**Impacto:** sem essa etapa, a aplicação permanece validada principalmente em ambiente local ou temporário, sem homologação pública definitiva.

### 3.2 Conectar o front-end ao API Hub público e aos microsserviços reais

**Categoria:** Crítica  
**Necessidade:** configurar `VITE_API_HUB_URL` público e executar as jornadas contra os 25 microsserviços em ambiente externo.  
**Inclui:** autenticação, autorização, CRUD, persistência, upload, pagamentos sandbox, auditoria, eventos, outbox e tratamento de falhas.  
**Impacto:** o fallback local demonstra a interface, mas não comprova o funcionamento integrado de produção.

### 3.3 Reexecutar a auditoria integral das rotas no ambiente publicado

**Categoria:** Crítica  
**Necessidade:** repetir a auditoria automatizada das 335 rotas React contra o API Hub e a infraestrutura pública.  
**Critérios mínimos:** ausência de erros JavaScript, ausência de telas travadas, formulários funcionais, controles habilitados, persistência correta, autenticação válida e respostas coerentes dos serviços.  
**Impacto:** a aprovação local não substitui a homologação ponta a ponta.

### 3.4 Proteger e governar a assinatura Android de produção

**Categoria:** Crítica  
**Necessidade:** armazenar o keystore e as credenciais de assinatura em cofre seguro, criar backup controlado e definir formalmente o uso de Play App Signing e da upload key.  
**Impacto:** a perda da chave ou das senhas pode impedir futuras atualizações do aplicativo publicado.

### 3.5 Homologar autenticação Google real no APK

**Categoria:** Crítica  
**Necessidade:** executar o login completo com conta de teste real, obter o token, validar sessão, renovação, logout, cancelamento, erro de rede e vínculo com o backend.  
**Impacto:** o acionamento do Credential Manager foi validado, mas o fluxo real de ponta a ponta ainda depende de conta Google disponível no dispositivo de teste.

## 4. Pendências de prioridade alta

### 4.1 Concluir sincronização remota do Google Stitch

**Categoria:** Alta  
**Necessidade:** fornecer `STITCH_API_KEY` por secret e executar a sincronização remota dos projetos e telas.  
**Escopo imediato:** gerar e validar a tela `finance/entity_valley_gold_ledger_entries` e verificar qualquer tela adicionada após o último manifesto.  
**Impacto:** o manifesto prevê 181 telas, mas a última evidência registrou 180 geradas e uma pendente.

### 4.2 Homologar infraestrutura produtiva e serviços externos

**Categoria:** Alta  
**Necessidade:** validar billing, IAM, provedores reais, cluster produtivo, bancos gerenciados, mensageria, observabilidade, secrets, backups, restauração e políticas de rede.  
**Impacto:** os testes locais e manifests não comprovam capacidade, segurança e resiliência do ambiente real.

### 4.3 Validar workflows do GitHub Actions após as integrações recentes

**Categoria:** Alta  
**Necessidade:** confirmar o resultado dos workflows no `main`, especialmente segurança, testes, banco de dados, Android, web, Docker, artefatos gerados e publicação.  
**Observação:** houve merges recentes com conflitos resolvidos em arquivos sensíveis, incluindo workflows, configurações VS Code, migrations, scripts de validação, STATUS e aplicações.  
**Impacto:** conflitos resolvidos incorretamente podem manter o código compilável localmente e ainda quebrar gates remotos.

### 4.4 Criar backlog oficial por issues ou project board

**Categoria:** Alta  
**Necessidade:** transformar as pendências deste documento em itens rastreáveis, com responsável, prioridade, dependências, critérios de aceite e evidências.  
**Impacto:** sem backlog oficial, pendências ficam escondidas em documentos extensos e PRs encerrados.

### 4.5 Auditar consistência entre documentação e implementação

**Categoria:** Alta  
**Necessidade:** confrontar `STATUS.md`, `ROADMAP.md`, `EXECUTION_PLAN.md`, contratos OpenAPI, catálogo de módulos, manifests Stitch, migrations e código executável.  
**Impacto:** o repositório possui grande volume de declarações de conclusão; divergências podem gerar uma fotografia excessivamente otimista do estado real.

## 5. Pendências de prioridade média

### 5.1 Revalidar o emulador Android e a instalação do APK

**Categoria:** Média  
**Necessidade:** aguardar boot completo, confirmar `sys.boot_completed`, instalar novamente o APK e repetir smoke tests.  
**Impacto:** evita tratar um emulador parcialmente inicializado como evidência final de execução.

### 5.2 Centralizar evidências de validação

**Categoria:** Média  
**Necessidade:** registrar, por versão, logs, relatórios, screenshots, artefatos, hashes, URLs e resultados dos testes.  
**Impacto:** facilita auditoria e impede que evidências antigas sejam confundidas com o estado atual.

### 5.3 Revisar dados demonstrativos e separação de ambiente

**Categoria:** Média  
**Necessidade:** garantir separação explícita entre dados fictícios, sandbox, homologação e produção, incluindo banners e flags de ambiente.  
**Impacto:** reduz risco de demonstrações serem interpretadas como transações reais.

### 5.4 Verificar integridade dos contratos após padronização massiva

**Categoria:** Média  
**Necessidade:** validar compatibilidade entre DTOs, formulários, persistência, OpenAPI, eventos e migrations de todas as entidades alteradas.  
**Impacto:** mudanças em massa podem introduzir campos sem persistência, tipos incompatíveis ou telas sem cobertura real.

### 5.5 Revisar performance, acessibilidade e responsividade em dispositivos reais

**Categoria:** Média  
**Necessidade:** executar Lighthouse, Web Vitals, testes de teclado, leitor de tela, contraste, zoom, telas pequenas e aparelhos Android de desempenho limitado.  
**Impacto:** builds e testes funcionais não garantem experiência adequada para usuários reais.

## 6. Pendências secundárias

### 6.1 Ampliar documentação funcional para clientes pessoa física e jurídica

**Categoria:** Secundária  
**Necessidade:** descrever cada módulo, serviço e microsserviço em linguagem comercial, incluindo aplicação, benefícios, comodidade, usabilidade, custo e economia para o cliente, sem expor custos internos, margens ou lucros.  
**Impacto:** melhora apresentação, onboarding, vendas e entendimento do ecossistema.

### 6.2 Padronizar nomenclatura e idioma do front-end

**Categoria:** Secundária  
**Necessidade:** concluir revisão pt-BR, pluralização, acentuação, mensagens de erro, labels, ajuda contextual e manutenção apenas dos termos estrangeiros consolidados no Brasil.  
**Impacto:** melhora clareza e reduz fricção para públicos diversos.

## 7. Itens antigos reclassificados

### 7.1 Ativos oficiais da marca Valley

**Status:** Resolvido em princípio, aguardando validação técnica.  
**Ação de verificação:** confirmar que todas as superfícies usam exclusivamente o ativo oficial vigente, sem redesenho, alteração de linhas, formas ou cores.

### 7.2 Ativos oficiais da marca Valley Riders

**Status:** Resolvido em princípio, aguardando validação técnica.  
**Ação de verificação:** confirmar presença do PNG oficial com fundo transparente e ausência de versões provisórias ou modificadas.

## 8. Próxima atividade recomendada

1. Executar e registrar todos os workflows do `main`.
2. Publicar o ambiente externo definitivo.
3. Configurar o API Hub público.
4. Rodar a auditoria ponta a ponta das 335 rotas.
5. Homologar login Google real e assinatura Android.
6. Sincronizar a tela Stitch pendente.
7. Converter este documento em backlog rastreável.

## 9. Critério de encerramento

Uma pendência somente poderá ser marcada como concluída quando houver:

- implementação versionada;
- teste automatizado ou procedimento de validação reproduzível;
- evidência do ambiente correto;
- ausência de bloqueio externo não declarado;
- atualização deste documento com data e referência da evidência.

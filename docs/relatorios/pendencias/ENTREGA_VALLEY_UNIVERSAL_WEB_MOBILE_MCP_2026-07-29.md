# Entrega Valley Universal — Web, Mobile e MCP

- Data: 29/07/2026;
- classificação: `Pendências > Técnico`;
- público-alvo: Pessoa Física (B2C), Pessoa Jurídica (B2B) e Equipe Técnica;
- branch: `feat/valley-universal-web-mobile-20260729`;
- status geral: implementação concluída em branch isolada, aguardando validação conjunta do pull request e decisão de merge.

## 1. Aplicação web/PWA

- nome: Valley Universal;
- AppDeploy ID: `84e9680fcfa2a84551`;
- URL: `https://84e9680fcfa2a84551.v2.appdeploy.ai/`;
- resultado AppDeploy: pronto;
- testes E2E: 4 de 4 aprovados;
- erros de frontend: nenhum;
- erros de backend: nenhum;
- erros de rede no QA: nenhum.

### Funções

- entrada como usuário;
- entrada administrativa separada;
- autenticação Google;
- perfil persistente;
- contexto Pessoal;
- contexto Rider;
- contexto Business;
- contexto One Service;
- contexto PDV;
- solicitação de ativação de contexto;
- aprovação administrativa protegida;
- navegação desktop e mobile;
- manifesto PWA;
- service worker;
- instalação pela tela inicial;
- notificações mediante ação explícita;
- modo de demonstração claramente identificado.

## 2. Aplicativo Android Universal

Módulo: `apps/valley-android/universal`.

### Entregas

- WebView endurecida;
- HTTPS obrigatório;
- política de mesma origem;
- login Google em janela separada;
- destinos externos fora da WebView principal;
- bloqueio de conteúdo misto;
- acesso local a arquivos desabilitado;
- Safe Browsing quando suportado;
- tela de recuperação de conexão;
- restauração de estado;
- ícone gerado diretamente do ativo oficial Valley;
- testes unitários da política de URL;
- lint Android;
- build debug;
- checksum SHA-256;
- publicação como artifact do GitHub Actions.

Workflow: `.github/workflows/valley-universal-android-apk.yml`.

Saídas esperadas:

- `Valley-Universal-1.0.0-debug.apk`;
- `Valley-Universal-1.0.0-debug.apk.sha256`.

## 3. Valley Universal MCP

Diretório: `apps/valley-universal-mcp`.

### Ferramentas

- `valley_list_contexts`;
- `valley_get_release_status`;
- `valley_open_app`.

A versão 1.0 é somente leitura. O MCP não autentica no lugar do Valley, não concede permissões, não aprova cadastros e não movimenta valores.

Workflow: `.github/workflows/valley-universal-mcp.yml`.

Validações:

- instalação limpa das dependências;
- TypeScript estrito;
- inicialização do servidor;
- disponibilidade do endpoint `/mcp`.

## 4. Aplicativos especializados preservados

A implementação não remove nem substitui:

- Valley consumidor;
- Valley Rider;
- Valley Business;
- One Service;
- AIO Admin;
- Valley PDV;
- All in One PDV Desktop offline.

O Valley Universal passa a ser a vertente flexível. Os aplicativos especializados continuam sendo a vertente direta e mais restrita.

## 5. Limites da entrega atual

- o APK gerado pelo workflow é debug e não substitui uma versão release assinada;
- publicação na Play Store exige keystore, assinatura, conta de desenvolvedor e materiais de loja;
- instalação em iPhone está disponível como PWA; um pacote nativo iOS exige projeto e assinatura Apple;
- o MCP foi versionado, mas sua publicação externa é separada do AppDeploy;
- os dados funcionais atuais do AppDeploy não substituem todas as integrações do API Hub de produção;
- os documentos definitivos de privacidade e termos ainda deverão ser associados ao fluxo de autenticação;
- o merge na `main` não é executado automaticamente.

## 6. Critério para liberação

A liberação para `main` deverá ocorrer somente após:

1. aprovação dos workflows Android e MCP;
2. revisão do pull request;
3. confirmação dos ativos oficiais;
4. validação do fluxo de login real;
5. definição de assinatura Android de produção;
6. aprovação expressa do responsável pelo projeto.

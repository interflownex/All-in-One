# All in One PDV Desktop

Aplicativo instalável para Windows, construído para continuar operando mesmo quando a internet ou a página web estiverem indisponíveis.

## Entregas geradas

- Instalador NSIS para Windows, com atalho na área de trabalho e no menu Iniciar.
- Executável portátil para Windows 64 bits.
- Executável portátil para Windows 32 bits.
- Base local persistente em JSON transacional com cópia automática de segurança.
- Fila de sincronização com idempotência para enviar eventos ao servidor quando a conexão voltar.

## Funcionalidades locais

- abertura e fechamento de caixa;
- suprimento e sangria com PIN gerencial;
- catálogo, preço, custo, código de barras e estoque;
- carrinho, cupom, desconto manual e aprovação gerencial;
- pagamento em dinheiro, Pix, cartão, carteira e pagamento misto;
- fila de pedidos: recebido, em preparo, pronto e entregue;
- estorno com recomposição do estoque;
- impressão de comprovante pelo Windows;
- promoções presenciais e geolocalizadas;
- relatórios, ticket médio, formas de pagamento e produtos mais vendidos;
- exportação CSV;
- backup e restauração manual;
- auditoria local;
- sincronização opcional com API Hub.

## Operação offline

A interface, as regras e a base de dados ficam dentro do computador. A criação de vendas, baixa de estoque, controle de caixa, pedidos, impressão e relatórios não fazem chamadas obrigatórias à internet.

Quando a sincronização está habilitada, cada alteração gera um evento na fila local. O aplicativo tenta enviá-lo ao endpoint configurado e remove da fila somente após confirmação do servidor. A chave de idempotência impede a criação duplicada da mesma venda.

## Local dos dados

O caminho exato é exibido em **Configurações > Segurança e cópias**. O aplicativo mantém:

- `pdv-data.json`: base principal;
- `pdv-data.backup.json`: cópia anterior automática;
- `pdv-secrets.json`: token da API criptografado pelo mecanismo seguro do Windows.

A desinstalação não apaga automaticamente a base de dados.

## Desenvolvimento

```bash
cd apps/all-in-one-pdv-desktop
npm install
npm test
npm start
```

## Gerar os executáveis Windows

Em um computador Windows:

```bash
npm install
npm test
npm run dist:win
```

Os arquivos serão gravados na pasta `dist/`.

## Critérios de segurança

- `contextIsolation` habilitado;
- `nodeIntegration` desabilitado no renderer;
- API restrita pelo preload;
- política CSP local;
- token remoto criptografado pelo Windows;
- nenhum segredo incluído no Git;
- PIN armazenado como hash SHA-256 com namespace da aplicação;
- cópia anterior preservada antes de cada gravação da base;
- idempotência em toda venda local.

## Homologação necessária antes da produção fiscal

A operação comercial local está pronta. A emissão fiscal, o TEF/SmartPOS e o envio de notificações ao aplicativo do cliente dependem das credenciais e contratos dos provedores escolhidos. A ausência dessas credenciais não bloqueia a venda offline, mas deixa os eventos aguardando sincronização.

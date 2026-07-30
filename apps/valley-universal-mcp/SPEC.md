# SPEC — Valley Universal MCP

## 1. Objetivo

Disponibilizar uma camada MCP segura e somente leitura para que assistentes compatíveis possam explicar o Valley Universal, listar seus contextos, consultar o estado público da entrega e orientar a abertura do aplicativo web.

O MCP não autentica usuários no lugar do Valley, não concede papéis, não aprova cadastros e não executa operações financeiras, administrativas ou comerciais.

## 2. Usuários simultâneos

A experiência é projetada para dois participantes:

- a pessoa, que decide qual contexto deseja usar;
- o assistente, que consulta ferramentas estruturadas e apresenta a informação de forma compreensível.

## 3. Fonte funcional

- aplicação: Valley Universal;
- AppDeploy ID: `84e9680fcfa2a84551`;
- URL pública: `https://84e9680fcfa2a84551.v2.appdeploy.ai/`;
- contextos: Pessoal, Rider, Business, One Service e PDV;
- administração: ambiente separado, autenticado e sujeito a allowlist.

## 4. Ferramentas da versão 1.0

### `valley_list_contexts`

Retorna os contextos disponíveis, seus públicos e suas finalidades.

### `valley_get_release_status`

Retorna o estado público da versão web/PWA, Android e MCP.

### `valley_open_app`

Retorna a URL oficial do Valley Universal e registra qual contexto o usuário pretende acessar. A seleção não concede autorização e deverá ser confirmada dentro do aplicativo após o login.

## 5. Limites de segurança

- nenhuma ferramenta de mutação nesta versão;
- nenhuma credencial no código ou na resposta das ferramentas;
- nenhuma concessão de acesso por parâmetro local;
- nenhuma ferramenta administrativa sem OAuth, confirmação explícita e integração com o API Hub;
- nenhuma exposição de IDs internos, tokens, segredos ou dados pessoais;
- a autoridade final de acesso permanece no backend do Valley;
- o MCP não substitui RBAC, ABAC, homologação, KYC, vínculo empresarial ou auditoria.

## 6. Futuras ferramentas condicionadas

Somente poderão ser adicionadas depois da integração autenticada com o API Hub:

- consultar os contextos autorizados do usuário;
- solicitar ativação de contexto;
- consultar pedidos, entregas ou agenda próprios;
- trocar o contexto ativo;
- abrir uma tarefa no aplicativo com confirmação da pessoa.

Aprovação administrativa, estorno, pagamento, alteração financeira, exclusão e concessão de papéis não deverão ser expostos sem uma revisão de segurança específica.

## 7. Critérios de aceite

- servidor Skybridge compila com tipagem estrita;
- ferramentas retornam conteúdo estruturado;
- nenhuma ferramenta altera dados;
- a URL retornada corresponde à aplicação publicada;
- os nomes e descrições dos contextos correspondem à diretriz oficial;
- o servidor exporta `AppType` para clientes tipados;
- o processo pode ser iniciado localmente pela porta configurada;
- a documentação deixa explícito que autenticação e autorização pertencem ao Valley.

## 8. Estado

Scaffold MCP implementado e versionado. A publicação externa do endpoint MCP permanece separada da publicação AppDeploy e exige ambiente Skybridge/Alpic ou infraestrutura compatível.

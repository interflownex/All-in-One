# Identidade Visual do Grupo All in One

## Regra mandatória

Toda tela, aplicativo, mockup, documento visual e entrega gerada por qualquer agente deve usar exclusivamente os ativos canônicos declarados em `config/branding/authorized_assets.json`.

As marcas abrangidas são:

- All in One, marca guarda-chuva do ecossistema;
- Valley, marca das superfícies Valley;
- Valley Riders, marca das jornadas de motoristas, entregadores e viagens.

## Regra de transparência

- todo favicon deve ter fundo totalmente transparente;
- toda logomarca exportada para uso digital deve ter fundo externo totalmente transparente;
- não é permitido inserir fundo branco, preto, cinza, colorido, degradê, caixa sólida, moldura fechada ou placa de preenchimento atrás do ativo;
- a regra vale para favicon, símbolo isolado, logotipo, logomarca completa, versão horizontal, versão vertical, versão reduzida, ícone de aplicativo, ícone de menu, avatar institucional e qualquer outra derivação visual.

## Ativos canônicos

- All in One: `assets/brand/all-in-one-logo-official.png`;
- Valley: `assets/brand/valley-logo-official.png`;
- Valley Riders: `assets/brand/valley-riders-logo-official.png`, cuja utilização permanece bloqueada até a ingestão do binário original aprovado `LOGO OFICIAL VALLEY RIDERS_2.png`;
- manifesto de ativos: `config/branding/authorized_assets.json`;
- contrato de identidade: `config/branding/brand_identity.json`;
- inventário humano: `assets/brand/README.md`.

Os arquivos reconstruídos `all-in-one-logo-transparent.svg` e `valley-logo-transparent.svg` não são ativos canônicos e não podem substituir as artes originais.

## Operações permitidas sem nova autorização

1. remover somente o fundo externo, sem tocar em nenhuma parte da marca;
2. redimensionar proporcionalmente, preservando a proporção original.

Qualquer outra alteração exige autorização explícita do proprietário da marca.

## Alterações proibidas

É proibido redesenhar, recolorir, recortar, girar, distorcer, mudar tipografia, alterar linhas, curvas, formas ou composição, aplicar filtros, máscaras, opacidade decorativa ou criar símbolo alternativo.

Quando o arquivo original não estiver disponível, nenhum agente pode fabricar uma aproximação. A utilização deve permanecer bloqueada até a recuperação do binário oficial.

## Remediação imediata

Ao identificar uma violação clara e objetiva, o próprio agente que a encontrou deve:

1. executar `python3 scripts/check_brand_integrity.py --fix`;
2. restaurar o ativo canônico sem alterar a arte;
3. executar `python3 scripts/check_brand_integrity.py` e as validações relevantes;
4. registrar e sincronizar a correção no Git.

Não é necessário pedir nova autorização para restaurar a conformidade. Essa autorização não permite decisões criativas nem modificações na arte oficial.

## Aplicação no Stitch e em outros geradores

Os prompts e contratos de geração devem carregar as mesmas regras. Toda tela deve posicionar a marca All in One no shell ou cabeçalho global. Superfícies Valley também exibem Valley. Superfícies Riders somente poderão exibir Valley Riders quando o ativo original estiver versionado.

## Regras de uso

- preservar área de respiro mínima de 16 px;
- usar largura mínima de 120 px para All in One e 104 px para Valley;
- manter textos alternativos `All in One`, `Valley` e `Valley Riders`;
- não colocar dados sensíveis, documentos, biometria, chaves ou tokens em exemplos de marca.

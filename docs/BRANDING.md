# Identidade Visual All-in-One E Valley

## Regra Mandatoria

Toda tela, app, mockup, documento visual e entrega gerada no Stitch deve usar a
marca All-in-One como marca guarda-chuva. Apps Valley tambem devem exibir a logo
Valley de forma consistente.

## Regra de transparencia

- todo favicon deve ter fundo totalmente transparente;
- toda logomarca exportada para uso digital deve ter fundo totalmente transparente;
- nao e permitido inserir fundo branco, preto, cinza, colorido, degradê, caixa
  solida, moldura fechada ou placa de preenchimento atras do ativo;
- a regra vale para favicon, simbolo isolado, logotipo, logomarca completa,
  versao horizontal, versao vertical, versao reduzida, icone de app, icone de
  menu, avatar institucional e qualquer outra derivacao visual.

## Favicons adaptativos

O projeto usa favicons SVG transparentes com variacao automatica por contexto de
tema. As versoes oficiais sao:

- V1 para leitura forte em contextos claros;
- V2 como fallback equilibrado;
- V3 para maior contraste em temas escuros.

## Ativos canonicos

- All-in-One transparente: `assets/brand/all-in-one-logo-transparent.svg`
- All-in-One favicon: `assets/brand/favicon-all-in-one.svg`
- Valley transparente: `assets/brand/valley-logo-transparent.svg`
- Valley favicon: `assets/brand/favicon-valley.svg`
- Contrato versionado: `config/branding/brand_identity.json`

## Aplicacao No Stitch

O `scripts/stitch_orchestrator.py` injeta o contrato de marca nos prompts. Toda
tela deve posicionar a marca All-in-One no shell/header global. Quando a tela
atender `valley`, `valley-business` ou `valley-rider`, o prompt tambem exige a
logo Valley padronizada, sem distorcer, recolorir, cortar ou recriar o ativo.

## Regras De Uso

- Preservar area de respiro minima de 16 px.
- Usar largura minima de 120 px para All-in-One e 104 px para Valley.
- Manter texto alternativo `All-in-One` e `Valley`.
- Nao colocar dados sensiveis, documentos, biometria, chaves ou tokens em
  exemplos de marca.

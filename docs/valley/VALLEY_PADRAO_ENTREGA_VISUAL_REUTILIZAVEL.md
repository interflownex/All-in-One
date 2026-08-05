# VALLEY — Padrão Mandatório de Entrega Visual Reutilizável

**Projeto:** All in One + Valley  
**Classificação:** Pendências / Técnico / Equipe Técnica  
**Público-alvo:** Pessoa Física (B2C) e Equipe Técnica  
**Status:** Diretriz operacional persistente  
**Versão:** 1.0  
**Data de formalização:** 2026-08-05  
**Responsável:** Anderson Carvalho Nazarete

## 1. Objetivo

Definir o padrão obrigatório para todas as próximas entregas visuais do aplicativo VALLEY.

Este padrão abrange:

- tamanho e consistência da tipografia;
- uso da logomarca oficial;
- construção de telas;
- criação de elementos PNG reutilizáveis;
- organização dos pacotes ZIP;
- manifesto de integridade;
- arquivo Markdown para a IA desenvolvedora;
- links individuais de download entregues no chat.

## 2. Regra de precedência

Esta diretriz prevalece sobre versões anteriores de entrega visual sempre que houver divergência.

Uma tela aprovada somente poderá ser modificada por solicitação expressa de Anderson Carvalho Nazarete.

## 3. Logomarca oficial

A logomarca oficial VALLEY é um ativo visual imutável.

### Obrigatório

- usar o arquivo oficial do projeto;
- preservar cores, linhas, formas, tipografia e proporções;
- redimensionar somente de forma proporcional;
- utilizar a marca como fonte da identidade visual da tela;
- trabalhar prioritariamente com fundo branco e tons claros derivados da marca.

### Proibido

- redesenhar a logomarca;
- alterar cores;
- alterar a tipografia;
- remover ou incluir elementos;
- deformar;
- substituir por uma interpretação;
- usar uma marca gerada por IA como substituta do arquivo oficial.

### Caminho canônico no repositório

```text
assets/brand/valley-logo-official.png
```

## 4. Padrão tipográfico global

A tipografia deve oferecer leitura confortável em smartphone e reduzir desistências durante cadastros e jornadas longas.

A escala abaixo passa a ser o padrão do aplicativo.

### Tokens para implementação

| Uso | Tamanho recomendado |
|---|---:|
| Texto auxiliar pequeno | 16 sp |
| Corpo de texto | 18 sp |
| Campo de formulário | 18 sp |
| Rótulo de campo | 18 sp, semibold |
| Subtítulo de seção | 20 sp |
| Texto de botão | 22 sp, bold |
| Título de tela | 32 sp, bold |
| Título principal / hero | 36 a 40 sp, bold |

### Regras

- não reduzir a fonte de um botão isolado para acomodar uma palavra maior;
- todos os botões equivalentes devem usar o mesmo tamanho de fonte;
- aumentar a largura ou o espaço interno antes de diminuir a fonte;
- respeitar as configurações de tamanho de fonte e acessibilidade do sistema;
- usar altura de linha entre 1,3 e 1,5;
- garantir contraste suficiente entre texto e fundo;
- textos essenciais não podem depender apenas de imagem.

### Referência para mockups em 1080 px de largura

| Uso | Tamanho de referência |
|---|---:|
| Texto auxiliar | 24 a 28 px |
| Campo / placeholder | 34 a 38 px |
| Rótulo do campo | 32 a 34 px |
| Botão | 42 a 46 px |
| Título de tela | 56 a 60 px |
| Título principal | 60 a 68 px |

## 5. Padrão visual dos botões

Os botões principais da VALLEY devem seguir o padrão visual aprovado.

### Aparência

- material plastificado ou acrílico translúcido;
- alto relevo claramente perceptível;
- sombreamento suave e visível;
- reflexo luminoso superior;
- bordas arredondadas;
- tons claros baseados na identidade da marca;
- texto em baixo relevo ou depressão;
- texto em roxo profundo;
- sem imagem e sem ícone quando o botão for baseado em intenção.

### Elementos obrigatórios no pacote

Para cada conjunto de botões, entregar:

1. botão base sem texto e com fundo transparente;
2. cada botão rotulado em PNG transparente;
3. grade completa dos botões, quando aplicável;
4. especificação técnica para reconstrução com componentes reais.

## 6. Elementos reutilizáveis

Os arquivos entregues não podem ser simples recortes da tela montada.

Cada elemento deve ser criado como um ativo independente e reutilizável.

### Exemplos

- botão base sem texto;
- botões rotulados;
- moldura do avatar;
- avatar de exemplo;
- fundo base;
- bloco de título;
- cabeçalho;
- grade de botões;
- sombras separadas;
- brilhos separados;
- logomarca oficial copiada sem alterações.

### Transparência

Usar PNG transparente em todos os elementos que não necessitam de fundo opaco.

## 7. Foto de perfil

Quando a tela possuir foto de perfil:

- posicionar no canto superior direito;
- utilizar tamanho reduzido e proporcional;
- colocar a foto dentro de um aro visual baseado no aro da logomarca;
- não inserir texto embaixo;
- o toque deve abrir o perfil do usuário;
- o avatar é separado da logomarca oficial;
- o avatar não pode substituir ou alterar o ícone do aplicativo.

Para mockups, utilizar somente pessoa fictícia, imagem licenciada ou imagem criada especificamente para o modelo.

## 8. Comportamento da logomarca na Home

Quando definido na jornada:

- tocar na logomarca abre o dock com todos os módulos;
- tocar no avatar abre o perfil;
- as duas áreas devem possuir alvos de toque independentes;
- a logomarca não deve ser deslocada, reduzida ou modificada para acomodar o avatar, salvo ordem expressa.

## 9. Estrutura obrigatória de cada pacote ZIP

O arquivo ZIP deve ser nomeado de forma clara:

```text
Tela_<numero>_VALLEY_Pacote_Completo.zip
```

### Ordem obrigatória

1. tela pronta;
2. elementos PNG reutilizáveis;
3. arquivo Markdown;
4. manifesto JSON.

### Estrutura sugerida

```text
Tela_<numero>_VALLEY_Pacote_Completo/
└── Pendencias/
    └── Tecnico/
        └── Equipe_Tecnica/
            └── Tela_<numero>/
                ├── PNGs/
                │   ├── 01_tela_<numero>_pronta.png
                │   ├── 02_fundo_base.png
                │   ├── 03_logomarca_oficial_valley.png
                │   ├── 04_elemento_reutilizavel.png
                │   └── ...
                └── Tela_<numero>_Diretrizes.md
└── MANIFESTO_SHA256.json
```

## 10. Regra da primeira imagem

O primeiro arquivo visual do pacote deve ser sempre:

```text
01_tela_<numero>_pronta.png
```

Essa imagem apresenta o resultado final para aprovação imediata.

## 11. Arquivo Markdown obrigatório

Cada pacote deve incluir um Markdown contendo:

- projeto;
- classificação;
- público-alvo;
- objetivo da tela;
- imagem da tela pronta;
- inventário de arquivos;
- regras visuais;
- regras funcionais;
- dimensões;
- tipografia;
- acessibilidade;
- estados da tela;
- comportamento dos botões;
- comportamento da logomarca;
- comportamento do avatar;
- critérios de aceite;
- instruções para a IA desenvolvedora;
- nomes exatos dos ativos.

## 12. Manifesto JSON obrigatório

O arquivo deve se chamar:

```text
MANIFESTO_SHA256.json
```

Para cada arquivo, registrar:

```json
{
  "arquivo": "caminho/relativo/arquivo.png",
  "sha256": "hash_do_arquivo",
  "bytes": 123456,
  "mime_type": "image/png",
  "largura": 1080,
  "altura": 2400,
  "fundo_transparente": true
}
```

Para arquivos não visuais, largura, altura e transparência podem ser omitidas.

## 13. Nomenclatura

Usar:

- números no início para ordenar;
- nomes em português;
- letras minúsculas;
- palavras separadas por `_`;
- nenhum nome genérico como `imagem1.png`;
- nenhuma sequência opaca sem significado.

Exemplo:

```text
07_botao_base_translucido_sem_texto.png
08_botao_comprar.png
09_botao_vender.png
```

## 14. Links obrigatórios no chat

Toda entrega deve conter links separados para:

1. baixar o ZIP completo;
2. baixar somente a tela pronta;
3. baixar somente o Markdown;
4. baixar somente o manifesto JSON.

Quando solicitado, também fornecer links individuais para elementos específicos.

## 15. Critérios de aceite

A entrega somente é considerada completa quando:

- a logomarca oficial foi preservada;
- a tela pronta está em primeiro lugar;
- os elementos são reutilizáveis e não simples recortes;
- os PNGs reutilizáveis possuem transparência adequada;
- existe botão base sem texto quando houver botões;
- todos os elementos estão nomeados;
- o Markdown está presente;
- o manifesto JSON está presente;
- os hashes foram calculados;
- os links individuais foram fornecidos;
- a escala tipográfica global foi aplicada;
- a tela aprovada não foi alterada sem autorização.

## 16. Diretriz resumida para agentes e IAs

```yaml
valley_visual_delivery_standard:
  mandatory: true
  official_logo:
    immutable: true
    canonical_path: "assets/brand/valley-logo-official.png"

  typography:
    body_sp: 18
    input_sp: 18
    field_label_sp: 18
    subtitle_sp: 20
    button_sp: 22
    screen_title_sp: 32
    hero_title_sp: "36-40"
    preserve_equal_button_font_size: true
    respect_system_font_scaling: true

  reusable_assets:
    required: true
    transparent_png_when_applicable: true
    screen_crops_are_not_reusable_assets: true

  zip:
    required: true
    first_file: "01_tela_<numero>_pronta.png"
    include:
      - "tela pronta"
      - "PNGs reutilizáveis"
      - "Markdown"
      - "MANIFESTO_SHA256.json"

  chat_downloads:
    - "ZIP completo"
    - "imagem pronta"
    - "Markdown"
    - "manifesto JSON"

  buttons:
    material: "plastificado/acrílico translúcido"
    high_relief: true
    debossed_text: true
    base_without_text_required: true

  approved_screen:
    modify_only_with_explicit_authorization: true
```

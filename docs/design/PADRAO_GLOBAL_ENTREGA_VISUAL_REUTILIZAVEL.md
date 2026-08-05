# Padrão Global de Entrega Visual Reutilizável

**Projeto:** All in One + Valley  
**Classificação:** Pendências / Técnico / Equipe Técnica  
**Público-alvo:** Pessoa Física (B2C), Pessoa Jurídica (B2B) e Equipe Técnica  
**Versão:** 1.0.0  
**Data:** 05/08/2026 01:03, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/global-visual-delivery-standard-2026-08-05`

## 1. Objetivo

Esta diretriz torna obrigatório, em todos os aplicativos atuais e futuros do repositório, o mesmo padrão de:

- legibilidade;
- identidade visual;
- preservação das marcas oficiais;
- construção de botões e componentes;
- criação de elementos PNG realmente reutilizáveis;
- empacotamento ZIP;
- documentação Markdown;
- manifesto de integridade JSON;
- links individuais de download.

A política executável correspondente fica em `config/ui/global_visual_delivery_policy.json`.

## 2. Escopo obrigatório

A regra se aplica automaticamente a projetos localizados em:

- `apps/`;
- `desktop/`;
- `frontend/`;
- `mobile/`;
- `web/`.

Abrange, no mínimo:

- All in One Web e Mobile;
- VALLEY Consumidor;
- VALLEY Business;
- VALLEY Rider;
- AIO Admin Web e Mobile;
- PDV Desktop;
- novos aplicativos incorporados ao repositório.

Nenhum aplicativo pode desativar localmente esta política.

## 3. Fontes de verdade

- Ativos autorizados: `config/branding/authorized_assets.json`.
- Identidade visual: `config/branding/brand_identity.json`.
- Ativos oficiais: `assets/brand/`.
- Política global: `config/ui/global_visual_delivery_policy.json`.
- Validador: `scripts/validate_global_visual_delivery.py`.
- Gate de CI: `.github/workflows/global-visual-delivery.yml`.

## 4. Tipografia global

A tipografia deve ser confortável em smartphone e reduzir o abandono em cadastros e jornadas extensas.

### 4.1 Tokens para interfaces reais

| Uso | Tamanho mínimo recomendado |
|---|---:|
| Texto auxiliar pequeno | 16 sp |
| Corpo de texto | 18 sp |
| Campo de formulário | 18 sp |
| Rótulo de campo | 18 sp, semibold |
| Subtítulo de seção | 20 sp |
| Botão | 22 sp, bold |
| Título de tela | 32 sp, bold |
| Título principal | 36 a 40 sp, bold |

### 4.2 Referência para mockups com 1080 px de largura

| Uso | Faixa |
|---|---:|
| Texto auxiliar | 24 a 28 px |
| Campo e placeholder | 34 a 38 px |
| Rótulo do campo | 32 a 34 px |
| Texto de botão | 42 a 46 px |
| Título de tela | 56 a 60 px |
| Título principal | 60 a 68 px |

### 4.3 Regras de legibilidade

- Botões equivalentes usam a mesma fonte e o mesmo tamanho.
- É proibido reduzir apenas uma palavra para fazê-la caber.
- Aumentar largura, espaçamento ou altura antes de reduzir a fonte.
- Respeitar a escala de fonte configurada pelo sistema operacional.
- Usar altura de linha entre 1,3 e 1,5.
- Garantir contraste WCAG AA ou superior.
- Textos essenciais devem permanecer como componentes reais, não apenas dentro de imagens.

## 5. Governança de marca

As logomarcas oficiais são imutáveis.

Sem nova autorização expressa, somente são permitidos:

- redimensionamento proporcional;
- remoção exclusiva do fundo externo sem tocar na arte.

É proibido:

- redesenhar;
- recolorir;
- recortar;
- deformar;
- girar;
- trocar tipografia;
- alterar linhas, curvas, formas ou composição;
- substituir por aproximação ou imagem gerada.

Cada aplicativo deve usar o ativo oficial compatível com a sua identidade, conforme os manifestos de marca.

## 6. Botões de intenção

Botões como `Comprar`, `Vender`, `Contratar`, `Alugar`, `Consertar`, `Pagar`, `Receber` e `Trabalhar` devem seguir o padrão:

- sem imagem;
- sem ícone, salvo decisão funcional expressa;
- material plastificado ou acrílico translúcido;
- alto relevo claramente perceptível;
- sombra suave e visível;
- reflexo luminoso superior;
- bordas arredondadas;
- texto em baixo relevo ou depressão;
- mesma tipografia e mesmo tamanho entre botões equivalentes.

Quando exportados como artefatos, deve existir obrigatoriamente um botão base sem texto em PNG transparente.

## 7. Elementos reutilizáveis

Recortes de uma tela pronta não são considerados ativos reutilizáveis.

O pacote deve fornecer componentes independentes, criados separadamente, como:

- fundo base;
- logomarca oficial sem alteração;
- botão base sem texto;
- botões rotulados;
- moldura de avatar;
- avatar de exemplo;
- bloco de título;
- cabeçalho;
- sombra separada;
- brilho separado;
- grade de botões.

Usar PNG transparente sempre que o elemento não exigir fundo opaco.

## 8. Perfil e cabeçalho

Quando existir avatar:

- posicionar no canto superior direito;
- manter tamanho compacto;
- utilizar aro visual compatível com a linguagem da marca;
- não adicionar texto embaixo;
- tocar no avatar abre o perfil;
- o avatar não substitui nem altera a logomarca.

Em mockups, usar pessoa fictícia, imagem licenciada ou imagem criada especificamente para a demonstração.

Quando configurado, tocar na logomarca abre o dock com todos os módulos. Avatar e logomarca devem ter alvos de toque independentes.

## 9. Pacote obrigatório de entrega

Nome recomendado:

```text
Tela_<numero>_<aplicativo>_Pacote_Completo.zip
```

Ordem interna obrigatória:

1. `01_tela_<numero>_pronta.png`;
2. PNGs reutilizáveis nomeados;
3. arquivo Markdown;
4. `MANIFESTO_SHA256.json`.

A primeira imagem sempre deve mostrar o resultado final para aprovação imediata.

## 10. Markdown obrigatório

Cada pacote deve documentar:

- projeto;
- classificação;
- público-alvo;
- objetivo da tela;
- imagem pronta;
- inventário dos ativos;
- regras visuais e funcionais;
- dimensões;
- tipografia;
- acessibilidade;
- estados da tela;
- comportamento da marca;
- comportamento do avatar;
- comportamento dos botões;
- critérios de aceite;
- instruções para a IA desenvolvedora.

## 11. Manifesto JSON obrigatório

Nome:

```text
MANIFESTO_SHA256.json
```

Campos mínimos de cada arquivo:

```json
{
  "arquivo": "caminho/relativo/arquivo.png",
  "sha256": "hash",
  "bytes": 123456,
  "mime_type": "image/png"
}
```

Para imagens, incluir também:

```json
{
  "largura": 1080,
  "altura": 2400,
  "fundo_transparente": true
}
```

## 12. Links obrigatórios no chat

Toda entrega deve conter links separados para:

1. ZIP completo;
2. tela pronta;
3. Markdown;
4. manifesto JSON.

## 13. Telas aprovadas

Uma tela aprovada só pode ser modificada mediante autorização expressa do proprietário do projeto.

Adicionar um novo elemento não autoriza reposicionar, reduzir, ampliar ou redesenhar os elementos aprovados, salvo quando a solicitação disser isso de forma explícita.

## 14. Enforcement

O repositório executa:

```bash
python3 scripts/validate_global_visual_delivery.py
python3 -m pytest tests/test_global_visual_delivery_policy.py -q
```

O workflow `.github/workflows/global-visual-delivery.yml` executa essas verificações em mudanças que atinjam aplicativos, política, documentação, validadores ou testes.

Falha no contrato visual deve bloquear a integração até correção.

## 15. Critérios de aceite globais

- política marcada como obrigatória;
- opt-out local proibido;
- logomarca oficial preservada;
- tipografia mínima aplicada;
- componentes equivalentes com fonte consistente;
- PNGs reutilizáveis criados de forma independente;
- botão base sem texto incluído quando houver botões;
- ZIP ordenado corretamente;
- Markdown incluído;
- manifesto JSON incluído;
- links individuais fornecidos;
- tela aprovada não alterada sem autorização;
- CI verde no mesmo SHA da entrega.

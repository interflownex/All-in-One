# VALLEY Consumidor — Carrossel de mídia, detalhe do anúncio e comunicação protegida

## Classificação

- **Projeto:** All in One + Valley
- **Pasta lógica:** Pendências
- **Assunto:** Técnico
- **Público-alvo:** Pessoa Física (B2C) e Equipe Técnica
- **Aplicações:** `apps/valley` e empacotamento `apps/valley-flutter`
- **Módulos:** Marketplace e Stock
- **Branch:** `codex/valley-consumer-reference-ui-2026-08-04`
- **Pull Request:** #239
- **Status:** implementação versionada; validação completa dos pipelines pendente

## Visão do produto

Cada anúncio exibido no feed vertical do Marketplace ou do Estoque pode possuir diversas imagens e vídeos. A navegação deve separar claramente os dois gestos:

1. **Deslizar para cima ou para baixo:** muda de anúncio.
2. **Deslizar para a esquerda ou para a direita:** muda a imagem ou o vídeo do anúncio atual.
3. **Tocar na mídia:** abre a tela de detalhes do anúncio.

O toque na mídia não deve pausar nem alternar a reprodução do vídeo. O vídeo ativo é controlado pela visibilidade do anúncio e da página do carrossel.

## Requisitos funcionais mandatórios

### 1. Carrossel horizontal

- Preservar todas as mídias válidas recebidas do anúncio.
- Aceitar imagens e vídeos na mesma galeria.
- Dar prioridade ao vídeo principal quando fornecido.
- Utilizar a imagem principal como poster ou fallback.
- Remover URLs vazias e duplicadas.
- Usar paginação visual discreta para indicar a posição atual.
- Manter `scroll-snap` horizontal por página.
- Não interceptar a rolagem vertical quando o gesto for predominantemente vertical.

### 2. Reprodução de vídeo

- Reproduzir automaticamente somente o vídeo da página de mídia ativa.
- Manter o vídeo sem controles nativos de pausa no feed.
- Pausar vídeos que saírem da página horizontal ativa ou do anúncio visível.
- Manter `muted`, `playsInline` e `loop` no feed.
- Abrir o detalhe ao tocar no vídeo, sem executar `pause()` como efeito do toque.
- No detalhe, continuar exibindo a galeria completa.

### 3. Detalhe do anúncio

Ao tocar na imagem ou no vídeo, abrir uma superfície de detalhe contendo, quando disponíveis:

- galeria completa de imagens e vídeos;
- título do anúncio;
- preço;
- descrição completa;
- categoria e subcategoria;
- marca e modelo;
- SKU ou identificação pública do item;
- condição e disponibilidade;
- quantidade em estoque, quando pública;
- prazo estimado de entrega;
- avaliações e quantidade de avaliações;
- distância, quando aplicável ao Marketplace local;
- informação de anúncio patrocinado;
- origem Marketplace ou Estoque;
- ações `Falar no Valley`, `Adicionar ao carrinho` e `Comprar`.

Dados ausentes não devem ser inventados. O detalhe exibe somente campos realmente fornecidos pelo contrato público.

### 4. Perfil público do fornecedor

O detalhe pode exibir apenas dados públicos e necessários:

- nome público ou nome da loja;
- condição de fornecedor cadastrado ou verificado;
- região geral de atendimento;
- avaliação agregada;
- quantidade de avaliações;
- identificação da origem, como Marketplace local ou fornecedor homologado do Estoque.

### 5. Proibição de contato externo

É proibido expor no feed ou no detalhe:

- telefone;
- e-mail;
- WhatsApp;
- Telegram;
- Instagram;
- Facebook;
- outras redes sociais;
- site externo;
- endereço particular ou contato pessoal;
- qualquer campo que permita retirar a negociação do VALLEY.

O botão **Falar com o fornecedor** deve criar uma atividade interna com:

```json
{
  "activity_type": "supplier_message",
  "channel": "valley_in_app"
}
```

A comunicação deve permanecer autenticada, auditável e vinculada ao anúncio, ao comprador e ao fornecedor, sem revelar contatos externos.

## Contratos de mídia

O front-end deve aceitar galerias vindas de campos equivalentes a:

- `media`;
- `gallery`;
- `images`;
- `videos`;
- `primary_image_url`;
- `image_url`;
- `video_url`.

Cada mídia normalizada deve possuir:

```ts
type FeedMedia = {
  url: string;
  type: 'image' | 'video';
  posterUrl?: string;
  alt?: string;
};
```

A classificação de vídeo pode utilizar o tipo MIME informado ou extensões conhecidas, sem executar conteúdo arbitrário.

## Arquivos implementados

- `apps/valley/src/components/ProductFeed.tsx`
  - carrossel horizontal;
  - reprodução do vídeo ativo;
  - toque para abrir detalhes;
  - detalhe completo;
  - perfil público sanitizado do fornecedor;
  - aviso de privacidade e comunicação interna.

- `apps/valley/src/views/ProductViews.tsx`
  - preservação de galerias do Marketplace e do Estoque;
  - normalização de imagens, vídeos, características e fornecedor;
  - exclusão de campos externos de contato;
  - manutenção do canal `valley_in_app`.

- `apps/valley/src/product_feed.css`
  - rolagem horizontal com encaixe;
  - indicadores de página;
  - detalhe responsivo;
  - suporte a áreas seguras e redução de movimento.

- `apps/valley/src/main.tsx`
  - carregamento dos estilos do carrossel.

- `tests/test_valley_product_carousel_contract.py`
  - proteção contra regressões funcionais e de privacidade.

## Segurança e privacidade

- Não carregar HTML fornecido pelo anunciante.
- Não usar URLs de contato externo como ação do fornecedor.
- Não incluir contatos em telemetria, logs ou eventos do feed.
- Não confiar apenas no front-end para ocultar campos; o contrato público do backend também deve ser minimizado.
- Validar esquema, origem e protocolo das URLs de mídia.
- Manter autenticação para mensagens internas.
- Registrar correlação e auditoria sem copiar o conteúdo integral da conversa para logs comuns.
- Não revelar dados pessoais ou empresariais privados no perfil público.

## Acessibilidade

- Cada mídia clicável deve aceitar Enter e Espaço.
- O detalhe deve usar `role="dialog"` e `aria-modal="true"`.
- O botão de fechar precisa ter rótulo acessível.
- A paginação deve informar a posição atual da mídia.
- O carrossel não pode impedir a navegação por leitor de tela.
- Respeitar `prefers-reduced-motion`.

## Testes obrigatórios

1. Anúncio com uma imagem.
2. Anúncio com várias imagens.
3. Anúncio com vídeo e imagens.
4. Vídeo principal seguido por imagens.
5. URLs duplicadas são removidas.
6. Rolagem horizontal não troca o anúncio vertical.
7. Rolagem vertical não troca a mídia horizontal indevidamente.
8. Tocar na imagem abre o detalhe.
9. Tocar no vídeo abre o detalhe sem pausar por ação do toque.
10. Somente o vídeo da página ativa permanece em reprodução.
11. O detalhe exibe descrição e características disponíveis.
12. Campos ausentes não geram valores inventados.
13. O perfil público não contém telefone, e-mail, site ou rede social.
14. `Falar com o fornecedor` usa somente `valley_in_app`.
15. Marketplace e Estoque usam o mesmo contrato visual.
16. Layout funciona em telas Android pequenas e grandes.
17. Redução de movimento não quebra a navegação.
18. Build React/Vite, lint e testes de contrato passam.
19. Análise e testes Flutter passam após o empacotamento.
20. APK funcional contém o bundle atualizado e passa pela auditoria.

## Critérios de aceite

- [x] carrossel horizontal implementado no feed;
- [x] galeria completa preservada no Marketplace;
- [x] galeria completa preservada no Estoque;
- [x] vídeo ativo controlado por visibilidade;
- [x] toque na mídia abre o detalhe;
- [x] toque não é comando de pausa;
- [x] detalhe reúne informações públicas disponíveis;
- [x] perfil público do fornecedor sanitizado;
- [x] comunicação limitada ao canal interno do VALLEY;
- [x] teste de contrato versionado;
- [ ] lint e build React/Vite confirmados no head final;
- [ ] testes Python confirmados no head final;
- [ ] análise e testes Flutter confirmados no head final;
- [ ] Security, CodeQL, DAST, OSV, Database e CI verdes no mesmo SHA;
- [ ] revisão visual em aparelho Android;
- [ ] PR integrado somente por Squash and Merge com `expected_head_sha`.

## Regra de conclusão

A existência do código não equivale à homologação final. A atividade somente pode ser marcada como concluída após todos os gates aplicáveis terminarem com sucesso no mesmo SHA, revisão visual do carrossel e confirmação de que nenhum dado externo de contato do fornecedor aparece no APK.

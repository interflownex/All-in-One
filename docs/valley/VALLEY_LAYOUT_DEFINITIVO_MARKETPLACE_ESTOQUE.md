# VALLEY — Layout definitivo da tela inicial do Marketplace e do Estoque

**Classificação:** Pendências / Técnico / Equipe Técnica  
**Público-alvo:** Pessoa Física (B2C) e Equipe Técnica  
**Status:** definitivo e persistente  
**Responsável:** Anderson Carvalho Nazarete

## Decisão visual

A tela de abertura do Marketplace e do módulo Estoque deve usar o mesmo layout visual. A diferença entre os módulos estará apenas na origem, consulta e disponibilidade dos produtos.

## Regras imutáveis

1. A imagem ou o vídeo do produto preenche toda a tela.
2. Não existe rodapé.
3. Não existe barra inferior com botões Comprar ou Adicionar ao carrinho.
4. As ações aparecem sobre a mídia, na lateral direita.
5. No topo aparecem exatamente quatro áreas interativas, da esquerda para a direita:
   - logomarca oficial VALLEY;
   - voltar;
   - busca;
   - foto de perfil.
6. A logomarca abre o dock com todos os módulos.
7. Voltar retorna à tela anterior.
8. Busca abre a pesquisa do módulo atual.
9. A foto abre o perfil do usuário.
10. A foto deve aparecer dentro de um aro visual inspirado no aro da identidade VALLEY.
11. O preço aparece no canto inferior esquerdo, acima da descrição, com aproximadamente o dobro da escala do texto comum, peso forte e cor de destaque.
12. Título, variação, preço, descrição e selos ficam sobre a mídia do produto.
13. A comunicação com o fornecedor ocorre somente dentro do VALLEY.
14. Não exibir telefone, e-mail, WhatsApp, site ou redes sociais externas.
15. Usar somente a logomarca oficial localizada em `assets/brand/valley-logo-official.png`.

## Ações laterais

- Favoritar
- Compartilhar
- Comentar
- Carrinho
- Comprar
- Conversar

## Marketplace

- catálogo local;
- raio recomendado de até 10 km;
- busca por produto, marca e categoria;
- produtos de lojas e vendedores cadastrados.

## Estoque

- catálogo de fornecedores homologados;
- busca por produto, marca, categoria e fornecedor;
- mostrar disponibilidade e condições de entrega.

## Ativos reutilizáveis obrigatórios

Cada entrega deve conter:

- tela pronta como primeiro arquivo;
- logomarca oficial intacta;
- botão da logomarca com aro neon;
- botão Voltar;
- botão Busca;
- moldura do perfil;
- avatar fictício de referência;
- botão lateral base sem ícone;
- ações laterais separadas;
- bloco do título;
- preço destacado;
- descrição;
- badge base sem texto;
- badges rotulados;
- overlay superior;
- overlay lateral;
- overlay inferior;
- overlay completo sem fundo de produto;
- arquivo Markdown;
- especificação JSON;
- `MANIFESTO_SHA256.json`.

## Critérios de aceite

A tela somente é aceita quando:

- a mídia preenche todo o fundo;
- os quatro controles superiores estão na ordem aprovada;
- a foto aparece, sem a palavra Perfil;
- as ações estão sobre a mídia;
- não existe rodapé;
- o preço está destacado;
- a logomarca oficial não foi alterada;
- o mesmo layout funciona no Marketplace e no Estoque;
- os elementos são reutilizáveis em PNG transparente quando aplicável.

# Design como Requisito Estratégico do Projeto

**Projeto:** All in One + Valley  
**Classificação:** Pendências / Técnico / Conceitual  
**Público-alvo:** Pessoa Física (B2C), Pessoa Jurídica (B2B) e Equipe Técnica  
**Status:** Mandatório e persistente  
**Versão:** 1.0.0  

## 1. Decisão

Design é requisito de produto, engenharia, acessibilidade e confiança em todos os aplicativos do projeto.

Não deve ser tratado como decoração, acabamento posterior ou atividade opcional. Uma funcionalidade tecnicamente operacional não está concluída se a experiência for confusa, ilegível, inconsistente, inacessível ou não responsiva.

A política executável está em:

```text
config/ui/global_visual_delivery_policy.json
```

A validação automática está em:

```text
scripts/validate_global_visual_delivery.py
```

## 2. Escopo

A regra vale para todos os aplicativos presentes e futuros em:

- `apps/`;
- `desktop/`;
- `frontend/`;
- `mobile/`;
- `web/`.

Nenhum aplicativo pode desativar localmente esta governança.

## 3. Dimensões obrigatórias de qualidade

Toda tela, fluxo ou componente deve ser avaliado quanto a:

- clareza da jornada;
- consistência visual;
- legibilidade;
- acessibilidade;
- responsividade;
- hierarquia da informação;
- feedback de interação;
- redução de esforço do usuário;
- continuidade entre telas.

## 4. Artefatos mínimos antes da implementação

Antes de implementar uma nova jornada visual, registrar:

1. fluxo da jornada;
2. tela de referência ou wireframe;
3. inventário de componentes reutilizáveis;
4. estados vazio, carregando, erro e sucesso;
5. critérios de aceite de design e experiência.

A ausência desses elementos deve ser tratada como pendência técnica.

## 5. Gates obrigatórios

Toda mudança visual relevante deve passar por:

- revisão de UX;
- revisão de acessibilidade;
- revisão responsiva;
- revisão de consistência visual;
- revisão de regressão visual.

Os gates não substituem testes funcionais. Eles complementam a validação técnica.

## 6. Viewports mínimos

Validar, no mínimo:

- smartphone pequeno;
- smartphone padrão;
- tablet;
- desktop quando aplicável.

Não é aceitável aprovar uma tela que funcione apenas em uma resolução de referência.

## 7. Definição de pronto

Uma entrega visual somente está pronta quando:

- usa a identidade e os ativos oficiais corretos;
- mantém consistência com o design system;
- possui estados interativos e mensagens definidos;
- não apresenta overflow, corte ou sobreposição indevida;
- preserva leitura confortável com escala do sistema;
- evita navegação redundante;
- preserva telas já aprovadas;
- documenta componentes reutilizáveis;
- passa pelo validador e pelos testes do contrato visual.

## 8. Proibições

É proibido:

- tratar design como acabamento opcional;
- implementar tela sem hierarquia visual definida;
- duplicar navegação sem necessidade funcional;
- reduzir legibilidade apenas para acomodar conteúdo;
- aprovar tela sem estados de erro e carregamento;
- ignorar comportamento responsivo;
- alterar uma tela aprovada sem autorização expressa.

## 9. Validação

Executar antes de concluir ou integrar alterações visuais:

```bash
python3 scripts/validate_global_visual_delivery.py
python3 -m pytest tests/test_global_visual_delivery_policy.py -q
git diff --check
```

Falha nesses comandos bloqueia a conclusão e o merge.

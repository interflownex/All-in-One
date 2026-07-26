# Plano de Implementacao - 24 Ideias Aprovadas

Versao: 1.0
Data: 2026-07-26
Hora: 14:32:04
Fuso: America/Sao_Paulo
Repositorio: interflownex/All-in-One
Branch: feature/primicias-selecionadas-v1
Commit de referencia: 77fa6fab5f1c881ba6289dc288dc64e20421614a
Janela de planejamento: 8 horas (tolerancia operacional de 4 horas)

## Objetivo
Executar as 24 ideias aprovadas com rollout seguro por ondas, mantendo rastreabilidade por feature flag, contrato e teste.

## Escopo da fase atual
- Fase atual: planejamento e governanca tecnica.
- Sem alteracao funcional entregue nesta etapa.
- Proxima etapa: implementacao por ondas com validacao por modulo.

## Sequencia de execucao recomendada
1. Onda 0 - Fundacao de governanca (1h a 2h)
2. Onda 1 - Prioridades criticas (2h a 4h)
3. Onda 2 - Prioridades altas por jornada (3h a 5h)
4. Onda 3 - Prioridades medias e fechamento (2h a 3h)

## Onda 0 - Fundacao
- Criar matriz de feature flags por ideia.
- Definir payload padrao de consentimento com prazo e finalidade.
- Definir convenção de eventos de auditoria por modulo.
- Congelar contratos base para evitar quebra cruzada.

## Onda 1 - Criticas
- VLY-20260726-02 Escudo Valley Antigolpe.
- VLY-20260726-05 Permissao com prazo e finalidade.
- VLY-20260726-07 Piloto de contas.

## Onda 2 - Altas com alto impacto
- VLY-20260726-01 Jobs passaporte verificavel.
- VLY-20260726-03 Selo de confianca explicavel.
- VLY-20260726-04 Central conecte minha vida.
- VLY-20260726-06 Carrinho cooperativo.
- VLY-20260726-08 Substituto compativel.
- VLY-20260726-09 Helena no aparelho.
- VLY-20260726-11 Janela viva de entrega.
- VLY-20260726-12 Orcamento comparavel.
- VLY-20260726-16 Retirada sem fila.
- VLY-20260726-17 Historico portatil.
- VLY-20260726-19 Botao resolver.
- VLY-20260726-20 Cofre de validade.
- VLY-20260726-21 Cartao de saude controlado.
- VLY-20260726-23 Contrato em camadas.

## Onda 3 - Medias e consolidacao
- VLY-20260726-10 Meu bairro em numeros.
- VLY-20260726-13 Entrega assistida.
- VLY-20260726-14 Rota de confianca.
- VLY-20260726-15 Escolha de entrega com impacto.
- VLY-20260726-18 Planejador de evento de vida.
- VLY-20260726-22 Carteira de beneficios portatil.
- VLY-20260726-24 Radar de vida no imovel.

## Testes obrigatorios
- Unitarios por modulo alterado.
- Integracao entre API Hub, Identity e Permissions.
- Teste temporal de expiracao de consentimento.
- Teste de regressao de autenticacao em fluxos criticos.
- Teste de contrato para endpoints novos/alterados.

## Evidencias esperadas
- Lista de arquivos alterados por ideia.
- Saida de testes com comando e resultado.
- Registro de feature flags ativas e desativadas.
- Log de eventos de auditoria por fluxo validado.

## Riscos e mitigacao
1. Risco: acoplamento forte entre modulos.
   Mitigacao: contratos versionados e flags por ideia.
2. Risco: expiracao indevida de permissoes.
   Mitigacao: testes de fronteira temporal e fallback orientado ao usuario.
3. Risco: regressao de login ou sessao.
   Mitigacao: smoke tests de identidade a cada onda.

## Bloqueios atuais
- Existem alteracoes locais preexistentes em diversos modulos.
- Esta entrega evitou editar esses modulos para nao sobrepor trabalho em andamento.
- Recomendado: consolidar ou isolar essas alteracoes antes da onda funcional.

## Procedimento de entrega da proxima etapa
1. Executar preflight e lock multiagente.
2. Implementar uma onda por vez, com commit rastreavel.
3. Rodar testes da onda antes de avancar.
4. Atualizar tarefas.md com evidencias e pendencias restantes.
5. Publicar branch e preparar PR para revisao.

## Historico
- v1.0 (2026-07-26 14:32:04 -03): plano inicial de execucao por ondas para as 24 ideias aprovadas.

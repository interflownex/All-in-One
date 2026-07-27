# Security: Health

- OAuth2/JWT ou API key com escopo de modulo no API Hub.
- MFA para aprovacoes, pagamentos e leitura de dados sensiveis.
- RBAC/ABAC, device fingerprint, rate limit e auditoria imutavel.
- Segredos apenas via vault ou variaveis de ambiente.
- Retencao, consentimento e anonimizacao em conformidade com LGPD.
- Dados sensiveis devem ser criptografados e expostos somente por escopo autorizado.

## Wearables e dispositivos

- Vincular relogio, celular, usuario e All-in-One ID por fluxo autenticado.
- Registrar fabricante, modelo, sistema, capacidades e origem de cada medicao.
- Exigir nova confirmacao para troca de celular, relogio ou responsavel.
- Aplicar tokens curtos para sessoes de telemonitoramento.
- Recusar dados sem procedencia, horario ou identificacao do dispositivo.
- Proibir sinais vitais e localizacao detalhada em logs comuns.
- Aplicar sincronizacao idempotente e protecao contra replay.

## SafeZone e localizacao

- Localizacao e dado sensivel e deve ter finalidade, responsavel e prazo.
- Exigir vinculo legitimo de cuidado ou responsabilidade legal.
- Indicar para a pessoa quando o acompanhamento estiver ativo, salvo excecao
  juridicamente fundamentada e revisada.
- Impedir rastreamento oculto, perseguicao e compartilhamento comercial.
- Permitir revogacao, expiracao e revisao de responsaveis.
- Notificar inclusao de novo responsavel ou dispositivo.
- Registrar quem acessou localizacao, quando e com qual finalidade.
- Ativar localizacao detalhada somente durante regra necessaria ou incidente.
- Reter somente o minimo necessario fora de incidentes.
- Oferecer denuncia, bloqueio e revisao de suspeita de abuso.
- Nao compartilhar localizacao individual com empregadores.

## Menores e pessoas dependentes

- Aplicar controles proporcionais a idade, capacidade e responsabilidade legal.
- Separar permissao para configurar cerca, receber alerta, visualizar saude e
  acompanhar localizacao temporaria.
- Preservar dignidade, autonomia possivel e transparencia adequada ao usuario.

## Limites

O produto nao garante localizacao perfeita, funcionamento sem bateria,
deteccao de emergencia, diagnostico ou substituicao de cuidador, medico,
ambulancia ou servico oficial de emergencia.

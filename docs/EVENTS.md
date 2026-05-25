# Eventos De Dominio

RabbitMQ e o barramento inicial. O exchange `all-in-one.domain` recebe
routing keys versionadas, payload minimizado e identificadores de correlacao.
O outbox relacional inicial e `audit.domain_events`; cada tentativa publicada
fica preservada de modo imutavel em `audit.event_deliveries`.

## Dispatcher de outbox

`workers/outbox_dispatcher` consome eventos `pending` em lotes com
`FOR UPDATE SKIP LOCKED`, publica mensagens persistentes no exchange e exige
publisher confirm antes de marcar `published_at` e `status = 'published'`.
Falhas geram entrega `failed_retryable` append-only e deixam o evento pendente
para nova tentativa.

A entrega e `at-least-once`: se o broker confirmar e a transacao PostgreSQL
falhar depois, a mensagem pode reaparecer. Consumidores deduplicam por
`event_id`.

Eventos Jobs sao publicados com allowlist de dados de processo. PDF CTPS,
chaves de storage, texto livre do curriculo e dados brutos do documento nunca
saem na mensagem.

## Fluxos obrigatorios cobertos

- Identity: `identity.user.created`, `identity.user.verified`,
  `identity.user.duplicate_detected`.
- Business e RBAC: `business.company.created`, `business.company.submitted`,
  `business.company.approved`, `business.company.rejected`,
  `business.user.invited`, `business.role.assigned`.
- Riders e entrega: `rider.submitted`, `rider.approved`, `rider.rejected`,
  `rider.vehicle.approved`, `delivery.request.created`,
  `delivery.rider.assigned`, `delivery.picked_up`, `delivery.completed`,
  `delivery.cancelled`.
- Commerce: `marketplace.store.created`, `marketplace.product.created`,
  `marketplace.order.created`, `marketplace.order.paid`,
  `marketplace.order.delivered`, `stock.product.imported`,
  `stock.order.created`.
- Services e Mobility: `services.visit.created`, `services.visit.completed`,
  `services.quote.created`, `services.contract.created`,
  `services.contract.completed`, `mobility.ride.requested`,
  `mobility.ride.accepted`, `mobility.ride.completed`,
  `mobility.ticket.purchased`, `mobility.ticket.used`.
- Jobs: `jobs.resume.created`, `jobs.resume.ctps_imported`,
  `jobs.employment.ctps_imported`, `jobs.employment.self_declared`,
  `jobs.job_posting.created`, `jobs.job_posting.published`,
  `jobs.application.created`, `jobs.resume.viewed`.
- Finance e seguros: `payment.escrow.created`, `payment.escrow.released`,
  `payment.refunded`, `payment.split.executed`, `insurance.quote.created`,
  `insurance.policy.created`, `insurance.claim.created`.
- Health e ERP: `health.appointment.created`,
  `health.telemedicine.started`, `health.prescription.issued`,
  `erp.invoice.created`.

Consumidores devem persistir `event_id` como chave idempotente e nao incluir
biometria, documentos ou prontuario em mensagens fora de referencias seguras.

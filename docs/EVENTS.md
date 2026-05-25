# Eventos De Dominio

RabbitMQ e o barramento inicial. O exchange `all-in-one.domain` recebe
routing keys versionadas, payload minimizado e identificadores de correlacao.
O outbox relacional inicial e `audit.domain_events`; cada tentativa publicada
fica preservada de modo imutavel em `audit.event_deliveries`.

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

Consumidores devem persistir idempotency key e nao incluir biometria,
documentos ou prontuario em mensagens fora de referencias seguras.

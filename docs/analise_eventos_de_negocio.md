# Análise de Eventos de Negócio (Fase 1.4)

**Referência:** `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md`

Este documento consolida a lista de todos os eventos de negócio identificados nos 25 arquivos de contrato do diretório `contracts/`. O objetivo é criar um inventário centralizado que servirá de base para a modelagem de dados e o design de interações do sistema, conforme a etapa 6.4 do memorando mestre.

As definições de payload, consumidores e outras propriedades detalhadas serão complementadas na fase de construção do catálogo de dados.

---

## 1. Domínio: AI Core (`ai_core`)

- `ai.memory.created`
- `ai.memory.indexed`
- `ai.memory.updated`
- `ai.moderation.created`
- `ai.moderation.submitted`
- `ai.moderation.approved`
- `ai.moderation.rejected`
- `ai.moderation.completed`
- `ai.model_run.requested`
- `ai.model_run.completed`
- `ai.model_run.failed`
- `ai.model_run.cost_approved`

## 2. Domínio: API Hub (`api_hub`)

- `api.client.created`
- `api.client.submitted`
- `api.client.approved`
- `api.client.rejected`
- `api.key.created`
- `api.key.submitted`
- `api.key.approved`
- `api.key.rejected`
- `api.webhook.created`
- `api.webhook.submitted`
- `api.webhook.approved`
- `api.webhook.rejected`
- `api.integration_run.created`
- `api.integration_run.submitted`
- `api.integration_run.approved`
- `api.integration_run.rejected`
- `api.webhook.delivered`

## 3. Domínio: BI (`bi`)

- `bi.dataset.created`
- `bi.dataset.refreshed`
- `bi.dataset.published`
- `bi.dashboard.created`
- `bi.dashboard.published`
- `bi.dashboard.archived`
- `bi.indicator.created`
- `bi.indicator.submitted`
- `bi.indicator.cancelled`
- `bi.indicator.completed`
- `bi.export.requested`
- `bi.export.completed`

## 4. Domínio: BPM (`bpm`)

- `bpm.process.started`
- `bpm.task.created`
- `bpm.task.escalated`
- `bpm.task.completed`
- `bpm.sla_policy.published`

## 5. Domínio: Business (`business`)

- `business.company.created`
- `business.company.submitted`
- `business.company.approved`
- `business.company.rejected`
- `business.branche.created`
- `business.branche.submitted`
- `business.branche.cancelled`
- `business.branche.completed`
- `business.company_document.created`
- `business.company_document.submitted`
- `business.company_document.cancelled`
- `business.company_document.completed`
- `business.user.invited`
- `business.role.assigned`
- `business.user.revoked`
- `business.catalog_offer.created`
- `business.catalog_offer.submitted`
- `business.catalog_offer.cancelled`
- `business.catalog_offer.completed`
- `valley.catalog.offer.synced`
- `business.catalog_offer.paused`

## 6. Domínio: CRM (`crm`)

- `crm.lead.created`
- `crm.lead.qualified`
- `crm.lead.disqualified`
- `crm.opportunity.created`
- `crm.opportunity.proposed`
- `crm.opportunity.won`
- `crm.opportunity.lost`
- `crm.activity.created`
- `crm.activity.completed`
- `crm.campaign.created`
- `crm.campaign.launched`
- `crm.campaign.closed`

## 7. Domínio: Delivery (`delivery`)

- `delivery.request.created`
- `delivery.rider.assigned`
- `delivery.picked_up`
- `delivery.completed`
- `delivery.proof.recorded`
- `delivery.cancelled`

## 8. Domínio: Document (`document`)

- `document.uploaded`
- `document.versioned`
- `document.signed`

## 9. Domínio: ERP (`erp`)

- `erp.account.created`
- `erp.cost_center.created`
- `erp.payable.created`
- `erp.payment.approved`
- `erp.payable.paid`
- `erp.receivable.created`
- `erp.receivable.received`
- `erp.receivable.reconciled`
- `erp.invoice.created`
- `erp.invoice.submitted`
- `erp.invoice.completed`
- `erp.invoice.cancelled`

## 10. Domínio: Finance (`finance`)

- `payment.escrow.created`
- `payment.escrow.released`
- `payment.refunded`
- `payment.split.executed`
- `valley.gold.ledger.posted`

## 11. Domínio: Health (`health`)

- `health.appointment.created`
- `health.telemedicine.started`
- `health.prescription.issued`

## 12. Domínio: HR (`hr`)

- `hr.employee.created`
- `hr.payroll.opened`
- `hr.payroll.closed`
- `hr.training.assigned`
- `hr.training.completed`

## 13. Domínio: Identity (`identity`)

- `identity.user.created`
- `identity.user.verified`
- `identity.user.duplicate_detected`
- `identity.document.created`
- `identity.document.approved`
- `identity.document.rejected`
- `identity.biometric.captured`
- `identity.session.created`
- `identity.session.revoked`
- `identity.kyc.submitted`
- `identity.kyc.approved`
- `identity.kyc.rejected`
- `identity.consent.recorded`

## 14. Domínio: Jobs (`jobs`)

- `jobs.resume.created`
- `jobs.resume.ctps_imported`
- `jobs.employment.self_declared`
- `jobs.resume_document.created`
- `jobs.job_posting.created`
- `jobs.job_posting.published`
- `jobs.job_posting.closed`
- `jobs.application.created`
- `jobs.application.reviewed`
- `jobs.application.shortlisted`
- `jobs.application.interview_scheduled`
- `jobs.application.rejected`
- `jobs.application.withdrawn`
- `jobs.resume.viewed`
- `jobs.resume_access_log.created`

## 15. Domínio: Legal (`legal`)

- `legal.case.created`
- `legal.deadline.created`
- `legal.deadline.alerted`
- `legal.deadline.completed`
- `legal.hearing.scheduled`

## 16. Domínio: Marketplace (`marketplace`)

- `marketplace.store.created`
- `marketplace.product.created`
- `marketplace.order.created`
- `marketplace.order.paid`
- `marketplace.order.delivered`
- `marketplace.dispute.created`
- `support.ticket.created`
- `support.ticket.triaged`
- `support.ticket.resolved`
- `support.ticket.closed`
- `valley.review.created`
- `valley.review.published`
- `valley.review.rejected`
- `valley.pepitas.granted`

## 17. Domínio: Mobility (`mobility`)

- `mobility.ride.requested`
- `mobility.ride.accepted`
- `mobility.ride.completed`
- `mobility.route.eta_quoted`
- `mobility.ticket.purchased`
- `mobility.ticket.used`
- `mobility.fare_rule.published`

## 18. Domínio: Permissions (`permissions`)

- `permissions.role.created`
- `permissions.role.assigned`

## 19. Domínio: Property (`property`)

- `property.lease.created`
- `property.lease.activated`
- `property.lease.terminated`
- `property.maintenance.requested`
- `property.maintenance.scheduled`
- `property.maintenance.completed`

## 20. Domínio: Riders (`riders`)

- `rider.submitted`
- `rider.approved`
- `rider.rejected`
- `rider.vehicle.approved`

## 21. Domínio: Services (`services`)

- `services.visit.created`
- `services.visit.completed`
- `services.quote.created`
- `services.contract.created`
- `services.contract.completed`

## 22. Domínio: Stock (`stock`)

- `stock.product.imported`
- `stock.supplier_order.created`
- `stock.supplier_order.acknowledged`
- `stock.supplier_order.shipped`
- `stock.supplier_order.delivered`
- `stock.supplier_order.cancelled`
- `valley.stock.discount.quoted`

## 23. Domínio: TMS (`tms`)

- `tms.carrier.created`
- `tms.carrier.submitted`
- `tms.carrier.approved`
- `tms.carrier.rejected`
- `tms.route.created`
- `tms.route.activated`
- `tms.freight.created`
- `tms.freight.approved`
- `tms.freight.dispatched`
- `tms.freight.completed`
- `tms.delivery.proved`
- `tms.freight.audit_created`
- `tms.freight.audit_closed`

## 24. Domínio: Vision (`vision`)

- `vision.device.registered`
- `vision.device.submitted`
- `vision.device.cancelled`
- `vision.device.completed`
- `vision.stream.started`
- `vision.stream.paused`
- `vision.stream.resumed`
- `vision.recording.stored`
- `vision.motion.detected`
- `vision.incident.created`
- `vision.incident.resolved`

## 25. Domínio: WMS (`wms`)

- `wms.warehouse.created`
- `wms.bin.created`
- `wms.inventory.received`
- `wms.inventory.allocated`
- `wms.picking.created`
- `wms.picking.completed`
- `wms.picking.closed`
- `wms.shipment.created`
- `wms.shipment.dispatched`

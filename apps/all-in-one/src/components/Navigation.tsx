import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const modulesData = [
    { slug: "ai_core", title: "Ai_core", icon: "📦", screens: [
        { title: "ModelRunsList", path: "/ai_core/modelruns" },
        { title: "ModerationDecisionsList", path: "/ai_core/moderationdecisions" },
        { title: "ModelRunsForm", path: "/ai_core/modelruns-form" },
        { title: "Ai_corePermissions", path: "/ai_core/ai_corepermissions" },
        { title: "Ai_coreOverview", path: "/ai_core/ai_core" },
        { title: "AiMemoriesForm", path: "/ai_core/aimemories-form" },
        { title: "AiMemoriesList", path: "/ai_core/aimemories" },
        { title: "ModerationDecisionsForm", path: "/ai_core/moderationdecisions-form" }
    ] },
    { slug: "api_hub", title: "Api_hub", icon: "📦", screens: [
        { title: "ApiClientsForm", path: "/api_hub/apiclients-form" },
        { title: "Api_hubPermissions", path: "/api_hub/api_hubpermissions" },
        { title: "ApiKeysForm", path: "/api_hub/apikeys-form" },
        { title: "ApiClientsList", path: "/api_hub/apiclients" },
        { title: "ApiKeysList", path: "/api_hub/apikeys" },
        { title: "IntegrationRunsForm", path: "/api_hub/integrationruns-form" },
        { title: "WebhooksList", path: "/api_hub/webhooks" },
        { title: "Api_hubOverview", path: "/api_hub/api_hub" },
        { title: "WebhooksForm", path: "/api_hub/webhooks-form" },
        { title: "IntegrationRunsList", path: "/api_hub/integrationruns" }
    ] },
    { slug: "bi", title: "Bi", icon: "📦", screens: [
        { title: "DatasetsList", path: "/bi/datasets" },
        { title: "BiPermissions", path: "/bi/bipermissions" },
        { title: "BiOverview", path: "/bi/bi" },
        { title: "DashboardsList", path: "/bi/dashboards" },
        { title: "ExportsForm", path: "/bi/exports-form" },
        { title: "DashboardsForm", path: "/bi/dashboards-form" },
        { title: "IndicatorsForm", path: "/bi/indicators-form" },
        { title: "IndicatorsList", path: "/bi/indicators" },
        { title: "ExportsList", path: "/bi/exports" },
        { title: "DatasetsForm", path: "/bi/datasets-form" }
    ] },
    { slug: "bpm", title: "Bpm", icon: "📦", screens: [
        { title: "ProcessesList", path: "/bpm/processes" },
        { title: "ProcessesForm", path: "/bpm/processes-form" },
        { title: "BpmPermissions", path: "/bpm/bpmpermissions" },
        { title: "SlaPoliciesForm", path: "/bpm/slapolicies-form" },
        { title: "BpmOverview", path: "/bpm/bpm" },
        { title: "WorkflowInstancesForm", path: "/bpm/workflowinstances-form" },
        { title: "TasksForm", path: "/bpm/tasks-form" },
        { title: "TasksList", path: "/bpm/tasks" },
        { title: "SlaPoliciesList", path: "/bpm/slapolicies" },
        { title: "WorkflowInstancesList", path: "/bpm/workflowinstances" }
    ] },
    { slug: "business", title: "Business", icon: "🏢", screens: [
        { title: "UserCompanyMembershipsList", path: "/business/usercompanymemberships" },
        { title: "CompanyDocumentsList", path: "/business/companydocuments" },
        { title: "UserCompanyMembershipsForm", path: "/business/usercompanymemberships-form" },
        { title: "CatalogOffersList", path: "/business/catalogoffers" },
        { title: "CompaniesList", path: "/business/companies" },
        { title: "BranchesForm", path: "/business/branches-form" },
        { title: "BusinessPermissions", path: "/business/businesspermissions" },
        { title: "CompaniesForm", path: "/business/companies-form" },
        { title: "BranchesList", path: "/business/branches" },
        { title: "CompanyDocumentsForm", path: "/business/companydocuments-form" },
        { title: "CatalogOffersForm", path: "/business/catalogoffers-form" },
        { title: "BusinessOverview", path: "/business/business" }
    ] },
    { slug: "crm", title: "Crm", icon: "📦", screens: [
        { title: "ActivitiesForm", path: "/crm/activities-form" },
        { title: "OpportunitiesList", path: "/crm/opportunities" },
        { title: "LeadsForm", path: "/crm/leads-form" },
        { title: "LeadsList", path: "/crm/leads" },
        { title: "CampaignsList", path: "/crm/campaigns" },
        { title: "OpportunitiesForm", path: "/crm/opportunities-form" },
        { title: "CrmOverview", path: "/crm/crm" },
        { title: "CampaignsForm", path: "/crm/campaigns-form" },
        { title: "CrmPermissions", path: "/crm/crmpermissions" },
        { title: "ActivitiesList", path: "/crm/activities" }
    ] },
    { slug: "delivery", title: "Delivery", icon: "🚚", screens: [
        { title: "InsuranceOptionsList", path: "/delivery/insuranceoptions" },
        { title: "ProofsForm", path: "/delivery/proofs-form" },
        { title: "DeliveryRequestsList", path: "/delivery/deliveryrequests" },
        { title: "AssignmentsList", path: "/delivery/assignments" },
        { title: "DeliveryOverview", path: "/delivery/delivery" },
        { title: "ProofsList", path: "/delivery/proofs" },
        { title: "QuotesList", path: "/delivery/quotes" },
        { title: "InsuranceOptionsForm", path: "/delivery/insuranceoptions-form" },
        { title: "DeliveryPermissions", path: "/delivery/deliverypermissions" },
        { title: "DeliveryRequestsForm", path: "/delivery/deliveryrequests-form" },
        { title: "QuotesForm", path: "/delivery/quotes-form" },
        { title: "AssignmentsForm", path: "/delivery/assignments-form" }
    ] },
    { slug: "document", title: "Document", icon: "📦", screens: [
        { title: "FoldersList", path: "/document/folders" },
        { title: "VersionsForm", path: "/document/versions-form" },
        { title: "DocumentsForm", path: "/document/documents-form" },
        { title: "DocumentPermissions", path: "/document/documentpermissions" },
        { title: "DocumentOverview", path: "/document/document" },
        { title: "RetentionPoliciesForm", path: "/document/retentionpolicies-form" },
        { title: "FoldersForm", path: "/document/folders-form" },
        { title: "RetentionPoliciesList", path: "/document/retentionpolicies" },
        { title: "VersionsList", path: "/document/versions" },
        { title: "DocumentsList", path: "/document/documents" }
    ] },
    { slug: "erp", title: "Erp", icon: "📦", screens: [
        { title: "CostCentersForm", path: "/erp/costcenters-form" },
        { title: "PayablesList", path: "/erp/payables" },
        { title: "FiscalDocumentsForm", path: "/erp/fiscaldocuments-form" },
        { title: "CostCentersList", path: "/erp/costcenters" },
        { title: "AccountsForm", path: "/erp/accounts-form" },
        { title: "PayablesForm", path: "/erp/payables-form" },
        { title: "FiscalDocumentsList", path: "/erp/fiscaldocuments" },
        { title: "ErpOverview", path: "/erp/erp" },
        { title: "ReceivablesList", path: "/erp/receivables" },
        { title: "ReceivablesForm", path: "/erp/receivables-form" },
        { title: "AccountsList", path: "/erp/accounts" },
        { title: "ErpPermissions", path: "/erp/erppermissions" }
    ] },
    { slug: "finance", title: "Finance", icon: "💰", screens: [
        { title: "InvoicesList", path: "/finance/invoices" },
        { title: "EscrowsList", path: "/finance/escrows" },
        { title: "EscrowsForm", path: "/finance/escrows-form" },
        { title: "WalletsForm", path: "/finance/wallets-form" },
        { title: "LedgerEntriesList", path: "/finance/ledgerentries" },
        { title: "SplitsForm", path: "/finance/splits-form" },
        { title: "FinancePermissions", path: "/finance/financepermissions" },
        { title: "FinanceOverview", path: "/finance/finance" },
        { title: "InvoicesForm", path: "/finance/invoices-form" },
        { title: "WalletsList", path: "/finance/wallets" },
        { title: "SplitsList", path: "/finance/splits" },
        { title: "WalletLedger", path: "/finance/walletledger" },
        { title: "LedgerEntriesForm", path: "/finance/ledgerentries-form" }
    ] },
    { slug: "health", title: "Health", icon: "🏥", screens: [
        { title: "AppointmentsForm", path: "/health/appointments-form" },
        { title: "PrescriptionsList", path: "/health/prescriptions" },
        { title: "PatientsForm", path: "/health/patients-form" },
        { title: "MedicalRecordsForm", path: "/health/medicalrecords-form" },
        { title: "BedsForm", path: "/health/beds-form" },
        { title: "MedicalRecordsList", path: "/health/medicalrecords" },
        { title: "AppointmentsList", path: "/health/appointments" },
        { title: "HealthPermissions", path: "/health/healthpermissions" },
        { title: "PrescriptionsForm", path: "/health/prescriptions-form" },
        { title: "HealthOverview", path: "/health/health" },
        { title: "BedsList", path: "/health/beds" },
        { title: "PatientsList", path: "/health/patients" }
    ] },
    { slug: "hr", title: "Hr", icon: "📦", screens: [
        { title: "CandidatesForm", path: "/hr/candidates-form" },
        { title: "CoursesList", path: "/hr/courses" },
        { title: "HrPermissions", path: "/hr/hrpermissions" },
        { title: "OccupationalRecordsList", path: "/hr/occupationalrecords" },
        { title: "EmployeesList", path: "/hr/employees" },
        { title: "PayrollRunsList", path: "/hr/payrollruns" },
        { title: "PayrollRunsForm", path: "/hr/payrollruns-form" },
        { title: "CandidatesList", path: "/hr/candidates" },
        { title: "OccupationalRecordsForm", path: "/hr/occupationalrecords-form" },
        { title: "HrOverview", path: "/hr/hr" },
        { title: "EmployeesForm", path: "/hr/employees-form" },
        { title: "CoursesForm", path: "/hr/courses-form" }
    ] },
    { slug: "identity", title: "Identity", icon: "🆔", screens: [
        { title: "SessionControl", path: "/identity/sessioncontrol" },
        { title: "KycVerification", path: "/identity/kycverification" },
        { title: "ConsentRecordsList", path: "/identity/consentrecords" },
        { title: "DocumentsForm", path: "/identity/documents-form" },
        { title: "ConsentLgpd", path: "/identity/consentlgpd" },
        { title: "SessionsForm", path: "/identity/sessions-form" },
        { title: "IdentityVerificationsForm", path: "/identity/identityverifications-form" },
        { title: "BiometricsList", path: "/identity/biometrics" },
        { title: "UsersList", path: "/identity/users" },
        { title: "IdentityPermissions", path: "/identity/identitypermissions" },
        { title: "IdentityOverview", path: "/identity/identity" },
        { title: "ConsentRecordsForm", path: "/identity/consentrecords-form" },
        { title: "KybBusiness", path: "/identity/kybbusiness" },
        { title: "AuthGateway", path: "/identity/authgateway" },
        { title: "BiometricsForm", path: "/identity/biometrics-form" },
        { title: "MfaManager", path: "/identity/mfamanager" },
        { title: "SessionsList", path: "/identity/sessions" },
        { title: "UsersForm", path: "/identity/users-form" },
        { title: "DocumentsList", path: "/identity/documents" },
        { title: "IdentityVerificationsList", path: "/identity/identityverifications" }
    ] },
    { slug: "jobs", title: "Jobs", icon: "💼", screens: [
        { title: "ResumesList", path: "/jobs/resumes" },
        { title: "ResumeAccessLogsForm", path: "/jobs/resumeaccesslogs-form" },
        { title: "EmploymentRecordsList", path: "/jobs/employmentrecords" },
        { title: "ResumeDocumentsForm", path: "/jobs/resumedocuments-form" },
        { title: "CtpsImport", path: "/jobs/ctpsimport" },
        { title: "CandidateResume", path: "/jobs/candidateresume" },
        { title: "ApplicationsForm", path: "/jobs/applications-form" },
        { title: "RecruiterResumeReview", path: "/jobs/recruiterresumereview" },
        { title: "VacancySearch", path: "/jobs/vacancysearch" },
        { title: "JobsOverview", path: "/jobs/jobs" },
        { title: "ResumesForm", path: "/jobs/resumes-form" },
        { title: "JobPostingsForm", path: "/jobs/jobpostings-form" },
        { title: "ResumeAccessLogsList", path: "/jobs/resumeaccesslogs" },
        { title: "JobsPermissions", path: "/jobs/jobspermissions" },
        { title: "ApplicationsList", path: "/jobs/applications" },
        { title: "JobPostingsList", path: "/jobs/jobpostings" },
        { title: "EmploymentRecordsForm", path: "/jobs/employmentrecords-form" },
        { title: "ResumeDocumentsList", path: "/jobs/resumedocuments" }
    ] },
    { slug: "legal", title: "Legal", icon: "📦", screens: [
        { title: "LegalPermissions", path: "/legal/legalpermissions" },
        { title: "HearingsForm", path: "/legal/hearings-form" },
        { title: "LegalOverview", path: "/legal/legal" },
        { title: "DeadlinesForm", path: "/legal/deadlines-form" },
        { title: "LegalContractsList", path: "/legal/legalcontracts" },
        { title: "DeadlinesList", path: "/legal/deadlines" },
        { title: "CasesList", path: "/legal/cases" },
        { title: "LegalContractsForm", path: "/legal/legalcontracts-form" },
        { title: "HearingsList", path: "/legal/hearings" },
        { title: "CasesForm", path: "/legal/cases-form" }
    ] },
    { slug: "marketplace", title: "Marketplace", icon: "🛍️", screens: [
        { title: "ProductsForm", path: "/marketplace/products-form" },
        { title: "PepitaGrantsForm", path: "/marketplace/pepitagrants-form" },
        { title: "MarketplaceOverview", path: "/marketplace/marketplace" },
        { title: "StoresList", path: "/marketplace/stores" },
        { title: "DisputesList", path: "/marketplace/disputes" },
        { title: "OrdersForm", path: "/marketplace/orders-form" },
        { title: "DisputesForm", path: "/marketplace/disputes-form" },
        { title: "MarketplacePermissions", path: "/marketplace/marketplacepermissions" },
        { title: "ProductsList", path: "/marketplace/products" },
        { title: "CartsForm", path: "/marketplace/carts-form" },
        { title: "CartsList", path: "/marketplace/carts" },
        { title: "OrdersList", path: "/marketplace/orders" },
        { title: "ReviewsList", path: "/marketplace/reviews" },
        { title: "StoresForm", path: "/marketplace/stores-form" },
        { title: "ReviewsForm", path: "/marketplace/reviews-form" },
        { title: "PepitaGrantsList", path: "/marketplace/pepitagrants" }
    ] },
    { slug: "mobility", title: "Mobility", icon: "📦", screens: [
        { title: "FareRulesForm", path: "/mobility/farerules-form" },
        { title: "RoutesForm", path: "/mobility/routes-form" },
        { title: "FareRulesList", path: "/mobility/farerules" },
        { title: "TicketsList", path: "/mobility/tickets" },
        { title: "RidesList", path: "/mobility/rides" },
        { title: "RoutesList", path: "/mobility/routes" },
        { title: "StopsForm", path: "/mobility/stops-form" },
        { title: "MobilityPermissions", path: "/mobility/mobilitypermissions" },
        { title: "RidesForm", path: "/mobility/rides-form" },
        { title: "StopsList", path: "/mobility/stops" },
        { title: "TicketsForm", path: "/mobility/tickets-form" },
        { title: "MobilityOverview", path: "/mobility/mobility" }
    ] },
    { slug: "permissions", title: "Permissions", icon: "📦", screens: [
        { title: "UserRolesList", path: "/permissions/userroles" },
        { title: "RolesList", path: "/permissions/roles" },
        { title: "ApprovalLimitsList", path: "/permissions/approvallimits" },
        { title: "PermissionsList", path: "/permissions/permissions" },
        { title: "UserRolesForm", path: "/permissions/userroles-form" },
        { title: "PermissionsPermissions", path: "/permissions/permissionspermissions" },
        { title: "PermissionsForm", path: "/permissions/permissions-form" },
        { title: "ApprovalLimitsForm", path: "/permissions/approvallimits-form" },
        { title: "AccessPoliciesList", path: "/permissions/accesspolicies" },
        { title: "PermissionsOverview", path: "/permissions/permissions" },
        { title: "RolesForm", path: "/permissions/roles-form" },
        { title: "AccessPoliciesForm", path: "/permissions/accesspolicies-form" }
    ] },
    { slug: "property", title: "Property", icon: "📦", screens: [
        { title: "AssembliesList", path: "/property/assemblies" },
        { title: "PropertiesList", path: "/property/properties" },
        { title: "LeasesForm", path: "/property/leases-form" },
        { title: "UnitsForm", path: "/property/units-form" },
        { title: "MaintenanceOrdersList", path: "/property/maintenanceorders" },
        { title: "PropertyOverview", path: "/property/property" },
        { title: "UnitsList", path: "/property/units" },
        { title: "PropertyPermissions", path: "/property/propertypermissions" },
        { title: "LeasesList", path: "/property/leases" },
        { title: "AssembliesForm", path: "/property/assemblies-form" },
        { title: "MaintenanceOrdersForm", path: "/property/maintenanceorders-form" },
        { title: "PropertiesForm", path: "/property/properties-form" }
    ] },
    { slug: "riders", title: "Riders", icon: "📦", screens: [
        { title: "VehiclesForm", path: "/riders/vehicles-form" },
        { title: "RiderProfilesList", path: "/riders/riderprofiles" },
        { title: "RiderDocumentsForm", path: "/riders/riderdocuments-form" },
        { title: "RiderDocumentsList", path: "/riders/riderdocuments" },
        { title: "RidersOverview", path: "/riders/riders" },
        { title: "RidersPermissions", path: "/riders/riderspermissions" },
        { title: "RiderReviewsForm", path: "/riders/riderreviews-form" },
        { title: "VehiclesList", path: "/riders/vehicles" },
        { title: "RiderProfilesForm", path: "/riders/riderprofiles-form" },
        { title: "RiderReviewsList", path: "/riders/riderreviews" }
    ] },
    { slug: "services", title: "Services", icon: "📦", screens: [
        { title: "ProvidersList", path: "/services/providers" },
        { title: "ServicesPermissions", path: "/services/servicespermissions" },
        { title: "ProvidersForm", path: "/services/providers-form" },
        { title: "VisitsForm", path: "/services/visits-form" },
        { title: "ServicesOverview", path: "/services/services" },
        { title: "EvidenceForm", path: "/services/evidence-form" },
        { title: "ServiceContractsForm", path: "/services/servicecontracts-form" },
        { title: "QuotesList", path: "/services/quotes" },
        { title: "ServiceContractsList", path: "/services/servicecontracts" },
        { title: "VisitsList", path: "/services/visits" },
        { title: "EvidenceList", path: "/services/evidence" },
        { title: "QuotesForm", path: "/services/quotes-form" }
    ] },
    { slug: "stock", title: "Stock", icon: "📦", screens: [
        { title: "PriceRulesList", path: "/stock/pricerules" },
        { title: "CatalogProductsForm", path: "/stock/catalogproducts-form" },
        { title: "PriceRulesForm", path: "/stock/pricerules-form" },
        { title: "SuppliersForm", path: "/stock/suppliers-form" },
        { title: "SupplierOrdersForm", path: "/stock/supplierorders-form" },
        { title: "DiscountQuotesForm", path: "/stock/discountquotes-form" },
        { title: "DiscountQuotesList", path: "/stock/discountquotes" },
        { title: "SupplierOrdersList", path: "/stock/supplierorders" },
        { title: "CatalogProductsList", path: "/stock/catalogproducts" },
        { title: "SuppliersList", path: "/stock/suppliers" },
        { title: "StockOverview", path: "/stock/stock" },
        { title: "StockPermissions", path: "/stock/stockpermissions" }
    ] },
    { slug: "tms", title: "Tms", icon: "📦", screens: [
        { title: "FreightsList", path: "/tms/freights" },
        { title: "RoutesForm", path: "/tms/routes-form" },
        { title: "TmsPermissions", path: "/tms/tmspermissions" },
        { title: "FreightAuditsList", path: "/tms/freightaudits" },
        { title: "ProofsOfDeliveryList", path: "/tms/proofsofdelivery" },
        { title: "TmsOverview", path: "/tms/tms" },
        { title: "RoutesList", path: "/tms/routes" },
        { title: "FreightsForm", path: "/tms/freights-form" },
        { title: "ProofsOfDeliveryForm", path: "/tms/proofsofdelivery-form" },
        { title: "CarriersList", path: "/tms/carriers" },
        { title: "CarriersForm", path: "/tms/carriers-form" },
        { title: "FreightAuditsForm", path: "/tms/freightaudits-form" }
    ] },
    { slug: "vision", title: "Vision", icon: "📦", screens: [
        { title: "StreamsForm", path: "/vision/streams-form" },
        { title: "RecordingsList", path: "/vision/recordings" },
        { title: "MotionAlertsForm", path: "/vision/motionalerts-form" },
        { title: "DevicesForm", path: "/vision/devices-form" },
        { title: "VisionPermissions", path: "/vision/visionpermissions" },
        { title: "StreamsList", path: "/vision/streams" },
        { title: "DevicesList", path: "/vision/devices" },
        { title: "VisionOverview", path: "/vision/vision" },
        { title: "MotionAlertsList", path: "/vision/motionalerts" },
        { title: "RecordingsForm", path: "/vision/recordings-form" }
    ] },
    { slug: "wms", title: "Wms", icon: "📦", screens: [
        { title: "InventoryForm", path: "/wms/inventory-form" },
        { title: "WarehousesForm", path: "/wms/warehouses-form" },
        { title: "ShipmentsForm", path: "/wms/shipments-form" },
        { title: "BinsList", path: "/wms/bins" },
        { title: "WmsPermissions", path: "/wms/wmspermissions" },
        { title: "BinsForm", path: "/wms/bins-form" },
        { title: "PickingWavesForm", path: "/wms/pickingwaves-form" },
        { title: "ShipmentsList", path: "/wms/shipments" },
        { title: "WarehousesList", path: "/wms/warehouses" },
        { title: "PickingWavesList", path: "/wms/pickingwaves" },
        { title: "InventoryList", path: "/wms/inventory" },
        { title: "WmsOverview", path: "/wms/wms" }
    ] },
];

const Navigation: React.FC = () => {
  const [openModule, setOpenModule] = useState<string | null>(null);

  return (
    <nav className="side-nav">
      <div className="nav-header">
        <Link to="/" className="logo">All-in-One</Link>
      </div>
      <div className="nav-section">
        <h3>Módulos e Telas</h3>
        <ul>
          {modulesData.map(mod => (
            <li key={mod.slug} className="nav-item-group">
              <div 
                className={`module-link ${openModule === mod.slug ? 'active' : ''}`}
                onClick={() => setOpenModule(openModule === mod.slug ? null : mod.slug)}
                style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '12px 16px', fontWeight: 700, border: '2px solid transparent' }}
              >
                <span className="icon" style={{ marginRight: '12px' }}>{mod.icon}</span>
                <span className="title" style={{ flex: 1 }}>{mod.title}</span>
                <span>{openModule === mod.slug ? '▼' : '▶'}</span>
              </div>
              {openModule === mod.slug && (
                <ul className="sub-menu" style={{ listStyle: 'none', paddingLeft: '24px', background: '#f9fafa' }}>
                  {mod.screens.map(screen => (
                    <li key={screen.path}>
                      <Link to={screen.path} style={{ fontSize: '13px', padding: '8px 16px', display: 'block', color: '#536159' }}>
                        {screen.title}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;

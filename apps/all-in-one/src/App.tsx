
import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Home from './pages/Home';
import './index.css';
const IdentityIdentityOverview = lazy(() => import('./pages/identity/IdentityOverview'));
const IdentityAuthGateway = lazy(() => import('./pages/identity/AuthGateway'));
const IdentityKycVerification = lazy(() => import('./pages/identity/KycVerification'));
const IdentityKybBusiness = lazy(() => import('./pages/identity/KybBusiness'));
const IdentityMfaManager = lazy(() => import('./pages/identity/MfaManager'));
const IdentityConsentLgpd = lazy(() => import('./pages/identity/ConsentLgpd'));
const IdentitySessionControl = lazy(() => import('./pages/identity/SessionControl'));
const BusinessBusinessOverview = lazy(() => import('./pages/business/BusinessOverview'));
const PermissionsPermissionsOverview = lazy(() => import('./pages/permissions/PermissionsOverview'));
const FinanceFinanceOverview = lazy(() => import('./pages/finance/FinanceOverview'));
const FinanceWalletLedger = lazy(() => import('./pages/finance/WalletLedger'));
const MarketplaceMarketplaceOverview = lazy(() => import('./pages/marketplace/MarketplaceOverview'));
const StockStockOverview = lazy(() => import('./pages/stock/StockOverview'));
const DeliveryDeliveryOverview = lazy(() => import('./pages/delivery/DeliveryOverview'));
const RidersRidersOverview = lazy(() => import('./pages/riders/RidersOverview'));
const ServicesServicesOverview = lazy(() => import('./pages/services/ServicesOverview'));
const MobilityMobilityOverview = lazy(() => import('./pages/mobility/MobilityOverview'));
const JobsJobsOverview = lazy(() => import('./pages/jobs/JobsOverview'));
const JobsCandidateResume = lazy(() => import('./pages/jobs/CandidateResume'));
const JobsCtpsImport = lazy(() => import('./pages/jobs/CtpsImport'));
const JobsVacancySearch = lazy(() => import('./pages/jobs/VacancySearch'));
const JobsRecruiterResumeReview = lazy(() => import('./pages/jobs/RecruiterResumeReview'));
const ErpErpOverview = lazy(() => import('./pages/erp/ErpOverview'));
const WmsWmsOverview = lazy(() => import('./pages/wms/WmsOverview'));
const TmsTmsOverview = lazy(() => import('./pages/tms/TmsOverview'));
const CrmCrmOverview = lazy(() => import('./pages/crm/CrmOverview'));
const BpmBpmOverview = lazy(() => import('./pages/bpm/BpmOverview'));
const DocumentDocumentOverview = lazy(() => import('./pages/document/DocumentOverview'));
const HrHrOverview = lazy(() => import('./pages/hr/HrOverview'));
const HealthHealthOverview = lazy(() => import('./pages/health/HealthOverview'));
const VisionVisionOverview = lazy(() => import('./pages/vision/VisionOverview'));
const LegalLegalOverview = lazy(() => import('./pages/legal/LegalOverview'));
const PropertyPropertyOverview = lazy(() => import('./pages/property/PropertyOverview'));
const BiBiOverview = lazy(() => import('./pages/bi/BiOverview'));
const Ai_coreAi_coreOverview = lazy(() => import('./pages/ai_core/Ai_coreOverview'));
const Api_hubApi_hubOverview = lazy(() => import('./pages/api_hub/Api_hubOverview'));

const BpmProcessesList = lazy(() => import('./pages/bpm/ProcessesList'));
const BpmProcessesForm = lazy(() => import('./pages/bpm/ProcessesForm'));
const BpmBpmPermissions = lazy(() => import('./pages/bpm/BpmPermissions'));
const BpmSlaPoliciesForm = lazy(() => import('./pages/bpm/SlaPoliciesForm'));
const BpmWorkflowInstancesForm = lazy(() => import('./pages/bpm/WorkflowInstancesForm'));
const BpmTasksForm = lazy(() => import('./pages/bpm/TasksForm'));
const BpmTasksList = lazy(() => import('./pages/bpm/TasksList'));
const BpmSlaPoliciesList = lazy(() => import('./pages/bpm/SlaPoliciesList'));
const BpmWorkflowInstancesList = lazy(() => import('./pages/bpm/WorkflowInstancesList'));
const HealthAppointmentsForm = lazy(() => import('./pages/health/AppointmentsForm'));
const HealthPrescriptionsList = lazy(() => import('./pages/health/PrescriptionsList'));
const HealthPatientsForm = lazy(() => import('./pages/health/PatientsForm'));
const HealthMedicalRecordsForm = lazy(() => import('./pages/health/MedicalRecordsForm'));
const HealthBedsForm = lazy(() => import('./pages/health/BedsForm'));
const HealthMedicalRecordsList = lazy(() => import('./pages/health/MedicalRecordsList'));
const HealthAppointmentsList = lazy(() => import('./pages/health/AppointmentsList'));
const HealthHealthPermissions = lazy(() => import('./pages/health/HealthPermissions'));
const HealthPrescriptionsForm = lazy(() => import('./pages/health/PrescriptionsForm'));
const HealthBedsList = lazy(() => import('./pages/health/BedsList'));
const HealthPatientsList = lazy(() => import('./pages/health/PatientsList'));
const JobsResumesList = lazy(() => import('./pages/jobs/ResumesList'));
const JobsResumeAccessLogsForm = lazy(() => import('./pages/jobs/ResumeAccessLogsForm'));
const JobsEmploymentRecordsList = lazy(() => import('./pages/jobs/EmploymentRecordsList'));
const JobsResumeDocumentsForm = lazy(() => import('./pages/jobs/ResumeDocumentsForm'));
const JobsApplicationsForm = lazy(() => import('./pages/jobs/ApplicationsForm'));
const JobsResumesForm = lazy(() => import('./pages/jobs/ResumesForm'));
const JobsJobPostingsForm = lazy(() => import('./pages/jobs/JobPostingsForm'));
const JobsResumeAccessLogsList = lazy(() => import('./pages/jobs/ResumeAccessLogsList'));
const JobsJobsPermissions = lazy(() => import('./pages/jobs/JobsPermissions'));
const JobsApplicationsList = lazy(() => import('./pages/jobs/ApplicationsList'));
const JobsJobPostingsList = lazy(() => import('./pages/jobs/JobPostingsList'));
const JobsEmploymentRecordsForm = lazy(() => import('./pages/jobs/EmploymentRecordsForm'));
const JobsResumeDocumentsList = lazy(() => import('./pages/jobs/ResumeDocumentsList'));
const IdentityConsentRecordsList = lazy(() => import('./pages/identity/ConsentRecordsList'));
const IdentityDocumentsForm = lazy(() => import('./pages/identity/DocumentsForm'));
const IdentitySessionsForm = lazy(() => import('./pages/identity/SessionsForm'));
const IdentityIdentityVerificationsForm = lazy(() => import('./pages/identity/IdentityVerificationsForm'));
const IdentityBiometricsList = lazy(() => import('./pages/identity/BiometricsList'));
const IdentityUsersList = lazy(() => import('./pages/identity/UsersList'));
const IdentityIdentityPermissions = lazy(() => import('./pages/identity/IdentityPermissions'));
const IdentityConsentRecordsForm = lazy(() => import('./pages/identity/ConsentRecordsForm'));
const IdentityBiometricsForm = lazy(() => import('./pages/identity/BiometricsForm'));
const IdentitySessionsList = lazy(() => import('./pages/identity/SessionsList'));
const IdentityUsersForm = lazy(() => import('./pages/identity/UsersForm'));
const IdentityDocumentsList = lazy(() => import('./pages/identity/DocumentsList'));
const IdentityIdentityVerificationsList = lazy(() => import('./pages/identity/IdentityVerificationsList'));
const MobilityFareRulesForm = lazy(() => import('./pages/mobility/FareRulesForm'));
const MobilityRoutesForm = lazy(() => import('./pages/mobility/RoutesForm'));
const MobilityFareRulesList = lazy(() => import('./pages/mobility/FareRulesList'));
const MobilityTicketsList = lazy(() => import('./pages/mobility/TicketsList'));
const MobilityRidesList = lazy(() => import('./pages/mobility/RidesList'));
const MobilityRoutesList = lazy(() => import('./pages/mobility/RoutesList'));
const MobilityStopsForm = lazy(() => import('./pages/mobility/StopsForm'));
const MobilityMobilityPermissions = lazy(() => import('./pages/mobility/MobilityPermissions'));
const MobilityRidesForm = lazy(() => import('./pages/mobility/RidesForm'));
const MobilityStopsList = lazy(() => import('./pages/mobility/StopsList'));
const MobilityTicketsForm = lazy(() => import('./pages/mobility/TicketsForm'));
const CrmActivitiesForm = lazy(() => import('./pages/crm/ActivitiesForm'));
const CrmOpportunitiesList = lazy(() => import('./pages/crm/OpportunitiesList'));
const CrmLeadsForm = lazy(() => import('./pages/crm/LeadsForm'));
const CrmLeadsList = lazy(() => import('./pages/crm/LeadsList'));
const CrmCampaignsList = lazy(() => import('./pages/crm/CampaignsList'));
const CrmOpportunitiesForm = lazy(() => import('./pages/crm/OpportunitiesForm'));
const CrmCampaignsForm = lazy(() => import('./pages/crm/CampaignsForm'));
const CrmCrmPermissions = lazy(() => import('./pages/crm/CrmPermissions'));
const CrmActivitiesList = lazy(() => import('./pages/crm/ActivitiesList'));
const BiDatasetsList = lazy(() => import('./pages/bi/DatasetsList'));
const BiBiPermissions = lazy(() => import('./pages/bi/BiPermissions'));
const BiDashboardsList = lazy(() => import('./pages/bi/DashboardsList'));
const BiExportsForm = lazy(() => import('./pages/bi/ExportsForm'));
const BiDashboardsForm = lazy(() => import('./pages/bi/DashboardsForm'));
const BiIndicatorsForm = lazy(() => import('./pages/bi/IndicatorsForm'));
const BiIndicatorsList = lazy(() => import('./pages/bi/IndicatorsList'));
const BiExportsList = lazy(() => import('./pages/bi/ExportsList'));
const BiDatasetsForm = lazy(() => import('./pages/bi/DatasetsForm'));
const MarketplaceProductsForm = lazy(() => import('./pages/marketplace/ProductsForm'));
const MarketplacePepitaGrantsForm = lazy(() => import('./pages/marketplace/PepitaGrantsForm'));
const MarketplaceStoresList = lazy(() => import('./pages/marketplace/StoresList'));
const MarketplaceDisputesList = lazy(() => import('./pages/marketplace/DisputesList'));
const MarketplaceOrdersForm = lazy(() => import('./pages/marketplace/OrdersForm'));
const MarketplaceDisputesForm = lazy(() => import('./pages/marketplace/DisputesForm'));
const MarketplaceMarketplacePermissions = lazy(() => import('./pages/marketplace/MarketplacePermissions'));
const MarketplaceProductsList = lazy(() => import('./pages/marketplace/ProductsList'));
const MarketplaceCartsForm = lazy(() => import('./pages/marketplace/CartsForm'));
const MarketplaceCartsList = lazy(() => import('./pages/marketplace/CartsList'));
const MarketplaceOrdersList = lazy(() => import('./pages/marketplace/OrdersList'));
const MarketplaceReviewsList = lazy(() => import('./pages/marketplace/ReviewsList'));
const MarketplaceStoresForm = lazy(() => import('./pages/marketplace/StoresForm'));
const MarketplaceReviewsForm = lazy(() => import('./pages/marketplace/ReviewsForm'));
const MarketplacePepitaGrantsList = lazy(() => import('./pages/marketplace/PepitaGrantsList'));
const BusinessUserCompanyMembershipsList = lazy(() => import('./pages/business/UserCompanyMembershipsList'));
const BusinessCompanyDocumentsList = lazy(() => import('./pages/business/CompanyDocumentsList'));
const BusinessUserCompanyMembershipsForm = lazy(() => import('./pages/business/UserCompanyMembershipsForm'));
const BusinessCatalogOffersList = lazy(() => import('./pages/business/CatalogOffersList'));
const BusinessCompaniesList = lazy(() => import('./pages/business/CompaniesList'));
const BusinessBranchesForm = lazy(() => import('./pages/business/BranchesForm'));
const BusinessBusinessPermissions = lazy(() => import('./pages/business/BusinessPermissions'));
const BusinessCompaniesForm = lazy(() => import('./pages/business/CompaniesForm'));
const BusinessBranchesList = lazy(() => import('./pages/business/BranchesList'));
const BusinessCompanyDocumentsForm = lazy(() => import('./pages/business/CompanyDocumentsForm'));
const BusinessCatalogOffersForm = lazy(() => import('./pages/business/CatalogOffersForm'));
const RidersVehiclesForm = lazy(() => import('./pages/riders/VehiclesForm'));
const RidersRiderProfilesList = lazy(() => import('./pages/riders/RiderProfilesList'));
const RidersRiderDocumentsForm = lazy(() => import('./pages/riders/RiderDocumentsForm'));
const RidersRiderDocumentsList = lazy(() => import('./pages/riders/RiderDocumentsList'));
const RidersRidersPermissions = lazy(() => import('./pages/riders/RidersPermissions'));
const RidersRiderReviewsForm = lazy(() => import('./pages/riders/RiderReviewsForm'));
const RidersVehiclesList = lazy(() => import('./pages/riders/VehiclesList'));
const RidersRiderProfilesForm = lazy(() => import('./pages/riders/RiderProfilesForm'));
const RidersRiderReviewsList = lazy(() => import('./pages/riders/RiderReviewsList'));
const VisionStreamsForm = lazy(() => import('./pages/vision/StreamsForm'));
const VisionRecordingsList = lazy(() => import('./pages/vision/RecordingsList'));
const VisionMotionAlertsForm = lazy(() => import('./pages/vision/MotionAlertsForm'));
const VisionDevicesForm = lazy(() => import('./pages/vision/DevicesForm'));
const VisionVisionPermissions = lazy(() => import('./pages/vision/VisionPermissions'));
const VisionStreamsList = lazy(() => import('./pages/vision/StreamsList'));
const VisionDevicesList = lazy(() => import('./pages/vision/DevicesList'));
const VisionMotionAlertsList = lazy(() => import('./pages/vision/MotionAlertsList'));
const VisionRecordingsForm = lazy(() => import('./pages/vision/RecordingsForm'));
const PermissionsUserRolesList = lazy(() => import('./pages/permissions/UserRolesList'));
const PermissionsRolesList = lazy(() => import('./pages/permissions/RolesList'));
const PermissionsApprovalLimitsList = lazy(() => import('./pages/permissions/ApprovalLimitsList'));
const PermissionsPermissionsList = lazy(() => import('./pages/permissions/PermissionsList'));
const PermissionsUserRolesForm = lazy(() => import('./pages/permissions/UserRolesForm'));
const PermissionsPermissionsPermissions = lazy(() => import('./pages/permissions/PermissionsPermissions'));
const PermissionsPermissionsForm = lazy(() => import('./pages/permissions/PermissionsForm'));
const PermissionsApprovalLimitsForm = lazy(() => import('./pages/permissions/ApprovalLimitsForm'));
const PermissionsAccessPoliciesList = lazy(() => import('./pages/permissions/AccessPoliciesList'));
const PermissionsRolesForm = lazy(() => import('./pages/permissions/RolesForm'));
const PermissionsAccessPoliciesForm = lazy(() => import('./pages/permissions/AccessPoliciesForm'));
const Api_hubApiClientsForm = lazy(() => import('./pages/api_hub/ApiClientsForm'));
const Api_hubApi_hubPermissions = lazy(() => import('./pages/api_hub/Api_hubPermissions'));
const Api_hubApiKeysForm = lazy(() => import('./pages/api_hub/ApiKeysForm'));
const Api_hubApiClientsList = lazy(() => import('./pages/api_hub/ApiClientsList'));
const Api_hubApiKeysList = lazy(() => import('./pages/api_hub/ApiKeysList'));
const Api_hubIntegrationRunsForm = lazy(() => import('./pages/api_hub/IntegrationRunsForm'));
const Api_hubWebhooksList = lazy(() => import('./pages/api_hub/WebhooksList'));
const Api_hubWebhooksForm = lazy(() => import('./pages/api_hub/WebhooksForm'));
const Api_hubIntegrationRunsList = lazy(() => import('./pages/api_hub/IntegrationRunsList'));
const LegalLegalPermissions = lazy(() => import('./pages/legal/LegalPermissions'));
const LegalHearingsForm = lazy(() => import('./pages/legal/HearingsForm'));
const LegalDeadlinesForm = lazy(() => import('./pages/legal/DeadlinesForm'));
const LegalLegalContractsList = lazy(() => import('./pages/legal/LegalContractsList'));
const LegalDeadlinesList = lazy(() => import('./pages/legal/DeadlinesList'));
const LegalCasesList = lazy(() => import('./pages/legal/CasesList'));
const LegalLegalContractsForm = lazy(() => import('./pages/legal/LegalContractsForm'));
const LegalHearingsList = lazy(() => import('./pages/legal/HearingsList'));
const LegalCasesForm = lazy(() => import('./pages/legal/CasesForm'));
const TmsFreightsList = lazy(() => import('./pages/tms/FreightsList'));
const TmsRoutesForm = lazy(() => import('./pages/tms/RoutesForm'));
const TmsTmsPermissions = lazy(() => import('./pages/tms/TmsPermissions'));
const TmsFreightAuditsList = lazy(() => import('./pages/tms/FreightAuditsList'));
const TmsProofsOfDeliveryList = lazy(() => import('./pages/tms/ProofsOfDeliveryList'));
const TmsRoutesList = lazy(() => import('./pages/tms/RoutesList'));
const TmsFreightsForm = lazy(() => import('./pages/tms/FreightsForm'));
const TmsProofsOfDeliveryForm = lazy(() => import('./pages/tms/ProofsOfDeliveryForm'));
const TmsCarriersList = lazy(() => import('./pages/tms/CarriersList'));
const TmsCarriersForm = lazy(() => import('./pages/tms/CarriersForm'));
const TmsFreightAuditsForm = lazy(() => import('./pages/tms/FreightAuditsForm'));
const DocumentFoldersList = lazy(() => import('./pages/document/FoldersList'));
const DocumentVersionsForm = lazy(() => import('./pages/document/VersionsForm'));
const DocumentDocumentsForm = lazy(() => import('./pages/document/DocumentsForm'));
const DocumentDocumentPermissions = lazy(() => import('./pages/document/DocumentPermissions'));
const DocumentRetentionPoliciesForm = lazy(() => import('./pages/document/RetentionPoliciesForm'));
const DocumentFoldersForm = lazy(() => import('./pages/document/FoldersForm'));
const DocumentRetentionPoliciesList = lazy(() => import('./pages/document/RetentionPoliciesList'));
const DocumentVersionsList = lazy(() => import('./pages/document/VersionsList'));
const DocumentDocumentsList = lazy(() => import('./pages/document/DocumentsList'));
const ServicesProvidersList = lazy(() => import('./pages/services/ProvidersList'));
const ServicesServicesPermissions = lazy(() => import('./pages/services/ServicesPermissions'));
const ServicesProvidersForm = lazy(() => import('./pages/services/ProvidersForm'));
const ServicesVisitsForm = lazy(() => import('./pages/services/VisitsForm'));
const ServicesEvidenceForm = lazy(() => import('./pages/services/EvidenceForm'));
const ServicesServiceContractsForm = lazy(() => import('./pages/services/ServiceContractsForm'));
const ServicesQuotesList = lazy(() => import('./pages/services/QuotesList'));
const ServicesServiceContractsList = lazy(() => import('./pages/services/ServiceContractsList'));
const ServicesVisitsList = lazy(() => import('./pages/services/VisitsList'));
const ServicesEvidenceList = lazy(() => import('./pages/services/EvidenceList'));
const ServicesQuotesForm = lazy(() => import('./pages/services/QuotesForm'));
const HrCandidatesForm = lazy(() => import('./pages/hr/CandidatesForm'));
const HrCoursesList = lazy(() => import('./pages/hr/CoursesList'));
const HrHrPermissions = lazy(() => import('./pages/hr/HrPermissions'));
const HrOccupationalRecordsList = lazy(() => import('./pages/hr/OccupationalRecordsList'));
const HrEmployeesList = lazy(() => import('./pages/hr/EmployeesList'));
const HrPayrollRunsList = lazy(() => import('./pages/hr/PayrollRunsList'));
const HrPayrollRunsForm = lazy(() => import('./pages/hr/PayrollRunsForm'));
const HrCandidatesList = lazy(() => import('./pages/hr/CandidatesList'));
const HrOccupationalRecordsForm = lazy(() => import('./pages/hr/OccupationalRecordsForm'));
const HrEmployeesForm = lazy(() => import('./pages/hr/EmployeesForm'));
const HrCoursesForm = lazy(() => import('./pages/hr/CoursesForm'));
const DeliveryInsuranceOptionsList = lazy(() => import('./pages/delivery/InsuranceOptionsList'));
const DeliveryProofsForm = lazy(() => import('./pages/delivery/ProofsForm'));
const DeliveryDeliveryRequestsList = lazy(() => import('./pages/delivery/DeliveryRequestsList'));
const DeliveryAssignmentsList = lazy(() => import('./pages/delivery/AssignmentsList'));
const DeliveryProofsList = lazy(() => import('./pages/delivery/ProofsList'));
const DeliveryQuotesList = lazy(() => import('./pages/delivery/QuotesList'));
const DeliveryInsuranceOptionsForm = lazy(() => import('./pages/delivery/InsuranceOptionsForm'));
const DeliveryDeliveryPermissions = lazy(() => import('./pages/delivery/DeliveryPermissions'));
const DeliveryDeliveryRequestsForm = lazy(() => import('./pages/delivery/DeliveryRequestsForm'));
const DeliveryQuotesForm = lazy(() => import('./pages/delivery/QuotesForm'));
const DeliveryAssignmentsForm = lazy(() => import('./pages/delivery/AssignmentsForm'));
const PropertyAssembliesList = lazy(() => import('./pages/property/AssembliesList'));
const PropertyPropertiesList = lazy(() => import('./pages/property/PropertiesList'));
const PropertyLeasesForm = lazy(() => import('./pages/property/LeasesForm'));
const PropertyUnitsForm = lazy(() => import('./pages/property/UnitsForm'));
const PropertyMaintenanceOrdersList = lazy(() => import('./pages/property/MaintenanceOrdersList'));
const PropertyUnitsList = lazy(() => import('./pages/property/UnitsList'));
const PropertyPropertyPermissions = lazy(() => import('./pages/property/PropertyPermissions'));
const PropertyLeasesList = lazy(() => import('./pages/property/LeasesList'));
const PropertyAssembliesForm = lazy(() => import('./pages/property/AssembliesForm'));
const PropertyMaintenanceOrdersForm = lazy(() => import('./pages/property/MaintenanceOrdersForm'));
const PropertyPropertiesForm = lazy(() => import('./pages/property/PropertiesForm'));
const StockPriceRulesList = lazy(() => import('./pages/stock/PriceRulesList'));
const StockCatalogProductsForm = lazy(() => import('./pages/stock/CatalogProductsForm'));
const StockPriceRulesForm = lazy(() => import('./pages/stock/PriceRulesForm'));
const StockSuppliersForm = lazy(() => import('./pages/stock/SuppliersForm'));
const StockSupplierOrdersForm = lazy(() => import('./pages/stock/SupplierOrdersForm'));
const StockDiscountQuotesForm = lazy(() => import('./pages/stock/DiscountQuotesForm'));
const StockDiscountQuotesList = lazy(() => import('./pages/stock/DiscountQuotesList'));
const StockSupplierOrdersList = lazy(() => import('./pages/stock/SupplierOrdersList'));
const StockCatalogProductsList = lazy(() => import('./pages/stock/CatalogProductsList'));
const StockSuppliersList = lazy(() => import('./pages/stock/SuppliersList'));
const StockStockPermissions = lazy(() => import('./pages/stock/StockPermissions'));
const ErpCostCentersForm = lazy(() => import('./pages/erp/CostCentersForm'));
const ErpPayablesList = lazy(() => import('./pages/erp/PayablesList'));
const ErpFiscalDocumentsForm = lazy(() => import('./pages/erp/FiscalDocumentsForm'));
const ErpCostCentersList = lazy(() => import('./pages/erp/CostCentersList'));
const ErpAccountsForm = lazy(() => import('./pages/erp/AccountsForm'));
const ErpPayablesForm = lazy(() => import('./pages/erp/PayablesForm'));
const ErpFiscalDocumentsList = lazy(() => import('./pages/erp/FiscalDocumentsList'));
const ErpReceivablesList = lazy(() => import('./pages/erp/ReceivablesList'));
const ErpReceivablesForm = lazy(() => import('./pages/erp/ReceivablesForm'));
const ErpAccountsList = lazy(() => import('./pages/erp/AccountsList'));
const ErpErpPermissions = lazy(() => import('./pages/erp/ErpPermissions'));
const WmsInventoryForm = lazy(() => import('./pages/wms/InventoryForm'));
const WmsWarehousesForm = lazy(() => import('./pages/wms/WarehousesForm'));
const WmsShipmentsForm = lazy(() => import('./pages/wms/ShipmentsForm'));
const WmsBinsList = lazy(() => import('./pages/wms/BinsList'));
const WmsWmsPermissions = lazy(() => import('./pages/wms/WmsPermissions'));
const WmsBinsForm = lazy(() => import('./pages/wms/BinsForm'));
const WmsPickingWavesForm = lazy(() => import('./pages/wms/PickingWavesForm'));
const WmsShipmentsList = lazy(() => import('./pages/wms/ShipmentsList'));
const WmsWarehousesList = lazy(() => import('./pages/wms/WarehousesList'));
const WmsPickingWavesList = lazy(() => import('./pages/wms/PickingWavesList'));
const WmsInventoryList = lazy(() => import('./pages/wms/InventoryList'));
const FinanceInvoicesList = lazy(() => import('./pages/finance/InvoicesList'));
const FinanceEscrowsList = lazy(() => import('./pages/finance/EscrowsList'));
const FinanceEscrowsForm = lazy(() => import('./pages/finance/EscrowsForm'));
const FinanceWalletsForm = lazy(() => import('./pages/finance/WalletsForm'));
const FinanceLedgerEntriesList = lazy(() => import('./pages/finance/LedgerEntriesList'));
const FinanceSplitsForm = lazy(() => import('./pages/finance/SplitsForm'));
const FinanceFinancePermissions = lazy(() => import('./pages/finance/FinancePermissions'));
const FinanceInvoicesForm = lazy(() => import('./pages/finance/InvoicesForm'));
const FinanceWalletsList = lazy(() => import('./pages/finance/WalletsList'));
const FinanceSplitsList = lazy(() => import('./pages/finance/SplitsList'));
const FinanceLedgerEntriesForm = lazy(() => import('./pages/finance/LedgerEntriesForm'));
const Ai_coreModelRunsList = lazy(() => import('./pages/ai_core/ModelRunsList'));
const Ai_coreModerationDecisionsList = lazy(() => import('./pages/ai_core/ModerationDecisionsList'));
const Ai_coreModelRunsForm = lazy(() => import('./pages/ai_core/ModelRunsForm'));
const Ai_coreAi_corePermissions = lazy(() => import('./pages/ai_core/Ai_corePermissions'));
const Ai_coreAiMemoriesForm = lazy(() => import('./pages/ai_core/AiMemoriesForm'));
const Ai_coreAiMemoriesList = lazy(() => import('./pages/ai_core/AiMemoriesList'));
const Ai_coreModerationDecisionsForm = lazy(() => import('./pages/ai_core/ModerationDecisionsForm'));

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Navigation />
        <main className="content-area">
          <Suspense fallback={<div className="loader">Carregando...</div>}>
            <Routes>
              <Route path="/" element={<Home />} />
                            <Route path="/identity" element={IdentityIdentityOverview ? <IdentityIdentityOverview /> : <div>Carregando...</div>} />
              <Route path="/identity/auth-gateway" element={IdentityAuthGateway ? <IdentityAuthGateway /> : <div>Carregando...</div>} />
              <Route path="/identity/kyc-verification" element={IdentityKycVerification ? <IdentityKycVerification /> : <div>Carregando...</div>} />
              <Route path="/identity/kyb-business" element={IdentityKybBusiness ? <IdentityKybBusiness /> : <div>Carregando...</div>} />
              <Route path="/identity/mfa-manager" element={IdentityMfaManager ? <IdentityMfaManager /> : <div>Carregando...</div>} />
              <Route path="/identity/consent-lgpd" element={IdentityConsentLgpd ? <IdentityConsentLgpd /> : <div>Carregando...</div>} />
              <Route path="/identity/session-control" element={IdentitySessionControl ? <IdentitySessionControl /> : <div>Carregando...</div>} />
              <Route path="/business" element={BusinessBusinessOverview ? <BusinessBusinessOverview /> : <div>Carregando...</div>} />
              <Route path="/permissions" element={PermissionsPermissionsOverview ? <PermissionsPermissionsOverview /> : <div>Carregando...</div>} />
              <Route path="/finance" element={FinanceFinanceOverview ? <FinanceFinanceOverview /> : <div>Carregando...</div>} />
              <Route path="/finance/wallet-ledger" element={FinanceWalletLedger ? <FinanceWalletLedger /> : <div>Carregando...</div>} />
              <Route path="/marketplace" element={MarketplaceMarketplaceOverview ? <MarketplaceMarketplaceOverview /> : <div>Carregando...</div>} />
              <Route path="/stock" element={StockStockOverview ? <StockStockOverview /> : <div>Carregando...</div>} />
              <Route path="/delivery" element={DeliveryDeliveryOverview ? <DeliveryDeliveryOverview /> : <div>Carregando...</div>} />
              <Route path="/riders" element={RidersRidersOverview ? <RidersRidersOverview /> : <div>Carregando...</div>} />
              <Route path="/services" element={ServicesServicesOverview ? <ServicesServicesOverview /> : <div>Carregando...</div>} />
              <Route path="/mobility" element={MobilityMobilityOverview ? <MobilityMobilityOverview /> : <div>Carregando...</div>} />
              <Route path="/jobs" element={JobsJobsOverview ? <JobsJobsOverview /> : <div>Carregando...</div>} />
              <Route path="/jobs/candidate-resume" element={JobsCandidateResume ? <JobsCandidateResume /> : <div>Carregando...</div>} />
              <Route path="/jobs/ctps-import" element={JobsCtpsImport ? <JobsCtpsImport /> : <div>Carregando...</div>} />
              <Route path="/jobs/vacancy-search" element={JobsVacancySearch ? <JobsVacancySearch /> : <div>Carregando...</div>} />
              <Route path="/jobs/recruiter-resume-review" element={JobsRecruiterResumeReview ? <JobsRecruiterResumeReview /> : <div>Carregando...</div>} />
              <Route path="/erp" element={ErpErpOverview ? <ErpErpOverview /> : <div>Carregando...</div>} />
              <Route path="/wms" element={WmsWmsOverview ? <WmsWmsOverview /> : <div>Carregando...</div>} />
              <Route path="/tms" element={TmsTmsOverview ? <TmsTmsOverview /> : <div>Carregando...</div>} />
              <Route path="/crm" element={CrmCrmOverview ? <CrmCrmOverview /> : <div>Carregando...</div>} />
              <Route path="/bpm" element={BpmBpmOverview ? <BpmBpmOverview /> : <div>Carregando...</div>} />
              <Route path="/document" element={DocumentDocumentOverview ? <DocumentDocumentOverview /> : <div>Carregando...</div>} />
              <Route path="/hr" element={HrHrOverview ? <HrHrOverview /> : <div>Carregando...</div>} />
              <Route path="/health" element={HealthHealthOverview ? <HealthHealthOverview /> : <div>Carregando...</div>} />
              <Route path="/vision" element={VisionVisionOverview ? <VisionVisionOverview /> : <div>Carregando...</div>} />
              <Route path="/legal" element={LegalLegalOverview ? <LegalLegalOverview /> : <div>Carregando...</div>} />
              <Route path="/property" element={PropertyPropertyOverview ? <PropertyPropertyOverview /> : <div>Carregando...</div>} />
              <Route path="/bi" element={BiBiOverview ? <BiBiOverview /> : <div>Carregando...</div>} />
              <Route path="/ai_core" element={Ai_coreAi_coreOverview ? <Ai_coreAi_coreOverview /> : <div>Carregando...</div>} />
              <Route path="/api_hub" element={Api_hubApi_hubOverview ? <Api_hubApi_hubOverview /> : <div>Carregando...</div>} />
                          <Route path="/bpm/processes" element={BpmProcessesList ? <BpmProcessesList /> : <div>Carregando...</div>} />
              <Route path="/bpm/processes-form" element={BpmProcessesForm ? <BpmProcessesForm /> : <div>Carregando...</div>} />
              <Route path="/bpm/bpmpermissions" element={BpmBpmPermissions ? <BpmBpmPermissions /> : <div>Carregando...</div>} />
              <Route path="/bpm/slapolicies-form" element={BpmSlaPoliciesForm ? <BpmSlaPoliciesForm /> : <div>Carregando...</div>} />
              <Route path="/bpm/bpm" element={BpmBpmOverview ? <BpmBpmOverview /> : <div>Carregando...</div>} />
              <Route path="/bpm/workflowinstances-form" element={BpmWorkflowInstancesForm ? <BpmWorkflowInstancesForm /> : <div>Carregando...</div>} />
              <Route path="/bpm/tasks-form" element={BpmTasksForm ? <BpmTasksForm /> : <div>Carregando...</div>} />
              <Route path="/bpm/tasks" element={BpmTasksList ? <BpmTasksList /> : <div>Carregando...</div>} />
              <Route path="/bpm/slapolicies" element={BpmSlaPoliciesList ? <BpmSlaPoliciesList /> : <div>Carregando...</div>} />
              <Route path="/bpm/workflowinstances" element={BpmWorkflowInstancesList ? <BpmWorkflowInstancesList /> : <div>Carregando...</div>} />
              <Route path="/health/appointments-form" element={HealthAppointmentsForm ? <HealthAppointmentsForm /> : <div>Carregando...</div>} />
              <Route path="/health/prescriptions" element={HealthPrescriptionsList ? <HealthPrescriptionsList /> : <div>Carregando...</div>} />
              <Route path="/health/patients-form" element={HealthPatientsForm ? <HealthPatientsForm /> : <div>Carregando...</div>} />
              <Route path="/health/medicalrecords-form" element={HealthMedicalRecordsForm ? <HealthMedicalRecordsForm /> : <div>Carregando...</div>} />
              <Route path="/health/beds-form" element={HealthBedsForm ? <HealthBedsForm /> : <div>Carregando...</div>} />
              <Route path="/health/medicalrecords" element={HealthMedicalRecordsList ? <HealthMedicalRecordsList /> : <div>Carregando...</div>} />
              <Route path="/health/appointments" element={HealthAppointmentsList ? <HealthAppointmentsList /> : <div>Carregando...</div>} />
              <Route path="/health/healthpermissions" element={HealthHealthPermissions ? <HealthHealthPermissions /> : <div>Carregando...</div>} />
              <Route path="/health/prescriptions-form" element={HealthPrescriptionsForm ? <HealthPrescriptionsForm /> : <div>Carregando...</div>} />
              <Route path="/health/health" element={HealthHealthOverview ? <HealthHealthOverview /> : <div>Carregando...</div>} />
              <Route path="/health/beds" element={HealthBedsList ? <HealthBedsList /> : <div>Carregando...</div>} />
              <Route path="/health/patients" element={HealthPatientsList ? <HealthPatientsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumes" element={JobsResumesList ? <JobsResumesList /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumeaccesslogs-form" element={JobsResumeAccessLogsForm ? <JobsResumeAccessLogsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/employmentrecords" element={JobsEmploymentRecordsList ? <JobsEmploymentRecordsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumedocuments-form" element={JobsResumeDocumentsForm ? <JobsResumeDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/ctpsimport" element={JobsCtpsImport ? <JobsCtpsImport /> : <div>Carregando...</div>} />
              <Route path="/jobs/candidateresume" element={JobsCandidateResume ? <JobsCandidateResume /> : <div>Carregando...</div>} />
              <Route path="/jobs/applications-form" element={JobsApplicationsForm ? <JobsApplicationsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/recruiterresumereview" element={JobsRecruiterResumeReview ? <JobsRecruiterResumeReview /> : <div>Carregando...</div>} />
              <Route path="/jobs/vacancysearch" element={JobsVacancySearch ? <JobsVacancySearch /> : <div>Carregando...</div>} />
              <Route path="/jobs/jobs" element={JobsJobsOverview ? <JobsJobsOverview /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumes-form" element={JobsResumesForm ? <JobsResumesForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/jobpostings-form" element={JobsJobPostingsForm ? <JobsJobPostingsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumeaccesslogs" element={JobsResumeAccessLogsList ? <JobsResumeAccessLogsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/jobspermissions" element={JobsJobsPermissions ? <JobsJobsPermissions /> : <div>Carregando...</div>} />
              <Route path="/jobs/applications" element={JobsApplicationsList ? <JobsApplicationsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/jobpostings" element={JobsJobPostingsList ? <JobsJobPostingsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/employmentrecords-form" element={JobsEmploymentRecordsForm ? <JobsEmploymentRecordsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumedocuments" element={JobsResumeDocumentsList ? <JobsResumeDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/identity/sessioncontrol" element={IdentitySessionControl ? <IdentitySessionControl /> : <div>Carregando...</div>} />
              <Route path="/identity/kycverification" element={IdentityKycVerification ? <IdentityKycVerification /> : <div>Carregando...</div>} />
              <Route path="/identity/consentrecords" element={IdentityConsentRecordsList ? <IdentityConsentRecordsList /> : <div>Carregando...</div>} />
              <Route path="/identity/documents-form" element={IdentityDocumentsForm ? <IdentityDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/consentlgpd" element={IdentityConsentLgpd ? <IdentityConsentLgpd /> : <div>Carregando...</div>} />
              <Route path="/identity/sessions-form" element={IdentitySessionsForm ? <IdentitySessionsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/identityverifications-form" element={IdentityIdentityVerificationsForm ? <IdentityIdentityVerificationsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/biometrics" element={IdentityBiometricsList ? <IdentityBiometricsList /> : <div>Carregando...</div>} />
              <Route path="/identity/users" element={IdentityUsersList ? <IdentityUsersList /> : <div>Carregando...</div>} />
              <Route path="/identity/identitypermissions" element={IdentityIdentityPermissions ? <IdentityIdentityPermissions /> : <div>Carregando...</div>} />
              <Route path="/identity/identity" element={IdentityIdentityOverview ? <IdentityIdentityOverview /> : <div>Carregando...</div>} />
              <Route path="/identity/consentrecords-form" element={IdentityConsentRecordsForm ? <IdentityConsentRecordsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/kybbusiness" element={IdentityKybBusiness ? <IdentityKybBusiness /> : <div>Carregando...</div>} />
              <Route path="/identity/authgateway" element={IdentityAuthGateway ? <IdentityAuthGateway /> : <div>Carregando...</div>} />
              <Route path="/identity/biometrics-form" element={IdentityBiometricsForm ? <IdentityBiometricsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/mfamanager" element={IdentityMfaManager ? <IdentityMfaManager /> : <div>Carregando...</div>} />
              <Route path="/identity/sessions" element={IdentitySessionsList ? <IdentitySessionsList /> : <div>Carregando...</div>} />
              <Route path="/identity/users-form" element={IdentityUsersForm ? <IdentityUsersForm /> : <div>Carregando...</div>} />
              <Route path="/identity/documents" element={IdentityDocumentsList ? <IdentityDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/identity/identityverifications" element={IdentityIdentityVerificationsList ? <IdentityIdentityVerificationsList /> : <div>Carregando...</div>} />
              <Route path="/mobility/farerules-form" element={MobilityFareRulesForm ? <MobilityFareRulesForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/routes-form" element={MobilityRoutesForm ? <MobilityRoutesForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/farerules" element={MobilityFareRulesList ? <MobilityFareRulesList /> : <div>Carregando...</div>} />
              <Route path="/mobility/tickets" element={MobilityTicketsList ? <MobilityTicketsList /> : <div>Carregando...</div>} />
              <Route path="/mobility/rides" element={MobilityRidesList ? <MobilityRidesList /> : <div>Carregando...</div>} />
              <Route path="/mobility/routes" element={MobilityRoutesList ? <MobilityRoutesList /> : <div>Carregando...</div>} />
              <Route path="/mobility/stops-form" element={MobilityStopsForm ? <MobilityStopsForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/mobilitypermissions" element={MobilityMobilityPermissions ? <MobilityMobilityPermissions /> : <div>Carregando...</div>} />
              <Route path="/mobility/rides-form" element={MobilityRidesForm ? <MobilityRidesForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/stops" element={MobilityStopsList ? <MobilityStopsList /> : <div>Carregando...</div>} />
              <Route path="/mobility/tickets-form" element={MobilityTicketsForm ? <MobilityTicketsForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/mobility" element={MobilityMobilityOverview ? <MobilityMobilityOverview /> : <div>Carregando...</div>} />
              <Route path="/crm/activities-form" element={CrmActivitiesForm ? <CrmActivitiesForm /> : <div>Carregando...</div>} />
              <Route path="/crm/opportunities" element={CrmOpportunitiesList ? <CrmOpportunitiesList /> : <div>Carregando...</div>} />
              <Route path="/crm/leads-form" element={CrmLeadsForm ? <CrmLeadsForm /> : <div>Carregando...</div>} />
              <Route path="/crm/leads" element={CrmLeadsList ? <CrmLeadsList /> : <div>Carregando...</div>} />
              <Route path="/crm/campaigns" element={CrmCampaignsList ? <CrmCampaignsList /> : <div>Carregando...</div>} />
              <Route path="/crm/opportunities-form" element={CrmOpportunitiesForm ? <CrmOpportunitiesForm /> : <div>Carregando...</div>} />
              <Route path="/crm/crm" element={CrmCrmOverview ? <CrmCrmOverview /> : <div>Carregando...</div>} />
              <Route path="/crm/campaigns-form" element={CrmCampaignsForm ? <CrmCampaignsForm /> : <div>Carregando...</div>} />
              <Route path="/crm/crmpermissions" element={CrmCrmPermissions ? <CrmCrmPermissions /> : <div>Carregando...</div>} />
              <Route path="/crm/activities" element={CrmActivitiesList ? <CrmActivitiesList /> : <div>Carregando...</div>} />
              <Route path="/bi/datasets" element={BiDatasetsList ? <BiDatasetsList /> : <div>Carregando...</div>} />
              <Route path="/bi/bipermissions" element={BiBiPermissions ? <BiBiPermissions /> : <div>Carregando...</div>} />
              <Route path="/bi/bi" element={BiBiOverview ? <BiBiOverview /> : <div>Carregando...</div>} />
              <Route path="/bi/dashboards" element={BiDashboardsList ? <BiDashboardsList /> : <div>Carregando...</div>} />
              <Route path="/bi/exports-form" element={BiExportsForm ? <BiExportsForm /> : <div>Carregando...</div>} />
              <Route path="/bi/dashboards-form" element={BiDashboardsForm ? <BiDashboardsForm /> : <div>Carregando...</div>} />
              <Route path="/bi/indicators-form" element={BiIndicatorsForm ? <BiIndicatorsForm /> : <div>Carregando...</div>} />
              <Route path="/bi/indicators" element={BiIndicatorsList ? <BiIndicatorsList /> : <div>Carregando...</div>} />
              <Route path="/bi/exports" element={BiExportsList ? <BiExportsList /> : <div>Carregando...</div>} />
              <Route path="/bi/datasets-form" element={BiDatasetsForm ? <BiDatasetsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/products-form" element={MarketplaceProductsForm ? <MarketplaceProductsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/pepitagrants-form" element={MarketplacePepitaGrantsForm ? <MarketplacePepitaGrantsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/marketplace" element={MarketplaceMarketplaceOverview ? <MarketplaceMarketplaceOverview /> : <div>Carregando...</div>} />
              <Route path="/marketplace/stores" element={MarketplaceStoresList ? <MarketplaceStoresList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/disputes" element={MarketplaceDisputesList ? <MarketplaceDisputesList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/orders-form" element={MarketplaceOrdersForm ? <MarketplaceOrdersForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/disputes-form" element={MarketplaceDisputesForm ? <MarketplaceDisputesForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/marketplacepermissions" element={MarketplaceMarketplacePermissions ? <MarketplaceMarketplacePermissions /> : <div>Carregando...</div>} />
              <Route path="/marketplace/products" element={MarketplaceProductsList ? <MarketplaceProductsList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/carts-form" element={MarketplaceCartsForm ? <MarketplaceCartsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/carts" element={MarketplaceCartsList ? <MarketplaceCartsList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/orders" element={MarketplaceOrdersList ? <MarketplaceOrdersList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/reviews" element={MarketplaceReviewsList ? <MarketplaceReviewsList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/stores-form" element={MarketplaceStoresForm ? <MarketplaceStoresForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/reviews-form" element={MarketplaceReviewsForm ? <MarketplaceReviewsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/pepitagrants" element={MarketplacePepitaGrantsList ? <MarketplacePepitaGrantsList /> : <div>Carregando...</div>} />
              <Route path="/business/usercompanymemberships" element={BusinessUserCompanyMembershipsList ? <BusinessUserCompanyMembershipsList /> : <div>Carregando...</div>} />
              <Route path="/business/companydocuments" element={BusinessCompanyDocumentsList ? <BusinessCompanyDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/business/usercompanymemberships-form" element={BusinessUserCompanyMembershipsForm ? <BusinessUserCompanyMembershipsForm /> : <div>Carregando...</div>} />
              <Route path="/business/catalogoffers" element={BusinessCatalogOffersList ? <BusinessCatalogOffersList /> : <div>Carregando...</div>} />
              <Route path="/business/companies" element={BusinessCompaniesList ? <BusinessCompaniesList /> : <div>Carregando...</div>} />
              <Route path="/business/branches-form" element={BusinessBranchesForm ? <BusinessBranchesForm /> : <div>Carregando...</div>} />
              <Route path="/business/businesspermissions" element={BusinessBusinessPermissions ? <BusinessBusinessPermissions /> : <div>Carregando...</div>} />
              <Route path="/business/companies-form" element={BusinessCompaniesForm ? <BusinessCompaniesForm /> : <div>Carregando...</div>} />
              <Route path="/business/branches" element={BusinessBranchesList ? <BusinessBranchesList /> : <div>Carregando...</div>} />
              <Route path="/business/companydocuments-form" element={BusinessCompanyDocumentsForm ? <BusinessCompanyDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/business/catalogoffers-form" element={BusinessCatalogOffersForm ? <BusinessCatalogOffersForm /> : <div>Carregando...</div>} />
              <Route path="/business/business" element={BusinessBusinessOverview ? <BusinessBusinessOverview /> : <div>Carregando...</div>} />
              <Route path="/riders/vehicles-form" element={RidersVehiclesForm ? <RidersVehiclesForm /> : <div>Carregando...</div>} />
              <Route path="/riders/riderprofiles" element={RidersRiderProfilesList ? <RidersRiderProfilesList /> : <div>Carregando...</div>} />
              <Route path="/riders/riderdocuments-form" element={RidersRiderDocumentsForm ? <RidersRiderDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/riders/riderdocuments" element={RidersRiderDocumentsList ? <RidersRiderDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/riders/riders" element={RidersRidersOverview ? <RidersRidersOverview /> : <div>Carregando...</div>} />
              <Route path="/riders/riderspermissions" element={RidersRidersPermissions ? <RidersRidersPermissions /> : <div>Carregando...</div>} />
              <Route path="/riders/riderreviews-form" element={RidersRiderReviewsForm ? <RidersRiderReviewsForm /> : <div>Carregando...</div>} />
              <Route path="/riders/vehicles" element={RidersVehiclesList ? <RidersVehiclesList /> : <div>Carregando...</div>} />
              <Route path="/riders/riderprofiles-form" element={RidersRiderProfilesForm ? <RidersRiderProfilesForm /> : <div>Carregando...</div>} />
              <Route path="/riders/riderreviews" element={RidersRiderReviewsList ? <RidersRiderReviewsList /> : <div>Carregando...</div>} />
              <Route path="/vision/streams-form" element={VisionStreamsForm ? <VisionStreamsForm /> : <div>Carregando...</div>} />
              <Route path="/vision/recordings" element={VisionRecordingsList ? <VisionRecordingsList /> : <div>Carregando...</div>} />
              <Route path="/vision/motionalerts-form" element={VisionMotionAlertsForm ? <VisionMotionAlertsForm /> : <div>Carregando...</div>} />
              <Route path="/vision/devices-form" element={VisionDevicesForm ? <VisionDevicesForm /> : <div>Carregando...</div>} />
              <Route path="/vision/visionpermissions" element={VisionVisionPermissions ? <VisionVisionPermissions /> : <div>Carregando...</div>} />
              <Route path="/vision/streams" element={VisionStreamsList ? <VisionStreamsList /> : <div>Carregando...</div>} />
              <Route path="/vision/devices" element={VisionDevicesList ? <VisionDevicesList /> : <div>Carregando...</div>} />
              <Route path="/vision/vision" element={VisionVisionOverview ? <VisionVisionOverview /> : <div>Carregando...</div>} />
              <Route path="/vision/motionalerts" element={VisionMotionAlertsList ? <VisionMotionAlertsList /> : <div>Carregando...</div>} />
              <Route path="/vision/recordings-form" element={VisionRecordingsForm ? <VisionRecordingsForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/userroles" element={PermissionsUserRolesList ? <PermissionsUserRolesList /> : <div>Carregando...</div>} />
              <Route path="/permissions/roles" element={PermissionsRolesList ? <PermissionsRolesList /> : <div>Carregando...</div>} />
              <Route path="/permissions/approvallimits" element={PermissionsApprovalLimitsList ? <PermissionsApprovalLimitsList /> : <div>Carregando...</div>} />
              <Route path="/permissions/permissions" element={PermissionsPermissionsList ? <PermissionsPermissionsList /> : <div>Carregando...</div>} />
              <Route path="/permissions/userroles-form" element={PermissionsUserRolesForm ? <PermissionsUserRolesForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/permissionspermissions" element={PermissionsPermissionsPermissions ? <PermissionsPermissionsPermissions /> : <div>Carregando...</div>} />
              <Route path="/permissions/permissions-form" element={PermissionsPermissionsForm ? <PermissionsPermissionsForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/approvallimits-form" element={PermissionsApprovalLimitsForm ? <PermissionsApprovalLimitsForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/accesspolicies" element={PermissionsAccessPoliciesList ? <PermissionsAccessPoliciesList /> : <div>Carregando...</div>} />
              <Route path="/permissions/permissions" element={PermissionsPermissionsOverview ? <PermissionsPermissionsOverview /> : <div>Carregando...</div>} />
              <Route path="/permissions/roles-form" element={PermissionsRolesForm ? <PermissionsRolesForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/accesspolicies-form" element={PermissionsAccessPoliciesForm ? <PermissionsAccessPoliciesForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/apiclients-form" element={Api_hubApiClientsForm ? <Api_hubApiClientsForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/api_hubpermissions" element={Api_hubApi_hubPermissions ? <Api_hubApi_hubPermissions /> : <div>Carregando...</div>} />
              <Route path="/api_hub/apikeys-form" element={Api_hubApiKeysForm ? <Api_hubApiKeysForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/apiclients" element={Api_hubApiClientsList ? <Api_hubApiClientsList /> : <div>Carregando...</div>} />
              <Route path="/api_hub/apikeys" element={Api_hubApiKeysList ? <Api_hubApiKeysList /> : <div>Carregando...</div>} />
              <Route path="/api_hub/integrationruns-form" element={Api_hubIntegrationRunsForm ? <Api_hubIntegrationRunsForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/webhooks" element={Api_hubWebhooksList ? <Api_hubWebhooksList /> : <div>Carregando...</div>} />
              <Route path="/api_hub/api_hub" element={Api_hubApi_hubOverview ? <Api_hubApi_hubOverview /> : <div>Carregando...</div>} />
              <Route path="/api_hub/webhooks-form" element={Api_hubWebhooksForm ? <Api_hubWebhooksForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/integrationruns" element={Api_hubIntegrationRunsList ? <Api_hubIntegrationRunsList /> : <div>Carregando...</div>} />
              <Route path="/legal/legalpermissions" element={LegalLegalPermissions ? <LegalLegalPermissions /> : <div>Carregando...</div>} />
              <Route path="/legal/hearings-form" element={LegalHearingsForm ? <LegalHearingsForm /> : <div>Carregando...</div>} />
              <Route path="/legal/legal" element={LegalLegalOverview ? <LegalLegalOverview /> : <div>Carregando...</div>} />
              <Route path="/legal/deadlines-form" element={LegalDeadlinesForm ? <LegalDeadlinesForm /> : <div>Carregando...</div>} />
              <Route path="/legal/legalcontracts" element={LegalLegalContractsList ? <LegalLegalContractsList /> : <div>Carregando...</div>} />
              <Route path="/legal/deadlines" element={LegalDeadlinesList ? <LegalDeadlinesList /> : <div>Carregando...</div>} />
              <Route path="/legal/cases" element={LegalCasesList ? <LegalCasesList /> : <div>Carregando...</div>} />
              <Route path="/legal/legalcontracts-form" element={LegalLegalContractsForm ? <LegalLegalContractsForm /> : <div>Carregando...</div>} />
              <Route path="/legal/hearings" element={LegalHearingsList ? <LegalHearingsList /> : <div>Carregando...</div>} />
              <Route path="/legal/cases-form" element={LegalCasesForm ? <LegalCasesForm /> : <div>Carregando...</div>} />
              <Route path="/tms/freights" element={TmsFreightsList ? <TmsFreightsList /> : <div>Carregando...</div>} />
              <Route path="/tms/routes-form" element={TmsRoutesForm ? <TmsRoutesForm /> : <div>Carregando...</div>} />
              <Route path="/tms/tmspermissions" element={TmsTmsPermissions ? <TmsTmsPermissions /> : <div>Carregando...</div>} />
              <Route path="/tms/freightaudits" element={TmsFreightAuditsList ? <TmsFreightAuditsList /> : <div>Carregando...</div>} />
              <Route path="/tms/proofsofdelivery" element={TmsProofsOfDeliveryList ? <TmsProofsOfDeliveryList /> : <div>Carregando...</div>} />
              <Route path="/tms/tms" element={TmsTmsOverview ? <TmsTmsOverview /> : <div>Carregando...</div>} />
              <Route path="/tms/routes" element={TmsRoutesList ? <TmsRoutesList /> : <div>Carregando...</div>} />
              <Route path="/tms/freights-form" element={TmsFreightsForm ? <TmsFreightsForm /> : <div>Carregando...</div>} />
              <Route path="/tms/proofsofdelivery-form" element={TmsProofsOfDeliveryForm ? <TmsProofsOfDeliveryForm /> : <div>Carregando...</div>} />
              <Route path="/tms/carriers" element={TmsCarriersList ? <TmsCarriersList /> : <div>Carregando...</div>} />
              <Route path="/tms/carriers-form" element={TmsCarriersForm ? <TmsCarriersForm /> : <div>Carregando...</div>} />
              <Route path="/tms/freightaudits-form" element={TmsFreightAuditsForm ? <TmsFreightAuditsForm /> : <div>Carregando...</div>} />
              <Route path="/document/folders" element={DocumentFoldersList ? <DocumentFoldersList /> : <div>Carregando...</div>} />
              <Route path="/document/versions-form" element={DocumentVersionsForm ? <DocumentVersionsForm /> : <div>Carregando...</div>} />
              <Route path="/document/documents-form" element={DocumentDocumentsForm ? <DocumentDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/document/documentpermissions" element={DocumentDocumentPermissions ? <DocumentDocumentPermissions /> : <div>Carregando...</div>} />
              <Route path="/document/document" element={DocumentDocumentOverview ? <DocumentDocumentOverview /> : <div>Carregando...</div>} />
              <Route path="/document/retentionpolicies-form" element={DocumentRetentionPoliciesForm ? <DocumentRetentionPoliciesForm /> : <div>Carregando...</div>} />
              <Route path="/document/folders-form" element={DocumentFoldersForm ? <DocumentFoldersForm /> : <div>Carregando...</div>} />
              <Route path="/document/retentionpolicies" element={DocumentRetentionPoliciesList ? <DocumentRetentionPoliciesList /> : <div>Carregando...</div>} />
              <Route path="/document/versions" element={DocumentVersionsList ? <DocumentVersionsList /> : <div>Carregando...</div>} />
              <Route path="/document/documents" element={DocumentDocumentsList ? <DocumentDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/services/providers" element={ServicesProvidersList ? <ServicesProvidersList /> : <div>Carregando...</div>} />
              <Route path="/services/servicespermissions" element={ServicesServicesPermissions ? <ServicesServicesPermissions /> : <div>Carregando...</div>} />
              <Route path="/services/providers-form" element={ServicesProvidersForm ? <ServicesProvidersForm /> : <div>Carregando...</div>} />
              <Route path="/services/visits-form" element={ServicesVisitsForm ? <ServicesVisitsForm /> : <div>Carregando...</div>} />
              <Route path="/services/services" element={ServicesServicesOverview ? <ServicesServicesOverview /> : <div>Carregando...</div>} />
              <Route path="/services/evidence-form" element={ServicesEvidenceForm ? <ServicesEvidenceForm /> : <div>Carregando...</div>} />
              <Route path="/services/servicecontracts-form" element={ServicesServiceContractsForm ? <ServicesServiceContractsForm /> : <div>Carregando...</div>} />
              <Route path="/services/quotes" element={ServicesQuotesList ? <ServicesQuotesList /> : <div>Carregando...</div>} />
              <Route path="/services/servicecontracts" element={ServicesServiceContractsList ? <ServicesServiceContractsList /> : <div>Carregando...</div>} />
              <Route path="/services/visits" element={ServicesVisitsList ? <ServicesVisitsList /> : <div>Carregando...</div>} />
              <Route path="/services/evidence" element={ServicesEvidenceList ? <ServicesEvidenceList /> : <div>Carregando...</div>} />
              <Route path="/services/quotes-form" element={ServicesQuotesForm ? <ServicesQuotesForm /> : <div>Carregando...</div>} />
              <Route path="/hr/candidates-form" element={HrCandidatesForm ? <HrCandidatesForm /> : <div>Carregando...</div>} />
              <Route path="/hr/courses" element={HrCoursesList ? <HrCoursesList /> : <div>Carregando...</div>} />
              <Route path="/hr/hrpermissions" element={HrHrPermissions ? <HrHrPermissions /> : <div>Carregando...</div>} />
              <Route path="/hr/occupationalrecords" element={HrOccupationalRecordsList ? <HrOccupationalRecordsList /> : <div>Carregando...</div>} />
              <Route path="/hr/employees" element={HrEmployeesList ? <HrEmployeesList /> : <div>Carregando...</div>} />
              <Route path="/hr/payrollruns" element={HrPayrollRunsList ? <HrPayrollRunsList /> : <div>Carregando...</div>} />
              <Route path="/hr/payrollruns-form" element={HrPayrollRunsForm ? <HrPayrollRunsForm /> : <div>Carregando...</div>} />
              <Route path="/hr/candidates" element={HrCandidatesList ? <HrCandidatesList /> : <div>Carregando...</div>} />
              <Route path="/hr/occupationalrecords-form" element={HrOccupationalRecordsForm ? <HrOccupationalRecordsForm /> : <div>Carregando...</div>} />
              <Route path="/hr/hr" element={HrHrOverview ? <HrHrOverview /> : <div>Carregando...</div>} />
              <Route path="/hr/employees-form" element={HrEmployeesForm ? <HrEmployeesForm /> : <div>Carregando...</div>} />
              <Route path="/hr/courses-form" element={HrCoursesForm ? <HrCoursesForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/insuranceoptions" element={DeliveryInsuranceOptionsList ? <DeliveryInsuranceOptionsList /> : <div>Carregando...</div>} />
              <Route path="/delivery/proofs-form" element={DeliveryProofsForm ? <DeliveryProofsForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/deliveryrequests" element={DeliveryDeliveryRequestsList ? <DeliveryDeliveryRequestsList /> : <div>Carregando...</div>} />
              <Route path="/delivery/assignments" element={DeliveryAssignmentsList ? <DeliveryAssignmentsList /> : <div>Carregando...</div>} />
              <Route path="/delivery/delivery" element={DeliveryDeliveryOverview ? <DeliveryDeliveryOverview /> : <div>Carregando...</div>} />
              <Route path="/delivery/proofs" element={DeliveryProofsList ? <DeliveryProofsList /> : <div>Carregando...</div>} />
              <Route path="/delivery/quotes" element={DeliveryQuotesList ? <DeliveryQuotesList /> : <div>Carregando...</div>} />
              <Route path="/delivery/insuranceoptions-form" element={DeliveryInsuranceOptionsForm ? <DeliveryInsuranceOptionsForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/deliverypermissions" element={DeliveryDeliveryPermissions ? <DeliveryDeliveryPermissions /> : <div>Carregando...</div>} />
              <Route path="/delivery/deliveryrequests-form" element={DeliveryDeliveryRequestsForm ? <DeliveryDeliveryRequestsForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/quotes-form" element={DeliveryQuotesForm ? <DeliveryQuotesForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/assignments-form" element={DeliveryAssignmentsForm ? <DeliveryAssignmentsForm /> : <div>Carregando...</div>} />
              <Route path="/property/assemblies" element={PropertyAssembliesList ? <PropertyAssembliesList /> : <div>Carregando...</div>} />
              <Route path="/property/properties" element={PropertyPropertiesList ? <PropertyPropertiesList /> : <div>Carregando...</div>} />
              <Route path="/property/leases-form" element={PropertyLeasesForm ? <PropertyLeasesForm /> : <div>Carregando...</div>} />
              <Route path="/property/units-form" element={PropertyUnitsForm ? <PropertyUnitsForm /> : <div>Carregando...</div>} />
              <Route path="/property/maintenanceorders" element={PropertyMaintenanceOrdersList ? <PropertyMaintenanceOrdersList /> : <div>Carregando...</div>} />
              <Route path="/property/property" element={PropertyPropertyOverview ? <PropertyPropertyOverview /> : <div>Carregando...</div>} />
              <Route path="/property/units" element={PropertyUnitsList ? <PropertyUnitsList /> : <div>Carregando...</div>} />
              <Route path="/property/propertypermissions" element={PropertyPropertyPermissions ? <PropertyPropertyPermissions /> : <div>Carregando...</div>} />
              <Route path="/property/leases" element={PropertyLeasesList ? <PropertyLeasesList /> : <div>Carregando...</div>} />
              <Route path="/property/assemblies-form" element={PropertyAssembliesForm ? <PropertyAssembliesForm /> : <div>Carregando...</div>} />
              <Route path="/property/maintenanceorders-form" element={PropertyMaintenanceOrdersForm ? <PropertyMaintenanceOrdersForm /> : <div>Carregando...</div>} />
              <Route path="/property/properties-form" element={PropertyPropertiesForm ? <PropertyPropertiesForm /> : <div>Carregando...</div>} />
              <Route path="/stock/pricerules" element={StockPriceRulesList ? <StockPriceRulesList /> : <div>Carregando...</div>} />
              <Route path="/stock/catalogproducts-form" element={StockCatalogProductsForm ? <StockCatalogProductsForm /> : <div>Carregando...</div>} />
              <Route path="/stock/pricerules-form" element={StockPriceRulesForm ? <StockPriceRulesForm /> : <div>Carregando...</div>} />
              <Route path="/stock/suppliers-form" element={StockSuppliersForm ? <StockSuppliersForm /> : <div>Carregando...</div>} />
              <Route path="/stock/supplierorders-form" element={StockSupplierOrdersForm ? <StockSupplierOrdersForm /> : <div>Carregando...</div>} />
              <Route path="/stock/discountquotes-form" element={StockDiscountQuotesForm ? <StockDiscountQuotesForm /> : <div>Carregando...</div>} />
              <Route path="/stock/discountquotes" element={StockDiscountQuotesList ? <StockDiscountQuotesList /> : <div>Carregando...</div>} />
              <Route path="/stock/supplierorders" element={StockSupplierOrdersList ? <StockSupplierOrdersList /> : <div>Carregando...</div>} />
              <Route path="/stock/catalogproducts" element={StockCatalogProductsList ? <StockCatalogProductsList /> : <div>Carregando...</div>} />
              <Route path="/stock/suppliers" element={StockSuppliersList ? <StockSuppliersList /> : <div>Carregando...</div>} />
              <Route path="/stock/stock" element={StockStockOverview ? <StockStockOverview /> : <div>Carregando...</div>} />
              <Route path="/stock/stockpermissions" element={StockStockPermissions ? <StockStockPermissions /> : <div>Carregando...</div>} />
              <Route path="/erp/costcenters-form" element={ErpCostCentersForm ? <ErpCostCentersForm /> : <div>Carregando...</div>} />
              <Route path="/erp/payables" element={ErpPayablesList ? <ErpPayablesList /> : <div>Carregando...</div>} />
              <Route path="/erp/fiscaldocuments-form" element={ErpFiscalDocumentsForm ? <ErpFiscalDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/erp/costcenters" element={ErpCostCentersList ? <ErpCostCentersList /> : <div>Carregando...</div>} />
              <Route path="/erp/accounts-form" element={ErpAccountsForm ? <ErpAccountsForm /> : <div>Carregando...</div>} />
              <Route path="/erp/payables-form" element={ErpPayablesForm ? <ErpPayablesForm /> : <div>Carregando...</div>} />
              <Route path="/erp/fiscaldocuments" element={ErpFiscalDocumentsList ? <ErpFiscalDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/erp/erp" element={ErpErpOverview ? <ErpErpOverview /> : <div>Carregando...</div>} />
              <Route path="/erp/receivables" element={ErpReceivablesList ? <ErpReceivablesList /> : <div>Carregando...</div>} />
              <Route path="/erp/receivables-form" element={ErpReceivablesForm ? <ErpReceivablesForm /> : <div>Carregando...</div>} />
              <Route path="/erp/accounts" element={ErpAccountsList ? <ErpAccountsList /> : <div>Carregando...</div>} />
              <Route path="/erp/erppermissions" element={ErpErpPermissions ? <ErpErpPermissions /> : <div>Carregando...</div>} />
              <Route path="/wms/inventory-form" element={WmsInventoryForm ? <WmsInventoryForm /> : <div>Carregando...</div>} />
              <Route path="/wms/warehouses-form" element={WmsWarehousesForm ? <WmsWarehousesForm /> : <div>Carregando...</div>} />
              <Route path="/wms/shipments-form" element={WmsShipmentsForm ? <WmsShipmentsForm /> : <div>Carregando...</div>} />
              <Route path="/wms/bins" element={WmsBinsList ? <WmsBinsList /> : <div>Carregando...</div>} />
              <Route path="/wms/wmspermissions" element={WmsWmsPermissions ? <WmsWmsPermissions /> : <div>Carregando...</div>} />
              <Route path="/wms/bins-form" element={WmsBinsForm ? <WmsBinsForm /> : <div>Carregando...</div>} />
              <Route path="/wms/pickingwaves-form" element={WmsPickingWavesForm ? <WmsPickingWavesForm /> : <div>Carregando...</div>} />
              <Route path="/wms/shipments" element={WmsShipmentsList ? <WmsShipmentsList /> : <div>Carregando...</div>} />
              <Route path="/wms/warehouses" element={WmsWarehousesList ? <WmsWarehousesList /> : <div>Carregando...</div>} />
              <Route path="/wms/pickingwaves" element={WmsPickingWavesList ? <WmsPickingWavesList /> : <div>Carregando...</div>} />
              <Route path="/wms/inventory" element={WmsInventoryList ? <WmsInventoryList /> : <div>Carregando...</div>} />
              <Route path="/wms/wms" element={WmsWmsOverview ? <WmsWmsOverview /> : <div>Carregando...</div>} />
              <Route path="/finance/invoices" element={FinanceInvoicesList ? <FinanceInvoicesList /> : <div>Carregando...</div>} />
              <Route path="/finance/escrows" element={FinanceEscrowsList ? <FinanceEscrowsList /> : <div>Carregando...</div>} />
              <Route path="/finance/escrows-form" element={FinanceEscrowsForm ? <FinanceEscrowsForm /> : <div>Carregando...</div>} />
              <Route path="/finance/wallets-form" element={FinanceWalletsForm ? <FinanceWalletsForm /> : <div>Carregando...</div>} />
              <Route path="/finance/ledgerentries" element={FinanceLedgerEntriesList ? <FinanceLedgerEntriesList /> : <div>Carregando...</div>} />
              <Route path="/finance/splits-form" element={FinanceSplitsForm ? <FinanceSplitsForm /> : <div>Carregando...</div>} />
              <Route path="/finance/financepermissions" element={FinanceFinancePermissions ? <FinanceFinancePermissions /> : <div>Carregando...</div>} />
              <Route path="/finance/finance" element={FinanceFinanceOverview ? <FinanceFinanceOverview /> : <div>Carregando...</div>} />
              <Route path="/finance/invoices-form" element={FinanceInvoicesForm ? <FinanceInvoicesForm /> : <div>Carregando...</div>} />
              <Route path="/finance/wallets" element={FinanceWalletsList ? <FinanceWalletsList /> : <div>Carregando...</div>} />
              <Route path="/finance/splits" element={FinanceSplitsList ? <FinanceSplitsList /> : <div>Carregando...</div>} />
              <Route path="/finance/walletledger" element={FinanceWalletLedger ? <FinanceWalletLedger /> : <div>Carregando...</div>} />
              <Route path="/finance/ledgerentries-form" element={FinanceLedgerEntriesForm ? <FinanceLedgerEntriesForm /> : <div>Carregando...</div>} />
              <Route path="/ai_core/modelruns" element={Ai_coreModelRunsList ? <Ai_coreModelRunsList /> : <div>Carregando...</div>} />
              <Route path="/ai_core/moderationdecisions" element={Ai_coreModerationDecisionsList ? <Ai_coreModerationDecisionsList /> : <div>Carregando...</div>} />
              <Route path="/ai_core/modelruns-form" element={Ai_coreModelRunsForm ? <Ai_coreModelRunsForm /> : <div>Carregando...</div>} />
              <Route path="/ai_core/ai_corepermissions" element={Ai_coreAi_corePermissions ? <Ai_coreAi_corePermissions /> : <div>Carregando...</div>} />
              <Route path="/ai_core/ai_core" element={Ai_coreAi_coreOverview ? <Ai_coreAi_coreOverview /> : <div>Carregando...</div>} />
              <Route path="/ai_core/aimemories-form" element={Ai_coreAiMemoriesForm ? <Ai_coreAiMemoriesForm /> : <div>Carregando...</div>} />
              <Route path="/ai_core/aimemories" element={Ai_coreAiMemoriesList ? <Ai_coreAiMemoriesList /> : <div>Carregando...</div>} />
              <Route path="/ai_core/moderationdecisions-form" element={Ai_coreModerationDecisionsForm ? <Ai_coreModerationDecisionsForm /> : <div>Carregando...</div>} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </Router>
  );
}

export default App;

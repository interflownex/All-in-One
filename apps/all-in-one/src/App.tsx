
import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import './index.css';
const IdentityOverview = lazy(() => import('./pages/identity/IdentityOverview'));
const AuthGateway = lazy(() => import('./pages/identity/AuthGateway'));
const KycVerification = lazy(() => import('./pages/identity/KycVerification'));
const KybBusiness = lazy(() => import('./pages/identity/KybBusiness'));
const MfaManager = lazy(() => import('./pages/identity/MfaManager'));
const ConsentLgpd = lazy(() => import('./pages/identity/ConsentLgpd'));
const SessionControl = lazy(() => import('./pages/identity/SessionControl'));
const BusinessOverview = lazy(() => import('./pages/business/BusinessOverview'));
const PermissionsOverview = lazy(() => import('./pages/permissions/PermissionsOverview'));
const FinanceOverview = lazy(() => import('./pages/finance/FinanceOverview'));
const WalletLedger = lazy(() => import('./pages/finance/WalletLedger'));
const MarketplaceOverview = lazy(() => import('./pages/marketplace/MarketplaceOverview'));
const StockOverview = lazy(() => import('./pages/stock/StockOverview'));
const DeliveryOverview = lazy(() => import('./pages/delivery/DeliveryOverview'));
const RidersOverview = lazy(() => import('./pages/riders/RidersOverview'));
const ServicesOverview = lazy(() => import('./pages/services/ServicesOverview'));
const MobilityOverview = lazy(() => import('./pages/mobility/MobilityOverview'));
const JobsOverview = lazy(() => import('./pages/jobs/JobsOverview'));
const CandidateResume = lazy(() => import('./pages/jobs/CandidateResume'));
const CtpsImport = lazy(() => import('./pages/jobs/CtpsImport'));
const VacancySearch = lazy(() => import('./pages/jobs/VacancySearch'));
const RecruiterResumeReview = lazy(() => import('./pages/jobs/RecruiterResumeReview'));
const ErpOverview = lazy(() => import('./pages/erp/ErpOverview'));
const WmsOverview = lazy(() => import('./pages/wms/WmsOverview'));
const TmsOverview = lazy(() => import('./pages/tms/TmsOverview'));
const CrmOverview = lazy(() => import('./pages/crm/CrmOverview'));
const BpmOverview = lazy(() => import('./pages/bpm/BpmOverview'));
const DocumentOverview = lazy(() => import('./pages/document/DocumentOverview'));
const HrOverview = lazy(() => import('./pages/hr/HrOverview'));
const HealthOverview = lazy(() => import('./pages/health/HealthOverview'));
const VisionOverview = lazy(() => import('./pages/vision/VisionOverview'));
const LegalOverview = lazy(() => import('./pages/legal/LegalOverview'));
const PropertyOverview = lazy(() => import('./pages/property/PropertyOverview'));
const BiOverview = lazy(() => import('./pages/bi/BiOverview'));
const Ai_coreOverview = lazy(() => import('./pages/ai_core/Ai_coreOverview'));
const Api_hubOverview = lazy(() => import('./pages/api_hub/Api_hubOverview'));

const ProcessesList = lazy(() => import('./pages/bpm/ProcessesList'));
const ProcessesForm = lazy(() => import('./pages/bpm/ProcessesForm'));
const BpmPermissions = lazy(() => import('./pages/bpm/BpmPermissions'));
const SlaPoliciesForm = lazy(() => import('./pages/bpm/SlaPoliciesForm'));
const WorkflowInstancesForm = lazy(() => import('./pages/bpm/WorkflowInstancesForm'));
const TasksForm = lazy(() => import('./pages/bpm/TasksForm'));
const TasksList = lazy(() => import('./pages/bpm/TasksList'));
const SlaPoliciesList = lazy(() => import('./pages/bpm/SlaPoliciesList'));
const WorkflowInstancesList = lazy(() => import('./pages/bpm/WorkflowInstancesList'));
const AppointmentsForm = lazy(() => import('./pages/health/AppointmentsForm'));
const PrescriptionsList = lazy(() => import('./pages/health/PrescriptionsList'));
const PatientsForm = lazy(() => import('./pages/health/PatientsForm'));
const MedicalRecordsForm = lazy(() => import('./pages/health/MedicalRecordsForm'));
const BedsForm = lazy(() => import('./pages/health/BedsForm'));
const MedicalRecordsList = lazy(() => import('./pages/health/MedicalRecordsList'));
const AppointmentsList = lazy(() => import('./pages/health/AppointmentsList'));
const HealthPermissions = lazy(() => import('./pages/health/HealthPermissions'));
const PrescriptionsForm = lazy(() => import('./pages/health/PrescriptionsForm'));
const BedsList = lazy(() => import('./pages/health/BedsList'));
const PatientsList = lazy(() => import('./pages/health/PatientsList'));
const ResumesList = lazy(() => import('./pages/jobs/ResumesList'));
const ResumeAccessLogsForm = lazy(() => import('./pages/jobs/ResumeAccessLogsForm'));
const EmploymentRecordsList = lazy(() => import('./pages/jobs/EmploymentRecordsList'));
const ResumeDocumentsForm = lazy(() => import('./pages/jobs/ResumeDocumentsForm'));
const ApplicationsForm = lazy(() => import('./pages/jobs/ApplicationsForm'));
const ResumesForm = lazy(() => import('./pages/jobs/ResumesForm'));
const JobPostingsForm = lazy(() => import('./pages/jobs/JobPostingsForm'));
const ResumeAccessLogsList = lazy(() => import('./pages/jobs/ResumeAccessLogsList'));
const JobsPermissions = lazy(() => import('./pages/jobs/JobsPermissions'));
const ApplicationsList = lazy(() => import('./pages/jobs/ApplicationsList'));
const JobPostingsList = lazy(() => import('./pages/jobs/JobPostingsList'));
const EmploymentRecordsForm = lazy(() => import('./pages/jobs/EmploymentRecordsForm'));
const ResumeDocumentsList = lazy(() => import('./pages/jobs/ResumeDocumentsList'));
const ConsentRecordsList = lazy(() => import('./pages/identity/ConsentRecordsList'));
const DocumentsForm = lazy(() => import('./pages/identity/DocumentsForm'));
const SessionsForm = lazy(() => import('./pages/identity/SessionsForm'));
const IdentityVerificationsForm = lazy(() => import('./pages/identity/IdentityVerificationsForm'));
const BiometricsList = lazy(() => import('./pages/identity/BiometricsList'));
const UsersList = lazy(() => import('./pages/identity/UsersList'));
const IdentityPermissions = lazy(() => import('./pages/identity/IdentityPermissions'));
const ConsentRecordsForm = lazy(() => import('./pages/identity/ConsentRecordsForm'));
const BiometricsForm = lazy(() => import('./pages/identity/BiometricsForm'));
const SessionsList = lazy(() => import('./pages/identity/SessionsList'));
const UsersForm = lazy(() => import('./pages/identity/UsersForm'));
const DocumentsList = lazy(() => import('./pages/identity/DocumentsList'));
const IdentityVerificationsList = lazy(() => import('./pages/identity/IdentityVerificationsList'));
const FareRulesForm = lazy(() => import('./pages/mobility/FareRulesForm'));
const RoutesForm = lazy(() => import('./pages/mobility/RoutesForm'));
const FareRulesList = lazy(() => import('./pages/mobility/FareRulesList'));
const TicketsList = lazy(() => import('./pages/mobility/TicketsList'));
const RidesList = lazy(() => import('./pages/mobility/RidesList'));
const RoutesList = lazy(() => import('./pages/mobility/RoutesList'));
const StopsForm = lazy(() => import('./pages/mobility/StopsForm'));
const MobilityPermissions = lazy(() => import('./pages/mobility/MobilityPermissions'));
const RidesForm = lazy(() => import('./pages/mobility/RidesForm'));
const StopsList = lazy(() => import('./pages/mobility/StopsList'));
const TicketsForm = lazy(() => import('./pages/mobility/TicketsForm'));
const ActivitiesForm = lazy(() => import('./pages/crm/ActivitiesForm'));
const OpportunitiesList = lazy(() => import('./pages/crm/OpportunitiesList'));
const LeadsForm = lazy(() => import('./pages/crm/LeadsForm'));
const LeadsList = lazy(() => import('./pages/crm/LeadsList'));
const CampaignsList = lazy(() => import('./pages/crm/CampaignsList'));
const OpportunitiesForm = lazy(() => import('./pages/crm/OpportunitiesForm'));
const CampaignsForm = lazy(() => import('./pages/crm/CampaignsForm'));
const CrmPermissions = lazy(() => import('./pages/crm/CrmPermissions'));
const ActivitiesList = lazy(() => import('./pages/crm/ActivitiesList'));
const DatasetsList = lazy(() => import('./pages/bi/DatasetsList'));
const BiPermissions = lazy(() => import('./pages/bi/BiPermissions'));
const DashboardsList = lazy(() => import('./pages/bi/DashboardsList'));
const ExportsForm = lazy(() => import('./pages/bi/ExportsForm'));
const DashboardsForm = lazy(() => import('./pages/bi/DashboardsForm'));
const IndicatorsForm = lazy(() => import('./pages/bi/IndicatorsForm'));
const IndicatorsList = lazy(() => import('./pages/bi/IndicatorsList'));
const ExportsList = lazy(() => import('./pages/bi/ExportsList'));
const DatasetsForm = lazy(() => import('./pages/bi/DatasetsForm'));
const ProductsForm = lazy(() => import('./pages/marketplace/ProductsForm'));
const PepitaGrantsForm = lazy(() => import('./pages/marketplace/PepitaGrantsForm'));
const StoresList = lazy(() => import('./pages/marketplace/StoresList'));
const DisputesList = lazy(() => import('./pages/marketplace/DisputesList'));
const OrdersForm = lazy(() => import('./pages/marketplace/OrdersForm'));
const DisputesForm = lazy(() => import('./pages/marketplace/DisputesForm'));
const MarketplacePermissions = lazy(() => import('./pages/marketplace/MarketplacePermissions'));
const ProductsList = lazy(() => import('./pages/marketplace/ProductsList'));
const CartsForm = lazy(() => import('./pages/marketplace/CartsForm'));
const CartsList = lazy(() => import('./pages/marketplace/CartsList'));
const OrdersList = lazy(() => import('./pages/marketplace/OrdersList'));
const ReviewsList = lazy(() => import('./pages/marketplace/ReviewsList'));
const StoresForm = lazy(() => import('./pages/marketplace/StoresForm'));
const ReviewsForm = lazy(() => import('./pages/marketplace/ReviewsForm'));
const PepitaGrantsList = lazy(() => import('./pages/marketplace/PepitaGrantsList'));
const UserCompanyMembershipsList = lazy(() => import('./pages/business/UserCompanyMembershipsList'));
const CompanyDocumentsList = lazy(() => import('./pages/business/CompanyDocumentsList'));
const UserCompanyMembershipsForm = lazy(() => import('./pages/business/UserCompanyMembershipsForm'));
const CatalogOffersList = lazy(() => import('./pages/business/CatalogOffersList'));
const CompaniesList = lazy(() => import('./pages/business/CompaniesList'));
const BranchesForm = lazy(() => import('./pages/business/BranchesForm'));
const BusinessPermissions = lazy(() => import('./pages/business/BusinessPermissions'));
const CompaniesForm = lazy(() => import('./pages/business/CompaniesForm'));
const BranchesList = lazy(() => import('./pages/business/BranchesList'));
const CompanyDocumentsForm = lazy(() => import('./pages/business/CompanyDocumentsForm'));
const CatalogOffersForm = lazy(() => import('./pages/business/CatalogOffersForm'));
const VehiclesForm = lazy(() => import('./pages/riders/VehiclesForm'));
const RiderProfilesList = lazy(() => import('./pages/riders/RiderProfilesList'));
const RiderDocumentsForm = lazy(() => import('./pages/riders/RiderDocumentsForm'));
const RiderDocumentsList = lazy(() => import('./pages/riders/RiderDocumentsList'));
const RidersPermissions = lazy(() => import('./pages/riders/RidersPermissions'));
const RiderReviewsForm = lazy(() => import('./pages/riders/RiderReviewsForm'));
const VehiclesList = lazy(() => import('./pages/riders/VehiclesList'));
const RiderProfilesForm = lazy(() => import('./pages/riders/RiderProfilesForm'));
const RiderReviewsList = lazy(() => import('./pages/riders/RiderReviewsList'));
const StreamsForm = lazy(() => import('./pages/vision/StreamsForm'));
const RecordingsList = lazy(() => import('./pages/vision/RecordingsList'));
const MotionAlertsForm = lazy(() => import('./pages/vision/MotionAlertsForm'));
const DevicesForm = lazy(() => import('./pages/vision/DevicesForm'));
const VisionPermissions = lazy(() => import('./pages/vision/VisionPermissions'));
const StreamsList = lazy(() => import('./pages/vision/StreamsList'));
const DevicesList = lazy(() => import('./pages/vision/DevicesList'));
const MotionAlertsList = lazy(() => import('./pages/vision/MotionAlertsList'));
const RecordingsForm = lazy(() => import('./pages/vision/RecordingsForm'));
const UserRolesList = lazy(() => import('./pages/permissions/UserRolesList'));
const RolesList = lazy(() => import('./pages/permissions/RolesList'));
const ApprovalLimitsList = lazy(() => import('./pages/permissions/ApprovalLimitsList'));
const PermissionsList = lazy(() => import('./pages/permissions/PermissionsList'));
const UserRolesForm = lazy(() => import('./pages/permissions/UserRolesForm'));
const PermissionsPermissions = lazy(() => import('./pages/permissions/PermissionsPermissions'));
const PermissionsForm = lazy(() => import('./pages/permissions/PermissionsForm'));
const ApprovalLimitsForm = lazy(() => import('./pages/permissions/ApprovalLimitsForm'));
const AccessPoliciesList = lazy(() => import('./pages/permissions/AccessPoliciesList'));
const RolesForm = lazy(() => import('./pages/permissions/RolesForm'));
const AccessPoliciesForm = lazy(() => import('./pages/permissions/AccessPoliciesForm'));
const ApiClientsForm = lazy(() => import('./pages/api_hub/ApiClientsForm'));
const Api_hubPermissions = lazy(() => import('./pages/api_hub/Api_hubPermissions'));
const ApiKeysForm = lazy(() => import('./pages/api_hub/ApiKeysForm'));
const ApiClientsList = lazy(() => import('./pages/api_hub/ApiClientsList'));
const ApiKeysList = lazy(() => import('./pages/api_hub/ApiKeysList'));
const IntegrationRunsForm = lazy(() => import('./pages/api_hub/IntegrationRunsForm'));
const WebhooksList = lazy(() => import('./pages/api_hub/WebhooksList'));
const WebhooksForm = lazy(() => import('./pages/api_hub/WebhooksForm'));
const IntegrationRunsList = lazy(() => import('./pages/api_hub/IntegrationRunsList'));
const LegalPermissions = lazy(() => import('./pages/legal/LegalPermissions'));
const HearingsForm = lazy(() => import('./pages/legal/HearingsForm'));
const DeadlinesForm = lazy(() => import('./pages/legal/DeadlinesForm'));
const LegalContractsList = lazy(() => import('./pages/legal/LegalContractsList'));
const DeadlinesList = lazy(() => import('./pages/legal/DeadlinesList'));
const CasesList = lazy(() => import('./pages/legal/CasesList'));
const LegalContractsForm = lazy(() => import('./pages/legal/LegalContractsForm'));
const HearingsList = lazy(() => import('./pages/legal/HearingsList'));
const CasesForm = lazy(() => import('./pages/legal/CasesForm'));
const FreightsList = lazy(() => import('./pages/tms/FreightsList'));
const RoutesForm = lazy(() => import('./pages/tms/RoutesForm'));
const TmsPermissions = lazy(() => import('./pages/tms/TmsPermissions'));
const FreightAuditsList = lazy(() => import('./pages/tms/FreightAuditsList'));
const ProofsOfDeliveryList = lazy(() => import('./pages/tms/ProofsOfDeliveryList'));
const RoutesList = lazy(() => import('./pages/tms/RoutesList'));
const FreightsForm = lazy(() => import('./pages/tms/FreightsForm'));
const ProofsOfDeliveryForm = lazy(() => import('./pages/tms/ProofsOfDeliveryForm'));
const CarriersList = lazy(() => import('./pages/tms/CarriersList'));
const CarriersForm = lazy(() => import('./pages/tms/CarriersForm'));
const FreightAuditsForm = lazy(() => import('./pages/tms/FreightAuditsForm'));
const FoldersList = lazy(() => import('./pages/document/FoldersList'));
const VersionsForm = lazy(() => import('./pages/document/VersionsForm'));
const DocumentsForm = lazy(() => import('./pages/document/DocumentsForm'));
const DocumentPermissions = lazy(() => import('./pages/document/DocumentPermissions'));
const RetentionPoliciesForm = lazy(() => import('./pages/document/RetentionPoliciesForm'));
const FoldersForm = lazy(() => import('./pages/document/FoldersForm'));
const RetentionPoliciesList = lazy(() => import('./pages/document/RetentionPoliciesList'));
const VersionsList = lazy(() => import('./pages/document/VersionsList'));
const DocumentsList = lazy(() => import('./pages/document/DocumentsList'));
const ProvidersList = lazy(() => import('./pages/services/ProvidersList'));
const ServicesPermissions = lazy(() => import('./pages/services/ServicesPermissions'));
const ProvidersForm = lazy(() => import('./pages/services/ProvidersForm'));
const VisitsForm = lazy(() => import('./pages/services/VisitsForm'));
const EvidenceForm = lazy(() => import('./pages/services/EvidenceForm'));
const ServiceContractsForm = lazy(() => import('./pages/services/ServiceContractsForm'));
const QuotesList = lazy(() => import('./pages/services/QuotesList'));
const ServiceContractsList = lazy(() => import('./pages/services/ServiceContractsList'));
const VisitsList = lazy(() => import('./pages/services/VisitsList'));
const EvidenceList = lazy(() => import('./pages/services/EvidenceList'));
const QuotesForm = lazy(() => import('./pages/services/QuotesForm'));
const CandidatesForm = lazy(() => import('./pages/hr/CandidatesForm'));
const CoursesList = lazy(() => import('./pages/hr/CoursesList'));
const HrPermissions = lazy(() => import('./pages/hr/HrPermissions'));
const OccupationalRecordsList = lazy(() => import('./pages/hr/OccupationalRecordsList'));
const EmployeesList = lazy(() => import('./pages/hr/EmployeesList'));
const PayrollRunsList = lazy(() => import('./pages/hr/PayrollRunsList'));
const PayrollRunsForm = lazy(() => import('./pages/hr/PayrollRunsForm'));
const CandidatesList = lazy(() => import('./pages/hr/CandidatesList'));
const OccupationalRecordsForm = lazy(() => import('./pages/hr/OccupationalRecordsForm'));
const EmployeesForm = lazy(() => import('./pages/hr/EmployeesForm'));
const CoursesForm = lazy(() => import('./pages/hr/CoursesForm'));
const InsuranceOptionsList = lazy(() => import('./pages/delivery/InsuranceOptionsList'));
const ProofsForm = lazy(() => import('./pages/delivery/ProofsForm'));
const DeliveryRequestsList = lazy(() => import('./pages/delivery/DeliveryRequestsList'));
const AssignmentsList = lazy(() => import('./pages/delivery/AssignmentsList'));
const ProofsList = lazy(() => import('./pages/delivery/ProofsList'));
const QuotesList = lazy(() => import('./pages/delivery/QuotesList'));
const InsuranceOptionsForm = lazy(() => import('./pages/delivery/InsuranceOptionsForm'));
const DeliveryPermissions = lazy(() => import('./pages/delivery/DeliveryPermissions'));
const DeliveryRequestsForm = lazy(() => import('./pages/delivery/DeliveryRequestsForm'));
const QuotesForm = lazy(() => import('./pages/delivery/QuotesForm'));
const AssignmentsForm = lazy(() => import('./pages/delivery/AssignmentsForm'));
const AssembliesList = lazy(() => import('./pages/property/AssembliesList'));
const PropertiesList = lazy(() => import('./pages/property/PropertiesList'));
const LeasesForm = lazy(() => import('./pages/property/LeasesForm'));
const UnitsForm = lazy(() => import('./pages/property/UnitsForm'));
const MaintenanceOrdersList = lazy(() => import('./pages/property/MaintenanceOrdersList'));
const UnitsList = lazy(() => import('./pages/property/UnitsList'));
const PropertyPermissions = lazy(() => import('./pages/property/PropertyPermissions'));
const LeasesList = lazy(() => import('./pages/property/LeasesList'));
const AssembliesForm = lazy(() => import('./pages/property/AssembliesForm'));
const MaintenanceOrdersForm = lazy(() => import('./pages/property/MaintenanceOrdersForm'));
const PropertiesForm = lazy(() => import('./pages/property/PropertiesForm'));
const PriceRulesList = lazy(() => import('./pages/stock/PriceRulesList'));
const CatalogProductsForm = lazy(() => import('./pages/stock/CatalogProductsForm'));
const PriceRulesForm = lazy(() => import('./pages/stock/PriceRulesForm'));
const SuppliersForm = lazy(() => import('./pages/stock/SuppliersForm'));
const SupplierOrdersForm = lazy(() => import('./pages/stock/SupplierOrdersForm'));
const DiscountQuotesForm = lazy(() => import('./pages/stock/DiscountQuotesForm'));
const DiscountQuotesList = lazy(() => import('./pages/stock/DiscountQuotesList'));
const SupplierOrdersList = lazy(() => import('./pages/stock/SupplierOrdersList'));
const CatalogProductsList = lazy(() => import('./pages/stock/CatalogProductsList'));
const SuppliersList = lazy(() => import('./pages/stock/SuppliersList'));
const StockPermissions = lazy(() => import('./pages/stock/StockPermissions'));
const CostCentersForm = lazy(() => import('./pages/erp/CostCentersForm'));
const PayablesList = lazy(() => import('./pages/erp/PayablesList'));
const FiscalDocumentsForm = lazy(() => import('./pages/erp/FiscalDocumentsForm'));
const CostCentersList = lazy(() => import('./pages/erp/CostCentersList'));
const AccountsForm = lazy(() => import('./pages/erp/AccountsForm'));
const PayablesForm = lazy(() => import('./pages/erp/PayablesForm'));
const FiscalDocumentsList = lazy(() => import('./pages/erp/FiscalDocumentsList'));
const ReceivablesList = lazy(() => import('./pages/erp/ReceivablesList'));
const ReceivablesForm = lazy(() => import('./pages/erp/ReceivablesForm'));
const AccountsList = lazy(() => import('./pages/erp/AccountsList'));
const ErpPermissions = lazy(() => import('./pages/erp/ErpPermissions'));
const InventoryForm = lazy(() => import('./pages/wms/InventoryForm'));
const WarehousesForm = lazy(() => import('./pages/wms/WarehousesForm'));
const ShipmentsForm = lazy(() => import('./pages/wms/ShipmentsForm'));
const BinsList = lazy(() => import('./pages/wms/BinsList'));
const WmsPermissions = lazy(() => import('./pages/wms/WmsPermissions'));
const BinsForm = lazy(() => import('./pages/wms/BinsForm'));
const PickingWavesForm = lazy(() => import('./pages/wms/PickingWavesForm'));
const ShipmentsList = lazy(() => import('./pages/wms/ShipmentsList'));
const WarehousesList = lazy(() => import('./pages/wms/WarehousesList'));
const PickingWavesList = lazy(() => import('./pages/wms/PickingWavesList'));
const InventoryList = lazy(() => import('./pages/wms/InventoryList'));
const InvoicesList = lazy(() => import('./pages/finance/InvoicesList'));
const EscrowsList = lazy(() => import('./pages/finance/EscrowsList'));
const EscrowsForm = lazy(() => import('./pages/finance/EscrowsForm'));
const WalletsForm = lazy(() => import('./pages/finance/WalletsForm'));
const LedgerEntriesList = lazy(() => import('./pages/finance/LedgerEntriesList'));
const SplitsForm = lazy(() => import('./pages/finance/SplitsForm'));
const FinancePermissions = lazy(() => import('./pages/finance/FinancePermissions'));
const InvoicesForm = lazy(() => import('./pages/finance/InvoicesForm'));
const WalletsList = lazy(() => import('./pages/finance/WalletsList'));
const SplitsList = lazy(() => import('./pages/finance/SplitsList'));
const LedgerEntriesForm = lazy(() => import('./pages/finance/LedgerEntriesForm'));
const ModelRunsList = lazy(() => import('./pages/ai_core/ModelRunsList'));
const ModerationDecisionsList = lazy(() => import('./pages/ai_core/ModerationDecisionsList'));
const ModelRunsForm = lazy(() => import('./pages/ai_core/ModelRunsForm'));
const Ai_corePermissions = lazy(() => import('./pages/ai_core/Ai_corePermissions'));
const AiMemoriesForm = lazy(() => import('./pages/ai_core/AiMemoriesForm'));
const AiMemoriesList = lazy(() => import('./pages/ai_core/AiMemoriesList'));
const ModerationDecisionsForm = lazy(() => import('./pages/ai_core/ModerationDecisionsForm'));

const FeaturedItems = () => {
  const items = [
    {
      id: '1',
      title: 'Hambúrguer Gourmet Valley',
      desc: 'Blend de 180g de carne premium, queijo canastra derretido, cebola caramelizada e pão artesanal.',
      price: 'R$ 45,90',
      image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80',
      video: 'https://www.w3schools.com/html/mov_bbb.mp4'
    },
    {
      id: '2',
      title: 'Monitor Gamer UltraSharp 4K',
      desc: 'Monitor de 32 polegadas, 144Hz, HDR1000 e tempo de resposta de 1ms. O auge da imersão.',
      price: 'R$ 3.499,00',
      image: 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80',
      video: 'https://www.w3schools.com/html/movie.mp4'
    },
    {
      id: '3',
      title: 'Consultoria de IA Estratégica',
      desc: 'Implementação de agentes inteligentes e automação de processos via LLMs de última geração.',
      price: 'Sob consulta',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80',
      video: 'https://www.w3schools.com/html/mov_bbb.mp4'
    }
  ];

  return (
    <div className="container">
      <section className="hero">
        <h1>Bem-vindo ao All-in-One</h1>
        <p>Selecione um módulo no menu lateral ou confira nossos itens em destaque abaixo.</p>
      </section>

      <div className="featured-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginTop: '40px' }}>
        {items.map(item => (
          <div key={item.id} className="offer-card neo-brutalism" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="media-container" style={{ position: 'relative', height: '200px', overflow: 'hidden', borderRadius: '4px', marginBottom: '12px', border: '2px solid #17211c' }}>
              <img src={item.image} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              <video 
                src={item.video} 
                muted 
                loop 
                onMouseOver={(e) => e.currentTarget.play()} 
                onMouseOut={(e) => { e.currentTarget.pause(); e.currentTarget.currentTime = 0; }}
                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0, transition: 'opacity 0.3s' }}
                onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
                onMouseLeave={(e) => e.currentTarget.style.opacity = '0'}
              />
              <div style={{ position: 'absolute', bottom: '8px', right: '8px', background: 'rgba(0,0,0,0.6)', color: '#fff', padding: '2px 6px', fontSize: '10px', borderRadius: '4px' }}>Passe o mouse para ver vídeo</div>
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '800', marginBottom: '8px' }}>{item.title}</h3>
            <p style={{ fontSize: '0.875rem', color: '#536159', flex: 1, marginBottom: '16px' }}>{item.desc}</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '1.125rem', fontWeight: '900', color: '#126b45' }}>{item.price}</span>
              <button className="btn-primary" style={{ padding: '8px 16px', fontSize: '0.875rem' }}>Ver Detalhes</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Navigation />
        <main className="content-area">
          <Suspense fallback={<div className="loader">Carregando...</div>}>
            <Routes>
              <Route path="/" element={<FeaturedItems />} />
                            <Route path="/identity" element={IdentityOverview ? <IdentityOverview /> : <div>Carregando...</div>} />
              <Route path="/identity/auth-gateway" element={AuthGateway ? <AuthGateway /> : <div>Carregando...</div>} />
              <Route path="/identity/kyc-verification" element={KycVerification ? <KycVerification /> : <div>Carregando...</div>} />
              <Route path="/identity/kyb-business" element={KybBusiness ? <KybBusiness /> : <div>Carregando...</div>} />
              <Route path="/identity/mfa-manager" element={MfaManager ? <MfaManager /> : <div>Carregando...</div>} />
              <Route path="/identity/consent-lgpd" element={ConsentLgpd ? <ConsentLgpd /> : <div>Carregando...</div>} />
              <Route path="/identity/session-control" element={SessionControl ? <SessionControl /> : <div>Carregando...</div>} />
              <Route path="/business" element={BusinessOverview ? <BusinessOverview /> : <div>Carregando...</div>} />
              <Route path="/permissions" element={PermissionsOverview ? <PermissionsOverview /> : <div>Carregando...</div>} />
              <Route path="/finance" element={FinanceOverview ? <FinanceOverview /> : <div>Carregando...</div>} />
              <Route path="/finance/wallet-ledger" element={WalletLedger ? <WalletLedger /> : <div>Carregando...</div>} />
              <Route path="/marketplace" element={MarketplaceOverview ? <MarketplaceOverview /> : <div>Carregando...</div>} />
              <Route path="/stock" element={StockOverview ? <StockOverview /> : <div>Carregando...</div>} />
              <Route path="/delivery" element={DeliveryOverview ? <DeliveryOverview /> : <div>Carregando...</div>} />
              <Route path="/riders" element={RidersOverview ? <RidersOverview /> : <div>Carregando...</div>} />
              <Route path="/services" element={ServicesOverview ? <ServicesOverview /> : <div>Carregando...</div>} />
              <Route path="/mobility" element={MobilityOverview ? <MobilityOverview /> : <div>Carregando...</div>} />
              <Route path="/jobs" element={JobsOverview ? <JobsOverview /> : <div>Carregando...</div>} />
              <Route path="/jobs/candidate-resume" element={CandidateResume ? <CandidateResume /> : <div>Carregando...</div>} />
              <Route path="/jobs/ctps-import" element={CtpsImport ? <CtpsImport /> : <div>Carregando...</div>} />
              <Route path="/jobs/vacancy-search" element={VacancySearch ? <VacancySearch /> : <div>Carregando...</div>} />
              <Route path="/jobs/recruiter-resume-review" element={RecruiterResumeReview ? <RecruiterResumeReview /> : <div>Carregando...</div>} />
              <Route path="/erp" element={ErpOverview ? <ErpOverview /> : <div>Carregando...</div>} />
              <Route path="/wms" element={WmsOverview ? <WmsOverview /> : <div>Carregando...</div>} />
              <Route path="/tms" element={TmsOverview ? <TmsOverview /> : <div>Carregando...</div>} />
              <Route path="/crm" element={CrmOverview ? <CrmOverview /> : <div>Carregando...</div>} />
              <Route path="/bpm" element={BpmOverview ? <BpmOverview /> : <div>Carregando...</div>} />
              <Route path="/document" element={DocumentOverview ? <DocumentOverview /> : <div>Carregando...</div>} />
              <Route path="/hr" element={HrOverview ? <HrOverview /> : <div>Carregando...</div>} />
              <Route path="/health" element={HealthOverview ? <HealthOverview /> : <div>Carregando...</div>} />
              <Route path="/vision" element={VisionOverview ? <VisionOverview /> : <div>Carregando...</div>} />
              <Route path="/legal" element={LegalOverview ? <LegalOverview /> : <div>Carregando...</div>} />
              <Route path="/property" element={PropertyOverview ? <PropertyOverview /> : <div>Carregando...</div>} />
              <Route path="/bi" element={BiOverview ? <BiOverview /> : <div>Carregando...</div>} />
              <Route path="/ai_core" element={Ai_coreOverview ? <Ai_coreOverview /> : <div>Carregando...</div>} />
              <Route path="/api_hub" element={Api_hubOverview ? <Api_hubOverview /> : <div>Carregando...</div>} />
                          <Route path="/bpm/processes" element={ProcessesList ? <ProcessesList /> : <div>Carregando...</div>} />
              <Route path="/bpm/processes-form" element={ProcessesForm ? <ProcessesForm /> : <div>Carregando...</div>} />
              <Route path="/bpm/bpmpermissions" element={BpmPermissions ? <BpmPermissions /> : <div>Carregando...</div>} />
              <Route path="/bpm/slapolicies-form" element={SlaPoliciesForm ? <SlaPoliciesForm /> : <div>Carregando...</div>} />
              <Route path="/bpm/bpm" element={BpmOverview ? <BpmOverview /> : <div>Carregando...</div>} />
              <Route path="/bpm/workflowinstances-form" element={WorkflowInstancesForm ? <WorkflowInstancesForm /> : <div>Carregando...</div>} />
              <Route path="/bpm/tasks-form" element={TasksForm ? <TasksForm /> : <div>Carregando...</div>} />
              <Route path="/bpm/tasks" element={TasksList ? <TasksList /> : <div>Carregando...</div>} />
              <Route path="/bpm/slapolicies" element={SlaPoliciesList ? <SlaPoliciesList /> : <div>Carregando...</div>} />
              <Route path="/bpm/workflowinstances" element={WorkflowInstancesList ? <WorkflowInstancesList /> : <div>Carregando...</div>} />
              <Route path="/health/appointments-form" element={AppointmentsForm ? <AppointmentsForm /> : <div>Carregando...</div>} />
              <Route path="/health/prescriptions" element={PrescriptionsList ? <PrescriptionsList /> : <div>Carregando...</div>} />
              <Route path="/health/patients-form" element={PatientsForm ? <PatientsForm /> : <div>Carregando...</div>} />
              <Route path="/health/medicalrecords-form" element={MedicalRecordsForm ? <MedicalRecordsForm /> : <div>Carregando...</div>} />
              <Route path="/health/beds-form" element={BedsForm ? <BedsForm /> : <div>Carregando...</div>} />
              <Route path="/health/medicalrecords" element={MedicalRecordsList ? <MedicalRecordsList /> : <div>Carregando...</div>} />
              <Route path="/health/appointments" element={AppointmentsList ? <AppointmentsList /> : <div>Carregando...</div>} />
              <Route path="/health/healthpermissions" element={HealthPermissions ? <HealthPermissions /> : <div>Carregando...</div>} />
              <Route path="/health/prescriptions-form" element={PrescriptionsForm ? <PrescriptionsForm /> : <div>Carregando...</div>} />
              <Route path="/health/health" element={HealthOverview ? <HealthOverview /> : <div>Carregando...</div>} />
              <Route path="/health/beds" element={BedsList ? <BedsList /> : <div>Carregando...</div>} />
              <Route path="/health/patients" element={PatientsList ? <PatientsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumes" element={ResumesList ? <ResumesList /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumeaccesslogs-form" element={ResumeAccessLogsForm ? <ResumeAccessLogsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/employmentrecords" element={EmploymentRecordsList ? <EmploymentRecordsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumedocuments-form" element={ResumeDocumentsForm ? <ResumeDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/ctpsimport" element={CtpsImport ? <CtpsImport /> : <div>Carregando...</div>} />
              <Route path="/jobs/candidateresume" element={CandidateResume ? <CandidateResume /> : <div>Carregando...</div>} />
              <Route path="/jobs/applications-form" element={ApplicationsForm ? <ApplicationsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/recruiterresumereview" element={RecruiterResumeReview ? <RecruiterResumeReview /> : <div>Carregando...</div>} />
              <Route path="/jobs/vacancysearch" element={VacancySearch ? <VacancySearch /> : <div>Carregando...</div>} />
              <Route path="/jobs/jobs" element={JobsOverview ? <JobsOverview /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumes-form" element={ResumesForm ? <ResumesForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/jobpostings-form" element={JobPostingsForm ? <JobPostingsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumeaccesslogs" element={ResumeAccessLogsList ? <ResumeAccessLogsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/jobspermissions" element={JobsPermissions ? <JobsPermissions /> : <div>Carregando...</div>} />
              <Route path="/jobs/applications" element={ApplicationsList ? <ApplicationsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/jobpostings" element={JobPostingsList ? <JobPostingsList /> : <div>Carregando...</div>} />
              <Route path="/jobs/employmentrecords-form" element={EmploymentRecordsForm ? <EmploymentRecordsForm /> : <div>Carregando...</div>} />
              <Route path="/jobs/resumedocuments" element={ResumeDocumentsList ? <ResumeDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/identity/sessioncontrol" element={SessionControl ? <SessionControl /> : <div>Carregando...</div>} />
              <Route path="/identity/kycverification" element={KycVerification ? <KycVerification /> : <div>Carregando...</div>} />
              <Route path="/identity/consentrecords" element={ConsentRecordsList ? <ConsentRecordsList /> : <div>Carregando...</div>} />
              <Route path="/identity/documents-form" element={DocumentsForm ? <DocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/consentlgpd" element={ConsentLgpd ? <ConsentLgpd /> : <div>Carregando...</div>} />
              <Route path="/identity/sessions-form" element={SessionsForm ? <SessionsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/identityverifications-form" element={IdentityVerificationsForm ? <IdentityVerificationsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/biometrics" element={BiometricsList ? <BiometricsList /> : <div>Carregando...</div>} />
              <Route path="/identity/users" element={UsersList ? <UsersList /> : <div>Carregando...</div>} />
              <Route path="/identity/identitypermissions" element={IdentityPermissions ? <IdentityPermissions /> : <div>Carregando...</div>} />
              <Route path="/identity/identity" element={IdentityOverview ? <IdentityOverview /> : <div>Carregando...</div>} />
              <Route path="/identity/consentrecords-form" element={ConsentRecordsForm ? <ConsentRecordsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/kybbusiness" element={KybBusiness ? <KybBusiness /> : <div>Carregando...</div>} />
              <Route path="/identity/authgateway" element={AuthGateway ? <AuthGateway /> : <div>Carregando...</div>} />
              <Route path="/identity/biometrics-form" element={BiometricsForm ? <BiometricsForm /> : <div>Carregando...</div>} />
              <Route path="/identity/mfamanager" element={MfaManager ? <MfaManager /> : <div>Carregando...</div>} />
              <Route path="/identity/sessions" element={SessionsList ? <SessionsList /> : <div>Carregando...</div>} />
              <Route path="/identity/users-form" element={UsersForm ? <UsersForm /> : <div>Carregando...</div>} />
              <Route path="/identity/documents" element={DocumentsList ? <DocumentsList /> : <div>Carregando...</div>} />
              <Route path="/identity/identityverifications" element={IdentityVerificationsList ? <IdentityVerificationsList /> : <div>Carregando...</div>} />
              <Route path="/mobility/farerules-form" element={FareRulesForm ? <FareRulesForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/routes-form" element={RoutesForm ? <RoutesForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/farerules" element={FareRulesList ? <FareRulesList /> : <div>Carregando...</div>} />
              <Route path="/mobility/tickets" element={TicketsList ? <TicketsList /> : <div>Carregando...</div>} />
              <Route path="/mobility/rides" element={RidesList ? <RidesList /> : <div>Carregando...</div>} />
              <Route path="/mobility/routes" element={RoutesList ? <RoutesList /> : <div>Carregando...</div>} />
              <Route path="/mobility/stops-form" element={StopsForm ? <StopsForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/mobilitypermissions" element={MobilityPermissions ? <MobilityPermissions /> : <div>Carregando...</div>} />
              <Route path="/mobility/rides-form" element={RidesForm ? <RidesForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/stops" element={StopsList ? <StopsList /> : <div>Carregando...</div>} />
              <Route path="/mobility/tickets-form" element={TicketsForm ? <TicketsForm /> : <div>Carregando...</div>} />
              <Route path="/mobility/mobility" element={MobilityOverview ? <MobilityOverview /> : <div>Carregando...</div>} />
              <Route path="/crm/activities-form" element={ActivitiesForm ? <ActivitiesForm /> : <div>Carregando...</div>} />
              <Route path="/crm/opportunities" element={OpportunitiesList ? <OpportunitiesList /> : <div>Carregando...</div>} />
              <Route path="/crm/leads-form" element={LeadsForm ? <LeadsForm /> : <div>Carregando...</div>} />
              <Route path="/crm/leads" element={LeadsList ? <LeadsList /> : <div>Carregando...</div>} />
              <Route path="/crm/campaigns" element={CampaignsList ? <CampaignsList /> : <div>Carregando...</div>} />
              <Route path="/crm/opportunities-form" element={OpportunitiesForm ? <OpportunitiesForm /> : <div>Carregando...</div>} />
              <Route path="/crm/crm" element={CrmOverview ? <CrmOverview /> : <div>Carregando...</div>} />
              <Route path="/crm/campaigns-form" element={CampaignsForm ? <CampaignsForm /> : <div>Carregando...</div>} />
              <Route path="/crm/crmpermissions" element={CrmPermissions ? <CrmPermissions /> : <div>Carregando...</div>} />
              <Route path="/crm/activities" element={ActivitiesList ? <ActivitiesList /> : <div>Carregando...</div>} />
              <Route path="/bi/datasets" element={DatasetsList ? <DatasetsList /> : <div>Carregando...</div>} />
              <Route path="/bi/bipermissions" element={BiPermissions ? <BiPermissions /> : <div>Carregando...</div>} />
              <Route path="/bi/bi" element={BiOverview ? <BiOverview /> : <div>Carregando...</div>} />
              <Route path="/bi/dashboards" element={DashboardsList ? <DashboardsList /> : <div>Carregando...</div>} />
              <Route path="/bi/exports-form" element={ExportsForm ? <ExportsForm /> : <div>Carregando...</div>} />
              <Route path="/bi/dashboards-form" element={DashboardsForm ? <DashboardsForm /> : <div>Carregando...</div>} />
              <Route path="/bi/indicators-form" element={IndicatorsForm ? <IndicatorsForm /> : <div>Carregando...</div>} />
              <Route path="/bi/indicators" element={IndicatorsList ? <IndicatorsList /> : <div>Carregando...</div>} />
              <Route path="/bi/exports" element={ExportsList ? <ExportsList /> : <div>Carregando...</div>} />
              <Route path="/bi/datasets-form" element={DatasetsForm ? <DatasetsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/products-form" element={ProductsForm ? <ProductsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/pepitagrants-form" element={PepitaGrantsForm ? <PepitaGrantsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/marketplace" element={MarketplaceOverview ? <MarketplaceOverview /> : <div>Carregando...</div>} />
              <Route path="/marketplace/stores" element={StoresList ? <StoresList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/disputes" element={DisputesList ? <DisputesList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/orders-form" element={OrdersForm ? <OrdersForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/disputes-form" element={DisputesForm ? <DisputesForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/marketplacepermissions" element={MarketplacePermissions ? <MarketplacePermissions /> : <div>Carregando...</div>} />
              <Route path="/marketplace/products" element={ProductsList ? <ProductsList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/carts-form" element={CartsForm ? <CartsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/carts" element={CartsList ? <CartsList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/orders" element={OrdersList ? <OrdersList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/reviews" element={ReviewsList ? <ReviewsList /> : <div>Carregando...</div>} />
              <Route path="/marketplace/stores-form" element={StoresForm ? <StoresForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/reviews-form" element={ReviewsForm ? <ReviewsForm /> : <div>Carregando...</div>} />
              <Route path="/marketplace/pepitagrants" element={PepitaGrantsList ? <PepitaGrantsList /> : <div>Carregando...</div>} />
              <Route path="/business/usercompanymemberships" element={UserCompanyMembershipsList ? <UserCompanyMembershipsList /> : <div>Carregando...</div>} />
              <Route path="/business/companydocuments" element={CompanyDocumentsList ? <CompanyDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/business/usercompanymemberships-form" element={UserCompanyMembershipsForm ? <UserCompanyMembershipsForm /> : <div>Carregando...</div>} />
              <Route path="/business/catalogoffers" element={CatalogOffersList ? <CatalogOffersList /> : <div>Carregando...</div>} />
              <Route path="/business/companies" element={CompaniesList ? <CompaniesList /> : <div>Carregando...</div>} />
              <Route path="/business/branches-form" element={BranchesForm ? <BranchesForm /> : <div>Carregando...</div>} />
              <Route path="/business/businesspermissions" element={BusinessPermissions ? <BusinessPermissions /> : <div>Carregando...</div>} />
              <Route path="/business/companies-form" element={CompaniesForm ? <CompaniesForm /> : <div>Carregando...</div>} />
              <Route path="/business/branches" element={BranchesList ? <BranchesList /> : <div>Carregando...</div>} />
              <Route path="/business/companydocuments-form" element={CompanyDocumentsForm ? <CompanyDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/business/catalogoffers-form" element={CatalogOffersForm ? <CatalogOffersForm /> : <div>Carregando...</div>} />
              <Route path="/business/business" element={BusinessOverview ? <BusinessOverview /> : <div>Carregando...</div>} />
              <Route path="/riders/vehicles-form" element={VehiclesForm ? <VehiclesForm /> : <div>Carregando...</div>} />
              <Route path="/riders/riderprofiles" element={RiderProfilesList ? <RiderProfilesList /> : <div>Carregando...</div>} />
              <Route path="/riders/riderdocuments-form" element={RiderDocumentsForm ? <RiderDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/riders/riderdocuments" element={RiderDocumentsList ? <RiderDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/riders/riders" element={RidersOverview ? <RidersOverview /> : <div>Carregando...</div>} />
              <Route path="/riders/riderspermissions" element={RidersPermissions ? <RidersPermissions /> : <div>Carregando...</div>} />
              <Route path="/riders/riderreviews-form" element={RiderReviewsForm ? <RiderReviewsForm /> : <div>Carregando...</div>} />
              <Route path="/riders/vehicles" element={VehiclesList ? <VehiclesList /> : <div>Carregando...</div>} />
              <Route path="/riders/riderprofiles-form" element={RiderProfilesForm ? <RiderProfilesForm /> : <div>Carregando...</div>} />
              <Route path="/riders/riderreviews" element={RiderReviewsList ? <RiderReviewsList /> : <div>Carregando...</div>} />
              <Route path="/vision/streams-form" element={StreamsForm ? <StreamsForm /> : <div>Carregando...</div>} />
              <Route path="/vision/recordings" element={RecordingsList ? <RecordingsList /> : <div>Carregando...</div>} />
              <Route path="/vision/motionalerts-form" element={MotionAlertsForm ? <MotionAlertsForm /> : <div>Carregando...</div>} />
              <Route path="/vision/devices-form" element={DevicesForm ? <DevicesForm /> : <div>Carregando...</div>} />
              <Route path="/vision/visionpermissions" element={VisionPermissions ? <VisionPermissions /> : <div>Carregando...</div>} />
              <Route path="/vision/streams" element={StreamsList ? <StreamsList /> : <div>Carregando...</div>} />
              <Route path="/vision/devices" element={DevicesList ? <DevicesList /> : <div>Carregando...</div>} />
              <Route path="/vision/vision" element={VisionOverview ? <VisionOverview /> : <div>Carregando...</div>} />
              <Route path="/vision/motionalerts" element={MotionAlertsList ? <MotionAlertsList /> : <div>Carregando...</div>} />
              <Route path="/vision/recordings-form" element={RecordingsForm ? <RecordingsForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/userroles" element={UserRolesList ? <UserRolesList /> : <div>Carregando...</div>} />
              <Route path="/permissions/roles" element={RolesList ? <RolesList /> : <div>Carregando...</div>} />
              <Route path="/permissions/approvallimits" element={ApprovalLimitsList ? <ApprovalLimitsList /> : <div>Carregando...</div>} />
              <Route path="/permissions/permissions" element={PermissionsList ? <PermissionsList /> : <div>Carregando...</div>} />
              <Route path="/permissions/userroles-form" element={UserRolesForm ? <UserRolesForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/permissionspermissions" element={PermissionsPermissions ? <PermissionsPermissions /> : <div>Carregando...</div>} />
              <Route path="/permissions/permissions-form" element={PermissionsForm ? <PermissionsForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/approvallimits-form" element={ApprovalLimitsForm ? <ApprovalLimitsForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/accesspolicies" element={AccessPoliciesList ? <AccessPoliciesList /> : <div>Carregando...</div>} />
              <Route path="/permissions/permissions" element={PermissionsOverview ? <PermissionsOverview /> : <div>Carregando...</div>} />
              <Route path="/permissions/roles-form" element={RolesForm ? <RolesForm /> : <div>Carregando...</div>} />
              <Route path="/permissions/accesspolicies-form" element={AccessPoliciesForm ? <AccessPoliciesForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/apiclients-form" element={ApiClientsForm ? <ApiClientsForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/api_hubpermissions" element={Api_hubPermissions ? <Api_hubPermissions /> : <div>Carregando...</div>} />
              <Route path="/api_hub/apikeys-form" element={ApiKeysForm ? <ApiKeysForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/apiclients" element={ApiClientsList ? <ApiClientsList /> : <div>Carregando...</div>} />
              <Route path="/api_hub/apikeys" element={ApiKeysList ? <ApiKeysList /> : <div>Carregando...</div>} />
              <Route path="/api_hub/integrationruns-form" element={IntegrationRunsForm ? <IntegrationRunsForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/webhooks" element={WebhooksList ? <WebhooksList /> : <div>Carregando...</div>} />
              <Route path="/api_hub/api_hub" element={Api_hubOverview ? <Api_hubOverview /> : <div>Carregando...</div>} />
              <Route path="/api_hub/webhooks-form" element={WebhooksForm ? <WebhooksForm /> : <div>Carregando...</div>} />
              <Route path="/api_hub/integrationruns" element={IntegrationRunsList ? <IntegrationRunsList /> : <div>Carregando...</div>} />
              <Route path="/legal/legalpermissions" element={LegalPermissions ? <LegalPermissions /> : <div>Carregando...</div>} />
              <Route path="/legal/hearings-form" element={HearingsForm ? <HearingsForm /> : <div>Carregando...</div>} />
              <Route path="/legal/legal" element={LegalOverview ? <LegalOverview /> : <div>Carregando...</div>} />
              <Route path="/legal/deadlines-form" element={DeadlinesForm ? <DeadlinesForm /> : <div>Carregando...</div>} />
              <Route path="/legal/legalcontracts" element={LegalContractsList ? <LegalContractsList /> : <div>Carregando...</div>} />
              <Route path="/legal/deadlines" element={DeadlinesList ? <DeadlinesList /> : <div>Carregando...</div>} />
              <Route path="/legal/cases" element={CasesList ? <CasesList /> : <div>Carregando...</div>} />
              <Route path="/legal/legalcontracts-form" element={LegalContractsForm ? <LegalContractsForm /> : <div>Carregando...</div>} />
              <Route path="/legal/hearings" element={HearingsList ? <HearingsList /> : <div>Carregando...</div>} />
              <Route path="/legal/cases-form" element={CasesForm ? <CasesForm /> : <div>Carregando...</div>} />
              <Route path="/tms/freights" element={FreightsList ? <FreightsList /> : <div>Carregando...</div>} />
              <Route path="/tms/routes-form" element={RoutesForm ? <RoutesForm /> : <div>Carregando...</div>} />
              <Route path="/tms/tmspermissions" element={TmsPermissions ? <TmsPermissions /> : <div>Carregando...</div>} />
              <Route path="/tms/freightaudits" element={FreightAuditsList ? <FreightAuditsList /> : <div>Carregando...</div>} />
              <Route path="/tms/proofsofdelivery" element={ProofsOfDeliveryList ? <ProofsOfDeliveryList /> : <div>Carregando...</div>} />
              <Route path="/tms/tms" element={TmsOverview ? <TmsOverview /> : <div>Carregando...</div>} />
              <Route path="/tms/routes" element={RoutesList ? <RoutesList /> : <div>Carregando...</div>} />
              <Route path="/tms/freights-form" element={FreightsForm ? <FreightsForm /> : <div>Carregando...</div>} />
              <Route path="/tms/proofsofdelivery-form" element={ProofsOfDeliveryForm ? <ProofsOfDeliveryForm /> : <div>Carregando...</div>} />
              <Route path="/tms/carriers" element={CarriersList ? <CarriersList /> : <div>Carregando...</div>} />
              <Route path="/tms/carriers-form" element={CarriersForm ? <CarriersForm /> : <div>Carregando...</div>} />
              <Route path="/tms/freightaudits-form" element={FreightAuditsForm ? <FreightAuditsForm /> : <div>Carregando...</div>} />
              <Route path="/document/folders" element={FoldersList ? <FoldersList /> : <div>Carregando...</div>} />
              <Route path="/document/versions-form" element={VersionsForm ? <VersionsForm /> : <div>Carregando...</div>} />
              <Route path="/document/documents-form" element={DocumentsForm ? <DocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/document/documentpermissions" element={DocumentPermissions ? <DocumentPermissions /> : <div>Carregando...</div>} />
              <Route path="/document/document" element={DocumentOverview ? <DocumentOverview /> : <div>Carregando...</div>} />
              <Route path="/document/retentionpolicies-form" element={RetentionPoliciesForm ? <RetentionPoliciesForm /> : <div>Carregando...</div>} />
              <Route path="/document/folders-form" element={FoldersForm ? <FoldersForm /> : <div>Carregando...</div>} />
              <Route path="/document/retentionpolicies" element={RetentionPoliciesList ? <RetentionPoliciesList /> : <div>Carregando...</div>} />
              <Route path="/document/versions" element={VersionsList ? <VersionsList /> : <div>Carregando...</div>} />
              <Route path="/document/documents" element={DocumentsList ? <DocumentsList /> : <div>Carregando...</div>} />
              <Route path="/services/providers" element={ProvidersList ? <ProvidersList /> : <div>Carregando...</div>} />
              <Route path="/services/servicespermissions" element={ServicesPermissions ? <ServicesPermissions /> : <div>Carregando...</div>} />
              <Route path="/services/providers-form" element={ProvidersForm ? <ProvidersForm /> : <div>Carregando...</div>} />
              <Route path="/services/visits-form" element={VisitsForm ? <VisitsForm /> : <div>Carregando...</div>} />
              <Route path="/services/services" element={ServicesOverview ? <ServicesOverview /> : <div>Carregando...</div>} />
              <Route path="/services/evidence-form" element={EvidenceForm ? <EvidenceForm /> : <div>Carregando...</div>} />
              <Route path="/services/servicecontracts-form" element={ServiceContractsForm ? <ServiceContractsForm /> : <div>Carregando...</div>} />
              <Route path="/services/quotes" element={QuotesList ? <QuotesList /> : <div>Carregando...</div>} />
              <Route path="/services/servicecontracts" element={ServiceContractsList ? <ServiceContractsList /> : <div>Carregando...</div>} />
              <Route path="/services/visits" element={VisitsList ? <VisitsList /> : <div>Carregando...</div>} />
              <Route path="/services/evidence" element={EvidenceList ? <EvidenceList /> : <div>Carregando...</div>} />
              <Route path="/services/quotes-form" element={QuotesForm ? <QuotesForm /> : <div>Carregando...</div>} />
              <Route path="/hr/candidates-form" element={CandidatesForm ? <CandidatesForm /> : <div>Carregando...</div>} />
              <Route path="/hr/courses" element={CoursesList ? <CoursesList /> : <div>Carregando...</div>} />
              <Route path="/hr/hrpermissions" element={HrPermissions ? <HrPermissions /> : <div>Carregando...</div>} />
              <Route path="/hr/occupationalrecords" element={OccupationalRecordsList ? <OccupationalRecordsList /> : <div>Carregando...</div>} />
              <Route path="/hr/employees" element={EmployeesList ? <EmployeesList /> : <div>Carregando...</div>} />
              <Route path="/hr/payrollruns" element={PayrollRunsList ? <PayrollRunsList /> : <div>Carregando...</div>} />
              <Route path="/hr/payrollruns-form" element={PayrollRunsForm ? <PayrollRunsForm /> : <div>Carregando...</div>} />
              <Route path="/hr/candidates" element={CandidatesList ? <CandidatesList /> : <div>Carregando...</div>} />
              <Route path="/hr/occupationalrecords-form" element={OccupationalRecordsForm ? <OccupationalRecordsForm /> : <div>Carregando...</div>} />
              <Route path="/hr/hr" element={HrOverview ? <HrOverview /> : <div>Carregando...</div>} />
              <Route path="/hr/employees-form" element={EmployeesForm ? <EmployeesForm /> : <div>Carregando...</div>} />
              <Route path="/hr/courses-form" element={CoursesForm ? <CoursesForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/insuranceoptions" element={InsuranceOptionsList ? <InsuranceOptionsList /> : <div>Carregando...</div>} />
              <Route path="/delivery/proofs-form" element={ProofsForm ? <ProofsForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/deliveryrequests" element={DeliveryRequestsList ? <DeliveryRequestsList /> : <div>Carregando...</div>} />
              <Route path="/delivery/assignments" element={AssignmentsList ? <AssignmentsList /> : <div>Carregando...</div>} />
              <Route path="/delivery/delivery" element={DeliveryOverview ? <DeliveryOverview /> : <div>Carregando...</div>} />
              <Route path="/delivery/proofs" element={ProofsList ? <ProofsList /> : <div>Carregando...</div>} />
              <Route path="/delivery/quotes" element={QuotesList ? <QuotesList /> : <div>Carregando...</div>} />
              <Route path="/delivery/insuranceoptions-form" element={InsuranceOptionsForm ? <InsuranceOptionsForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/deliverypermissions" element={DeliveryPermissions ? <DeliveryPermissions /> : <div>Carregando...</div>} />
              <Route path="/delivery/deliveryrequests-form" element={DeliveryRequestsForm ? <DeliveryRequestsForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/quotes-form" element={QuotesForm ? <QuotesForm /> : <div>Carregando...</div>} />
              <Route path="/delivery/assignments-form" element={AssignmentsForm ? <AssignmentsForm /> : <div>Carregando...</div>} />
              <Route path="/property/assemblies" element={AssembliesList ? <AssembliesList /> : <div>Carregando...</div>} />
              <Route path="/property/properties" element={PropertiesList ? <PropertiesList /> : <div>Carregando...</div>} />
              <Route path="/property/leases-form" element={LeasesForm ? <LeasesForm /> : <div>Carregando...</div>} />
              <Route path="/property/units-form" element={UnitsForm ? <UnitsForm /> : <div>Carregando...</div>} />
              <Route path="/property/maintenanceorders" element={MaintenanceOrdersList ? <MaintenanceOrdersList /> : <div>Carregando...</div>} />
              <Route path="/property/property" element={PropertyOverview ? <PropertyOverview /> : <div>Carregando...</div>} />
              <Route path="/property/units" element={UnitsList ? <UnitsList /> : <div>Carregando...</div>} />
              <Route path="/property/propertypermissions" element={PropertyPermissions ? <PropertyPermissions /> : <div>Carregando...</div>} />
              <Route path="/property/leases" element={LeasesList ? <LeasesList /> : <div>Carregando...</div>} />
              <Route path="/property/assemblies-form" element={AssembliesForm ? <AssembliesForm /> : <div>Carregando...</div>} />
              <Route path="/property/maintenanceorders-form" element={MaintenanceOrdersForm ? <MaintenanceOrdersForm /> : <div>Carregando...</div>} />
              <Route path="/property/properties-form" element={PropertiesForm ? <PropertiesForm /> : <div>Carregando...</div>} />
              <Route path="/stock/pricerules" element={PriceRulesList ? <PriceRulesList /> : <div>Carregando...</div>} />
              <Route path="/stock/catalogproducts-form" element={CatalogProductsForm ? <CatalogProductsForm /> : <div>Carregando...</div>} />
              <Route path="/stock/pricerules-form" element={PriceRulesForm ? <PriceRulesForm /> : <div>Carregando...</div>} />
              <Route path="/stock/suppliers-form" element={SuppliersForm ? <SuppliersForm /> : <div>Carregando...</div>} />
              <Route path="/stock/supplierorders-form" element={SupplierOrdersForm ? <SupplierOrdersForm /> : <div>Carregando...</div>} />
              <Route path="/stock/discountquotes-form" element={DiscountQuotesForm ? <DiscountQuotesForm /> : <div>Carregando...</div>} />
              <Route path="/stock/discountquotes" element={DiscountQuotesList ? <DiscountQuotesList /> : <div>Carregando...</div>} />
              <Route path="/stock/supplierorders" element={SupplierOrdersList ? <SupplierOrdersList /> : <div>Carregando...</div>} />
              <Route path="/stock/catalogproducts" element={CatalogProductsList ? <CatalogProductsList /> : <div>Carregando...</div>} />
              <Route path="/stock/suppliers" element={SuppliersList ? <SuppliersList /> : <div>Carregando...</div>} />
              <Route path="/stock/stock" element={StockOverview ? <StockOverview /> : <div>Carregando...</div>} />
              <Route path="/stock/stockpermissions" element={StockPermissions ? <StockPermissions /> : <div>Carregando...</div>} />
              <Route path="/erp/costcenters-form" element={CostCentersForm ? <CostCentersForm /> : <div>Carregando...</div>} />
              <Route path="/erp/payables" element={PayablesList ? <PayablesList /> : <div>Carregando...</div>} />
              <Route path="/erp/fiscaldocuments-form" element={FiscalDocumentsForm ? <FiscalDocumentsForm /> : <div>Carregando...</div>} />
              <Route path="/erp/costcenters" element={CostCentersList ? <CostCentersList /> : <div>Carregando...</div>} />
              <Route path="/erp/accounts-form" element={AccountsForm ? <AccountsForm /> : <div>Carregando...</div>} />
              <Route path="/erp/payables-form" element={PayablesForm ? <PayablesForm /> : <div>Carregando...</div>} />
              <Route path="/erp/fiscaldocuments" element={FiscalDocumentsList ? <FiscalDocumentsList /> : <div>Carregando...</div>} />
              <Route path="/erp/erp" element={ErpOverview ? <ErpOverview /> : <div>Carregando...</div>} />
              <Route path="/erp/receivables" element={ReceivablesList ? <ReceivablesList /> : <div>Carregando...</div>} />
              <Route path="/erp/receivables-form" element={ReceivablesForm ? <ReceivablesForm /> : <div>Carregando...</div>} />
              <Route path="/erp/accounts" element={AccountsList ? <AccountsList /> : <div>Carregando...</div>} />
              <Route path="/erp/erppermissions" element={ErpPermissions ? <ErpPermissions /> : <div>Carregando...</div>} />
              <Route path="/wms/inventory-form" element={InventoryForm ? <InventoryForm /> : <div>Carregando...</div>} />
              <Route path="/wms/warehouses-form" element={WarehousesForm ? <WarehousesForm /> : <div>Carregando...</div>} />
              <Route path="/wms/shipments-form" element={ShipmentsForm ? <ShipmentsForm /> : <div>Carregando...</div>} />
              <Route path="/wms/bins" element={BinsList ? <BinsList /> : <div>Carregando...</div>} />
              <Route path="/wms/wmspermissions" element={WmsPermissions ? <WmsPermissions /> : <div>Carregando...</div>} />
              <Route path="/wms/bins-form" element={BinsForm ? <BinsForm /> : <div>Carregando...</div>} />
              <Route path="/wms/pickingwaves-form" element={PickingWavesForm ? <PickingWavesForm /> : <div>Carregando...</div>} />
              <Route path="/wms/shipments" element={ShipmentsList ? <ShipmentsList /> : <div>Carregando...</div>} />
              <Route path="/wms/warehouses" element={WarehousesList ? <WarehousesList /> : <div>Carregando...</div>} />
              <Route path="/wms/pickingwaves" element={PickingWavesList ? <PickingWavesList /> : <div>Carregando...</div>} />
              <Route path="/wms/inventory" element={InventoryList ? <InventoryList /> : <div>Carregando...</div>} />
              <Route path="/wms/wms" element={WmsOverview ? <WmsOverview /> : <div>Carregando...</div>} />
              <Route path="/finance/invoices" element={InvoicesList ? <InvoicesList /> : <div>Carregando...</div>} />
              <Route path="/finance/escrows" element={EscrowsList ? <EscrowsList /> : <div>Carregando...</div>} />
              <Route path="/finance/escrows-form" element={EscrowsForm ? <EscrowsForm /> : <div>Carregando...</div>} />
              <Route path="/finance/wallets-form" element={WalletsForm ? <WalletsForm /> : <div>Carregando...</div>} />
              <Route path="/finance/ledgerentries" element={LedgerEntriesList ? <LedgerEntriesList /> : <div>Carregando...</div>} />
              <Route path="/finance/splits-form" element={SplitsForm ? <SplitsForm /> : <div>Carregando...</div>} />
              <Route path="/finance/financepermissions" element={FinancePermissions ? <FinancePermissions /> : <div>Carregando...</div>} />
              <Route path="/finance/finance" element={FinanceOverview ? <FinanceOverview /> : <div>Carregando...</div>} />
              <Route path="/finance/invoices-form" element={InvoicesForm ? <InvoicesForm /> : <div>Carregando...</div>} />
              <Route path="/finance/wallets" element={WalletsList ? <WalletsList /> : <div>Carregando...</div>} />
              <Route path="/finance/splits" element={SplitsList ? <SplitsList /> : <div>Carregando...</div>} />
              <Route path="/finance/walletledger" element={WalletLedger ? <WalletLedger /> : <div>Carregando...</div>} />
              <Route path="/finance/ledgerentries-form" element={LedgerEntriesForm ? <LedgerEntriesForm /> : <div>Carregando...</div>} />
              <Route path="/ai_core/modelruns" element={ModelRunsList ? <ModelRunsList /> : <div>Carregando...</div>} />
              <Route path="/ai_core/moderationdecisions" element={ModerationDecisionsList ? <ModerationDecisionsList /> : <div>Carregando...</div>} />
              <Route path="/ai_core/modelruns-form" element={ModelRunsForm ? <ModelRunsForm /> : <div>Carregando...</div>} />
              <Route path="/ai_core/ai_corepermissions" element={Ai_corePermissions ? <Ai_corePermissions /> : <div>Carregando...</div>} />
              <Route path="/ai_core/ai_core" element={Ai_coreOverview ? <Ai_coreOverview /> : <div>Carregando...</div>} />
              <Route path="/ai_core/aimemories-form" element={AiMemoriesForm ? <AiMemoriesForm /> : <div>Carregando...</div>} />
              <Route path="/ai_core/aimemories" element={AiMemoriesList ? <AiMemoriesList /> : <div>Carregando...</div>} />
              <Route path="/ai_core/moderationdecisions-form" element={ModerationDecisionsForm ? <ModerationDecisionsForm /> : <div>Carregando...</div>} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </Router>
  );
}

export default App;

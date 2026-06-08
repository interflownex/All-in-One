
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

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Navigation />
        <main className="content-area">
          <Suspense fallback={<div className="loader">Carregando...</div>}>
            <Routes>
              <Route path="/" element={<div className="container hero"><h1>Bem-vindo ao All-in-One</h1><p>Selecione um módulo no menu lateral para começar.</p></div>} />
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
            </Routes>
          </Suspense>
        </main>
      </div>
    </Router>
  );
}

export default App;

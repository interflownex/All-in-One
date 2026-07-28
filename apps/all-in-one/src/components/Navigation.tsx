import React, { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

const modulesData = [
  {
    slug: "ai_core",
    title: "Ai_core",
    icon: "🧠",
    screens: [
      { title: "Ai Memories", path: "/ai_core/aimemories-form" },
      { title: "Ai Memories", path: "/ai_core/aimemories" },
      { title: "Ai_core", path: "/ai_core/ai_core" },
      { title: "Ai_core Permissões", path: "/ai_core/ai_corepermissions" },
      { title: "Model Runs", path: "/ai_core/modelruns" },
      { title: "Model Runs", path: "/ai_core/modelruns-form" },
      { title: "Moderation Decisions", path: "/ai_core/moderationdecisions" },
      { title: "Moderation Decisions", path: "/ai_core/moderationdecisions-form" },
    ],
  },
  {
    slug: "api_hub",
    title: "Api_hub",
    icon: "📦",
    screens: [
      { title: "Api Clients", path: "/api_hub/apiclients-form" },
      { title: "Api Clients", path: "/api_hub/apiclients" },
      { title: "Api Keys", path: "/api_hub/apikeys-form" },
      { title: "Api Keys", path: "/api_hub/apikeys" },
      { title: "Api_hub", path: "/api_hub/api_hub" },
      { title: "Api_hub Permissões", path: "/api_hub/api_hubpermissions" },
      { title: "Integration Runs", path: "/api_hub/integrationruns-form" },
      { title: "Integration Runs", path: "/api_hub/integrationruns" },
      { title: "Webhooks", path: "/api_hub/webhooks" },
      { title: "Webhooks", path: "/api_hub/webhooks-form" },
    ],
  },
  {
    slug: "bi",
    title: "Bi",
    icon: "📈",
    screens: [
      { title: "Bi", path: "/bi/bi" },
      { title: "Bi Permissões", path: "/bi/bipermissions" },
      { title: "Dashboards", path: "/bi/dashboards" },
      { title: "Dashboards", path: "/bi/dashboards-form" },
      { title: "Datasets", path: "/bi/datasets" },
      { title: "Datasets", path: "/bi/datasets-form" },
      { title: "Exports", path: "/bi/exports-form" },
      { title: "Exports", path: "/bi/exports" },
      { title: "Indicators", path: "/bi/indicators-form" },
      { title: "Indicators", path: "/bi/indicators" },
    ],
  },
  {
    slug: "bpm",
    title: "Bpm",
    icon: "⚙️",
    screens: [
      { title: "Bpm", path: "/bpm/bpm" },
      { title: "Bpm Permissões", path: "/bpm/bpmpermissions" },
      { title: "Processes", path: "/bpm/processes" },
      { title: "Processes", path: "/bpm/processes-form" },
      { title: "Sla Policies", path: "/bpm/slapolicies-form" },
      { title: "Sla Policies", path: "/bpm/slapolicies" },
      { title: "Tasks", path: "/bpm/tasks-form" },
      { title: "Tasks", path: "/bpm/tasks" },
      { title: "Workflow Instances", path: "/bpm/workflowinstances-form" },
      { title: "Workflow Instances", path: "/bpm/workflowinstances" },
    ],
  },
  {
    slug: "business",
    title: "Business",
    icon: "🏢",
    screens: [
      { title: "Branches", path: "/business/branches-form" },
      { title: "Branches", path: "/business/branches" },
      { title: "Business", path: "/business/business" },
      { title: "Business Permissões", path: "/business/businesspermissions" },
      { title: "Catalog Offers", path: "/business/catalogoffers" },
      { title: "Catalog Offers", path: "/business/catalogoffers-form" },
      { title: "Companies", path: "/business/companies" },
      { title: "Companies", path: "/business/companies-form" },
      { title: "Company Documents", path: "/business/companydocuments" },
      { title: "Company Documents", path: "/business/companydocuments-form" },
      { title: "User Company Memberships", path: "/business/usercompanymemberships" },
      { title: "User Company Memberships", path: "/business/usercompanymemberships-form" },
    ],
  },
  {
    slug: "crm",
    title: "Crm",
    icon: "🤝",
    screens: [
      { title: "Activities", path: "/crm/activities-form" },
      { title: "Activities", path: "/crm/activities" },
      { title: "Campaigns", path: "/crm/campaigns" },
      { title: "Campaigns", path: "/crm/campaigns-form" },
      { title: "Crm", path: "/crm/crm" },
      { title: "Crm Permissões", path: "/crm/crmpermissions" },
      { title: "Leads", path: "/crm/leads-form" },
      { title: "Leads", path: "/crm/leads" },
      { title: "Opportunities", path: "/crm/opportunities" },
      { title: "Opportunities", path: "/crm/opportunities-form" },
    ],
  },
  {
    slug: "delivery",
    title: "Delivery",
    icon: "🚚",
    screens: [
      { title: "Assignments", path: "/delivery/assignments" },
      { title: "Assignments", path: "/delivery/assignments-form" },
      { title: "Delivery", path: "/delivery/delivery" },
      { title: "Delivery Permissões", path: "/delivery/deliverypermissions" },
      { title: "Delivery Requests", path: "/delivery/deliveryrequests" },
      { title: "Delivery Requests", path: "/delivery/deliveryrequests-form" },
      { title: "Insurance Options", path: "/delivery/insuranceoptions" },
      { title: "Insurance Options", path: "/delivery/insuranceoptions-form" },
      { title: "Proofs", path: "/delivery/proofs-form" },
      { title: "Proofs", path: "/delivery/proofs" },
      { title: "Quotes", path: "/delivery/quotes" },
      { title: "Quotes", path: "/delivery/quotes-form" },
    ],
  },
  {
    slug: "document",
    title: "Document",
    icon: "📦",
    screens: [
      { title: "Document", path: "/document/document" },
      { title: "Document Permissões", path: "/document/documentpermissions" },
      { title: "Documents", path: "/document/documents-form" },
      { title: "Documents", path: "/document/documents" },
      { title: "Folders", path: "/document/folders" },
      { title: "Folders", path: "/document/folders-form" },
      { title: "Retention Policies", path: "/document/retentionpolicies-form" },
      { title: "Retention Policies", path: "/document/retentionpolicies" },
      { title: "Versions", path: "/document/versions-form" },
      { title: "Versions", path: "/document/versions" },
    ],
  },
  {
    slug: "erp",
    title: "Erp",
    icon: "📊",
    screens: [
      { title: "Construtor de formulários", path: "/governance/dynamic-forms" },
      { title: "Unidades e Fiscal", path: "/governance/units-tax" },
      { title: "Accounts", path: "/erp/accounts-form" },
      { title: "Accounts", path: "/erp/accounts" },
      { title: "Cost Centers", path: "/erp/costcenters-form" },
      { title: "Cost Centers", path: "/erp/costcenters" },
      { title: "Erp", path: "/erp/erp" },
      { title: "Erp Permissões", path: "/erp/erppermissions" },
      { title: "Fiscal Documents", path: "/erp/fiscaldocuments-form" },
      { title: "Fiscal Documents", path: "/erp/fiscaldocuments" },
      { title: "Payables", path: "/erp/payables" },
      { title: "Payables", path: "/erp/payables-form" },
      { title: "Receivables", path: "/erp/receivables" },
      { title: "Receivables", path: "/erp/receivables-form" },
    ],
  },
  {
    slug: "finance",
    title: "Finance",
    icon: "💰",
    screens: [
      { title: "Escrows", path: "/finance/escrows" },
      { title: "Escrows", path: "/finance/escrows-form" },
      { title: "Finance", path: "/finance/finance" },
      { title: "Finance Permissões", path: "/finance/financepermissions" },
      { title: "Invoices", path: "/finance/invoices" },
      { title: "Invoices", path: "/finance/invoices-form" },
      { title: "Ledger Entries", path: "/finance/ledgerentries" },
      { title: "Ledger Entries", path: "/finance/ledgerentries-form" },
      { title: "Splits", path: "/finance/splits-form" },
      { title: "Splits", path: "/finance/splits" },
      { title: "Wallet Ledger", path: "/finance/walletledger" },
      { title: "Wallets", path: "/finance/wallets-form" },
      { title: "Wallets", path: "/finance/wallets" },
    ],
  },
  {
    slug: "health",
    title: "Health",
    icon: "🏥",
    screens: [
      { title: "Appointments", path: "/health/appointments-form" },
      { title: "Appointments", path: "/health/appointments" },
      { title: "Beds", path: "/health/beds-form" },
      { title: "Beds", path: "/health/beds" },
      { title: "Health", path: "/health/health" },
      { title: "Health Permissões", path: "/health/healthpermissions" },
      { title: "Medical Records", path: "/health/medicalrecords-form" },
      { title: "Medical Records", path: "/health/medicalrecords" },
      { title: "Patients", path: "/health/patients-form" },
      { title: "Patients", path: "/health/patients" },
      { title: "Prescriptions", path: "/health/prescriptions" },
      { title: "Prescriptions", path: "/health/prescriptions-form" },
    ],
  },
  {
    slug: "hr",
    title: "Hr",
    icon: "📦",
    screens: [
      { title: "Candidates", path: "/hr/candidates-form" },
      { title: "Candidates", path: "/hr/candidates" },
      { title: "Courses", path: "/hr/courses" },
      { title: "Courses", path: "/hr/courses-form" },
      { title: "Employees", path: "/hr/employees" },
      { title: "Employees", path: "/hr/employees-form" },
      { title: "Hr", path: "/hr/hr" },
      { title: "Hr Permissões", path: "/hr/hrpermissions" },
      { title: "Occupational Records", path: "/hr/occupationalrecords" },
      { title: "Occupational Records", path: "/hr/occupationalrecords-form" },
      { title: "Payroll Runs", path: "/hr/payrollruns" },
      { title: "Payroll Runs", path: "/hr/payrollruns-form" },
    ],
  },
  {
    slug: "identity",
    title: "Identity",
    icon: "🆔",
    screens: [
      { title: "Auth Gateway", path: "/identity/authgateway" },
      { title: "Biometrics", path: "/identity/biometrics" },
      { title: "Biometrics", path: "/identity/biometrics-form" },
      { title: "Consent Lgpd", path: "/identity/consentlgpd" },
      { title: "Consent Records", path: "/identity/consentrecords" },
      { title: "Consent Records", path: "/identity/consentrecords-form" },
      { title: "Documents", path: "/identity/documents-form" },
      { title: "Documents", path: "/identity/documents" },
      { title: "Identity", path: "/identity/identity" },
      { title: "Identity Permissões", path: "/identity/identitypermissions" },
      { title: "Identity Verifications", path: "/identity/identityverifications-form" },
      { title: "Identity Verifications", path: "/identity/identityverifications" },
      { title: "Kyb Business", path: "/identity/kybbusiness" },
      { title: "Kyc Verification", path: "/identity/kycverification" },
      { title: "Mfa Manager", path: "/identity/mfamanager" },
      { title: "Session Control", path: "/identity/sessioncontrol" },
      { title: "Sessions", path: "/identity/sessions-form" },
      { title: "Sessions", path: "/identity/sessions" },
      { title: "Users", path: "/identity/users" },
      { title: "Users", path: "/identity/users-form" },
    ],
  },
  {
    slug: "jobs",
    title: "Jobs",
    icon: "💼",
    screens: [
      { title: "Applications", path: "/jobs/applications-form" },
      { title: "Applications", path: "/jobs/applications" },
      { title: "Candidate Resume", path: "/jobs/candidateresume" },
      { title: "Ctps Import", path: "/jobs/ctpsimport" },
      { title: "Employment Records", path: "/jobs/employmentrecords" },
      { title: "Employment Records", path: "/jobs/employmentrecords-form" },
      { title: "Job Postings", path: "/jobs/jobpostings-form" },
      { title: "Job Postings", path: "/jobs/jobpostings" },
      { title: "Jobs", path: "/jobs/jobs" },
      { title: "Jobs Permissões", path: "/jobs/jobspermissions" },
      { title: "Recruiter Resume Review", path: "/jobs/recruiterresumereview" },
      { title: "Resume Access Logs", path: "/jobs/resumeaccesslogs-form" },
      { title: "Resume Access Logs", path: "/jobs/resumeaccesslogs" },
      { title: "Resume Documents", path: "/jobs/resumedocuments-form" },
      { title: "Resume Documents", path: "/jobs/resumedocuments" },
      { title: "Resumes", path: "/jobs/resumes" },
      { title: "Resumes", path: "/jobs/resumes-form" },
      { title: "Vacancy Search", path: "/jobs/vacancysearch" },
    ],
  },
  {
    slug: "legal",
    title: "Legal",
    icon: "📦",
    screens: [
      { title: "Cases", path: "/legal/cases" },
      { title: "Cases", path: "/legal/cases-form" },
      { title: "Deadlines", path: "/legal/deadlines-form" },
      { title: "Deadlines", path: "/legal/deadlines" },
      { title: "Hearings", path: "/legal/hearings-form" },
      { title: "Hearings", path: "/legal/hearings" },
      { title: "Legal", path: "/legal/legal" },
      { title: "Legal Contracts", path: "/legal/legalcontracts" },
      { title: "Legal Contracts", path: "/legal/legalcontracts-form" },
      { title: "Legal Permissões", path: "/legal/legalpermissions" },
    ],
  },
  {
    slug: "marketplace",
    title: "Marketplace",
    icon: "🛍️",
    screens: [
      { title: "Carts", path: "/marketplace/carts-form" },
      { title: "Carts", path: "/marketplace/carts" },
      { title: "Disputes", path: "/marketplace/disputes" },
      { title: "Disputes", path: "/marketplace/disputes-form" },
      { title: "Marketplace", path: "/marketplace/marketplace" },
      { title: "Marketplace Permissões", path: "/marketplace/marketplacepermissions" },
      { title: "Orders", path: "/marketplace/orders-form" },
      { title: "Orders", path: "/marketplace/orders" },
      { title: "Pepita Grants", path: "/marketplace/pepitagrants-form" },
      { title: "Pepita Grants", path: "/marketplace/pepitagrants" },
      { title: "Products", path: "/marketplace/products-form" },
      { title: "Products", path: "/marketplace/products" },
      { title: "Reviews", path: "/marketplace/reviews" },
      { title: "Reviews", path: "/marketplace/reviews-form" },
      { title: "Stores", path: "/marketplace/stores" },
      { title: "Stores", path: "/marketplace/stores-form" },
    ],
  },
  {
    slug: "mobility",
    title: "Mobility",
    icon: "📦",
    screens: [
      { title: "Fare Rules", path: "/mobility/farerules-form" },
      { title: "Fare Rules", path: "/mobility/farerules" },
      { title: "Mobility", path: "/mobility/mobility" },
      { title: "Mobility Permissões", path: "/mobility/mobilitypermissions" },
      { title: "Rides", path: "/mobility/rides" },
      { title: "Rides", path: "/mobility/rides-form" },
      { title: "Routes", path: "/mobility/routes-form" },
      { title: "Routes", path: "/mobility/routes" },
      { title: "Stops", path: "/mobility/stops-form" },
      { title: "Stops", path: "/mobility/stops" },
      { title: "Tickets", path: "/mobility/tickets" },
      { title: "Tickets", path: "/mobility/tickets-form" },
    ],
  },
  {
    slug: "permissions",
    title: "Permissions",
    icon: "📦",
    screens: [
      { title: "Access Policies", path: "/permissions/accesspolicies" },
      { title: "Access Policies", path: "/permissions/accesspolicies-form" },
      { title: "Approval Limits", path: "/permissions/approvallimits" },
      { title: "Approval Limits", path: "/permissions/approvallimits-form" },
      { title: "Permissões", path: "/permissions/permissions-form" },
      { title: "Permissões", path: "/permissions/permissions" },
      { title: "Permissões Permissões", path: "/permissions/permissionspermissions" },
      { title: "Roles", path: "/permissions/roles" },
      { title: "Roles", path: "/permissions/roles-form" },
      { title: "User Roles", path: "/permissions/userroles" },
      { title: "User Roles", path: "/permissions/userroles-form" },
    ],
  },
  {
    slug: "property",
    title: "Property",
    icon: "📦",
    screens: [
      { title: "Assemblies", path: "/property/assemblies" },
      { title: "Assemblies", path: "/property/assemblies-form" },
      { title: "Leases", path: "/property/leases-form" },
      { title: "Leases", path: "/property/leases" },
      { title: "Maintenance Orders", path: "/property/maintenanceorders" },
      { title: "Maintenance Orders", path: "/property/maintenanceorders-form" },
      { title: "Properties", path: "/property/properties" },
      { title: "Properties", path: "/property/properties-form" },
      { title: "Property", path: "/property/property" },
      { title: "Property Permissões", path: "/property/propertypermissions" },
      { title: "Units", path: "/property/units-form" },
      { title: "Units", path: "/property/units" },
    ],
  },
  {
    slug: "riders",
    title: "Riders",
    icon: "📦",
    screens: [
      { title: "Rider Documents", path: "/riders/riderdocuments-form" },
      { title: "Rider Documents", path: "/riders/riderdocuments" },
      { title: "Rider Profiles", path: "/riders/riderprofiles" },
      { title: "Rider Profiles", path: "/riders/riderprofiles-form" },
      { title: "Rider Reviews", path: "/riders/riderreviews-form" },
      { title: "Rider Reviews", path: "/riders/riderreviews" },
      { title: "Riders", path: "/riders/riders" },
      { title: "Riders Permissões", path: "/riders/riderspermissions" },
      { title: "Vehicles", path: "/riders/vehicles-form" },
      { title: "Vehicles", path: "/riders/vehicles" },
    ],
  },
  {
    slug: "services",
    title: "Services",
    icon: "📦",
    screens: [
      { title: "Evidence", path: "/services/evidence-form" },
      { title: "Evidence", path: "/services/evidence" },
      { title: "Providers", path: "/services/providers" },
      { title: "Providers", path: "/services/providers-form" },
      { title: "Quotes", path: "/services/quotes" },
      { title: "Quotes", path: "/services/quotes-form" },
      { title: "Service Contracts", path: "/services/servicecontracts-form" },
      { title: "Service Contracts", path: "/services/servicecontracts" },
      { title: "Services", path: "/services/services" },
      { title: "Services Permissões", path: "/services/servicespermissions" },
      { title: "Visits", path: "/services/visits-form" },
      { title: "Visits", path: "/services/visits" },
    ],
  },
  {
    slug: "stock",
    title: "STOCK",
    icon: "📦",
    screens: [
      { title: "Catalog Products", path: "/stock/catalogproducts-form" },
      { title: "Catalog Products", path: "/stock/catalogproducts" },
      { title: "Discount Quotes", path: "/stock/discountquotes-form" },
      { title: "Discount Quotes", path: "/stock/discountquotes" },
      { title: "Price Rules", path: "/stock/pricerules" },
      { title: "Price Rules", path: "/stock/pricerules-form" },
      { title: "STOCK", path: "/stock/stock" },
      { title: "Stock Permissões", path: "/stock/stockpermissions" },
      { title: "Supplier Orders", path: "/stock/supplierorders-form" },
      { title: "Supplier Orders", path: "/stock/supplierorders" },
      { title: "Suppliers", path: "/stock/suppliers-form" },
      { title: "Suppliers", path: "/stock/suppliers" },
    ],
  },
  {
    slug: "tms",
    title: "Tms",
    icon: "🗺️",
    screens: [
      { title: "Carriers", path: "/tms/carriers" },
      { title: "Carriers", path: "/tms/carriers-form" },
      { title: "Freight Audits", path: "/tms/freightaudits" },
      { title: "Freight Audits", path: "/tms/freightaudits-form" },
      { title: "Freights", path: "/tms/freights" },
      { title: "Freights", path: "/tms/freights-form" },
      { title: "Proofs Of Delivery", path: "/tms/proofsofdelivery" },
      { title: "Proofs Of Delivery", path: "/tms/proofsofdelivery-form" },
      { title: "Routes", path: "/tms/routes-form" },
      { title: "Routes", path: "/tms/routes" },
      { title: "Tms", path: "/tms/tms" },
      { title: "Tms Permissões", path: "/tms/tmspermissions" },
    ],
  },
  {
    slug: "wms",
    title: "Wms",
    icon: "🏗️",
    screens: [
      { title: "Bins", path: "/wms/bins" },
      { title: "Bins", path: "/wms/bins-form" },
      { title: "Inventory", path: "/wms/inventory-form" },
      { title: "Inventory", path: "/wms/inventory" },
      { title: "Picking Waves", path: "/wms/pickingwaves-form" },
      { title: "Picking Waves", path: "/wms/pickingwaves" },
      { title: "Shipments", path: "/wms/shipments-form" },
      { title: "Shipments", path: "/wms/shipments" },
      { title: "Warehouses", path: "/wms/warehouses-form" },
      { title: "Warehouses", path: "/wms/warehouses" },
      { title: "Wms", path: "/wms/wms" },
      { title: "Wms Permissões", path: "/wms/wmspermissions" },
    ],
  },
];

const Navigation: React.FC = () => {
  const [openModule, setOpenModule] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  useEffect(() => setMobileOpen(false), [location.pathname]);

  if (location.pathname === "/") return null;

  return (
    <>
      <button
        type="button"
        className="mobile-nav-toggle"
        aria-label={mobileOpen ? "Fechar menu de modulos" : "Abrir menu de modulos"}
        aria-expanded={mobileOpen}
        onClick={() => setMobileOpen((current) => !current)}
      >
        {mobileOpen ? "×" : "☰"}
      </button>
      <nav className={`side-nav${mobileOpen ? " mobile-open" : ""}`} aria-label="Modulos e telas">
        <div
          className="nav-header"
          style={{
            padding: "24px 16px",
            borderBottom: "2px solid #11142a",
            marginBottom: "16px",
            background: "#fff",
          }}
        >
          <Link to="/" className="logo-container" style={{ display: "block" }}>
            <img
              src="/assets/brand/all-in-one-logo-official.png"
              alt="All-in-One Logo"
              style={{ width: "100%", maxWidth: "140px", height: "auto", display: "block" }}
            />
          </Link>
        </div>
        <div className="nav-section">
          <h3>Módulos e Telas</h3>
          <ul>
            {modulesData.map((mod) => (
              <li key={mod.slug} className="nav-item-group" style={{ marginBottom: "4px" }}>
                <button
                  type="button"
                  className={`module-link ${openModule === mod.slug ? "active" : ""}`}
                  aria-expanded={openModule === mod.slug}
                  onClick={() => setOpenModule(openModule === mod.slug ? null : mod.slug)}
                  style={{
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    padding: "12px 16px",
                    fontWeight: 700,
                    border: "2px solid transparent",
                    background: openModule === mod.slug ? "#eef1ff" : "transparent",
                    borderColor: openModule === mod.slug ? "#11142a" : "transparent",
                    boxShadow: openModule === mod.slug ? "4px 4px 0px #11142a" : "none",
                  }}
                >
                  <span className="icon" style={{ marginRight: "12px" }}>
                    {mod.icon}
                  </span>
                  <span className="title" style={{ flex: 1 }}>
                    {mod.title}
                  </span>
                  <span style={{ fontSize: "10px" }}>{openModule === mod.slug ? "▼" : "▶"}</span>
                </button>
                {openModule === mod.slug && (
                  <ul
                    className="sub-menu"
                    style={{
                      listStyle: "none",
                      padding: "8px 0",
                      background: "#f9fafa",
                      borderLeft: "2px solid #11142a",
                      marginLeft: "24px",
                    }}
                  >
                    {mod.screens.map((screen) => (
                      <li key={screen.path}>
                        <Link
                          to={screen.path}
                          style={{
                            fontSize: "13px",
                            padding: "8px 16px",
                            display: "block",
                            color: "#626b8e",
                            textDecoration: "none",
                          }}
                        >
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
    </>
  );
};

export default Navigation;

import React from 'react';
import { Link } from 'react-router-dom';

const modules = [
    { slug: "identity", title: "Identity" },
    { slug: "business", title: "Business" },
    { slug: "permissions", title: "Permissions" },
    { slug: "finance", title: "Finance" },
    { slug: "marketplace", title: "Marketplace" },
    { slug: "stock", title: "Stock" },
    { slug: "delivery", title: "Delivery" },
    { slug: "riders", title: "Riders" },
    { slug: "services", title: "One Services" },
    { slug: "mobility", title: "Mobility" },
    { slug: "jobs", title: "Jobs" },
    { slug: "erp", title: "ERP" },
    { slug: "wms", title: "WMS" },
    { slug: "tms", title: "TMS" },
    { slug: "crm", title: "CRM" },
    { slug: "bpm", title: "BPM" },
    { slug: "document", title: "GED ECM" },
    { slug: "hr", title: "HR HCM" },
    { slug: "health", title: "Health" },
    { slug: "vision", title: "Vision" },
    { slug: "legal", title: "Legal" },
    { slug: "property", title: "Property" },
    { slug: "bi", title: "BI" },
    { slug: "ai_core", title: "AI Core" },
    { slug: "api_hub", title: "API Hub" }
];

const Navigation: React.FC = () => {
  return (
    <nav className="side-nav neo-brutalism">
      <div className="nav-header">
        <Link to="/" className="logo">All-in-One</Link>
      </div>
      <div className="nav-section">
        <h3>Módulos</h3>
        <ul>
          {modules.map(mod => (
            <li key={mod.slug}>
              <Link to={`/${mod.slug}`}>{mod.title}</Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;

import React from 'react';
import { Link } from 'react-router-dom';

const modules = [
    { slug: "identity", title: "Identity", icon: "🆔" },
    { slug: "business", title: "Business", icon: "🏢" },
    { slug: "permissions", title: "Permissions", icon: "🔐" },
    { slug: "finance", title: "Finance", icon: "💰" },
    { slug: "marketplace", title: "Marketplace", icon: "🛍️" },
    { slug: "stock", title: "Stock", icon: "📦" },
    { slug: "delivery", title: "Delivery", icon: "🚚" },
    { slug: "riders", title: "Riders", icon: "🛵" },
    { slug: "services", title: "One Services", icon: "🛠️" },
    { slug: "mobility", title: "Mobility", icon: "🚇" },
    { slug: "jobs", title: "Jobs", icon: "💼" },
    { slug: "erp", title: "ERP", icon: "📊" },
    { slug: "wms", title: "WMS", icon: "🏗️" },
    { slug: "tms", title: "TMS", icon: "🗺️" },
    { slug: "crm", title: "CRM", icon: "🤝" },
    { slug: "bpm", title: "BPM", icon: "⚙️" },
    { slug: "document", title: "GED ECM", icon: "📄" },
    { slug: "hr", title: "HR HCM", icon: "👥" },
    { slug: "health", title: "Health", icon: "🏥" },
    { slug: "vision", title: "Vision", icon: "👁️" },
    { slug: "legal", title: "Legal", icon: "⚖️" },
    { slug: "property", title: "Property", icon: "🏠" },
    { slug: "bi", title: "BI", icon: "📈" },
    { slug: "ai_core", title: "AI Core", icon: "🧠" },
    { slug: "api_hub", title: "API Hub", icon: "🔌" }
];

const Navigation: React.FC = () => {
  return (
    <nav className="side-nav">
      <div className="nav-header">
        <Link to="/" className="logo">All-in-One</Link>
      </div>
      <div className="nav-section">
        <h3>Módulos</h3>
        <ul>
          {modules.map(mod => (
            <li key={mod.slug}>
              <Link to={`/${mod.slug}`}>
                <span className="icon">{mod.icon}</span>
                <span className="title">{mod.title}</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;

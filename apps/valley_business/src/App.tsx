import { useState } from "react";
import { TelemetryDashboard } from "./TelemetryDashboard";
import CalculatorWidget from "./components/CalculatorWidget";
import LedgerTransactionList from "./components/LedgerTransactionList";
import "./index.css";

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div
          className="sidebar-logo"
          style={{
            padding: "24px 20px",
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            borderBottom: "1px solid var(--panel-border)",
          }}
        >
          <img
            src="/assets/brand/all-in-one-logo-transparent.svg"
            alt="All-in-One"
            style={{ width: "100%", maxWidth: "120px", height: "auto" }}
          />
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <img
              src="/assets/brand/valley-logo-transparent.svg"
              alt="Valley"
              style={{ height: "20px", width: "auto" }}
            />
            <span style={{ fontSize: "14px", fontWeight: 800, color: "var(--accent)" }}>
              Business
            </span>
          </div>
        </div>
        <nav className="sidebar-nav">
          <div
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            📊 Visão Geral
          </div>
          <div
            className={`nav-item ${activeTab === "wallet" ? "active" : ""}`}
            onClick={() => setActiveTab("wallet")}
          >
            🪙 Carteira Gold
          </div>
          <div
            className={`nav-item ${activeTab === "offers" ? "active" : ""}`}
            onClick={() => setActiveTab("offers")}
          >
            📦 Catálogo de Ofertas
          </div>
          <div
            className={`nav-item ${activeTab === "pepitas" ? "active" : ""}`}
            onClick={() => setActiveTab("pepitas")}
          >
            ⭐ Concessão de Pepitas
          </div>
          <div
            className={`nav-item ${activeTab === "telemetry" ? "active" : ""}`}
            onClick={() => setActiveTab("telemetry")}
          >
            📡 Telemetria Outbox
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="header">
          <h1>
            {activeTab === "dashboard" && "Visão Geral do Negócio"}
            {activeTab === "wallet" && "Gestão de Valley Gold"}
            {activeTab === "offers" && "Seus Produtos e Serviços"}
            {activeTab === "pepitas" && "Fidelização de Clientes"}
            {activeTab === "telemetry" && "Monitoramento de Telemetria"}
          </h1>
          <div className="wallet-badge">🪙 12.500 V-Gold</div>
        </header>

        {activeTab === "dashboard" && (
          <div className="grid-container">
            <div className="glass-card">
              <h3 className="card-title">Vendas Hoje</h3>
              <p className="metric-value">R$ 1.250,00</p>
              <p style={{ color: "#2ecc71", fontSize: "0.875rem" }}>↑ 15% em relação a ontem</p>
            </div>
            <div className="glass-card">
              <h3 className="card-title">Ofertas Ativas</h3>
              <p className="metric-value">24</p>
              <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
                2 pendentes de aprovação
              </p>
            </div>
            <div className="glass-card">
              <h3 className="card-title">Pepitas Distribuídas</h3>
              <p className="metric-value">3.400</p>
              <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Neste mês</p>
            </div>

            <div
              style={{
                gridColumn: "1 / -1",
                display: "flex",
                justifyContent: "center",
                marginTop: "1rem",
              }}
            >
              <CalculatorWidget />
            </div>
          </div>
        )}

        {activeTab === "wallet" && (
          <div className="grid-container">
            <div className="glass-card" style={{ gridColumn: "1 / -1" }}>
              <h3 className="card-title">Comprar Valley Gold (B2B)</h3>
              <p style={{ color: "var(--text-muted)", marginBottom: "1.5rem" }}>
                O Valley Gold é a reserva de valor necessária para que você possa distribuir
                "Pepitas" aos seus clientes, fomentando a fidelidade.
              </p>
              <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                <input
                  type="number"
                  placeholder="Quantidade de V-Gold"
                  style={{
                    padding: "0.75rem",
                    borderRadius: "8px",
                    border: "1px solid var(--panel-border)",
                    background: "rgba(0,0,0,0.2)",
                    color: "white",
                    flex: 1,
                  }}
                />
                <button className="btn-primary" style={{ width: "auto", marginTop: 0 }}>
                  Gerar Pix Copia e Cola
                </button>
              </div>
            </div>

            <div
              className="glass-card"
              style={{
                gridColumn: "1 / -1",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                background: "transparent",
                boxShadow: "none",
                border: "none",
              }}
            >
              <LedgerTransactionList />
            </div>
          </div>
        )}

        {activeTab === "offers" && (
          <div className="glass-card">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "1rem",
              }}
            >
              <h3 className="card-title" style={{ margin: 0 }}>
                Catálogo (Valley API Hub)
              </h3>
              <button className="btn-primary" style={{ width: "auto", marginTop: 0 }}>
                + Nova Oferta
              </button>
            </div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Tipo</th>
                    <th>Visibilidade</th>
                    <th>Status Publicação</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Corte de Cabelo + Barba</td>
                    <td>Serviço</td>
                    <td>Público (B2C)</td>
                    <td>
                      <span className="status-badge status-active">Publicado no Valley</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Kit Ferramentas Pro</td>
                    <td>Produto</td>
                    <td>Restrito (B2B)</td>
                    <td>
                      <span className="status-badge status-pending">Em Análise</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === "telemetry" && <TelemetryDashboard />}
      </main>
    </div>
  );
}

export default App;

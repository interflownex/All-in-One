import { useState } from "react";
import "./index.css";

function App() {
  const [tab, setTab] = useState("home");
  const [isOnline, setIsOnline] = useState(true);

  return (
    <div className="mobile-container">
      <header
        className="header"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "12px 20px",
          background: "#000",
        }}
      >
        <div className="brand-group" style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <img
            src="/assets/brand/valley-logo-transparent.svg"
            alt="All-in-One"
            style={{ height: "24px", width: "auto" }}
          />
          <div style={{ width: "1px", height: "16px", background: "rgba(255,255,255,0.3)" }}></div>
          <img
            src="/assets/brand/valley-logo-transparent.svg"
            alt="Valley Rider"
            style={{ height: "20px", width: "auto" }}
          />
          <span style={{ fontSize: "12px", fontWeight: 900, color: "var(--accent-rider)" }}>
            RIDER
          </span>
        </div>
        <div
          className="status-toggle"
          onClick={() => setIsOnline(!isOnline)}
          style={{
            background: isOnline ? "rgba(46, 204, 113, 0.1)" : "rgba(231, 76, 60, 0.1)",
            color: isOnline ? "var(--accent-success)" : "#e74c3c",
            borderColor: isOnline ? "var(--accent-success)" : "#e74c3c",
          }}
        >
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: isOnline ? "var(--accent-success)" : "#e74c3c",
            }}
          ></div>
          {isOnline ? "ONLINE" : "OFFLINE"}
        </div>
      </header>

      {tab === "home" && (
        <>
          <div className="map-placeholder">
            <span style={{ position: "relative", zIndex: 1 }}>Mapa Dinâmico (GPS Tracking)</span>
          </div>

          <div className="content-area">
            <h2 className="section-title">Oportunidades</h2>

            {!isOnline ? (
              <div style={{ textAlign: "center", padding: "2rem 0", color: "var(--text-muted)" }}>
                Fique online para receber solicitações de entrega e serviços.
              </div>
            ) : (
              <>
                <div className="job-card">
                  <div className="job-header">
                    <div>
                      <div style={{ fontWeight: 700 }}>Entrega Expressa</div>
                      <div className="job-distance">2.4 km • ~15 min</div>
                    </div>
                    <div className="job-price">R$ 14,50</div>
                  </div>

                  <div className="job-locations">
                    <div className="location-item">
                      <span style={{ color: "var(--accent-rider)" }}>📍</span>
                      <div>
                        <strong>Coleta:</strong> Restaurante Sabor do Vale
                        <div style={{ color: "var(--text-muted)" }}>Rua das Flores, 123</div>
                      </div>
                    </div>
                    <div className="location-item">
                      <span style={{ color: "var(--accent-success)" }}>🏁</span>
                      <div>
                        <strong>Entrega:</strong> Cliente Final
                        <div style={{ color: "var(--text-muted)" }}>
                          Av. Principal, 1000 - Apto 42
                        </div>
                      </div>
                    </div>
                  </div>

                  <button className="btn-accept">Aceitar Corrida</button>
                </div>

                <div className="job-card">
                  <div className="job-header">
                    <div>
                      <div style={{ fontWeight: 700 }}>Serviço de Frete</div>
                      <div className="job-distance">5.8 km • ~30 min</div>
                    </div>
                    <div className="job-price">R$ 45,00</div>
                  </div>
                  <button className="btn-accept" style={{ background: "#333", color: "#fff" }}>
                    Ver Detalhes
                  </button>
                </div>
              </>
            )}
          </div>
        </>
      )}

      {tab === "earnings" && (
        <div className="content-area">
          <h2 className="section-title">Ganhos</h2>
          <div className="job-card" style={{ textAlign: "center", padding: "2rem" }}>
            <div style={{ color: "var(--text-muted)", marginBottom: "0.5rem" }}>Ganhos Hoje</div>
            <div style={{ fontSize: "3rem", fontWeight: 800, color: "var(--accent-success)" }}>
              R$ 124,50
            </div>
            <div style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
              6 Entregas Concluídas
            </div>
          </div>
        </div>
      )}

      {tab === "profile" && (
        <div className="content-area">
          <h2 className="section-title">Perfil do Rider</h2>
          <div className="job-card">
            <div>
              <strong>Nome:</strong> Entregador Parceiro
            </div>
            <div>
              <strong>Veículo:</strong> Moto (Honda CG 160)
            </div>
            <div>
              <strong>Avaliação:</strong> ⭐ 4.98
            </div>
          </div>
        </div>
      )}

      <nav className="bottom-nav">
        <div className={`nav-tab ${tab === "home" ? "active" : ""}`} onClick={() => setTab("home")}>
          🚗
          <br />
          Corridas
        </div>
        <div
          className={`nav-tab ${tab === "earnings" ? "active" : ""}`}
          onClick={() => setTab("earnings")}
        >
          💰
          <br />
          Ganhos
        </div>
        <div
          className={`nav-tab ${tab === "profile" ? "active" : ""}`}
          onClick={() => setTab("profile")}
        >
          👤
          <br />
          Perfil
        </div>
      </nav>
    </div>
  );
}

export default App;

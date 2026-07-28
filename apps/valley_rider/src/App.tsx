import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import "./index.css";

const API_HUB_URL =
  import.meta.env.VITE_API_HUB_URL?.trim() || "https://all-in-one-api-hub.web.app";
const SESSION_KEY = "valley.rider.session.v1";

type RiderSession = {
  token: string;
  userId: string;
  email: string;
};

type DeliveryPayload = {
  service_type?: string;
  origin?: string | Record<string, unknown>;
  destination?: string | Record<string, unknown>;
  quoted_brl?: string | number;
  order_id?: string;
  store_name?: string;
  customer_name?: string;
  distance_km?: number;
  eta_minutes?: number;
};

type DeliveryRequest = {
  id: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  payload: DeliveryPayload;
};

function readSession(): RiderSession | null {
  try {
    const parsed = JSON.parse(window.sessionStorage.getItem(SESSION_KEY) || "null");
    if (parsed?.token && parsed?.userId && parsed?.email) return parsed as RiderSession;
  } catch {
    window.sessionStorage.removeItem(SESSION_KEY);
  }
  return null;
}

function saveSession(session: RiderSession | null) {
  if (session) window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
  else window.sessionStorage.removeItem(SESSION_KEY);
}

function money(value: string | number | undefined) {
  const amount = Number(value || 0);
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
    Number.isFinite(amount) ? amount : 0,
  );
}

function locationLabel(value: DeliveryPayload["origin"]) {
  if (!value) return "Endereço não informado";
  if (typeof value === "string") return value;
  const candidate =
    value.address || value.label || value.formatted_address || value.name || value.description;
  if (typeof candidate === "string" && candidate.trim()) return candidate;
  const lat = value.latitude ?? value.lat;
  const lng = value.longitude ?? value.lng;
  if (lat !== undefined && lng !== undefined) return `${lat}, ${lng}`;
  return "Localização registrada no pedido";
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    created: "Disponível",
    quoted: "Cotada",
    assigned: "Aceita",
    picked_up: "Coletada",
    completed: "Concluída",
    cancelled: "Cancelada",
  };
  return labels[status] || status;
}

async function apiRequest<T>(path: string, session: RiderSession, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_HUB_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${session.token}`,
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...(init?.headers || {}),
    },
  });
  const text = await response.text();
  let body: unknown = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = null;
  }
  if (!response.ok) {
    const detail =
      typeof body === "object" && body && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : `Falha HTTP ${response.status}`;
    throw new Error(detail);
  }
  return body as T;
}

function App() {
  const [tab, setTab] = useState<"home" | "earnings" | "profile">("home");
  const [isOnline, setIsOnline] = useState(true);
  const [session, setSession] = useState<RiderSession | null>(() => readSession());
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [deliveries, setDeliveries] = useState<DeliveryRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [busyId, setBusyId] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadDeliveries = useCallback(async () => {
    if (!session) return;
    setLoading(true);
    setError("");
    try {
      const data = await apiRequest<DeliveryRequest[]>(
        `/delivery/resources/delivery_requests?user_id=${encodeURIComponent(session.userId)}`,
        session,
      );
      setDeliveries(Array.isArray(data) ? data : []);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Falha ao carregar entregas.";
      setError(message);
      if (/token|sess[aã]o|autentic/i.test(message)) {
        saveSession(null);
        setSession(null);
      }
    } finally {
      setLoading(false);
    }
  }, [session]);

  useEffect(() => {
    void loadDeliveries();
  }, [loadDeliveries]);

  useEffect(() => {
    if (!session || !isOnline) return;
    const timer = window.setInterval(() => void loadDeliveries(), 20_000);
    return () => window.clearInterval(timer);
  }, [isOnline, loadDeliveries, session]);

  const activeDeliveries = useMemo(
    () => deliveries.filter((delivery) => !["completed", "cancelled"].includes(delivery.status)),
    [deliveries],
  );
  const completedDeliveries = useMemo(
    () => deliveries.filter((delivery) => delivery.status === "completed"),
    [deliveries],
  );
  const totalEarnings = useMemo(
    () =>
      completedDeliveries.reduce(
        (total, delivery) => total + Number(delivery.payload?.quoted_brl || 0),
        0,
      ),
    [completedDeliveries],
  );

  async function login(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_HUB_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Não foi possível entrar.");
      if (!body.access_token || !body.user_id) throw new Error("O servidor não retornou uma sessão válida.");
      const nextSession = {
        token: String(body.access_token),
        userId: String(body.user_id),
        email: email.trim().toLowerCase(),
      };
      saveSession(nextSession);
      setSession(nextSession);
      setPassword("");
      setNotice("Acesso confirmado. As entregas atribuídas serão atualizadas automaticamente.");
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : "Falha de autenticação.");
    } finally {
      setLoading(false);
    }
  }

  async function transition(delivery: DeliveryRequest, action: "assign" | "pickup" | "complete") {
    if (!session) return;
    setBusyId(delivery.id);
    setError("");
    setNotice("");
    const messages = {
      assign: "Entrega aceita.",
      pickup: "Coleta confirmada.",
      complete: "Entrega concluída e ganho contabilizado.",
    };
    try {
      await apiRequest(
        `/delivery/resources/delivery_requests/${encodeURIComponent(delivery.id)}/actions/${action}`,
        session,
        {
          method: "POST",
          body: JSON.stringify({
            reason: action === "assign" ? "aceite pelo rider" : `atualização ${action} pelo rider`,
            payload: {
              rider_user_id: session.userId,
              rider_email: session.email,
              [`${action}_at`]: new Date().toISOString(),
            },
          }),
        },
      );
      setNotice(messages[action]);
      await loadDeliveries();
    } catch (transitionError) {
      setError(
        transitionError instanceof Error ? transitionError.message : "Não foi possível atualizar a entrega.",
      );
    } finally {
      setBusyId("");
    }
  }

  function logout() {
    saveSession(null);
    setSession(null);
    setDeliveries([]);
    setNotice("");
    setError("");
  }

  if (!session) {
    return (
      <div className="mobile-container">
        <header className="header" style={{ padding: "18px 20px", background: "#000" }}>
          <div className="brand-group" style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <img src="/assets/brand/valley-logo-transparent.svg" alt="Valley" style={{ height: 28 }} />
            <strong style={{ color: "var(--accent-rider)" }}>RIDER</strong>
          </div>
        </header>
        <main className="content-area" style={{ paddingTop: 36 }}>
          <h1 className="section-title">Acesso do entregador</h1>
          <p style={{ color: "var(--text-muted)" }}>
            Entre com a conta aprovada no ecossistema Valley para receber e executar entregas reais.
          </p>
          <form className="job-card" onSubmit={login} style={{ display: "grid", gap: 14 }}>
            <label>
              <span>E-mail</span>
              <input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                style={{ width: "100%", padding: 12, marginTop: 6, boxSizing: "border-box" }}
              />
            </label>
            <label>
              <span>Senha</span>
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                style={{ width: "100%", padding: 12, marginTop: 6, boxSizing: "border-box" }}
              />
            </label>
            {error && <div role="alert" style={{ color: "#ff8f8f" }}>{error}</div>}
            <button className="btn-accept" type="submit" disabled={loading}>
              {loading ? "Validando..." : "Entrar no Valley Rider"}
            </button>
          </form>
        </main>
      </div>
    );
  }

  return (
    <div className="mobile-container">
      <header
        className="header"
        style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 20px", background: "#000" }}
      >
        <div className="brand-group" style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <img src="/assets/brand/valley-logo-transparent.svg" alt="Valley Rider" style={{ height: 24 }} />
          <strong style={{ fontSize: 12, color: "var(--accent-rider)" }}>RIDER</strong>
        </div>
        <button
          type="button"
          className="status-toggle"
          onClick={() => setIsOnline((value) => !value)}
          style={{
            background: isOnline ? "rgba(46, 204, 113, 0.1)" : "rgba(231, 76, 60, 0.1)",
            color: isOnline ? "var(--accent-success)" : "#e74c3c",
            borderColor: isOnline ? "var(--accent-success)" : "#e74c3c",
          }}
        >
          {isOnline ? "ONLINE" : "OFFLINE"}
        </button>
      </header>

      {(error || notice) && (
        <div role={error ? "alert" : "status"} style={{ padding: "12px 20px", color: error ? "#ff8f8f" : "var(--accent-success)" }}>
          {error || notice}
        </div>
      )}

      {tab === "home" && (
        <>
          <div className="map-placeholder">
            <span style={{ position: "relative", zIndex: 1 }}>
              Distribuição ativa • atualização automática a cada 20 segundos
            </span>
          </div>
          <div className="content-area">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <h2 className="section-title">Entregas atribuídas</h2>
              <button type="button" onClick={() => void loadDeliveries()} disabled={loading}>
                {loading ? "Atualizando..." : "Atualizar"}
              </button>
            </div>
            {!isOnline ? (
              <div style={{ textAlign: "center", padding: "2rem 0", color: "var(--text-muted)" }}>
                Você está offline. Fique online para acompanhar novas atribuições.
              </div>
            ) : activeDeliveries.length === 0 ? (
              <div className="job-card" style={{ textAlign: "center" }}>
                Nenhuma entrega atribuída agora. O painel operacional pode distribuir um novo pedido para esta conta.
              </div>
            ) : (
              activeDeliveries.map((delivery) => {
                const payload = delivery.payload || {};
                const nextAction =
                  delivery.status === "created" || delivery.status === "quoted"
                    ? "assign"
                    : delivery.status === "assigned"
                      ? "pickup"
                      : delivery.status === "picked_up"
                        ? "complete"
                        : null;
                const nextLabel =
                  nextAction === "assign"
                    ? "Aceitar entrega"
                    : nextAction === "pickup"
                      ? "Confirmar coleta"
                      : nextAction === "complete"
                        ? "Concluir entrega"
                        : "Aguardar atualização";
                return (
                  <article className="job-card" key={delivery.id}>
                    <div className="job-header">
                      <div>
                        <div style={{ fontWeight: 700 }}>{payload.store_name || payload.service_type || "Entrega Valley"}</div>
                        <div className="job-distance">
                          {statusLabel(delivery.status)}
                          {payload.distance_km ? ` • ${payload.distance_km} km` : ""}
                          {payload.eta_minutes ? ` • ~${payload.eta_minutes} min` : ""}
                        </div>
                      </div>
                      <div className="job-price">{money(payload.quoted_brl)}</div>
                    </div>
                    <div className="job-locations">
                      <div className="location-item">
                        <span style={{ color: "var(--accent-rider)" }}>●</span>
                        <div><strong>Coleta:</strong><div style={{ color: "var(--text-muted)" }}>{locationLabel(payload.origin)}</div></div>
                      </div>
                      <div className="location-item">
                        <span style={{ color: "var(--accent-success)" }}>●</span>
                        <div><strong>Entrega:</strong><div style={{ color: "var(--text-muted)" }}>{locationLabel(payload.destination)}</div></div>
                      </div>
                    </div>
                    {payload.order_id && <small>Pedido vinculado: {payload.order_id}</small>}
                    <button
                      type="button"
                      className="btn-accept"
                      disabled={!nextAction || busyId === delivery.id}
                      onClick={() => nextAction && void transition(delivery, nextAction)}
                    >
                      {busyId === delivery.id ? "Registrando..." : nextLabel}
                    </button>
                  </article>
                );
              })
            )}
          </div>
        </>
      )}

      {tab === "earnings" && (
        <div className="content-area">
          <h2 className="section-title">Ganhos confirmados</h2>
          <div className="job-card" style={{ textAlign: "center", padding: "2rem" }}>
            <div style={{ color: "var(--text-muted)", marginBottom: 8 }}>Total concluído</div>
            <div style={{ fontSize: "3rem", fontWeight: 800, color: "var(--accent-success)" }}>
              {money(totalEarnings)}
            </div>
            <div style={{ color: "var(--text-muted)", marginTop: 8 }}>
              {completedDeliveries.length} entrega(s) concluída(s)
            </div>
          </div>
          {completedDeliveries.map((delivery) => (
            <div className="job-card" key={delivery.id}>
              <strong>{delivery.payload?.store_name || "Entrega Valley"}</strong>
              <div>{money(delivery.payload?.quoted_brl)}</div>
              <small>{delivery.updated_at || delivery.created_at || "Data não informada"}</small>
            </div>
          ))}
        </div>
      )}

      {tab === "profile" && (
        <div className="content-area">
          <h2 className="section-title">Perfil do Rider</h2>
          <div className="job-card">
            <div><strong>Conta:</strong> {session.email}</div>
            <div><strong>ID operacional:</strong> {session.userId}</div>
            <div><strong>API Hub:</strong> conectado</div>
            <button type="button" onClick={logout} style={{ marginTop: 16 }}>Sair desta conta</button>
          </div>
        </div>
      )}

      <nav className="bottom-nav">
        <button className={`nav-tab ${tab === "home" ? "active" : ""}`} onClick={() => setTab("home")}>Entregas</button>
        <button className={`nav-tab ${tab === "earnings" ? "active" : ""}`} onClick={() => setTab("earnings")}>Ganhos</button>
        <button className={`nav-tab ${tab === "profile" ? "active" : ""}`} onClick={() => setTab("profile")}>Perfil</button>
      </nav>
    </div>
  );
}

export default App;

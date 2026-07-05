import { useEffect, useState, type FormEvent } from 'react'
import './index.css'

type TabKey = 'dashboard' | 'corridas' | 'bilhetes' | 'rotas' | 'tarifas'

type GatewayStatus = {
  service?: string
  status?: string
  security?: string
  rate_limit?: string
  routes?: string[]
}

type CommercialInsights = {
  orders_total?: number
  orders_paid?: number
  orders_completed?: number
  reviews_total?: number
  average_rating?: number | null
  support_cases_total?: number
  support_cases_open?: number
  support_cases_resolved?: number
  conversion_rate_percent?: number
  source?: string
}

type ModuleHealth = {
  module?: string
  service?: string
  status?: string
  storage?: string
  version?: string
}

type Ride = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    origin?: string
    destination?: string
    vehicle_type?: string
    rider_name?: string
    fare_brl?: string
    eta?: string
    qr_mode?: string
  }
}

type Ticket = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    route_code?: string
    amount_brl?: string
    qr_token_hash?: string
    mode?: string
    channel?: string
    validity?: string
  }
}

type TransitRoute = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    route_code?: string
    origin?: string
    destination?: string
    transport_mode?: string
    line_name?: string
    duration_minutes?: string
  }
}

type FareRule = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    route_code?: string
    base_fare_brl?: string
    peak_multiplier?: string
    discount_rule?: string
    payment_method?: string
  }
}

type Snapshot = {
  gateway: GatewayStatus
  commercial: CommercialInsights
  moduleHealth: ModuleHealth
  rides: Ride[]
  tickets: Ticket[]
  routes: TransitRoute[]
  fareRules: FareRule[]
}

type RideDraft = {
  origin: string
  destination: string
  vehicle_type: string
  rider_name: string
}

type TicketDraft = {
  route_code: string
  amount_brl: string
  qr_token_hash: string
  mode: string
  channel: string
}

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? 'http://127.0.0.1:8100'
const MOBILITY_URL = import.meta.env.VITE_MOBILITY_URL ?? 'http://127.0.0.1:8106'

const FALLBACK_GATEWAY: GatewayStatus = {
  service: 'api_hub',
  status: 'operational',
  security: 'gateway-signed',
  rate_limit: '60rpm',
  routes: ['/gateway/status', '/gateway/insights/commercial'],
}

const FALLBACK_COMMERCIAL: CommercialInsights = {
  orders_total: 14,
  orders_paid: 11,
  orders_completed: 10,
  reviews_total: 2,
  average_rating: 4.6,
  support_cases_total: 1,
  support_cases_open: 0,
  support_cases_resolved: 1,
  conversion_rate_percent: 21,
  source: 'fallback',
}

const FALLBACK_HEALTH: ModuleHealth = {
  module: 'mobility',
  service: 'mobility',
  status: 'healthy',
  storage: 'postgres',
  version: 'baseline',
}

const FALLBACK_RIDES: Ride[] = [
  {
    id: 'ride-1',
    status: 'accepted',
    created_at: '2026-07-04T09:00:00Z',
    payload: {
      origin: 'Centro, Sao Paulo',
      destination: 'Aeroporto de Congonhas',
      vehicle_type: 'comfort',
      rider_name: 'Marina Costa',
      fare_brl: '48.90',
      eta: '12 min',
      qr_mode: 'nfc',
    },
  },
  {
    id: 'ride-2',
    status: 'completed',
    created_at: '2026-07-04T12:20:00Z',
    payload: {
      origin: 'Campinas',
      destination: 'Shopping local',
      vehicle_type: 'economy',
      rider_name: 'Carlos Lima',
      fare_brl: '26.40',
      eta: '6 min',
      qr_mode: 'qr',
    },
  },
]

const FALLBACK_TICKETS: Ticket[] = [
  {
    id: 'ticket-1',
    status: 'active',
    created_at: '2026-07-04T13:00:00Z',
    payload: {
      route_code: 'MTR-101',
      amount_brl: '9.80',
      qr_token_hash: 'hash-mtr-101',
      mode: 'metro',
      channel: 'qr',
      validity: '90 minutos',
    },
  },
  {
    id: 'ticket-2',
    status: 'used',
    created_at: '2026-07-04T14:00:00Z',
    payload: {
      route_code: 'BUS-221',
      amount_brl: '6.20',
      qr_token_hash: 'hash-bus-221',
      mode: 'bus',
      channel: 'nfc',
      validity: '1 viagem',
    },
  },
]

const FALLBACK_ROUTES: TransitRoute[] = [
  {
    id: 'route-1',
    status: 'available',
    created_at: '2026-07-04T08:00:00Z',
    payload: {
      route_code: 'MTR-101',
      origin: 'Centro',
      destination: 'Zona Sul',
      transport_mode: 'metro',
      line_name: 'Linha Azul',
      duration_minutes: '24',
    },
  },
  {
    id: 'route-2',
    status: 'available',
    created_at: '2026-07-04T08:30:00Z',
    payload: {
      route_code: 'BUS-221',
      origin: 'Centro',
      destination: 'Bairro Industrial',
      transport_mode: 'bus',
      line_name: 'Linha 221',
      duration_minutes: '38',
    },
  },
]

const FALLBACK_FARES: FareRule[] = [
  {
    id: 'fare-1',
    status: 'active',
    created_at: '2026-07-04T08:40:00Z',
    payload: {
      route_code: 'MTR-101',
      base_fare_brl: '9.80',
      peak_multiplier: '1.2',
      discount_rule: 'off_peak_10',
      payment_method: 'qr+nfc',
    },
  },
  {
    id: 'fare-2',
    status: 'active',
    created_at: '2026-07-04T08:50:00Z',
    payload: {
      route_code: 'BUS-221',
      base_fare_brl: '6.20',
      peak_multiplier: '1.1',
      discount_rule: 'student_pass',
      payment_method: 'qr',
    },
  },
]

const TAB_CONTENT: Record<TabKey, { label: string; detail: string }> = {
  dashboard: { label: 'Dashboard', detail: 'mobilidade em tempo real' },
  corridas: { label: 'Corridas', detail: 'solicitar e acompanhar' },
  bilhetes: { label: 'Bilhetes', detail: 'QR e NFC' },
  rotas: { label: 'Rotas', detail: 'linhas e trajetos' },
  tarifas: { label: 'Tarifas', detail: 'preco e regras' },
}

function getStoredActorId() {
  const key = 'all-in-one-mobility.demo-user-id'
  const stored = window.localStorage.getItem(key)
  if (stored) return stored
  const generated = window.crypto.randomUUID()
  window.localStorage.setItem(key, generated)
  return generated
}

function formatDateTime(value?: string | null) {
  if (!value) return 'Sem data'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(parsed)
}

function formatCurrency(value?: string | null) {
  if (!value) return 'Sob consulta'
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return value
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(numeric)
}

function unwrapCollection<T>(payload: unknown, fallback: T[]) {
  if (Array.isArray(payload)) return payload as T[]
  if (payload && typeof payload === 'object') {
    const data = (payload as { data?: T[] }).data
    if (Array.isArray(data) && data.length > 0) return data
  }
  return fallback
}

function mergeHeaders(extra: HeadersInit | undefined, actorId: string) {
  return {
    'Content-Type': 'application/json',
    'X-Actor-User-Id': actorId,
    ...(extra ?? {}),
  }
}

async function fetchJson<T>(url: string, actorId: string, signal: AbortSignal, init: RequestInit = {}) {
  try {
    const response = await fetch(url, {
      ...init,
      signal,
      headers: mergeHeaders(init.headers, actorId),
    })
    if (!response.ok) return null
    return (await response.json()) as T
  } catch {
    return null
  }
}

function buildRideSeed(): RideDraft {
  return {
    origin: 'Centro, Sao Paulo',
    destination: 'Aeroporto de Congonhas',
    vehicle_type: 'comfort',
    rider_name: 'Pessoa Demo',
  }
}

function buildTicketSeed(): TicketDraft {
  return {
    route_code: 'MTR-101',
    amount_brl: '9.80',
    qr_token_hash: 'demo-qr-hash',
    mode: 'metro',
    channel: 'qr',
  }
}

export default function App() {
  const actorId = getStoredActorId()
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard')
  const [search, setSearch] = useState('')
  const [snapshot, setSnapshot] = useState<Snapshot>({
    gateway: FALLBACK_GATEWAY,
    commercial: FALLBACK_COMMERCIAL,
    moduleHealth: FALLBACK_HEALTH,
    rides: FALLBACK_RIDES,
    tickets: FALLBACK_TICKETS,
    routes: FALLBACK_ROUTES,
    fareRules: FALLBACK_FARES,
  })
  const [statusMessage, setStatusMessage] = useState<string | null>(null)
  const [statusError, setStatusError] = useState<string | null>(null)
  const [rideSubmitting, setRideSubmitting] = useState(false)
  const [ticketSubmitting, setTicketSubmitting] = useState(false)
  const [rideDraft, setRideDraft] = useState<RideDraft>(buildRideSeed())
  const [ticketDraft, setTicketDraft] = useState<TicketDraft>(buildTicketSeed())

  useEffect(() => {
    const controller = new AbortController()

    async function load() {
      const [gateway, commercial, moduleHealth, rides, tickets, routes, fareRules] = await Promise.all([
        fetchJson<GatewayStatus>(`${API_HUB_URL}/gateway/status`, actorId, controller.signal),
        fetchJson<CommercialInsights>(`${API_HUB_URL}/gateway/insights/commercial`, actorId, controller.signal),
        fetchJson<ModuleHealth>(`${MOBILITY_URL}/health`, actorId, controller.signal),
        fetchJson<unknown>(`${MOBILITY_URL}/resources/rides`, actorId, controller.signal),
        fetchJson<unknown>(`${MOBILITY_URL}/resources/tickets`, actorId, controller.signal),
        fetchJson<unknown>(`${MOBILITY_URL}/resources/routes`, actorId, controller.signal),
        fetchJson<unknown>(`${MOBILITY_URL}/resources/fare_rules`, actorId, controller.signal),
      ])

      const routeList = unwrapCollection(routes, FALLBACK_ROUTES)
      setSnapshot({
        gateway: gateway ?? FALLBACK_GATEWAY,
        commercial: commercial ?? FALLBACK_COMMERCIAL,
        moduleHealth: moduleHealth ?? FALLBACK_HEALTH,
        rides: unwrapCollection(rides, FALLBACK_RIDES),
        tickets: unwrapCollection(tickets, FALLBACK_TICKETS),
        routes: routeList,
        fareRules: unwrapCollection(fareRules, FALLBACK_FARES),
      })
      setTicketDraft((current) => (current.route_code ? current : { ...buildTicketSeed(), route_code: routeList[0]?.payload?.route_code ?? 'MTR-101' }))
    }

    void load()
    return () => controller.abort()
  }, [actorId])

  const query = search.trim().toLowerCase()
  const filteredRides = snapshot.rides.filter((item) => {
    const haystack = [
      item.id,
      item.status,
      item.payload?.origin,
      item.payload?.destination,
      item.payload?.vehicle_type,
      item.payload?.rider_name,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return !query || haystack.includes(query)
  })
  const filteredTickets = snapshot.tickets.filter((item) => {
    const haystack = [
      item.id,
      item.status,
      item.payload?.route_code,
      item.payload?.mode,
      item.payload?.channel,
      item.payload?.validity,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return !query || haystack.includes(query)
  })
  const filteredRoutes = snapshot.routes.filter((item) => {
    const haystack = [
      item.id,
      item.status,
      item.payload?.route_code,
      item.payload?.origin,
      item.payload?.destination,
      item.payload?.transport_mode,
      item.payload?.line_name,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return !query || haystack.includes(query)
  })
  const filteredFares = snapshot.fareRules.filter((item) => {
    const haystack = [
      item.id,
      item.status,
      item.payload?.route_code,
      item.payload?.discount_rule,
      item.payload?.payment_method,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return !query || haystack.includes(query)
  })

  async function handleRideSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setRideSubmitting(true)
    setStatusMessage(null)
    setStatusError(null)

    try {
      const response = await fetch(`${MOBILITY_URL}/resources/rides`, {
        method: 'POST',
        headers: mergeHeaders(undefined, actorId),
        body: JSON.stringify({
          user_id: actorId,
          payload: rideDraft,
        }),
      })

      if (!response.ok) {
        throw new Error('Nao foi possivel solicitar a corrida.')
      }

      const payload = (await response.json()) as { id?: string; status?: string }
      setStatusMessage(`Corrida solicitada com sucesso${payload.id ? `: ${payload.id}` : ''}.`)
      setActiveTab('corridas')
    } catch (error) {
      setStatusError(error instanceof Error ? error.message : 'Falha inesperada ao solicitar corrida.')
    } finally {
      setRideSubmitting(false)
    }
  }

  async function handleTicketSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setTicketSubmitting(true)
    setStatusMessage(null)
    setStatusError(null)

    try {
      const response = await fetch(`${MOBILITY_URL}/resources/tickets`, {
        method: 'POST',
        headers: mergeHeaders(undefined, actorId),
        body: JSON.stringify({
          user_id: actorId,
          payload: ticketDraft,
        }),
      })

      if (!response.ok) {
        throw new Error('Nao foi possivel emitir o bilhete.')
      }

      const payload = (await response.json()) as { id?: string; status?: string }
      setStatusMessage(`Bilhete emitido com sucesso${payload.id ? `: ${payload.id}` : ''}.`)
      setActiveTab('bilhetes')
    } catch (error) {
      setStatusError(error instanceof Error ? error.message : 'Falha inesperada ao emitir bilhete.')
    } finally {
      setTicketSubmitting(false)
    }
  }

  return (
    <div className="mobility-shell">
      <aside className="mobility-sidebar">
        <div className="brand-block">
          <div className="brand-mark">M</div>
          <div>
            <div className="brand-name">All-in-One Mobility</div>
            <div className="brand-subtitle">corridas, tickets e rotas</div>
          </div>
        </div>

        <div className="gateway-chip">
          <span className="status-dot" />
          <div>
            <strong>{snapshot.gateway.security ?? 'gateway-signed'}</strong>
            <p>
              {snapshot.gateway.status ?? 'operacional'} • {snapshot.moduleHealth.storage ?? 'postgres'}
            </p>
          </div>
        </div>

        <nav className="nav-stack" aria-label="Secoes do Mobility">
          {(Object.keys(TAB_CONTENT) as TabKey[]).map((key) => (
            <button
              key={key}
              type="button"
              className={`nav-pill ${activeTab === key ? 'active' : ''}`}
              onClick={() => setActiveTab(key)}
            >
              <strong>{TAB_CONTENT[key].label}</strong>
              <span>{TAB_CONTENT[key].detail}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-note">
          <strong>Mobilidade conectada</strong>
          <p>
            O shell Mobility usa o mesmo identificador demo persistente e conversa com o API Hub
            e o runtime do modulo para corridas, bilhetes e regras tarifarias.
          </p>
        </div>
      </aside>

      <main className="mobility-main">
        <section className="hero-panel">
          <div>
            <span className="eyebrow">Movimento urbano em tempo real</span>
            <h1>Corridas, tickets e tarifas com leitura rapida de rota.</h1>
            <p className="hero-copy">
              O app Mobility cruza a camada do API Hub com os recursos do modulo para exibir
              corridas, bilhetes QR/NFC, rotas e precificacao com fallback visual de demo.
            </p>
          </div>

          <div className="hero-side">
            <div className="search-box">
              <span>Buscar corrida, bilhete ou rota</span>
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Ex.: Aeroporto, MTR-101, NFC"
              />
            </div>

            <div className="hero-status">
              <div>
                <span className="muted">Rede urbana</span>
                <strong>{snapshot.moduleHealth.status ?? 'healthy'}</strong>
              </div>
              <div>
                <span className="muted">Conversao comercial</span>
                <strong>{snapshot.commercial.conversion_rate_percent ?? 0}%</strong>
              </div>
            </div>
          </div>
        </section>

        {statusMessage ? <div className="success-box">{statusMessage}</div> : null}
        {statusError ? <div className="warning-box">{statusError}</div> : null}

        <section className="metric-grid">
          <article className="metric-card highlight">
            <span>Corridas visiveis</span>
            <strong>{filteredRides.length}</strong>
            <small>
              {snapshot.moduleHealth.version ?? 'baseline'} • {snapshot.moduleHealth.storage ?? 'postgres'}
            </small>
          </article>
          <article className="metric-card">
            <span>Bilhetes ativos</span>
            <strong>{filteredTickets.length}</strong>
            <small>QR e NFC integrados</small>
          </article>
          <article className="metric-card">
            <span>Rotas publicadas</span>
            <strong>{filteredRoutes.length}</strong>
            <small>mapa urbano e transporte</small>
          </article>
          <article className="metric-card">
            <span>Tarifas ativas</span>
            <strong>{filteredFares.length}</strong>
            <small>regras e descontos</small>
          </article>
          <article className="metric-card">
            <span>Gateway</span>
            <strong>{snapshot.gateway.status ?? 'operational'}</strong>
            <small>{snapshot.gateway.rate_limit ?? '60rpm'}</small>
          </article>
        </section>

        <section className="content-grid">
          {activeTab === 'dashboard' ? (
            <>
              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Fluxo urbano</span>
                    <h2>Corridas ativas e tempo estimado</h2>
                  </div>
                  <span className="section-note">Fonte {snapshot.gateway.service ?? 'api_hub'}</span>
                </div>
                <div className="timeline">
                  {filteredRides.slice(0, 3).map((ride) => (
                    <div key={ride.id} className="timeline-item">
                      <span className="timeline-time">{formatDateTime(ride.created_at)}</span>
                      <div>
                        <strong>
                          {ride.payload?.origin ?? 'Origem'} → {ride.payload?.destination ?? 'Destino'}
                        </strong>
                        <p>
                          {ride.payload?.vehicle_type ?? 'economy'} • {ride.payload?.eta ?? '10 min'}
                        </p>
                        <small>{ride.payload?.rider_name ?? ride.id}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </article>

              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Mobilidade digital</span>
                    <h2>QR, NFC e precificacao</h2>
                  </div>
                </div>
                <div className="insight-stack">
                  <div className="insight-row">
                    <span>Ordens pagas</span>
                    <strong>{snapshot.commercial.orders_paid ?? 0}</strong>
                  </div>
                  <div className="insight-row">
                    <span>Avaliacao media</span>
                    <strong>{snapshot.commercial.average_rating ?? 0}</strong>
                  </div>
                  <div className="insight-row">
                    <span>Tickets usados</span>
                    <strong>{filteredTickets.filter((ticket) => ticket.status === 'used').length}</strong>
                  </div>
                </div>
              </article>
            </>
          ) : null}

          {activeTab === 'corridas' ? (
            <>
              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Nova corrida</span>
                    <h2>Solicitar viagem urbana</h2>
                  </div>
                </div>
                <form className="stack-form" onSubmit={handleRideSubmit}>
                  <label>
                    <span>Origem</span>
                    <input
                      value={rideDraft.origin}
                      onChange={(event) => setRideDraft((current) => ({ ...current, origin: event.target.value }))}
                      placeholder="Centro, Sao Paulo"
                    />
                  </label>
                  <label>
                    <span>Destino</span>
                    <input
                      value={rideDraft.destination}
                      onChange={(event) =>
                        setRideDraft((current) => ({ ...current, destination: event.target.value }))
                      }
                      placeholder="Aeroporto de Congonhas"
                    />
                  </label>
                  <label>
                    <span>Tipo de veiculo</span>
                    <input
                      value={rideDraft.vehicle_type}
                      onChange={(event) =>
                        setRideDraft((current) => ({ ...current, vehicle_type: event.target.value }))
                      }
                      placeholder="comfort"
                    />
                  </label>
                  <label>
                    <span>Nome do passageiro</span>
                    <input
                      value={rideDraft.rider_name}
                      onChange={(event) =>
                        setRideDraft((current) => ({ ...current, rider_name: event.target.value }))
                      }
                      placeholder="Pessoa Demo"
                    />
                  </label>
                  <button type="submit" className="primary-button" disabled={rideSubmitting}>
                    {rideSubmitting ? 'Solicitando...' : 'Solicitar corrida'}
                  </button>
                </form>
              </article>

              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Corridas vivas</span>
                    <h2>Status de deslocamento</h2>
                  </div>
                </div>
                <div className="card-grid">
                  {filteredRides.map((ride) => (
                    <div key={ride.id} className="info-card">
                      <span>{ride.status ?? 'requested'}</span>
                      <strong>{ride.payload?.rider_name ?? ride.id}</strong>
                      <p>
                        {ride.payload?.origin ?? 'Origem'} → {ride.payload?.destination ?? 'Destino'}
                      </p>
                      <small>{ride.payload?.vehicle_type ?? 'economy'} • {ride.payload?.eta ?? '10 min'}</small>
                      <small>{formatCurrency(ride.payload?.fare_brl)}</small>
                    </div>
                  ))}
                </div>
              </article>
            </>
          ) : null}

          {activeTab === 'bilhetes' ? (
            <>
              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Novo bilhete</span>
                    <h2>Emitir QR ou NFC</h2>
                  </div>
                </div>
                <form className="stack-form" onSubmit={handleTicketSubmit}>
                  <label>
                    <span>Codigo da rota</span>
                    <input
                      value={ticketDraft.route_code}
                      onChange={(event) =>
                        setTicketDraft((current) => ({ ...current, route_code: event.target.value }))
                      }
                      placeholder="MTR-101"
                    />
                  </label>
                  <label>
                    <span>Valor</span>
                    <input
                      value={ticketDraft.amount_brl}
                      onChange={(event) =>
                        setTicketDraft((current) => ({ ...current, amount_brl: event.target.value }))
                      }
                      placeholder="9.80"
                    />
                  </label>
                  <label>
                    <span>Hash QR</span>
                    <input
                      value={ticketDraft.qr_token_hash}
                      onChange={(event) =>
                        setTicketDraft((current) => ({ ...current, qr_token_hash: event.target.value }))
                      }
                      placeholder="demo-qr-hash"
                    />
                  </label>
                  <label>
                    <span>Canal</span>
                    <input
                      value={ticketDraft.channel}
                      onChange={(event) =>
                        setTicketDraft((current) => ({ ...current, channel: event.target.value }))
                      }
                      placeholder="qr"
                    />
                  </label>
                  <button type="submit" className="primary-button" disabled={ticketSubmitting}>
                    {ticketSubmitting ? 'Emitindo...' : 'Emitir bilhete'}
                  </button>
                </form>
              </article>

              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Bilhetes e acessos</span>
                    <h2>QR, NFC e validade</h2>
                  </div>
                </div>
                <div className="card-grid">
                  {filteredTickets.map((ticket) => (
                    <div key={ticket.id} className="info-card accent">
                      <span>{ticket.status ?? 'active'}</span>
                      <strong>{ticket.payload?.route_code ?? ticket.id}</strong>
                      <p>{formatCurrency(ticket.payload?.amount_brl)}</p>
                      <small>{ticket.payload?.mode ?? 'transporte'}</small>
                      <small>{ticket.payload?.channel ?? 'qr'} • {ticket.payload?.validity ?? '90 minutos'}</small>
                    </div>
                  ))}
                </div>
              </article>
            </>
          ) : null}

          {activeTab === 'rotas' ? (
            <article className="content-card span-two">
              <div className="section-head">
                <div>
                  <span className="section-label">Mapeamento urbano</span>
                  <h2>Rotas e trajetos disponiveis</h2>
                </div>
                <span className="section-note">Linhas publicadas pelo modulo Mobility</span>
              </div>
              <div className="card-grid">
                {filteredRoutes.map((route) => (
                  <div key={route.id} className="route-card">
                    <span>{route.payload?.transport_mode ?? 'route'}</span>
                    <strong>{route.payload?.route_code ?? route.id}</strong>
                    <p>
                      {route.payload?.origin ?? 'Origem'} → {route.payload?.destination ?? 'Destino'}
                    </p>
                    <small>{route.payload?.line_name ?? 'Linha urbana'}</small>
                    <small>{route.payload?.duration_minutes ?? '30'} min</small>
                  </div>
                ))}
              </div>
            </article>
          ) : null}

          {activeTab === 'tarifas' ? (
            <>
              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Precificacao</span>
                    <h2>Tarifas e regras ativas</h2>
                  </div>
                </div>
                <div className="card-grid">
                  {filteredFares.map((fare) => (
                    <div key={fare.id} className="fare-card">
                      <span>{fare.status ?? 'active'}</span>
                      <strong>{fare.payload?.route_code ?? fare.id}</strong>
                      <p>{formatCurrency(fare.payload?.base_fare_brl)}</p>
                      <small>Multiplicador pico: {fare.payload?.peak_multiplier ?? '1.0'}</small>
                      <small>Desconto: {fare.payload?.discount_rule ?? 'none'}</small>
                    </div>
                  ))}
                </div>
              </article>

              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Contexto ativo</span>
                    <h2>Token e canal persistentes</h2>
                  </div>
                </div>
                <div className="stack-note">
                  <strong>{actorId}</strong>
                  <p>
                    O shell Mobility persiste um UUID demo no navegador e envia o cabeçalho
                    X-Actor-User-Id em todas as chamadas ao backend.
                  </p>
                </div>
              </article>
            </>
          ) : null}
        </section>
      </main>
    </div>
  )
}

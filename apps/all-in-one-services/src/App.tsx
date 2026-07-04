import { useEffect, useState } from 'react'
import './index.css'

type TabKey = 'dashboard' | 'prestadores' | 'visitas' | 'orcamentos' | 'contratos' | 'evidencias'

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
  crm_records?: number
  bi_records?: number
  source?: string
}

type ServiceProvider = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    category?: string
    name?: string
    service_area?: string
    city?: string
    rating?: string
    verified?: boolean
    provider_type?: string
  }
}

type ServiceVisit = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    provider_id?: string
    scheduled_at?: string
    visit_price_brl?: string
    customer_name?: string
    service_type?: string
  }
}

type ServiceQuote = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    provider_id?: string
    service_type?: string
    quoted_brl?: string
    visit_price_brl?: string
  }
}

type ServiceContract = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    provider_id?: string
    contracted_price_brl?: string
    visit_price_brl?: string
    stage?: string
  }
}

type ServiceEvidence = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    kind?: string
    note?: string
    hash?: string
  }
}

type ModuleHealth = {
  module?: string
  service?: string
  status?: string
  storage?: string
  version?: string
}

type TimeSlotsResponse = {
  provider_id?: string
  date?: string
  available_slots?: string[]
}

type ReservationResponse = {
  status?: string
  provider_id?: string
  slot?: string
  customer_id?: string
  reservation_id?: string
}

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? 'http://127.0.0.1:8100'
const SERVICES_URL = import.meta.env.VITE_SERVICES_URL ?? 'http://127.0.0.1:8105'
const IDENTITY_URL = import.meta.env.VITE_IDENTITY_URL ?? 'http://127.0.0.1:8101'

const FALLBACK_PROVIDERS: ServiceProvider[] = [
  {
    id: 'provider-1',
    status: 'approved',
    created_at: '2026-07-04T00:00:00Z',
    payload: {
      category: 'assistencia tecnica',
      name: 'Solar Care',
      service_area: 'campo e cidade',
      city: 'Sao Paulo',
      rating: '4.9',
      verified: true,
    },
  },
  {
    id: 'provider-2',
    status: 'pending_review',
    created_at: '2026-07-04T00:00:00Z',
    payload: {
      category: 'instalacao',
      name: 'Prime Services',
      service_area: 'hibrido',
      city: 'Campinas',
      rating: '4.7',
      verified: false,
    },
  },
]

const FALLBACK_VISITS: ServiceVisit[] = [
  {
    id: 'visit-1',
    status: 'confirmed',
    created_at: '2026-07-04T08:00:00Z',
    payload: {
      provider_id: 'provider-1',
      service_type: 'visita tecnica',
      scheduled_at: '2026-07-05T14:00:00Z',
      visit_price_brl: '180.00',
      customer_name: 'Cliente Demo',
    },
  },
]

const FALLBACK_QUOTES: ServiceQuote[] = [
  {
    id: 'quote-1',
    status: 'created',
    created_at: '2026-07-04T09:00:00Z',
    payload: {
      provider_id: 'provider-1',
      service_type: 'orcamento rapido',
      quoted_brl: '320.00',
    },
  },
]

const FALLBACK_CONTRACTS: ServiceContract[] = [
  {
    id: 'contract-1',
    status: 'held',
    created_at: '2026-07-04T10:00:00Z',
    payload: {
      provider_id: 'provider-1',
      visit_price_brl: '180.00',
      contracted_price_brl: '320.00',
      stage: 'avaliacao',
    },
  },
]

const FALLBACK_EVIDENCE: ServiceEvidence[] = [
  {
    id: 'evidence-1',
    status: 'accepted',
    created_at: '2026-07-04T11:00:00Z',
    payload: {
      kind: 'photo',
      note: 'Evidencia de servico anexada ao contrato',
    },
  },
]

const FALLBACK_SLOTS = ['09:00', '11:30', '14:00', '15:30']

function getStoredUserId() {
  const key = 'all-in-one-services.demo-user-id'
  const stored = window.localStorage.getItem(key)
  if (stored) return stored
  const generated = window.crypto.randomUUID()
  window.localStorage.setItem(key, generated)
  return generated
}

function formatMoney(value?: string | null) {
  if (!value) return 'Sob consulta'
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return value
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(numeric)
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(new Date(value))
}

function formatDate(value?: string) {
  if (!value) return 'agora'
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(value))
}

function pickList<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) return payload as T[]
  if (payload && typeof payload === 'object') {
    const candidate = (payload as { data?: unknown }).data
    if (Array.isArray(candidate)) return candidate as T[]
  }
  return []
}

function metricValue(value: number | string | null | undefined) {
  if (value === null || value === undefined) return '0'
  return typeof value === 'number' ? value.toLocaleString('pt-BR') : value
}

function App() {
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard')
  const [userId] = useState(getStoredUserId)
  const [query, setQuery] = useState('')
  const [lastSyncedAt, setLastSyncedAt] = useState('')
  const [loadError, setLoadError] = useState('')
  const [gatewayStatus, setGatewayStatus] = useState<GatewayStatus | null>(null)
  const [commercialInsights, setCommercialInsights] = useState<CommercialInsights | null>(null)
  const [providers, setProviders] = useState<ServiceProvider[]>([])
  const [visits, setVisits] = useState<ServiceVisit[]>([])
  const [quotes, setQuotes] = useState<ServiceQuote[]>([])
  const [contracts, setContracts] = useState<ServiceContract[]>([])
  const [evidence, setEvidence] = useState<ServiceEvidence[]>([])
  const [servicesHealth, setServicesHealth] = useState<ModuleHealth | null>(null)
  const [identityHealth, setIdentityHealth] = useState<ModuleHealth | null>(null)
  const [selectedProviderId, setSelectedProviderId] = useState(FALLBACK_PROVIDERS[0].id)
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [availableSlots, setAvailableSlots] = useState<string[]>(FALLBACK_SLOTS)
  const [chosenSlot, setChosenSlot] = useState(FALLBACK_SLOTS[0])
  const [slotLoading, setSlotLoading] = useState(false)
  const [slotError, setSlotError] = useState('')
  const [reservationLoading, setReservationLoading] = useState(false)
  const [reservationMessage, setReservationMessage] = useState('')
  const [reservationError, setReservationError] = useState('')

  useEffect(() => {
    let cancelled = false

    const loadFeed = async () => {
      const headers = { 'X-Actor-User-Id': userId }
      const [
        gatewayResult,
        insightsResult,
        providersResult,
        visitsResult,
        quotesResult,
        contractsResult,
        evidenceResult,
        servicesHealthResult,
        identityHealthResult,
      ] = await Promise.allSettled([
        fetch(`${API_HUB_URL}/gateway/status`).then(async response => {
          if (!response.ok) throw new Error(`Gateway indisponivel (${response.status})`)
          return response.json() as Promise<GatewayStatus>
        }),
        fetch(`${API_HUB_URL}/gateway/insights/commercial`).then(async response => {
          if (!response.ok) throw new Error(`Indicadores comerciais indisponiveis (${response.status})`)
          return response.json() as Promise<CommercialInsights>
        }),
        fetch(`${SERVICES_URL}/resources/providers`, { headers }).then(async response => {
          if (!response.ok) throw new Error(`Prestadores indisponiveis (${response.status})`)
          return pickList<ServiceProvider>(await response.json())
        }),
        fetch(`${SERVICES_URL}/resources/visits`, { headers }).then(async response => {
          if (!response.ok) throw new Error(`Visitas indisponiveis (${response.status})`)
          return pickList<ServiceVisit>(await response.json())
        }),
        fetch(`${SERVICES_URL}/resources/quotes`, { headers }).then(async response => {
          if (!response.ok) throw new Error(`Orcamentos indisponiveis (${response.status})`)
          return pickList<ServiceQuote>(await response.json())
        }),
        fetch(`${SERVICES_URL}/resources/service_contracts`, { headers }).then(async response => {
          if (!response.ok) throw new Error(`Contratos indisponiveis (${response.status})`)
          return pickList<ServiceContract>(await response.json())
        }),
        fetch(`${SERVICES_URL}/resources/evidence`, { headers }).then(async response => {
          if (!response.ok) throw new Error(`Evidencias indisponiveis (${response.status})`)
          return pickList<ServiceEvidence>(await response.json())
        }),
        fetch(`${SERVICES_URL}/health`).then(async response => {
          if (!response.ok) throw new Error(`Health de Services indisponivel (${response.status})`)
          return response.json() as Promise<ModuleHealth>
        }),
        fetch(`${IDENTITY_URL}/health`).then(async response => {
          if (!response.ok) throw new Error(`Health de Identity indisponivel (${response.status})`)
          return response.json() as Promise<ModuleHealth>
        }),
      ])

      if (cancelled) return

      const errors: string[] = []

      if (gatewayResult.status === 'fulfilled') setGatewayStatus(gatewayResult.value)
      else errors.push(gatewayResult.reason instanceof Error ? gatewayResult.reason.message : String(gatewayResult.reason))

      if (insightsResult.status === 'fulfilled') setCommercialInsights(insightsResult.value)
      else errors.push(insightsResult.reason instanceof Error ? insightsResult.reason.message : String(insightsResult.reason))

      if (providersResult.status === 'fulfilled') setProviders(providersResult.value)
      else errors.push(providersResult.reason instanceof Error ? providersResult.reason.message : String(providersResult.reason))

      if (visitsResult.status === 'fulfilled') setVisits(visitsResult.value)
      else errors.push(visitsResult.reason instanceof Error ? visitsResult.reason.message : String(visitsResult.reason))

      if (quotesResult.status === 'fulfilled') setQuotes(quotesResult.value)
      else errors.push(quotesResult.reason instanceof Error ? quotesResult.reason.message : String(quotesResult.reason))

      if (contractsResult.status === 'fulfilled') setContracts(contractsResult.value)
      else errors.push(contractsResult.reason instanceof Error ? contractsResult.reason.message : String(contractsResult.reason))

      if (evidenceResult.status === 'fulfilled') setEvidence(evidenceResult.value)
      else errors.push(evidenceResult.reason instanceof Error ? evidenceResult.reason.message : String(evidenceResult.reason))

      if (servicesHealthResult.status === 'fulfilled') setServicesHealth(servicesHealthResult.value)
      else errors.push(servicesHealthResult.reason instanceof Error ? servicesHealthResult.reason.message : String(servicesHealthResult.reason))

      if (identityHealthResult.status === 'fulfilled') setIdentityHealth(identityHealthResult.value)
      else errors.push(identityHealthResult.reason instanceof Error ? identityHealthResult.reason.message : String(identityHealthResult.reason))

      setLoadError(errors.length > 0 ? errors.join(' • ') : '')
      setLastSyncedAt(
        new Intl.DateTimeFormat('pt-BR', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }).format(new Date()),
      )
    }

    loadFeed()
    const interval = window.setInterval(loadFeed, 30000)
    return () => {
      cancelled = true
      window.clearInterval(interval)
    }
  }, [userId])

  useEffect(() => {
    if (!providers.length) return
    if (providers.some(provider => provider.id === selectedProviderId)) return
    setSelectedProviderId(providers[0].id)
  }, [providers, selectedProviderId])

  useEffect(() => {
    if (!selectedProviderId) return

    let cancelled = false
    const loadSlots = async () => {
      setSlotLoading(true)
      setSlotError('')
      try {
        const response = await fetch(
          `${SERVICES_URL}/providers/${selectedProviderId}/time-slots?date=${encodeURIComponent(selectedDate)}`,
        )
        if (!response.ok) throw new Error(`Slots indisponiveis (${response.status})`)
        const payload = (await response.json()) as TimeSlotsResponse
        if (cancelled) return
        const slots = payload.available_slots && payload.available_slots.length > 0 ? payload.available_slots : FALLBACK_SLOTS
        setAvailableSlots(slots)
        setChosenSlot(current => (slots.includes(current) ? current : slots[0] ?? ''))
      } catch (error) {
        if (!cancelled) {
          setAvailableSlots(FALLBACK_SLOTS)
          setChosenSlot(current => (FALLBACK_SLOTS.includes(current) ? current : FALLBACK_SLOTS[0]))
          setSlotError(error instanceof Error ? error.message : String(error))
        }
      } finally {
        if (!cancelled) setSlotLoading(false)
      }
    }

    loadSlots()
    return () => {
      cancelled = true
    }
  }, [selectedProviderId, selectedDate])

  const liveProviders = providers.length > 0 ? providers : FALLBACK_PROVIDERS
  const liveVisits = visits.length > 0 ? visits : FALLBACK_VISITS
  const liveQuotes = quotes.length > 0 ? quotes : FALLBACK_QUOTES
  const liveContracts = contracts.length > 0 ? contracts : FALLBACK_CONTRACTS
  const liveEvidence = evidence.length > 0 ? evidence : FALLBACK_EVIDENCE

  const search = query.trim().toLowerCase()

  const filteredProviders = search
    ? liveProviders.filter(provider =>
        [provider.payload?.name, provider.payload?.category, provider.payload?.service_area, provider.payload?.city, provider.status]
          .filter((value): value is string => typeof value === 'string')
          .some(value => value.toLowerCase().includes(search)),
      )
    : liveProviders

  const filteredVisits = search
    ? liveVisits.filter(visit =>
        [visit.payload?.customer_name, visit.payload?.service_type, visit.payload?.scheduled_at, visit.status]
          .filter((value): value is string => typeof value === 'string')
          .some(value => value.toLowerCase().includes(search)),
      )
    : liveVisits

  const filteredQuotes = search
    ? liveQuotes.filter(quote =>
        [quote.payload?.service_type, quote.payload?.quoted_brl, quote.status]
          .filter((value): value is string => typeof value === 'string')
          .some(value => value.toLowerCase().includes(search)),
      )
    : liveQuotes

  const filteredContracts = search
    ? liveContracts.filter(contract =>
        [contract.payload?.contracted_price_brl, contract.payload?.visit_price_brl, contract.payload?.stage, contract.status]
          .filter((value): value is string => typeof value === 'string')
          .some(value => value.toLowerCase().includes(search)),
      )
    : liveContracts

  const filteredEvidence = search
    ? liveEvidence.filter(item =>
        [item.payload?.kind, item.payload?.note, item.status]
          .filter((value): value is string => typeof value === 'string')
          .some(value => value.toLowerCase().includes(search)),
      )
    : liveEvidence

  const currentProvider = liveProviders.find(provider => provider.id === selectedProviderId) ?? liveProviders[0]

  const navItems: Array<{ key: TabKey; label: string; description: string }> = [
    { key: 'dashboard', label: 'Dashboard', description: 'Agenda e visao geral' },
    { key: 'prestadores', label: 'Prestadores', description: 'Cadastro e agenda' },
    { key: 'visitas', label: 'Visitas', description: 'Atendimentos e visitas' },
    { key: 'orcamentos', label: 'Orcamentos', description: 'Propostas comerciais' },
    { key: 'contratos', label: 'Contratos', description: 'Acordos e estagios' },
    { key: 'evidencias', label: 'Evidencias', description: 'Anexos e auditoria' },
  ]

  const handleReserve = async () => {
    if (!selectedProviderId || !chosenSlot) return
    setReservationLoading(true)
    setReservationError('')
    setReservationMessage('')

    try {
      const response = await fetch(`${SERVICES_URL}/providers/${selectedProviderId}/reserve-slot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          slot: chosenSlot,
          customer_id: userId,
        }),
      })
      if (!response.ok) {
        const detail = await response.text()
        throw new Error(detail || `Reserva indisponivel (${response.status})`)
      }
      const result = (await response.json()) as ReservationResponse
      setReservationMessage(
        `Reserva confirmada: ${result.reservation_id ?? 'sem id'} em ${result.slot ?? chosenSlot}`,
      )
    } catch (error) {
      setReservationError(error instanceof Error ? error.message : String(error))
    } finally {
      setReservationLoading(false)
    }
  }

  return (
    <div className="services-app-shell">
      <aside className="side-panel">
        <div className="brand-block">
          <div className="brand-mark">SV</div>
          <div>
            <div className="brand-name">All-in-One Services</div>
            <div className="brand-subtitle">Prestadores, orcamentos e contratos</div>
          </div>
        </div>

        <div className="status-chip">
          <span className="status-dot" />
          Sincronizado {lastSyncedAt || 'agora'}
        </div>

        <nav className="nav-stack">
          {navItems.map(item => (
            <button
              key={item.key}
              type="button"
              className={`nav-pill ${activeTab === item.key ? 'active' : ''}`}
              onClick={() => setActiveTab(item.key)}
            >
              <strong>{item.label}</strong>
              <span>{item.description}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-panel">
        <header className="hero-panel">
          <div>
            <p className="eyebrow">All-in-One Services</p>
            <h1>{activeTab === 'dashboard' ? 'Operacao de servicos em tempo real' : navItems.find(item => item.key === activeTab)?.label}</h1>
            <p className="hero-copy">
              Um painel unico para prestadores, visitas, orcamentos, contratos e evidencias com leitura viva do backend local.
            </p>
          </div>

          <div className="hero-side">
            <label className="search-box">
              <span>Busca rapida</span>
              <input
                type="search"
                value={query}
                onChange={event => setQuery(event.target.value)}
                placeholder="Buscar prestadores, visitas e contratos"
              />
            </label>
            <div className="user-identity-card">
              <span className="muted">Usuario demo</span>
              <strong>{userId.slice(0, 12)}</strong>
              <small>Ator persistente usado em chamadas ao runtime de Services.</small>
            </div>
          </div>
        </header>

        {loadError && (
          <section className="alert-box" role="status">
            <strong>Algumas leituras ao vivo falharam:</strong> {loadError}
          </section>
        )}

        <section className="summary-grid">
          <article className="summary-card accent">
            <span className="summary-label">Gateway</span>
            <strong>{gatewayStatus?.status ?? 'online'}</strong>
            <small>{gatewayStatus?.security ?? 'seguranca ativa'}</small>
          </article>
          <article className="summary-card">
            <span className="summary-label">Services</span>
            <strong>{servicesHealth?.status ?? 'healthy'}</strong>
            <small>{servicesHealth?.storage ?? 'postgres'}</small>
          </article>
          <article className="summary-card">
            <span className="summary-label">Prestadores</span>
            <strong>{metricValue(liveProviders.length)}</strong>
            <small>{currentProvider?.payload?.category ?? 'categoria'}</small>
          </article>
          <article className="summary-card">
            <span className="summary-label">Visitas</span>
            <strong>{metricValue(liveVisits.length)}</strong>
            <small>{liveVisits[0]?.payload?.visit_price_brl ? formatMoney(liveVisits[0].payload?.visit_price_brl) : 'agenda ativa'}</small>
          </article>
          <article className="summary-card">
            <span className="summary-label">Orcamentos</span>
            <strong>{metricValue(liveQuotes.length)}</strong>
            <small>{commercialInsights?.source ?? 'marketplace'}</small>
          </article>
          <article className="summary-card">
            <span className="summary-label">Contratos</span>
            <strong>{metricValue(liveContracts.length)}</strong>
            <small>{identityHealth?.module ?? 'identity'}</small>
          </article>
        </section>

        {activeTab === 'dashboard' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Visao comercial</span>
                  <h2>Demanda e suporte</h2>
                </div>
                <button className="ghost-button" type="button" onClick={() => window.location.reload()}>
                  Atualizar
                </button>
              </div>
              <div className="metric-strip">
                <div>
                  <span>Pedidos pagos</span>
                  <strong>{metricValue(commercialInsights?.orders_paid)}</strong>
                </div>
                <div>
                  <span>Avaliacao media</span>
                  <strong>{commercialInsights?.average_rating ?? '0.0'}</strong>
                </div>
                <div>
                  <span>Conversao</span>
                  <strong>{commercialInsights?.conversion_rate_percent ?? 0}%</strong>
                </div>
                <div>
                  <span>Suporte aberto</span>
                  <strong>{metricValue(commercialInsights?.support_cases_open)}</strong>
                </div>
              </div>
            </article>

            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Agenda</span>
                  <h2>{currentProvider?.payload?.name ?? 'Prestador selecionado'}</h2>
                </div>
              </div>
              <p className="section-note">
                Slots reais de agenda por prestador, com reserva simulada no runtime Services.
              </p>
              <div className="mini-list">
                <div>
                  <span>Prestador</span>
                  <strong>{currentProvider?.payload?.name ?? currentProvider?.id}</strong>
                </div>
                <div>
                  <span>Data</span>
                  <strong>{selectedDate}</strong>
                </div>
                <div>
                  <span>Slots</span>
                  <strong>{availableSlots.length}</strong>
                </div>
              </div>
              {reservationMessage && <p className="success-box">{reservationMessage}</p>}
            </article>

            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Health</span>
                  <h2>Services e Identity</h2>
                </div>
              </div>
              <div className="data-list">
                <div className="data-row">
                  <div>
                    <strong>Services</strong>
                    <span>{servicesHealth?.module ?? 'services'}</span>
                  </div>
                  <div>
                    <strong>{servicesHealth?.status ?? 'healthy'}</strong>
                    <span>{servicesHealth?.version ?? 'baseline'}</span>
                  </div>
                </div>
                <div className="data-row">
                  <div>
                    <strong>Identity</strong>
                    <span>{identityHealth?.module ?? 'identity'}</span>
                  </div>
                  <div>
                    <strong>{identityHealth?.status ?? 'healthy'}</strong>
                    <span>{identityHealth?.storage ?? 'postgres'}</span>
                  </div>
                </div>
              </div>
            </article>
          </section>
        )}

        {activeTab === 'prestadores' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Prestadores</span>
                  <h2>Base operacional</h2>
                </div>
              </div>
              <div className="provider-grid">
                {filteredProviders.map(provider => (
                  <button
                    key={provider.id}
                    type="button"
                    className={`provider-card ${selectedProviderId === provider.id ? 'active' : ''}`}
                    onClick={() => setSelectedProviderId(provider.id)}
                  >
                    <span className={`offer-pill ${provider.payload?.verified ? 'active' : ''}`}>
                      {provider.payload?.verified ? 'verificado' : provider.status ?? 'pending'}
                    </span>
                    <strong>{provider.payload?.name ?? provider.id}</strong>
                    <span>{provider.payload?.category ?? 'categoria'}</span>
                    <small>
                      {provider.payload?.service_area ?? 'area' } • {provider.payload?.city ?? 'local'}
                    </small>
                  </button>
                ))}
              </div>
            </article>

            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Agenda</span>
                  <h2>Slots do prestador</h2>
                </div>
              </div>
              <label className="search-box compact">
                <span>Data da visita</span>
                <input type="date" value={selectedDate} onChange={event => setSelectedDate(event.target.value)} />
              </label>
              <p className="section-note">{slotLoading ? 'Carregando slots...' : `Prestador atual: ${currentProvider?.payload?.name ?? currentProvider?.id}`}</p>
              {slotError && <p className="warning-box">{slotError}</p>}
              <div className="slot-grid">
                {availableSlots.map(slot => (
                  <button
                    key={slot}
                    type="button"
                    className={`slot-chip ${chosenSlot === slot ? 'active' : ''}`}
                    onClick={() => setChosenSlot(slot)}
                  >
                    {slot}
                  </button>
                ))}
              </div>
              <button className="cta-button" type="button" onClick={handleReserve} disabled={reservationLoading}>
                {reservationLoading ? 'Reservando...' : 'Reservar slot'}
              </button>
              {reservationError && <p className="warning-box">{reservationError}</p>}
              {reservationMessage && <p className="success-box">{reservationMessage}</p>}
            </article>
          </section>
        )}

        {activeTab === 'visitas' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Visitas</span>
                  <h2>Atendimentos programados</h2>
                </div>
              </div>
              <div className="data-list">
                {filteredVisits.map(visit => (
                  <div key={visit.id} className="data-row">
                    <div>
                      <strong>{visit.payload?.customer_name ?? 'Cliente'}</strong>
                      <span>{visit.payload?.service_type ?? 'visita'}</span>
                    </div>
                    <div>
                      <strong>{formatMoney(visit.payload?.visit_price_brl)}</strong>
                      <span>{visit.status ?? 'active'} • {formatDate(visit.payload?.scheduled_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}

        {activeTab === 'orcamentos' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Orcamentos</span>
                  <h2>Propostas em aberto</h2>
                </div>
              </div>
              <div className="offer-grid">
                {filteredQuotes.map(quote => (
                  <div key={quote.id} className="offer-card">
                    <span className={`offer-pill ${quote.status === 'created' ? 'active' : ''}`}>{quote.status ?? 'created'}</span>
                    <strong>{quote.payload?.service_type ?? 'Orcamento'}</strong>
                    <span>{quote.payload?.provider_id ?? 'prestador'}</span>
                    <small>{formatMoney(quote.payload?.quoted_brl ?? quote.payload?.visit_price_brl)}</small>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}

        {activeTab === 'contratos' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Contratos</span>
                  <h2>Escopo e evolucao</h2>
                </div>
              </div>
              <div className="data-list">
                {filteredContracts.map(contract => (
                  <div key={contract.id} className="data-row">
                    <div>
                      <strong>{contract.payload?.stage ?? contract.status ?? 'held'}</strong>
                      <span>{contract.payload?.provider_id ?? 'prestador vinculado'}</span>
                    </div>
                    <div>
                      <strong>{formatMoney(contract.payload?.contracted_price_brl)}</strong>
                      <span>{formatMoney(contract.payload?.visit_price_brl)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}

        {activeTab === 'evidencias' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Evidencias</span>
                  <h2>Auditoria e anexos</h2>
                </div>
              </div>
              <div className="data-list">
                {filteredEvidence.map(item => (
                  <div key={item.id} className="data-row">
                    <div>
                      <strong>{item.payload?.kind ?? 'evidence'}</strong>
                      <span>{item.payload?.note ?? item.id}</span>
                    </div>
                    <div>
                      <strong>{item.status ?? 'accepted'}</strong>
                      <span>{formatDate(item.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}
      </main>
    </div>
  )
}

export default App

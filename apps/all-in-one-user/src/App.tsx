import { useEffect, useState } from 'react'
import allInOneLogo from '../../../assets/brand/all-in-one-logo-official.png'
import './index.css'

type TabKey = 'dashboard' | 'conta' | 'carteira' | 'mercado' | 'vagas' | 'operacao'

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

type Offer = {
  offer_id: string
  title: string
  consumer_category?: string
  offer_type_label?: string
  primary_action_label?: string
  region_label?: string
  price_amount?: string | null
  verified_seller?: boolean
  source_module?: string
}

type Wallet = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    wallet_type?: string
    currency?: string
    balance_brl?: string
  }
}

type Vacancy = {
  id: string
  title?: string
  company_name?: string
  description?: string
  amount_brl?: string
  region_label?: string
  status?: string
}

type ModuleHealth = {
  module?: string
  service?: string
  status?: string
  storage?: string
  version?: string
}

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? 'http://127.0.0.1:8100'
const IDENTITY_URL = import.meta.env.VITE_IDENTITY_URL ?? 'http://127.0.0.1:8101'
const FINANCE_URL = import.meta.env.VITE_FINANCE_URL ?? 'http://127.0.0.1:8102'
const DELIVERY_URL = import.meta.env.VITE_DELIVERY_URL ?? 'http://127.0.0.1:8104'
const MOBILITY_URL = import.meta.env.VITE_MOBILITY_URL ?? 'http://127.0.0.1:8106'
const JOBS_URL = import.meta.env.VITE_JOBS_URL ?? 'http://127.0.0.1:8112'

const FALLBACK_OFFERS: Offer[] = [
  {
    offer_id: 'offer-1',
    title: 'Hamburguer Gourmet Valley',
    consumer_category: 'Alimentacao',
    offer_type_label: 'Alimento',
    primary_action_label: 'Comprar Agora',
    region_label: 'Centro',
    price_amount: '45.90',
    verified_seller: true,
    source_module: 'marketplace',
  },
  {
    offer_id: 'offer-2',
    title: 'Consultoria de IA Estrategica',
    consumer_category: 'Tecnologia',
    offer_type_label: 'Servico',
    primary_action_label: 'Solicitar Orcamento',
    region_label: 'Online',
    price_amount: null,
    verified_seller: true,
    source_module: 'marketplace',
  },
]

const FALLBACK_WALLETS: Wallet[] = [
  {
    id: 'wallet-1',
    status: 'active',
    created_at: '2026-07-04T00:00:00Z',
    payload: {
      wallet_type: 'consumer',
      currency: 'BRL',
      balance_brl: '1280.55',
    },
  },
]

const FALLBACK_VACANCIES: Vacancy[] = [
  {
    id: 'vac-1',
    title: 'Analista de Operacoes',
    company_name: 'Valley Tech',
    region_label: 'Hibrido',
    amount_brl: '5200.00',
    status: 'published',
  },
]

function getStoredUserId() {
  const key = 'all-in-one-user.demo-user-id'
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
  const [offers, setOffers] = useState<Offer[]>([])
  const [wallets, setWallets] = useState<Wallet[]>([])
  const [vacancies, setVacancies] = useState<Vacancy[]>([])
  const [identityHealth, setIdentityHealth] = useState<ModuleHealth | null>(null)
  const [deliveryHealth, setDeliveryHealth] = useState<ModuleHealth | null>(null)
  const [mobilityHealth, setMobilityHealth] = useState<ModuleHealth | null>(null)

  useEffect(() => {
    let cancelled = false

    const loadFeed = async () => {
      const headers = { 'X-Actor-User-Id': userId }

      const [
        gatewayResult,
        insightsResult,
        offersResult,
        walletsResult,
        vacanciesResult,
        identityResult,
        deliveryResult,
        mobilityResult,
      ] = await Promise.allSettled([
        fetch(`${API_HUB_URL}/gateway/status`).then(async response => {
          if (!response.ok) throw new Error(`Gateway indisponivel (${response.status})`)
          return response.json() as Promise<GatewayStatus>
        }),
        fetch(`${API_HUB_URL}/gateway/insights/commercial`).then(async response => {
          if (!response.ok) throw new Error(`Resumo comercial indisponivel (${response.status})`)
          return response.json() as Promise<CommercialInsights>
        }),
        fetch(`${API_HUB_URL}/gateway/catalog/offers?limit=8&verified_only=true`).then(async response => {
          if (!response.ok) throw new Error(`Catalogo indisponivel (${response.status})`)
          return pickList<Offer>(await response.json())
        }),
        fetch(`${FINANCE_URL}/wallets/${userId}`, { headers }).then(async response => {
          if (!response.ok) throw new Error(`Carteira indisponivel (${response.status})`)
          return pickList<Wallet>(await response.json())
        }),
        fetch(`${JOBS_URL}/vacancies?q=operacoes`).then(async response => {
          if (!response.ok) throw new Error(`Vagas indisponiveis (${response.status})`)
          return pickList<Vacancy>(await response.json())
        }),
        fetch(`${IDENTITY_URL}/health`).then(async response => {
          if (!response.ok) throw new Error(`Identity health indisponivel (${response.status})`)
          return response.json() as Promise<ModuleHealth>
        }),
        fetch(`${DELIVERY_URL}/health`).then(async response => {
          if (!response.ok) throw new Error(`Delivery health indisponivel (${response.status})`)
          return response.json() as Promise<ModuleHealth>
        }),
        fetch(`${MOBILITY_URL}/health`).then(async response => {
          if (!response.ok) throw new Error(`Mobility health indisponivel (${response.status})`)
          return response.json() as Promise<ModuleHealth>
        }),
      ])

      if (cancelled) return

      const errors: string[] = []

      if (gatewayResult.status === 'fulfilled') {
        setGatewayStatus(gatewayResult.value)
      } else {
        errors.push(gatewayResult.reason instanceof Error ? gatewayResult.reason.message : String(gatewayResult.reason))
      }

      if (insightsResult.status === 'fulfilled') {
        setCommercialInsights(insightsResult.value)
      } else {
        errors.push(insightsResult.reason instanceof Error ? insightsResult.reason.message : String(insightsResult.reason))
      }

      if (offersResult.status === 'fulfilled') {
        setOffers(offersResult.value)
      } else {
        errors.push(offersResult.reason instanceof Error ? offersResult.reason.message : String(offersResult.reason))
      }

      if (walletsResult.status === 'fulfilled') {
        setWallets(walletsResult.value)
      } else {
        errors.push(walletsResult.reason instanceof Error ? walletsResult.reason.message : String(walletsResult.reason))
      }

      if (vacanciesResult.status === 'fulfilled') {
        setVacancies(vacanciesResult.value)
      } else {
        errors.push(vacanciesResult.reason instanceof Error ? vacanciesResult.reason.message : String(vacanciesResult.reason))
      }

      if (identityResult.status === 'fulfilled') {
        setIdentityHealth(identityResult.value)
      } else {
        errors.push(identityResult.reason instanceof Error ? identityResult.reason.message : String(identityResult.reason))
      }

      if (deliveryResult.status === 'fulfilled') {
        setDeliveryHealth(deliveryResult.value)
      } else {
        errors.push(deliveryResult.reason instanceof Error ? deliveryResult.reason.message : String(deliveryResult.reason))
      }

      if (mobilityResult.status === 'fulfilled') {
        setMobilityHealth(mobilityResult.value)
      } else {
        errors.push(mobilityResult.reason instanceof Error ? mobilityResult.reason.message : String(mobilityResult.reason))
      }

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
    const interval = window.setInterval(loadFeed, 20000)
    return () => {
      cancelled = true
      window.clearInterval(interval)
    }
  }, [userId])

  const search = query.trim().toLowerCase()
  const liveOffers = offers.length > 0 ? offers : FALLBACK_OFFERS
  const liveWallets = wallets.length > 0 ? wallets : FALLBACK_WALLETS
  const liveVacancies = vacancies.length > 0 ? vacancies : FALLBACK_VACANCIES

  const filteredOffers = search
    ? liveOffers.filter(offer =>
        [offer.title, offer.consumer_category, offer.offer_type_label, offer.region_label]
          .filter((value): value is string => typeof value === 'string')
          .some(value => value.toLowerCase().includes(search)),
      )
    : liveOffers

  const filteredVacancies = search
    ? liveVacancies.filter(vacancy =>
        [vacancy.title, vacancy.company_name, vacancy.region_label, vacancy.description]
          .filter((value): value is string => typeof value === 'string')
          .some(value => value.toLowerCase().includes(search)),
      )
    : liveVacancies

  const navItems: Array<{ key: TabKey; label: string; description: string }> = [
    { key: 'dashboard', label: 'Dashboard', description: 'Visao geral ao vivo' },
    { key: 'conta', label: 'Conta', description: 'Identidade e consentimento' },
    { key: 'carteira', label: 'Carteira', description: 'Finance e saldo' },
    { key: 'mercado', label: 'Mercado', description: 'Ofertas e compras' },
    { key: 'vagas', label: 'Vagas', description: 'Jobs e curriculo' },
    { key: 'operacao', label: 'Operacao', description: 'Entrega e mobilidade' },
  ]

  return (
    <div className="user-app-shell">
      <aside className="side-panel">
        <div className="brand-block">
          <img className="brand-mark" src={allInOneLogo} alt="All in One" />
          <div>
            <div className="brand-name">All-in-One User</div>
            <div className="brand-subtitle">Cadastro, carteira, mercado e operacao</div>
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
            <p className="eyebrow">All-in-One ID</p>
            <h1>{activeTab === 'dashboard' ? 'Experiencia do usuario em tempo real' : navItems.find(item => item.key === activeTab)?.label}</h1>
            <p className="hero-copy">
              Um unico ponto de entrada para identidade, carteira, marketplace, vagas, entregas e corridas com leitura viva do backend.
            </p>
          </div>

          <div className="hero-side">
            <label className="search-box">
              <span>Busca rapida</span>
              <input
                type="search"
                value={query}
                onChange={event => setQuery(event.target.value)}
                placeholder="Buscar ofertas, vagas e servicos"
              />
            </label>
            <div className="user-identity-card">
              <span className="muted">Usuario demo</span>
              <strong>{userId.slice(0, 12)}</strong>
              <small>Usado como ator em chamadas ao API Hub e aos modulos.</small>
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
            <span className="summary-label">Carteiras</span>
            <strong>{metricValue(liveWallets.length)}</strong>
            <small>{liveWallets[0]?.payload?.wallet_type ?? 'consumer'}</small>
          </article>
          <article className="summary-card">
            <span className="summary-label">Ofertas</span>
            <strong>{metricValue(liveOffers.length)}</strong>
            <small>{commercialInsights?.source ?? 'marketplace'}</small>
          </article>
          <article className="summary-card">
            <span className="summary-label">Vagas</span>
            <strong>{metricValue(liveVacancies.length)}</strong>
            <small>{commercialInsights?.average_rating ?? 'jobs.search'}</small>
          </article>
          <article className="summary-card">
            <span className="summary-label">Identity</span>
            <strong>{identityHealth?.storage ?? identityHealth?.status ?? 'healthy'}</strong>
            <small>{identityHealth?.module ?? 'identity'}</small>
          </article>
          <article className="summary-card">
            <span className="summary-label">Operacao</span>
            <strong>{deliveryHealth?.status ?? mobilityHealth?.status ?? 'healthy'}</strong>
            <small>delivery + mobility</small>
          </article>
        </section>

        {activeTab === 'dashboard' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Resumo comercial</span>
                  <h2>Valley e All-in-One em sintonia</h2>
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
                  <span className="eyebrow">Identidade</span>
                  <h2>Conta e consentimento</h2>
                </div>
              </div>
              <p className="section-note">
                O shell usa um identificador demo persistente para se comportar como um usuario autenticado na navegacao local.
              </p>
              <div className="mini-list">
                <div>
                  <span>Usuario</span>
                  <strong>{userId}</strong>
                </div>
                <div>
                  <span>Module</span>
                  <strong>{identityHealth?.module ?? 'identity'}</strong>
                </div>
                <div>
                  <span>Storage</span>
                  <strong>{identityHealth?.storage ?? 'sqlite'}</strong>
                </div>
              </div>
            </article>

            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Carteira</span>
                  <h2>Saldo e perfis</h2>
                </div>
              </div>
              <div className="data-list">
                {liveWallets.map(wallet => (
                  <div key={wallet.id} className="data-row">
                    <div>
                      <strong>{wallet.payload?.wallet_type ?? 'wallet'}</strong>
                      <span>{wallet.id}</span>
                    </div>
                    <div>
                      <strong>{wallet.payload?.balance_brl ? formatMoney(wallet.payload.balance_brl) : 'Sob consulta'}</strong>
                      <span>{wallet.status ?? 'active'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Mercado</span>
                  <h2>Ofertas ao vivo</h2>
                </div>
              </div>
              <div className="offer-grid compact">
                {filteredOffers.slice(0, 2).map(offer => (
                  <div key={offer.offer_id} className="offer-card">
                    <span className={`offer-pill ${offer.verified_seller ? 'active' : ''}`}>{offer.offer_type_label ?? 'Oferta'}</span>
                    <strong>{offer.title}</strong>
                    <span>{offer.consumer_category ?? 'Categoria geral'}</span>
                    <small>{offer.region_label ?? 'Sem regiao'} • {formatMoney(offer.price_amount)}</small>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}

        {activeTab === 'conta' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Conta</span>
                  <h2>Identidade, login e consentimento</h2>
                </div>
              </div>
              <p className="section-note">
                Aqui a experiencia do usuario e guiada pelo baseline de identidade, com leitura de health real e contexto persistente.
              </p>
              <div className="metric-strip">
                <div>
                  <span>Module</span>
                  <strong>{identityHealth?.module ?? 'identity'}</strong>
                </div>
                <div>
                  <span>Status</span>
                  <strong>{identityHealth?.status ?? 'healthy'}</strong>
                </div>
                <div>
                  <span>Storage</span>
                  <strong>{identityHealth?.storage ?? 'sqlite'}</strong>
                </div>
                <div>
                  <span>Versao</span>
                  <strong>{identityHealth?.version ?? 'baseline'}</strong>
                </div>
              </div>
            </article>
          </section>
        )}

        {activeTab === 'carteira' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Carteira</span>
                  <h2>Wallets do usuario</h2>
                </div>
              </div>
              <div className="data-list">
                {liveWallets.map(wallet => (
                  <div key={wallet.id} className="data-row">
                    <div>
                      <strong>{wallet.payload?.wallet_type ?? 'consumer'}</strong>
                      <span>{wallet.created_at ? formatTime(wallet.created_at) : 'agora'}</span>
                    </div>
                    <div>
                      <strong>{wallet.payload?.balance_brl ? formatMoney(wallet.payload.balance_brl) : 'Sob consulta'}</strong>
                      <span>{wallet.payload?.currency ?? 'BRL'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}

        {activeTab === 'mercado' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Mercado</span>
                  <h2>Ofertas e acoes disponiveis</h2>
                </div>
              </div>
              <div className="offer-grid">
                {filteredOffers.length > 0 ? filteredOffers.map(offer => (
                  <div key={offer.offer_id} className="offer-card">
                    <span className={`offer-pill ${offer.verified_seller ? 'active' : ''}`}>{offer.offer_type_label ?? 'Oferta'}</span>
                    <strong>{offer.title}</strong>
                    <span>{offer.consumer_category ?? 'Categoria geral'}</span>
                    <small>{offer.primary_action_label ?? 'Acao operacional'} • {offer.region_label ?? 'Local'}</small>
                  </div>
                )) : (
                  <p className="empty-copy">Nenhuma oferta encontrada para a busca atual.</p>
                )}
              </div>
            </article>
          </section>
        )}

        {activeTab === 'vagas' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Jobs</span>
                  <h2>Vagas e historico de candidatura</h2>
                </div>
              </div>
              <div className="offer-grid">
                {filteredVacancies.map(vacancy => (
                  <div key={vacancy.id} className="offer-card">
                    <span className="offer-pill active">{vacancy.status ?? 'published'}</span>
                    <strong>{vacancy.title ?? 'Vaga operacional'}</strong>
                    <span>{vacancy.company_name ?? 'Empresa parceira'}</span>
                    <small>{vacancy.region_label ?? 'Regiao local'} • {formatMoney(vacancy.amount_brl)}</small>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}

        {activeTab === 'operacao' && (
          <section className="content-grid">
            <article className="glass-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">Operacao</span>
                  <h2>Entrega e mobilidade</h2>
                </div>
              </div>
              <div className="metric-strip">
                <div>
                  <span>Delivery</span>
                  <strong>{deliveryHealth?.status ?? 'healthy'}</strong>
                </div>
                <div>
                  <span>Mobility</span>
                  <strong>{mobilityHealth?.status ?? 'healthy'}</strong>
                </div>
                <div>
                  <span>Delivery storage</span>
                  <strong>{deliveryHealth?.storage ?? 'postgres'}</strong>
                </div>
                <div>
                  <span>Mobility storage</span>
                  <strong>{mobilityHealth?.storage ?? 'postgres'}</strong>
                </div>
              </div>
            </article>
          </section>
        )}
      </main>
    </div>
  )
}

export default App

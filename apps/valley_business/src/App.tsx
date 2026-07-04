import { useEffect, useState } from 'react'
import { TelemetryDashboard } from './TelemetryDashboard'
import CalculatorWidget from './components/CalculatorWidget'
import LedgerTransactionList from './components/LedgerTransactionList'
import './index.css'

type TabKey = 'dashboard' | 'wallet' | 'offers' | 'pepitas' | 'telemetry'

type GatewayStatus = {
  service: string
  status: string
  security: string
  rate_limit: string
  routes: string[]
}

type CommercialInsights = {
  orders_total: number
  orders_paid: number
  orders_completed: number
  reviews_total: number
  average_rating: number | null
  support_cases_total: number
  support_cases_open: number
  support_cases_resolved: number
  conversion_rate_percent: number
  crm_records: number
  crm_audit_events: number
  crm_outbox_events: number
  bi_records: number
  bi_audit_events: number
  bi_outbox_events: number
  source: string
}

type CatalogOffer = {
  offer_id: string
  title: string
  consumer_category?: string
  offer_type_label?: string
  primary_action_label?: string
  region_label?: string
  verified_seller?: boolean
  price_amount?: string | null
  source_module?: string
}

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? 'http://127.0.0.1:8100'

const DEMO_OFFERS: CatalogOffer[] = [
  {
    offer_id: 'local-offer-1',
    title: 'Corte de Cabelo + Barba',
    consumer_category: 'Beleza',
    offer_type_label: 'Serviço',
    primary_action_label: 'Publicado no Valley',
    region_label: 'B2C',
    verified_seller: true,
    price_amount: '79.90',
    source_module: 'marketplace',
  },
  {
    offer_id: 'local-offer-2',
    title: 'Kit Ferramentas Pro',
    consumer_category: 'Casa e Reparos',
    offer_type_label: 'Produto',
    primary_action_label: 'Em análise',
    region_label: 'B2B',
    verified_seller: false,
    price_amount: '229.90',
    source_module: 'stock',
  },
]

function formatMoney(value?: string | null) {
  if (!value) return 'Sob consulta'
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return value
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(numeric)
}

function App() {
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard')
  const [gatewayStatus, setGatewayStatus] = useState<GatewayStatus | null>(null)
  const [commercialInsights, setCommercialInsights] = useState<CommercialInsights | null>(null)
  const [catalogOffers, setCatalogOffers] = useState<CatalogOffer[]>([])
  const [lastSyncedAt, setLastSyncedAt] = useState<string>('')
  const [loadError, setLoadError] = useState('')
  const [refreshCounter, setRefreshCounter] = useState(0)

  useEffect(() => {
    let cancelled = false

    const loadDashboard = async () => {
      const [statusResult, insightsResult, offersResult] = await Promise.allSettled([
        fetch(`${API_HUB_URL}/gateway/status`).then(async response => {
          if (!response.ok) throw new Error(`Gateway indisponível (${response.status})`)
          return response.json() as Promise<GatewayStatus>
        }),
        fetch(`${API_HUB_URL}/gateway/insights/commercial`).then(async response => {
          if (!response.ok) throw new Error(`Resumo comercial indisponível (${response.status})`)
          return response.json() as Promise<CommercialInsights>
        }),
        fetch(`${API_HUB_URL}/gateway/catalog/offers?limit=8&verified_only=true`).then(async response => {
          if (!response.ok) throw new Error(`Catálogo indisponível (${response.status})`)
          const payload = await response.json()
          const offers = Array.isArray(payload) ? payload : payload.data ?? []
          return offers as CatalogOffer[]
        }),
      ])

      if (cancelled) return

      const errors: string[] = []

      if (statusResult.status === 'fulfilled') {
        setGatewayStatus(statusResult.value)
      } else {
        errors.push(statusResult.reason instanceof Error ? statusResult.reason.message : String(statusResult.reason))
      }

      if (insightsResult.status === 'fulfilled') {
        setCommercialInsights(insightsResult.value)
      } else {
        errors.push(insightsResult.reason instanceof Error ? insightsResult.reason.message : String(insightsResult.reason))
      }

      if (offersResult.status === 'fulfilled') {
        setCatalogOffers(offersResult.value)
      } else {
        errors.push(offersResult.reason instanceof Error ? offersResult.reason.message : String(offersResult.reason))
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

    loadDashboard()
    const interval = window.setInterval(loadDashboard, 15000)
    return () => {
      cancelled = true
      window.clearInterval(interval)
    }
  }, [refreshCounter])

  const liveOffers = catalogOffers.length > 0 ? catalogOffers : DEMO_OFFERS
  const averageRating = commercialInsights?.average_rating ?? null
  const routesCount = gatewayStatus?.routes?.length ?? 0

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="sidebar-logo" style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column', gap: '12px', borderBottom: '1px solid var(--panel-border)' }}>
          <img
            src="/assets/brand/all-in-one-logo-light-official.png"
            alt="All-in-One"
            style={{ width: '100%', maxWidth: '120px', height: 'auto' }}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <img
              src="/assets/brand/valley-logo-official.png"
              alt="Valley"
              style={{ height: '20px', width: 'auto' }}
            />
            <span style={{ fontSize: '14px', fontWeight: 800, color: 'var(--accent)' }}>Business</span>
          </div>
        </div>
        <nav className="sidebar-nav">
          <div
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Visão Geral
          </div>
          <div
            className={`nav-item ${activeTab === 'wallet' ? 'active' : ''}`}
            onClick={() => setActiveTab('wallet')}
          >
            🪙 Carteira Gold
          </div>
          <div
            className={`nav-item ${activeTab === 'offers' ? 'active' : ''}`}
            onClick={() => setActiveTab('offers')}
          >
            📦 Catálogo de Ofertas
          </div>
          <div
            className={`nav-item ${activeTab === 'pepitas' ? 'active' : ''}`}
            onClick={() => setActiveTab('pepitas')}
          >
            ⭐ Concessão de Pepitas
          </div>
          <div
            className={`nav-item ${activeTab === 'telemetry' ? 'active' : ''}`}
            onClick={() => setActiveTab('telemetry')}
          >
            📡 Telemetria Outbox
          </div>
        </nav>
      </aside>

      <main className="main-content">
        <header className="header">
          <div>
            <h1>
              {activeTab === 'dashboard' && 'Visão Geral do Negócio'}
              {activeTab === 'wallet' && 'Gestão de Valley Gold'}
              {activeTab === 'offers' && 'Seus Produtos e Serviços'}
              {activeTab === 'pepitas' && 'Fidelização de Clientes'}
              {activeTab === 'telemetry' && 'Monitoramento de Telemetria'}
            </h1>
            <div style={{ marginTop: '0.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {lastSyncedAt ? `Atualizado às ${lastSyncedAt}` : 'Carregando visão operacional...'}
            </div>
          </div>
          <div className="wallet-badge">
            🪙 12.500 V-Gold
          </div>
        </header>

        {loadError && (
          <div
            style={{
              marginBottom: '1.5rem',
              padding: '1rem 1.25rem',
              borderRadius: '12px',
              background: 'rgba(231, 76, 60, 0.12)',
              border: '1px solid rgba(231, 76, 60, 0.35)',
              color: '#ffb7b1',
            }}
          >
            <strong>Algumas leituras ao vivo falharam:</strong> {loadError}
          </div>
        )}

        {activeTab === 'dashboard' && (
          <div className="grid-container">
            <div className="glass-card">
              <h3 className="card-title">Pedidos Concluídos</h3>
              <p className="metric-value">{commercialInsights?.orders_completed ?? '—'}</p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                {commercialInsights ? `${commercialInsights.orders_paid} pedidos pagos` : 'Leitura comercial ao vivo'}
              </p>
            </div>
            <div className="glass-card">
              <h3 className="card-title">Conversão</h3>
              <p className="metric-value">
                {commercialInsights ? `${commercialInsights.conversion_rate_percent.toFixed(1)}%` : '—'}
              </p>
              <p style={{ color: '#2ecc71', fontSize: '0.875rem' }}>
                {commercialInsights?.source ?? 'gateway.insights.commercial'}
              </p>
            </div>
            <div className="glass-card">
              <h3 className="card-title">Avaliação Média</h3>
              <p className="metric-value">
                {averageRating === null ? '—' : averageRating.toFixed(2)}
              </p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                {commercialInsights ? `${commercialInsights.reviews_total} avaliações` : 'Feedback de clientes'}
              </p>
            </div>
            <div className="glass-card">
              <h3 className="card-title">Casos Abertos</h3>
              <p className="metric-value">{commercialInsights?.support_cases_open ?? '—'}</p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                {commercialInsights ? `${commercialInsights.support_cases_resolved} resolvidos` : 'Suporte e disputa'}
              </p>
            </div>
            <div className="glass-card" style={{ gridColumn: '1 / -1' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <div>
                  <h3 className="card-title" style={{ marginBottom: '0.35rem' }}>Gateway e Rede Operacional</h3>
                  <p style={{ margin: 0, color: 'var(--text-muted)' }}>
                    {gatewayStatus?.service ?? 'API Hub Gateway'} • {gatewayStatus?.security ?? 'carregando segurança'} • {routesCount} rotas publicadas
                  </p>
                </div>
                <button
                  className="btn-primary"
                  style={{ width: 'auto', marginTop: 0 }}
                  onClick={() => setRefreshCounter(value => value + 1)}
                >
                  Atualizar visão
                </button>
              </div>
              <div className="grid-container" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', marginTop: '1rem' }}>
                <div className="glass-card" style={{ margin: 0 }}>
                  <h4 className="card-title" style={{ marginBottom: '0.25rem' }}>Status</h4>
                  <p className="metric-value" style={{ fontSize: '1.7rem' }}>{gatewayStatus?.status ?? '—'}</p>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>{gatewayStatus?.rate_limit ?? 'rate limit ativo'}</p>
                </div>
                <div className="glass-card" style={{ margin: 0 }}>
                  <h4 className="card-title" style={{ marginBottom: '0.25rem' }}>CRM</h4>
                  <p className="metric-value" style={{ fontSize: '1.7rem' }}>{commercialInsights?.crm_records ?? '—'}</p>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Registros, auditoria e outbox</p>
                </div>
                <div className="glass-card" style={{ margin: 0 }}>
                  <h4 className="card-title" style={{ marginBottom: '0.25rem' }}>BI</h4>
                  <p className="metric-value" style={{ fontSize: '1.7rem' }}>{commercialInsights?.bi_records ?? '—'}</p>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Métricas operacionais consolidadas</p>
                </div>
              </div>
            </div>

            <div className="glass-card" style={{ gridColumn: '1 / -1' }}>
              <h3 className="card-title">Ofertas em Destaque</h3>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Nome</th>
                      <th>Tipo</th>
                      <th>Categoria</th>
                      <th>Preço</th>
                    </tr>
                  </thead>
                  <tbody>
                    {liveOffers.map(offer => (
                      <tr key={offer.offer_id}>
                        <td>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                            <strong>{offer.title}</strong>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                              {offer.primary_action_label ?? offer.source_module ?? 'marketplace'}
                            </span>
                          </div>
                        </td>
                        <td>{offer.offer_type_label ?? 'Oferta'}</td>
                        <td>{offer.consumer_category ?? 'Geral'}</td>
                        <td>{formatMoney(offer.price_amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'center', marginTop: '1rem' }}>
              <CalculatorWidget />
            </div>
          </div>
        )}

        {activeTab === 'wallet' && (
          <div className="grid-container">
            <div className="glass-card" style={{ gridColumn: '1 / -1' }}>
              <h3 className="card-title">Comprar Valley Gold (B2B)</h3>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                O Valley Gold é a reserva de valor necessária para distribuir Pepitas com governança e trilha de auditoria.
              </p>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <input
                  type="number"
                  placeholder="Quantidade de V-Gold"
                  style={{
                    padding: '0.75rem',
                    borderRadius: '8px',
                    border: '1px solid var(--panel-border)',
                    background: 'rgba(0,0,0,0.2)',
                    color: 'white',
                    flex: 1,
                    minWidth: '220px',
                  }}
                />
                <button className="btn-primary" style={{ width: 'auto', marginTop: 0 }}>
                  Gerar Pix Copia e Cola
                </button>
              </div>
            </div>

            <div className="glass-card" style={{ gridColumn: '1 / -1', display: 'flex', flexDirection: 'column', alignItems: 'center', background: 'transparent', boxShadow: 'none', border: 'none' }}>
              <LedgerTransactionList />
            </div>
          </div>
        )}

        {activeTab === 'offers' && (
          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', gap: '1rem', flexWrap: 'wrap' }}>
              <div>
                <h3 className="card-title" style={{ margin: 0 }}>Catálogo (Valley API Hub)</h3>
                <p style={{ margin: '0.35rem 0 0', color: 'var(--text-muted)' }}>
                  Ofertas ao vivo carregadas do gateway e fallback local preservado para teste visual.
                </p>
              </div>
              <button className="btn-primary" style={{ width: 'auto', marginTop: 0 }} onClick={() => setRefreshCounter(value => value + 1)}>
                Atualizar ofertas
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              {liveOffers.map((offer, index) => (
                <div key={offer.offer_id} className="glass-card" style={{ margin: 0 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', marginBottom: '0.75rem' }}>
                    <strong>Oferta em destaque {index + 1}</strong>
                    <span className={`status-badge ${offer.verified_seller ? 'status-active' : 'status-pending'}`}>
                      {offer.offer_type_label ?? 'Oferta'}
                    </span>
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                    {offer.consumer_category ?? 'Categoria geral'} • {offer.region_label ?? 'Sem região informada'} • {offer.source_module ?? 'marketplace'}
                  </div>
                  <div style={{ fontWeight: 800, fontSize: '1.1rem', marginBottom: '0.25rem' }}>
                    {formatMoney(offer.price_amount)}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    {offer.primary_action_label ?? 'Ação operacional disponível'}
                  </div>
                </div>
              ))}
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
                    <td><span className="status-badge status-active">Publicado no Valley</span></td>
                  </tr>
                  <tr>
                    <td>Kit Ferramentas Pro</td>
                    <td>Produto</td>
                    <td>Restrito (B2B)</td>
                    <td><span className="status-badge status-pending">Em Análise</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'pepitas' && (
          <div className="grid-container">
            <div className="glass-card" style={{ gridColumn: '1 / -1' }}>
              <h3 className="card-title">Fidelização com Governança</h3>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                Distribua Pepitas com regras auditáveis, desconto Stock e trilha de eventos pronta para validação.
              </p>
              <div className="grid-container" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
                <div className="glass-card" style={{ margin: 0 }}>
                  <h4 className="card-title">Pepitas emitidas</h4>
                  <p className="metric-value" style={{ fontSize: '1.8rem' }}>3.400</p>
                </div>
                <div className="glass-card" style={{ margin: 0 }}>
                  <h4 className="card-title">Conversão ativa</h4>
                  <p className="metric-value" style={{ fontSize: '1.8rem' }}>
                    {commercialInsights ? `${commercialInsights.conversion_rate_percent.toFixed(1)}%` : '—'}
                  </p>
                </div>
                <div className="glass-card" style={{ margin: 0 }}>
                  <h4 className="card-title">Status comercial</h4>
                  <p style={{ margin: 0, color: 'var(--text-muted)' }}>
                    {gatewayStatus?.status ?? 'gateway ativo'} • {gatewayStatus?.security ?? 'JWT edge'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'telemetry' && <TelemetryDashboard baseUrl={API_HUB_URL} />}
      </main>
    </div>
  )
}

export default App

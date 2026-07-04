import { useEffect, useState } from 'react'
import './index.css'

type TabKey = 'home' | 'earnings' | 'profile'

type Vacancy = {
  id: string
  title?: string
  description?: string
  company_name?: string
  status?: string
  region_label?: string
  amount_brl?: string
}

type ModuleStatus = {
  module: string
  state: string
  records: number
  audit_events: number
  outbox_events: number
  actor: string
}

type RiderFeed = {
  vacancies: Vacancy[]
  deliveryStatus: ModuleStatus | null
  mobilityStatus: ModuleStatus | null
  loading: boolean
  error: string
  updatedAt: string
}

const JOBS_URL = import.meta.env.VITE_JOBS_URL ?? 'http://127.0.0.1:8112'
const DELIVERY_URL = import.meta.env.VITE_DELIVERY_URL ?? 'http://127.0.0.1:8104'
const MOBILITY_URL = import.meta.env.VITE_MOBILITY_URL ?? 'http://127.0.0.1:8106'

const DEMO_OPPORTUNITIES: Vacancy[] = [
  {
    id: 'demo-1',
    title: 'Entrega Expressa',
    description: 'Coleta no centro e entrega em até 15 minutos.',
    company_name: 'Restaurante Sabor do Vale',
    region_label: '2.4 km',
    amount_brl: '14.50',
  },
  {
    id: 'demo-2',
    title: 'Serviço de Frete',
    description: 'Mover caixas leves com rastreio e aviso de chegada.',
    company_name: 'Valley Logística',
    region_label: '5.8 km',
    amount_brl: '45.00',
  },
]

function getDemoRiderId() {
  const stored = window.localStorage.getItem('valley.rider.user-id')
  if (stored) return stored
  const riderId = window.crypto.randomUUID()
  window.localStorage.setItem('valley.rider.user-id', riderId)
  return riderId
}

function formatMoney(value?: string) {
  if (!value) return 'Sob consulta'
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return value
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(numeric)
}

function App() {
  const [tab, setTab] = useState<TabKey>('home')
  const [isOnline, setIsOnline] = useState(true)
  const [riderId] = useState(getDemoRiderId)
  const [feed, setFeed] = useState<RiderFeed>({
    vacancies: [],
    deliveryStatus: null,
    mobilityStatus: null,
    loading: true,
    error: '',
    updatedAt: '',
  })

  useEffect(() => {
    if (!isOnline) {
      setFeed(current => ({ ...current, loading: false }))
      return
    }

    let cancelled = false

    const loadFeed = async () => {
      const [vacanciesResult, deliveryResult, mobilityResult] = await Promise.allSettled([
        fetch(`${JOBS_URL}/vacancies?q=operacoes`).then(async response => {
          if (!response.ok) throw new Error(`Jobs indisponível (${response.status})`)
          const payload = await response.json()
          return Array.isArray(payload) ? payload : payload.data ?? []
        }),
        fetch(`${DELIVERY_URL}/status`, {
          headers: { 'X-Actor-User-Id': riderId },
        }).then(async response => {
          if (!response.ok) throw new Error(`Delivery indisponível (${response.status})`)
          return response.json() as Promise<ModuleStatus>
        }),
        fetch(`${MOBILITY_URL}/status`, {
          headers: { 'X-Actor-User-Id': riderId },
        }).then(async response => {
          if (!response.ok) throw new Error(`Mobility indisponível (${response.status})`)
          return response.json() as Promise<ModuleStatus>
        }),
      ])

      if (cancelled) return

      const errors: string[] = []
      const nextFeed: RiderFeed = {
        vacancies: [],
        deliveryStatus: null,
        mobilityStatus: null,
        loading: false,
        error: '',
        updatedAt: new Intl.DateTimeFormat('pt-BR', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }).format(new Date()),
      }

      if (vacanciesResult.status === 'fulfilled') {
        nextFeed.vacancies = vacanciesResult.value
      } else {
        errors.push(vacanciesResult.reason instanceof Error ? vacanciesResult.reason.message : String(vacanciesResult.reason))
      }

      if (deliveryResult.status === 'fulfilled') {
        nextFeed.deliveryStatus = deliveryResult.value
      } else {
        errors.push(deliveryResult.reason instanceof Error ? deliveryResult.reason.message : String(deliveryResult.reason))
      }

      if (mobilityResult.status === 'fulfilled') {
        nextFeed.mobilityStatus = mobilityResult.value
      } else {
        errors.push(mobilityResult.reason instanceof Error ? mobilityResult.reason.message : String(mobilityResult.reason))
      }

      nextFeed.error = errors.length > 0 ? errors.join(' • ') : ''
      setFeed(nextFeed)
    }

    loadFeed()
    const interval = window.setInterval(loadFeed, 15000)
    return () => {
      cancelled = true
      window.clearInterval(interval)
    }
  }, [isOnline, riderId])

  const liveOpportunities = feed.vacancies.length > 0 ? feed.vacancies : DEMO_OPPORTUNITIES

  return (
    <div className="mobile-container">
      <header className="header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 20px', background: '#000' }}>
        <div className="brand-group" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <img
            src="/assets/brand/all-in-one-logo-light-official.png"
            alt="All-in-One"
            style={{ height: '24px', width: 'auto' }}
          />
          <div style={{ width: '1px', height: '16px', background: 'rgba(255,255,255,0.3)' }} />
          <img
            src="/assets/brand/valley-logo-official.png"
            alt="Valley Rider"
            style={{ height: '20px', width: 'auto' }}
          />
          <span style={{ fontSize: '12px', fontWeight: 900, color: 'var(--accent-rider)' }}>RIDER</span>
        </div>
        <div
          className="status-toggle"
          onClick={() => setIsOnline(!isOnline)}
          style={{
            background: isOnline ? 'rgba(46, 204, 113, 0.1)' : 'rgba(231, 76, 60, 0.1)',
            color: isOnline ? 'var(--accent-success)' : '#e74c3c',
            borderColor: isOnline ? 'var(--accent-success)' : '#e74c3c',
          }}
        >
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: isOnline ? 'var(--accent-success)' : '#e74c3c',
            }}
          />
          {isOnline ? 'ONLINE' : 'OFFLINE'}
        </div>
      </header>

      {tab === 'home' && (
        <>
          <div className="map-placeholder">
            <span style={{ position: 'relative', zIndex: 1 }}>Mapa Dinâmico (GPS Tracking)</span>
          </div>

          <div className="content-area">
            <h2 className="section-title">Oportunidades</h2>

            {!isOnline ? (
              <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--text-muted)' }}>
                Fique online para receber solicitações de entrega e serviços.
              </div>
            ) : (
              <>
                <div
                  className="job-card"
                  style={{
                    borderColor: 'rgba(46, 204, 113, 0.35)',
                    background: 'linear-gradient(180deg, rgba(46, 204, 113, 0.12), rgba(30, 30, 30, 0.98))',
                  }}
                >
                  <div className="job-header">
                    <div>
                      <div style={{ fontWeight: 700 }}>Painel ao vivo</div>
                      <div className="job-distance">
                        {feed.loading ? 'Sincronizando operação...' : `Rider ${riderId.slice(0, 8)} • ${feed.updatedAt || 'agora'}`}
                      </div>
                    </div>
                    <div className="job-price">{liveOpportunities.length}</div>
                  </div>

                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(108px, 1fr))',
                      gap: '0.75rem',
                    }}
                  >
                    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.85rem', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.35rem' }}>Vagas</div>
                      <strong>{feed.vacancies.length || liveOpportunities.length}</strong>
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.85rem', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.35rem' }}>Delivery</div>
                      <strong>{feed.deliveryStatus?.state ?? 'domain_engine_active'}</strong>
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.85rem', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.35rem' }}>Mobility</div>
                      <strong>{feed.mobilityStatus?.state ?? 'domain_engine_active'}</strong>
                    </div>
                  </div>
                </div>

                {feed.error && (
                  <div
                    style={{
                      marginBottom: '1rem',
                      padding: '0.85rem 1rem',
                      borderRadius: '10px',
                      border: '1px solid rgba(231, 76, 60, 0.35)',
                      background: 'rgba(231, 76, 60, 0.12)',
                      color: '#ffb7b1',
                    }}
                  >
                    <strong>Leitura parcial:</strong> {feed.error}
                  </div>
                )}

                <h2 className="section-title">Oportunidades ao vivo</h2>
                {liveOpportunities.map((opportunity, index) => (
                  <div key={opportunity.id} className="job-card">
                    <div className="job-header">
                      <div>
                        <div style={{ fontWeight: 700 }}>Oportunidade ao vivo {index + 1}</div>
                        <div className="job-distance">
                          {opportunity.company_name ?? 'Operação Valley'} • {opportunity.region_label ?? 'raio local'} • {opportunity.status ?? 'Oferta ativa'}
                        </div>
                      </div>
                      <div className="job-price">{formatMoney(opportunity.amount_brl)}</div>
                    </div>

                    <div className="job-locations">
                      <div className="location-item">
                        <span style={{ color: 'var(--accent-rider)' }}>📍</span>
                        <div>
                          <strong>Descrição:</strong> {opportunity.description ?? 'Atendimento, coleta ou entrega disponível.'}
                          <div style={{ color: 'var(--text-muted)' }}>{opportunity.status ?? 'published'}</div>
                        </div>
                      </div>
                    </div>

                    <button className="btn-accept">Aceitar corrida</button>
                  </div>
                ))}

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
                      <span style={{ color: 'var(--accent-rider)' }}>📍</span>
                      <div>
                        <strong>Coleta:</strong> Restaurante Sabor do Vale
                        <div style={{ color: 'var(--text-muted)' }}>Rua das Flores, 123</div>
                      </div>
                    </div>
                    <div className="location-item">
                      <span style={{ color: 'var(--accent-success)' }}>🏁</span>
                      <div>
                        <strong>Entrega:</strong> Cliente Final
                        <div style={{ color: 'var(--text-muted)' }}>Av. Principal, 1000 - Apto 42</div>
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
                  <button className="btn-accept" style={{ background: '#333', color: '#fff' }}>
                    Ver Detalhes
                  </button>
                </div>
              </>
            )}
          </div>
        </>
      )}

      {tab === 'earnings' && (
        <div className="content-area">
          <h2 className="section-title">Ganhos</h2>
          <div className="job-card" style={{ textAlign: 'center', padding: '2rem' }}>
            <div style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Ganhos Hoje</div>
            <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--accent-success)' }}>R$ 124,50</div>
            <div style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>6 Entregas Concluídas</div>
          </div>
        </div>
      )}

      {tab === 'profile' && (
        <div className="content-area">
          <h2 className="section-title">Perfil do Rider</h2>
          <div className="job-card">
            <div><strong>Nome:</strong> Entregador Parceiro</div>
            <div><strong>Veículo:</strong> Moto (Honda CG 160)</div>
            <div><strong>Avaliação:</strong> ⭐ 4.98</div>
            <div><strong>ID da operação:</strong> {riderId.slice(0, 12)}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              {feed.updatedAt ? `Dados sincronizados às ${feed.updatedAt}` : 'Sem sincronização recente'}
            </div>
          </div>
        </div>
      )}

      <nav className="bottom-nav">
        <div className={`nav-tab ${tab === 'home' ? 'active' : ''}`} onClick={() => setTab('home')}>
          🚗<br />Corridas
        </div>
        <div className={`nav-tab ${tab === 'earnings' ? 'active' : ''}`} onClick={() => setTab('earnings')}>
          💰<br />Ganhos
        </div>
        <div className={`nav-tab ${tab === 'profile' ? 'active' : ''}`} onClick={() => setTab('profile')}>
          👤<br />Perfil
        </div>
      </nav>
    </div>
  )
}

export default App

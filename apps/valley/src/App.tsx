import { useEffect, useState } from 'react'
import './index.css'
import CheckoutModal from './components/CheckoutModal'
import BookingModal from './components/BookingModal'
import LoginModal from './components/LoginModal'
import PaymentModal from './components/PaymentModal'
import OrdersDrawer from './components/OrdersDrawer'
import B2BDashboard from './components/B2BDashboard'
import LiveTracking from './components/LiveTracking'
import {
  type CatalogActionResponse,
  type CatalogFacets,
  createCatalogAction,
  isDemoModeEnabled,
  listOffers,
  moduleShowcase,
  type Offer,
  type PaymentIntent,
} from './lib/valleyPlatform'

function getStoredAuth() {
  const token = window.sessionStorage.getItem('valley.session.token')
  const userId = window.sessionStorage.getItem('valley.session.user-id')
  return { token, userId }
}

function setStoredAuth(token: string, userId: string) {
  window.sessionStorage.setItem('valley.session.token', token)
  window.sessionStorage.setItem('valley.session.user-id', userId)
}

function clearStoredAuth() {
  window.sessionStorage.removeItem('valley.session.token')
  window.sessionStorage.removeItem('valley.session.user-id')
}

function App() {
  const [offers, setOffers] = useState<Offer[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [currentView, setCurrentView] = useState<'consumer' | 'b2b' | 'tracking'>('consumer')
  const [auth, setAuth] = useState(getStoredAuth())
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [lat, setLat] = useState('-23.5505')
  const [lng, setLng] = useState('-46.6333')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [selectedCompanyType, setSelectedCompanyType] = useState('')
  const [selectedCompanyCategory, setSelectedCompanyCategory] = useState('')
  const [selectedBusinessActivity, setSelectedBusinessActivity] = useState('')
  const [facets, setFacets] = useState<CatalogFacets>({
    company_types: [],
    company_categories: [],
    business_activities: [],
  })
  const [activeOffer, setActiveOffer] = useState<Offer | null>(null)
  const [activeIntentKey, setActiveIntentKey] = useState('')
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false)
  const [isBookingOpen, setIsBookingOpen] = useState(false)
  const [isPaymentOpen, setIsPaymentOpen] = useState(false)
  const [isOrdersOpen, setIsOrdersOpen] = useState(false)
  const [paymentIntent, setPaymentIntent] = useState<PaymentIntent | null>(null)
  const [isDemoMode, setIsDemoMode] = useState(isDemoModeEnabled())

  const handleActionClick = (offer: Offer) => {
    setActiveOffer(offer)
    setActiveIntentKey(window.crypto.randomUUID())

    if (!auth.token || !auth.userId) {
      setIsLoginOpen(true)
      return
    }

    if (['book', 'hire', 'request'].includes(offer.consumer_action)) {
      setIsBookingOpen(true)
    } else {
      setIsCheckoutOpen(true)
    }
  }

  const submitCatalogAction = async (scheduledAt?: string, note?: string): Promise<CatalogActionResponse> => {
    if (!activeOffer) throw new Error('Selecione uma oferta para continuar.')
    if (!auth.token || !auth.userId) throw new Error('Usuario nao autenticado.')

    const payload = await createCatalogAction({
      offer: activeOffer,
      customerUserId: auth.userId,
      idempotencyKey: activeIntentKey,
      scheduledAt,
      note,
      token: auth.token,
    })

    if (payload.next_step === 'payment_required' && payload.payment_intent) {
      setPaymentIntent(payload.payment_intent)
      window.setTimeout(() => {
        setIsCheckoutOpen(false)
        setIsBookingOpen(false)
        setIsPaymentOpen(true)
      }, 1500)
    }

    return payload
  }

  const categories = [
    'Comida e Mercado',
    'Compras e Produtos',
    'Saude e Bem-estar',
    'Casa, Reparos e Imoveis',
    'Mobilidade, Entregas e Logistica',
    'Negocios e Profissionais',
    'Beneficios, Wallet e Recompensas',
    'Tecnologia, Seguranca e IA',
  ]

  const fetchOffers = () => {
    setLoading(true)
    setError('')
    listOffers({
      q: query,
      category: selectedCategory,
      offer_type: selectedType,
      company_type: selectedCompanyType,
      company_category: selectedCompanyCategory,
      business_activity: selectedBusinessActivity,
    })
      .then((data) => {
        setOffers(data.offers)
        setFacets(data.facets)
        setIsDemoMode(isDemoModeEnabled())
        if (data.partial) {
          setError('Algumas fontes estao temporariamente indisponiveis.')
        }
      })
      .catch(() => {
        setOffers([])
        setError('Nao foi possivel carregar as ofertas agora.')
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    const timer = window.setTimeout(fetchOffers, 0)
    return () => window.clearTimeout(timer)
  }, [selectedCategory, selectedType, selectedCompanyType, selectedCompanyCategory, selectedBusinessActivity])

  return (
    <>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 24px', background: '#120B2E', borderBottom: '2px solid #22D3EE' }}>
        <div className="brand-group" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <img src="./assets/brand/all-in-one-logo-light-official.png" alt="All-in-One" style={{ height: '32px', width: 'auto' }} />
          <div style={{ width: '2px', height: '24px', background: 'rgba(255,255,255,0.2)' }}></div>
          <img src="./assets/brand/valley-logo-official.png" alt="Valley" style={{ height: '28px', width: 'auto' }} />
        </div>
        <nav style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button className="btn-link" style={{ color: '#fff', fontWeight: currentView === 'consumer' ? 'bold' : 'normal' }} onClick={() => setCurrentView('consumer')}>Ofertas</button>
          <button className="btn-link" style={{ color: '#fff', fontWeight: currentView === 'b2b' ? 'bold' : 'normal' }} onClick={() => setCurrentView('b2b')}>Lojista (B2B)</button>
          <button className="btn-link" style={{ color: '#fff', fontWeight: currentView === 'tracking' ? 'bold' : 'normal' }} onClick={() => setCurrentView('tracking')}>Tracking</button>
          {auth.token ? (
            <>
              <button className="btn-link" style={{ color: '#fff' }} onClick={() => setIsOrdersOpen(true)}>Meus Pedidos</button>
              <button className="btn-link" style={{ color: '#fff' }} onClick={() => { clearStoredAuth(); setAuth({ token: null, userId: null }); setIsDemoMode(isDemoModeEnabled()) }}>Sair</button>
            </>
          ) : (
            <button className="btn-primary" onClick={() => setIsLoginOpen(true)}>Entrar / Cadastrar</button>
          )}
        </nav>
      </header>

      {currentView === 'b2b' && <B2BDashboard />}
      {currentView === 'tracking' && <LiveTracking />}

      {currentView === 'consumer' && (
        <main className="container">
          <section className="hero">
            <h1>Encontre o que precisa</h1>
            <p>Produtos, alimentos e servicos organizados de um jeito simples, com todos os modulos conectados para teste.</p>
            <div className="hero-status">
              <span className={`status-badge ${isDemoMode ? 'demo' : 'online'}`}>
                {isDemoMode ? 'Modo demonstracao ativo' : 'Modo conectado ao backend'}
              </span>
              <span className="hero-location">Latitude {lat} | Longitude {lng}</span>
            </div>
          </section>

          <section className="filters-section">
            <form className="search-row" onSubmit={(event) => { event.preventDefault(); fetchOffers() }}>
              <label className="search-field">
                <span>O que voce procura?</span>
                <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ex.: eletricista, marmita, psicologo" />
              </label>
              <button className="btn-primary" type="submit">Buscar</button>
            </form>

            <div className="type-filter" aria-label="Tipo de oferta">
              {[
                { id: null, label: 'Tudo' },
                { id: 'food', label: 'Alimentos' },
                { id: 'product', label: 'Produtos' },
                { id: 'service', label: 'Servicos' },
              ].map((type) => (
                <button
                  type="button"
                  key={type.label}
                  className={selectedType === type.id ? 'active' : ''}
                  onClick={() => setSelectedType(type.id)}
                >
                  {type.label}
                </button>
              ))}
            </div>

            <div className="filters-row">
              <div className="filter-group">
                <label htmlFor="latitude">Sua localizacao</label>
                <input id="latitude" type="text" value={lat} onChange={(e) => setLat(e.target.value)} placeholder="Latitude" />
                <input type="text" value={lng} onChange={(e) => setLng(e.target.value)} placeholder="Longitude" />
              </div>
              <button className="btn-secondary" onClick={fetchOffers}>Atualizar regiao</button>
            </div>

            <div className="business-filters">
              <label>
                <span>Quem oferece</span>
                <select value={selectedCompanyType} onChange={(event) => setSelectedCompanyType(event.target.value)}>
                  <option value="">Todos os vendedores e profissionais</option>
                  {facets.company_types.map((option) => (
                    <option key={option.id} value={option.id}>{option.label} ({option.count})</option>
                  ))}
                </select>
              </label>
              <label>
                <span>Area do negocio</span>
                <select value={selectedCompanyCategory} onChange={(event) => setSelectedCompanyCategory(event.target.value)}>
                  <option value="">Todas as areas</option>
                  {facets.company_categories.map((option) => (
                    <option key={option.id} value={option.id}>{option.label} ({option.count})</option>
                  ))}
                </select>
              </label>
              <label>
                <span>O que faz</span>
                <select value={selectedBusinessActivity} onChange={(event) => setSelectedBusinessActivity(event.target.value)}>
                  <option value="">Todos os ramos de atividade</option>
                  {facets.business_activities.map((option) => (
                    <option key={option.id} value={option.id}>{option.label} ({option.count})</option>
                  ))}
                </select>
              </label>
            </div>

            <div className="pills-container">
              <button type="button" className={`pill ${selectedCategory === null ? 'active' : ''}`} onClick={() => setSelectedCategory(null)}>
                Todas as categorias
              </button>
              {categories.map((category) => (
                <button
                  type="button"
                  key={category}
                  className={`pill ${selectedCategory === category ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category)}
                >
                  {category}
                </button>
              ))}
            </div>
          </section>

          {error && <p className="notice" role="status">{error}</p>}

          {loading ? (
            <div className="loader" aria-label="Carregando ofertas"></div>
          ) : (
            <div className="offers-grid">
              {offers.length > 0 ? offers.map((offer) => (
                <article className="offer-card" key={offer.offer_id} style={{ display: 'flex', flexDirection: 'column' }}>
                  <div className="media-container" style={{ position: 'relative', height: '160px', overflow: 'hidden', borderRadius: '12px', marginBottom: '12px', border: '1px solid #d4ddd8' }}>
                    <img src={offer.metadata?.image_url} alt={offer.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    {offer.metadata?.video_url && (
                      <video
                        src={offer.metadata.video_url}
                        muted
                        loop
                        onMouseOver={(e) => e.currentTarget.play()}
                        onMouseOut={(e) => { e.currentTarget.pause(); e.currentTarget.currentTime = 0 }}
                        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0, transition: 'opacity 0.3s' }}
                        onMouseEnter={(e) => { e.currentTarget.style.opacity = '1' }}
                        onMouseLeave={(e) => { e.currentTarget.style.opacity = '0' }}
                      />
                    )}
                  </div>
                  <div className="offer-tags">
                    <span className="badge">{offer.offer_type_label}</span>
                    <span>{offer.consumer_category}</span>
                  </div>
                  <div className="offer-title">{offer.title}</div>
                  <div className="offer-desc">{offer.short_description || offer.description}</div>
                  <div className="provider">
                    {offer.provider_label}{offer.verified_seller ? ' - verificado' : ''}
                  </div>
                  <div className="region">
                    {offer.distance_km != null ? `${offer.distance_km.toFixed(1)} km - ` : ''}{offer.region_label}
                  </div>
                  <div className="module-chip">{offer.source_module}</div>
                  <div className="offer-meta">
                    <span className="price">
                      {offer.price_amount ? `R$ ${Number(offer.price_amount).toFixed(2).replace('.', ',')}` : 'Sob orcamento'}
                    </span>
                    <button className="offer-action" onClick={() => handleActionClick(offer)}>
                      {offer.primary_action_label}
                    </button>
                  </div>
                </article>
              )) : (
                <div className="empty-state">
                  <h2>Nenhuma oferta encontrada</h2>
                  <p>Tente outra categoria, busca ou localizacao.</p>
                </div>
              )}
            </div>
          )}

          <section className="modules-section">
            <div className="section-heading">
              <div>
                <h2>Modulos e microservicos ativos nesta build</h2>
                <p>Jornadas prontas para teste com artefatos, simulacoes e ligacoes funcionais ao shell do consumidor.</p>
              </div>
            </div>
            <div className="modules-grid">
              {moduleShowcase.map((module) => (
                <article key={module.id} className="module-card">
                  <span className="module-tag">{module.title}</span>
                  <h3>{module.summary}</h3>
                  <p>{module.journey}</p>
                  <strong>{module.media}</strong>
                </article>
              ))}
            </div>
          </section>
        </main>
      )}

      <CheckoutModal
        key={`checkout-${activeIntentKey}`}
        isOpen={isCheckoutOpen}
        onClose={() => setIsCheckoutOpen(false)}
        onConfirm={() => submitCatalogAction()}
        offerTitle={activeOffer?.title ?? ''}
        priceAmount={activeOffer?.price_amount ?? null}
      />

      <BookingModal
        key={`booking-${activeIntentKey}`}
        isOpen={isBookingOpen}
        onClose={() => setIsBookingOpen(false)}
        onConfirm={submitCatalogAction}
        offerTitle={activeOffer?.title ?? ''}
      />

      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onSuccess={(token, userId) => {
          setStoredAuth(token, userId)
          setAuth({ token, userId })
          setIsDemoMode(isDemoModeEnabled())
          setIsLoginOpen(false)
          if (activeOffer) {
            if (['book', 'hire', 'request'].includes(activeOffer.consumer_action)) {
              setIsBookingOpen(true)
            } else {
              setIsCheckoutOpen(true)
            }
          }
        }}
      />

      <PaymentModal
        isOpen={isPaymentOpen}
        onClose={() => setIsPaymentOpen(false)}
        onSuccess={() => {
          setIsPaymentOpen(false)
          setIsOrdersOpen(true)
        }}
        paymentIntent={paymentIntent}
        token={auth.token}
      />

      <OrdersDrawer
        key={`orders-${isOrdersOpen}`}
        isOpen={isOrdersOpen}
        onClose={() => setIsOrdersOpen(false)}
        token={auth.token}
      />
    </>
  )
}

export default App

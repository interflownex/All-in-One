import { useEffect, useState } from 'react'
import './index.css'
import CheckoutModal from './components/CheckoutModal'
import BookingModal from './components/BookingModal'
import LoginModal from './components/LoginModal'
import PaymentModal, { type PaymentIntent } from './components/PaymentModal'
import OrdersDrawer from './components/OrdersDrawer'
import B2BDashboard from './components/B2BDashboard'
import LiveTracking from './components/LiveTracking'

interface Offer {
  offer_id: string
  title: string
  short_description?: string
  description?: string
  price_amount?: string | null
  price_type: string
  consumer_category: string
  offer_type: 'food' | 'product' | 'service'
  offer_type_label: string
  source_module: string
  provider_label: string
  region_label: string
  distance_km?: number | null
  consumer_action: 'view' | 'buy' | 'book' | 'hire' | 'apply' | 'request' | 'coming_soon'
  primary_action_label: string
  verified_seller: boolean
  metadata?: {
    image_url?: string
    video_url?: string
  }
}

interface FacetOption {
  id: string
  label: string
  count: number
}

interface CatalogFacets {
  company_types: FacetOption[]
  company_categories: FacetOption[]
  business_activities: FacetOption[]
}

interface CatalogActionResponse {
  message: string
  next_step: string
  payment_intent?: PaymentIntent
}

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? ''

function getStoredAuth() {
  const token = window.localStorage.getItem('valley.session.token')
  const userId = window.localStorage.getItem('valley.session.user-id')
  return { token, userId }
}

function setStoredAuth(token: string, userId: string) {
  window.localStorage.setItem('valley.session.token', token)
  window.localStorage.setItem('valley.session.user-id', userId)
}

function clearStoredAuth() {
  window.localStorage.removeItem('valley.session.token')
  window.localStorage.removeItem('valley.session.user-id')
}

function App() {
  const [offers, setOffers] = useState<Offer[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')

  
  const [currentView, setCurrentView] = useState<'consumer' | 'b2b' | 'tracking'>('consumer')

  
  const [auth, setAuth] = useState(getStoredAuth())
  const [isLoginOpen, setIsLoginOpen] = useState(false)

  const [lat, setLat] = useState<string>('-23.5505')
  const [lng, setLng] = useState<string>('-46.6333')
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

  const createCatalogAction = async (scheduledAt?: string, note?: string): Promise<CatalogActionResponse> => {
    if (!activeOffer) throw new Error('Selecione uma oferta para continuar.')
    if (!auth.token || !auth.userId) throw new Error('Usuario nao autenticado.')

    const response = await fetch(`${API_HUB_URL}/gateway/catalog/actions`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${auth.token}`
      },
      body: JSON.stringify({
        offer_id: activeOffer.offer_id,
        action: activeOffer.consumer_action,
        customer_user_id: auth.userId,
        idempotency_key: activeIntentKey,
        scheduled_at: scheduledAt || null,
        note: note || null,
        quantity: 1,
      }),
    })
    const payload = await response.json()
    if (!response.ok) {
      throw new Error(payload.detail || 'Nao foi possivel concluir a solicitacao.')
    }

    if (payload.next_step === 'payment_required' && payload.payment_intent) {
      setPaymentIntent(payload.payment_intent)
      setTimeout(() => {
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
    const params = new URLSearchParams()
    params.append('limit', '50')
    if (lat && lng) {
      params.append('lat', lat)
      params.append('lng', lng)
    }
    if (query.trim()) params.append('q', query.trim())
    if (selectedCategory) {
      params.append('category', selectedCategory)
    }
    if (selectedType) params.append('offer_type', selectedType)
    if (selectedCompanyType) params.append('company_type', selectedCompanyType)
    if (selectedCompanyCategory) params.append('company_category', selectedCompanyCategory)
    if (selectedBusinessActivity) params.append('business_activity', selectedBusinessActivity)

    fetch(`${API_HUB_URL}/gateway/catalog/offers?${params.toString()}`)
      .then(async res => {
        if (!res.ok) throw new Error(`Falha HTTP ${res.status}`)
        return res.json()
      })
      .then(data => {
        const remoteOffers = data.data ?? []
        setOffers(remoteOffers)
        setFacets(data.facets ?? {
          company_types: [],
          company_categories: [],
          business_activities: [],
        })
        if (data.partial) setError('Algumas fontes estao temporariamente indisponiveis.')
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
          <img 
            src="/assets/brand/all-in-one-logo-light-official.png" 
            alt="All-in-One" 
            style={{ height: '32px', width: 'auto' }} 
          />
          <div style={{ width: '2px', height: '24px', background: 'rgba(255,255,255,0.2)' }}></div>
          <img 
            src="/assets/brand/valley-logo-official.png" 
            alt="Valley" 
            style={{ height: '28px', width: 'auto' }} 
          />
        </div>
        <nav style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button className="btn-link" style={{ color: '#fff', fontWeight: currentView === 'consumer' ? 'bold' : 'normal' }} onClick={() => setCurrentView('consumer')}>Ofertas</button>
          <button className="btn-link" style={{ color: '#fff', fontWeight: currentView === 'b2b' ? 'bold' : 'normal' }} onClick={() => setCurrentView('b2b')}>Lojista (B2B)</button>
          <button className="btn-link" style={{ color: '#fff', fontWeight: currentView === 'tracking' ? 'bold' : 'normal' }} onClick={() => setCurrentView('tracking')}>GPS (WebSockets)</button>
          {auth.token ? (
            <>
              <button className="btn-link" style={{ color: '#fff' }} onClick={() => setIsOrdersOpen(true)}>Meus Pedidos</button>
              <button className="btn-link" style={{ color: '#fff' }} onClick={() => { clearStoredAuth(); setAuth({token: null, userId: null}) }}>Sair</button>
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
          <p>Produtos, alimentos e servicos organizados de um jeito simples.</p>
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
            ].map(type => (
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
                {facets.company_types.map(option => (
                  <option key={option.id} value={option.id}>{option.label} ({option.count})</option>
                ))}
              </select>
            </label>
            <label>
              <span>Area do negocio</span>
              <select value={selectedCompanyCategory} onChange={(event) => setSelectedCompanyCategory(event.target.value)}>
                <option value="">Todas as areas</option>
                {facets.company_categories.map(option => (
                  <option key={option.id} value={option.id}>{option.label} ({option.count})</option>
                ))}
              </select>
            </label>
            <label>
              <span>O que faz</span>
              <select value={selectedBusinessActivity} onChange={(event) => setSelectedBusinessActivity(event.target.value)}>
                <option value="">Todos os ramos de atividade</option>
                {facets.business_activities.map(option => (
                  <option key={option.id} value={option.id}>{option.label} ({option.count})</option>
                ))}
              </select>
            </label>
          </div>

          <div className="pills-container">
            <button
              type="button"
              className={`pill ${selectedCategory === null ? 'active' : ''}`}
              onClick={() => setSelectedCategory(null)}
            >
              Todas as categorias
            </button>
            {categories.map(category => (
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
                <div className="media-container" style={{ position: 'relative', height: '160px', overflow: 'hidden', borderRadius: '4px', marginBottom: '12px', border: '1px solid #d4ddd8' }}>
                  <img src={(offer as any).metadata?.image_url || 'https://via.placeholder.com/400x300?text=Sem+Imagem'} alt={offer.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  {(offer as any).metadata?.video_url && (
                    <video 
                      src={(offer as any).metadata?.video_url} 
                      muted 
                      loop 
                      onMouseOver={(e) => e.currentTarget.play()} 
                      onMouseOut={(e) => { e.currentTarget.pause(); e.currentTarget.currentTime = 0; }}
                      style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0, transition: 'opacity 0.3s' }}
                      onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
                      onMouseLeave={(e) => e.currentTarget.style.opacity = '0'}
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
                <div className="offer-meta">
                  <span className="price">
                    {offer.price_amount ? `R$ ${Number(offer.price_amount).toFixed(2).replace('.', ',')}` : 'Sob orcamento'}
                  </span>
                  <button
                    className="offer-action"
                    disabled={!['buy', 'book', 'hire', 'request'].includes(offer.consumer_action)}
                    onClick={() => handleActionClick(offer)}
                  >
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
      </main>
      )}

      <CheckoutModal
        key={`checkout-${activeIntentKey}`}
        isOpen={isCheckoutOpen}
        onClose={() => setIsCheckoutOpen(false)}
        onConfirm={() => createCatalogAction()}
        offerTitle={activeOffer?.title ?? ''}
        priceAmount={activeOffer?.price_amount ?? null}
      />

      <BookingModal
        key={`booking-${activeIntentKey}`}
        isOpen={isBookingOpen}
        onClose={() => setIsBookingOpen(false)}
        onConfirm={createCatalogAction}
        offerTitle={activeOffer?.title ?? ''}
      />
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onSuccess={(token, userId) => {
          setStoredAuth(token, userId)
          setAuth({ token, userId })
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

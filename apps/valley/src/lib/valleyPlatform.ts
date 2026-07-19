export interface Offer {
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
  consumer_action: 'view' | 'buy' | 'book' | 'hire' | 'request' | 'coming_soon'
  primary_action_label: string
  verified_seller: boolean
  metadata?: {
    image_url?: string
    video_url?: string
  }
}

export interface FacetOption {
  id: string
  label: string
  count: number
}

export interface CatalogFacets {
  company_types: FacetOption[]
  company_categories: FacetOption[]
  business_activities: FacetOption[]
}

export interface PaymentIntent {
  amount: string
  order_id: string
}

export interface CatalogActionResponse {
  message: string
  next_step: string
  payment_intent?: PaymentIntent
}

export interface OrderItem {
  id: string
  kind: 'order' | 'appointment' | 'service'
  title: string
  status: string
  amount_brl?: string | null
  scheduled_at?: string | null
  created_at?: string
}

export interface CommercialMetrics {
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
  bi_records: number
}

export interface DemoSession {
  token: string
  userId: string
  email: string
  source: 'email' | 'google'
}

export interface ModuleShowcaseItem {
  id: string
  title: string
  summary: string
  journey: string
  media: string
}

interface DemoUser {
  userId: string
  email: string
  password: string
  source: 'email' | 'google'
}

interface DemoReview {
  orderId: string
  rating: number
}

interface DemoSupportCase {
  orderId: string
  kind: 'support' | 'dispute'
  status: 'open' | 'resolved'
}

interface DemoCatalogFilters {
  q?: string
  category?: string | null
  offer_type?: string | null
  company_type?: string
  company_category?: string
  business_activity?: string
}

interface OfferDraft {
  offer_type: string
  category_id: string
  title: string
  short_description: string
  price_amount: number
  availability_type: string
  location_type: string
  source_module: string
}

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL?.trim() ?? ''
const DEMO_USERS_KEY = 'valley.demo.users'
const DEMO_OFFERS_KEY = 'valley.demo.offers'
const DEMO_ORDERS_KEY = 'valley.demo.orders'
const DEMO_REVIEWS_KEY = 'valley.demo.reviews'
const DEMO_SUPPORT_KEY = 'valley.demo.support'
const DEMO_MODE_KEY = 'valley.session.mode'

const companyTypes: Record<string, string> = {
  business: 'Lojas e empresas',
  professional: 'Profissionais autonomos',
  healthcare: 'Clinicas e saude',
  logistics: 'Operacao logistica',
}

const companyCategories: Record<string, string> = {
  marketplace: 'Marketplace',
  services: 'Servicos',
  health: 'Saude',
  mobility: 'Mobilidade',
  finance: 'Financeiro',
  jobs: 'Trabalho e talentos',
}

const businessActivities: Record<string, string> = {
  grocery: 'Mercado e abastecimento',
  beauty: 'Bem-estar e beleza',
  repair: 'Reparos e manutencao',
  diagnostics: 'Diagnostico clinico',
  delivery: 'Entregas e coletas',
  staffing: 'Selecao e recrutamento',
}

const demoVideoUrls = [
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
]

const defaultOffers: Offer[] = [
  buildOffer('offer-market-1', 'Cesta premium entregue em 30 minutos', 'Mercado com reposicao inteligente, cashback em Pepitas e entrega monitorada.', '149.90', 'Comida e Mercado', 'food', 'marketplace', 'Valley Fresh Center', 'Pinheiros, Sao Paulo', 'buy', 'business', 'marketplace', 'grocery', ['#133C55', '#3BC9DB'], 0),
  buildOffer('offer-service-1', 'Eletricista certificado com agenda hoje', 'Servico com checklist, previsao de chegada e suporte pos-atendimento.', '210.00', 'Casa, Reparos e Imoveis', 'service', 'services', 'Valley Home Care', 'Moema, Sao Paulo', 'hire', 'professional', 'services', 'repair', ['#3F2A56', '#F59E0B'], 1),
  buildOffer('offer-health-1', 'Consulta online com psicologa e prontuario seguro', 'Agendamento com teleatendimento, lembretes e historico protegido.', '189.00', 'Saude e Bem-estar', 'service', 'health', 'Valley Care Digital', 'Atendimento nacional', 'book', 'healthcare', 'health', 'diagnostics', ['#0E7490', '#22C55E'], 2),
  buildOffer('offer-mob-1', 'Entrega expressa com rastreio ao vivo', 'Coleta, auditoria de rota e notificacoes para consumidor e lojista.', '39.90', 'Mobilidade, Entregas e Logistica', 'service', 'delivery', 'Valley Flash Logistics', 'Berrini, Sao Paulo', 'request', 'logistics', 'mobility', 'delivery', ['#111827', '#38BDF8'], 3),
  buildOffer('offer-finance-1', 'Carteira Valley com bonus de onboarding', 'Wallet, split financeiro e pagamentos protegidos para novos clientes.', '59.00', 'Beneficios, Wallet e Recompensas', 'product', 'finance', 'Valley Pay', 'Disponivel no app', 'buy', 'business', 'finance', 'grocery', ['#0F172A', '#8B5CF6'], 0),
  buildOffer('offer-jobs-1', 'Pacote curriculo + entrevista com IA', 'Jornada de candidatura com analise de perfil, vagas e feedback.', '89.90', 'Negocios e Profissionais', 'service', 'jobs', 'Valley Talent Hub', 'Remoto', 'book', 'professional', 'jobs', 'staffing', ['#1D4ED8', '#A855F7'], 1),
  buildOffer('offer-vision-1', 'Inspecao visual com IA para estoque e documentos', 'Captura automatica para documentos, qualidade e conformidade.', '320.00', 'Tecnologia, Seguranca e IA', 'service', 'vision', 'Valley Vision Labs', 'Laboratorio remoto', 'hire', 'business', 'services', 'diagnostics', ['#312E81', '#22D3EE'], 2),
  buildOffer('offer-property-1', 'Tour guiado e proposta digital de imovel', 'Documentacao, agenda de visita e assinatura integrada.', null, 'Casa, Reparos e Imoveis', 'service', 'property', 'Valley Property Match', 'Vila Mariana, Sao Paulo', 'request', 'business', 'services', 'repair', ['#14532D', '#84CC16'], 3),
]

const defaultOrders: OrderItem[] = [
  {
    id: 'ord-demo-1',
    kind: 'order',
    title: 'Cesta premium entregue em 30 minutos',
    status: 'completed',
    amount_brl: '149.90',
    created_at: isoDaysAgo(4),
  },
  {
    id: 'ord-demo-2',
    kind: 'appointment',
    title: 'Consulta online com psicologa e prontuario seguro',
    status: 'accepted',
    amount_brl: '189.00',
    scheduled_at: isoDaysFromNow(1),
    created_at: isoDaysAgo(1),
  },
]

export const moduleShowcase: ModuleShowcaseItem[] = [
  moduleItem('identity', 'Identity', 'Login, cadastro, sessoes e consentimento LGPD.', 'Acesso seguro, autenticao Google e gestao de identidade.', 'Login, KYC e sessoes'),
  moduleItem('business', 'Business', 'Empresas, filiais, catalogos e vinculos operacionais.', 'Onboarding de sellers e operacao comercial multiempresa.', 'Empresas e filiais'),
  moduleItem('permissions', 'Permissions', 'Papeis, permissoes, politicas e aprovacoes.', 'Governanca de acesso por perfil, modulo e acao.', 'RBAC e auditoria'),
  moduleItem('finance', 'Finance', 'Wallet, split, faturas e ledger auditavel.', 'Pagamentos, escrows e trilha financeira do pedido.', 'Wallet e split'),
  moduleItem('marketplace', 'Marketplace', 'Vitrines, produtos, catalogo e descoberta.', 'Busca regional com filtros, imagens e jornada de compra.', 'Catalogo multivendedor'),
  moduleItem('stock', 'Stock', 'Estoque, reserva e disponibilidade em tempo real.', 'Controle de saldo com impacto direto no catalogo.', 'Reserva de inventario'),
  moduleItem('delivery', 'Delivery', 'Entregas, coletas e rastreio da jornada.', 'Pedidos com tracking ao vivo e prova de entrega.', 'Tracking operacional'),
  moduleItem('riders', 'Riders', 'Operacao do entregador e telemetria.', 'Acompanhamento de rota, sinal e eventos de campo.', 'Jornada do entregador'),
  moduleItem('services', 'Services', 'Prestadores, disponibilidade e contratacoes.', 'Agendamento, solicitacao e avaliacao do servico.', 'Prestadores e agenda'),
  moduleItem('mobility', 'Mobility', 'Deslocamentos, corridas e roteamento.', 'Solicitacoes urbanas com status em tempo real.', 'Corridas e trajeto'),
  moduleItem('jobs', 'Jobs', 'Vagas, curriculos e fluxo de recrutamento.', 'Candidatura guiada com trilha auditavel.', 'Talent marketplace'),
  moduleItem('erp', 'ERP', 'Operacao interna, pedidos e consolidacao.', 'Visao de backoffice para sellers e operacao.', 'Backoffice integrado'),
  moduleItem('wms', 'WMS', 'Armazem, separacao e expedicao.', 'Preparacao de pedidos e eventos de deposito.', 'Separacao e expedicao'),
  moduleItem('tms', 'TMS', 'Transporte, roteirizacao e entregas externas.', 'Planejamento logistico e distribuicao.', 'Rota e frota'),
  moduleItem('crm', 'CRM', 'Relacionamento, tickets e historico comercial.', 'Atendimento, engajamento e retencao.', 'Clientes e funil'),
  moduleItem('bpm', 'BPM', 'Fluxos, etapas e aprovacoes cross-module.', 'Orquestracao de processos entre equipes.', 'Fluxos e SLAs'),
  moduleItem('document', 'GED / ECM', 'Documentos, anexos e compliance documental.', 'Arquivos e evidencias anexadas a operacoes.', 'Repositorio documental'),
  moduleItem('hr', 'HR', 'Pessoas, treinamentos e operacao de time.', 'Capacitacao e trilhas para operacao e sellers.', 'Equipe e capacitacao'),
  moduleItem('health', 'Health', 'Consultas, agendamentos e atendimento digital.', 'Prontuario simplificado e jornadas de cuidado.', 'Cuidado digital'),
  moduleItem('vision', 'Vision', 'IA visual para provas, leitura e classificacao.', 'OCR, capturas e inspecoes operacionais.', 'Visao computacional'),
  moduleItem('legal', 'Legal', 'Contratos, disputas e trilha juridica.', 'Gestao de casos e evidencias de suporte.', 'Contratos e casos'),
  moduleItem('property', 'Property', 'Imoveis, visitas e documentacao de proposta.', 'Gestao de leads e visitas guiadas.', 'Vendas imobiliarias'),
  moduleItem('bi', 'BI', 'Indicadores, funis e consolidacao executiva.', 'Leitura de conversao, atendimento e receita.', 'Dashboards executivos'),
  moduleItem('ai_core', 'AI Core', 'Orquestracao de modelos, prompts e assistentes.', 'Automacoes e insights para vendedor e consumidor.', 'Automacao inteligente'),
  moduleItem('api_hub', 'API Hub', 'Gateway, contratos e agregacao entre servicos.', 'Conecta todos os modulos e microservicos da jornada.', 'Gateway unificado'),
]

export function isDemoModeEnabled() {
  return !API_HUB_URL || window.localStorage.getItem(DEMO_MODE_KEY) === 'true'
}

export async function signInWithEmail(email: string, password: string, createAccount: boolean): Promise<DemoSession> {
  const normalizedEmail = email.trim().toLowerCase()
  validateEmail(normalizedEmail)
  if (password.length < 6) {
    throw new Error('A senha precisa ter ao menos 6 caracteres.')
  }

  if (!isDemoModeEnabled()) {
    try {
      if (createAccount) {
        const now = new Date().toISOString()
        await postJson('/registrations', {
          full_name: normalizedEmail.split('@')[0].replace(/[._-]+/g, ' '),
          email: normalizedEmail,
          password_hash: password,
          document_cpf: buildCpf(normalizedEmail),
          terms_accepted_at: now,
          lgpd_consent_at: now,
        })
      }
      const session = await postJson('/auth/login', { email: normalizedEmail, password })
      window.localStorage.removeItem(DEMO_MODE_KEY)
      return { token: session.access_token, userId: session.user_id, email: normalizedEmail, source: 'email' }
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }

  const users = readStorage<DemoUser[]>(DEMO_USERS_KEY, defaultUsers())
  let user = users.find((candidate) => candidate.email === normalizedEmail)
  if (createAccount && !user) {
    user = { userId: `usr-${slugify(normalizedEmail)}-${randomId(6)}`, email: normalizedEmail, password, source: 'email' }
    users.unshift(user)
    writeStorage(DEMO_USERS_KEY, users)
  }
  if (!user || user.password !== password) {
    throw new Error('E-mail ou senha invalidos.')
  }
  return demoSessionFor(user, 'email')
}

export async function signInWithGoogle(email: string): Promise<DemoSession> {
  const normalizedEmail = email.trim().toLowerCase()
  validateEmail(normalizedEmail)

  if (!isDemoModeEnabled()) {
    try {
      const googlePassword = buildGooglePassword(normalizedEmail)
      await signInWithEmail(normalizedEmail, googlePassword, true)
      const session = await postJson('/auth/login', { email: normalizedEmail, password: googlePassword })
      window.localStorage.removeItem(DEMO_MODE_KEY)
      return { token: session.access_token, userId: session.user_id, email: normalizedEmail, source: 'google' }
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }

  const users = readStorage<DemoUser[]>(DEMO_USERS_KEY, defaultUsers())
  let user = users.find((candidate) => candidate.email === normalizedEmail)
  if (!user) {
    user = { userId: `usr-google-${slugify(normalizedEmail)}`, email: normalizedEmail, password: buildGooglePassword(normalizedEmail), source: 'google' }
    users.unshift(user)
    writeStorage(DEMO_USERS_KEY, users)
  }
  return demoSessionFor(user, 'google')
}

export async function listOffers(filters: DemoCatalogFilters): Promise<{ offers: Offer[]; facets: CatalogFacets; partial: boolean }> {
  if (!isDemoModeEnabled()) {
    try {
      const params = new URLSearchParams()
      params.append('limit', '50')
      if (filters.q?.trim()) params.append('q', filters.q.trim())
      if (filters.category) params.append('category', filters.category)
      if (filters.offer_type) params.append('offer_type', filters.offer_type)
      if (filters.company_type) params.append('company_type', filters.company_type)
      if (filters.company_category) params.append('company_category', filters.company_category)
      if (filters.business_activity) params.append('business_activity', filters.business_activity)
      const data = await getJson(`/gateway/catalog/offers?${params.toString()}`)
      return { offers: data.data ?? [], facets: data.facets ?? emptyFacets(), partial: Boolean(data.partial) }
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }

  const offers = readStorage<Offer[]>(DEMO_OFFERS_KEY, defaultOffers)
  const normalizedQuery = filters.q?.trim().toLowerCase() ?? ''
  const filtered = offers.filter((offer) => {
    if (filters.category && offer.consumer_category !== filters.category) return false
    if (filters.offer_type && offer.offer_type !== filters.offer_type) return false
    if (filters.company_type && getOfferMeta(offer, 'company_type') !== filters.company_type) return false
    if (filters.company_category && getOfferMeta(offer, 'company_category') !== filters.company_category) return false
    if (filters.business_activity && getOfferMeta(offer, 'business_activity') !== filters.business_activity) return false
    if (!normalizedQuery) return true
    const haystack = [offer.title, offer.short_description, offer.description, offer.provider_label, offer.source_module].join(' ').toLowerCase()
    return haystack.includes(normalizedQuery)
  })
  return { offers: filtered, facets: buildFacets(offers), partial: false }
}

export async function createCatalogAction(params: {
  offer: Offer
  customerUserId: string
  idempotencyKey: string
  scheduledAt?: string
  note?: string
  token?: string | null
}): Promise<CatalogActionResponse> {
  if (!isDemoModeEnabled() && params.token) {
    try {
      return await postJson('/gateway/catalog/actions', {
        offer_id: params.offer.offer_id,
        action: params.offer.consumer_action,
        customer_user_id: params.customerUserId,
        idempotency_key: params.idempotencyKey,
        scheduled_at: params.scheduledAt ?? null,
        note: params.note ?? null,
        quantity: 1,
      }, params.token)
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }

  const orders = readStorage<OrderItem[]>(DEMO_ORDERS_KEY, defaultOrders)
  const orderId = `ord-${randomId(8)}`
  const needsPayment = ['buy', 'hire'].includes(params.offer.consumer_action)
  orders.unshift({
    id: orderId,
    kind: params.offer.consumer_action === 'book' ? 'appointment' : params.offer.offer_type === 'service' ? 'service' : 'order',
    title: params.offer.title,
    status: needsPayment ? 'awaiting_payment' : 'accepted',
    amount_brl: params.offer.price_amount ?? '0.00',
    scheduled_at: params.scheduledAt ?? null,
    created_at: new Date().toISOString(),
  })
  writeStorage(DEMO_ORDERS_KEY, orders)

  if (needsPayment) {
    return {
      message: 'Pedido criado e reservado. Prossiga para o pagamento seguro.',
      next_step: 'payment_required',
      payment_intent: { amount: params.offer.price_amount ?? '0.00', order_id: orderId },
    }
  }
  return {
    message: params.offer.consumer_action === 'book' ? 'Horario solicitado com sucesso. Voce recebera confirmacao no app.' : 'Solicitacao enviada com sucesso.',
    next_step: 'completed',
  }
}

export async function authorizePayment(paymentIntent: PaymentIntent, token?: string | null): Promise<{ message: string }> {
  if (!isDemoModeEnabled() && token) {
    try {
      return await postJson('/gateway/payments/sandbox/authorize', {
        order_id: paymentIntent.order_id,
        method: 'pix_sandbox',
        idempotency_key: `payment-${paymentIntent.order_id}`,
      }, token)
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }
  const orders = readStorage<OrderItem[]>(DEMO_ORDERS_KEY, defaultOrders)
  writeStorage(DEMO_ORDERS_KEY, orders.map((item) => item.id === paymentIntent.order_id ? { ...item, status: 'paid' } : item))
  return { message: 'Pagamento autorizado em ambiente seguro de demonstracao.' }
}

export async function getOrders(token?: string | null): Promise<OrderItem[]> {
  if (!isDemoModeEnabled() && token) {
    try {
      const data = await getJson('/gateway/consumer/orders', token)
      return data.data ?? []
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }
  return readStorage<OrderItem[]>(DEMO_ORDERS_KEY, defaultOrders)
}

export async function submitReview(orderId: string, rating: number, comment: string, token?: string | null): Promise<{ message: string }> {
  if (!isDemoModeEnabled() && token) {
    try {
      return await postJson(`/gateway/consumer/orders/${orderId}/reviews`, {
        rating,
        comment: comment || null,
        idempotency_key: `review-${orderId}-${randomId(8)}`,
      }, token)
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }
  const reviews = readStorage<DemoReview[]>(DEMO_REVIEWS_KEY, [])
  reviews.push({ orderId, rating })
  writeStorage(DEMO_REVIEWS_KEY, reviews)
  return { message: 'Avaliacao registrada com sucesso na simulacao.' }
}

export async function submitSupportCase(orderId: string, kind: 'support' | 'dispute', subject: string, message: string, desiredResolution: string, token?: string | null): Promise<{ message: string }> {
  if (!isDemoModeEnabled() && token) {
    try {
      return await postJson(`/gateway/consumer/orders/${orderId}/support`, {
        kind,
        subject: subject || null,
        message,
        desired_resolution: desiredResolution || null,
        idempotency_key: `support-${orderId}-${randomId(8)}`,
      }, token)
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }
  const supportCases = readStorage<DemoSupportCase[]>(DEMO_SUPPORT_KEY, [])
  supportCases.push({ orderId, kind, status: 'open' })
  writeStorage(DEMO_SUPPORT_KEY, supportCases)
  return { message: 'Caso aberto com sucesso na central demonstrativa.' }
}

export async function getCommercialMetrics(): Promise<CommercialMetrics> {
  if (!isDemoModeEnabled()) {
    try {
      const data = await getJson('/gateway/insights/commercial')
      return {
        orders_total: data.orders_total ?? 0,
        orders_paid: data.orders_paid ?? 0,
        orders_completed: data.orders_completed ?? 0,
        reviews_total: data.reviews_total ?? 0,
        average_rating: data.average_rating ?? null,
        support_cases_total: data.support_cases_total ?? 0,
        support_cases_open: data.support_cases_open ?? 0,
        support_cases_resolved: data.support_cases_resolved ?? 0,
        conversion_rate_percent: data.conversion_rate_percent ?? 0,
        crm_records: data.crm_records ?? 0,
        bi_records: data.bi_records ?? 0,
      }
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }

  const orders = readStorage<OrderItem[]>(DEMO_ORDERS_KEY, defaultOrders)
  const reviews = readStorage<DemoReview[]>(DEMO_REVIEWS_KEY, [{ orderId: 'ord-demo-1', rating: 5 }])
  const supportCases = readStorage<DemoSupportCase[]>(DEMO_SUPPORT_KEY, [{ orderId: 'ord-demo-2', kind: 'support', status: 'open' }])
  const paid = orders.filter((item) => ['paid', 'accepted', 'in_progress', 'delivered', 'completed'].includes(item.status)).length
  const completed = orders.filter((item) => ['delivered', 'completed'].includes(item.status)).length
  const averageRating = reviews.length ? reviews.reduce((total, item) => total + item.rating, 0) / reviews.length : null
  return {
    orders_total: orders.length,
    orders_paid: paid,
    orders_completed: completed,
    reviews_total: reviews.length,
    average_rating: averageRating,
    support_cases_total: supportCases.length,
    support_cases_open: supportCases.filter((item) => item.status === 'open').length,
    support_cases_resolved: supportCases.filter((item) => item.status === 'resolved').length,
    conversion_rate_percent: orders.length ? Number(((paid / orders.length) * 100).toFixed(2)) : 0,
    crm_records: orders.length * 3,
    bi_records: moduleShowcase.length * 2,
  }
}

export async function getAvailableSlots() {
  if (!isDemoModeEnabled()) {
    try {
      const data = await getJson('/services/providers/mock-provider/time-slots?date=2026-07-16')
      return data.available_slots ?? ['09:00', '10:00', '11:30', '14:00', '15:30']
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }
  return ['09:00', '10:00', '11:30', '14:00', '15:30', '17:00']
}

export async function reserveSlot(slot: string) {
  if (!isDemoModeEnabled()) {
    try {
      await postJson('/services/providers/mock-provider/reserve-slot', { slot, customer_id: 'cust-123' })
      return { message: `Horario ${slot} reservado com sucesso.` }
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }
  return { message: `Horario ${slot} reservado com sucesso no ambiente de teste.` }
}

export async function publishOffer(draft: OfferDraft) {
  if (!isDemoModeEnabled()) {
    try {
      const created = await postJson('/gateway/business/valley/catalog/offers', draft)
      await putJson(`/gateway/business/valley/catalog/offers/${created.id}/status`, { status: 'published' })
      return { message: 'Oferta publicada com sucesso no Valley.' }
    } catch {
      window.localStorage.setItem(DEMO_MODE_KEY, 'true')
    }
  }

  const offers = readStorage<Offer[]>(DEMO_OFFERS_KEY, defaultOffers)
  offers.unshift(buildOffer(
    `offer-published-${randomId(6)}`,
    draft.title || 'Oferta publicada',
    draft.short_description || 'Oferta criada no wizard do lojista.',
    draft.price_amount ? draft.price_amount.toFixed(2) : null,
    draft.category_id || 'Negocios e Profissionais',
    normalizeOfferType(draft.offer_type),
    draft.source_module || 'marketplace',
    'Seu negocio no Valley',
    draft.location_type === 'online' ? 'Atendimento online' : 'Area local',
    draft.offer_type === 'service' ? 'hire' : 'buy',
    'business',
    'marketplace',
    'staffing',
    ['#111827', '#EC4899'],
    0,
  ))
  writeStorage(DEMO_OFFERS_KEY, offers)
  return { message: 'Oferta publicada com sucesso na vitrine demonstrativa.' }
}

function buildOffer(
  offerId: string,
  title: string,
  summary: string,
  price: string | null,
  category: string,
  type: 'food' | 'product' | 'service',
  module: string,
  provider: string,
  region: string,
  action: 'buy' | 'book' | 'hire' | 'request',
  companyType: string,
  companyCategory: string,
  businessActivity: string,
  imageTheme: [string, string],
  videoIndex: number,
): Offer {
  const imageUrl = buildSvgDataUri(title, module.toUpperCase(), imageTheme[0], imageTheme[1])
  return {
    offer_id: offerId,
    title,
    short_description: summary,
    description: summary,
    price_amount: price,
    price_type: price ? 'fixed' : 'quote',
    consumer_category: category,
    offer_type: type,
    offer_type_label: type === 'food' ? 'Alimentos' : type === 'product' ? 'Produto' : 'Servico',
    source_module: module,
    provider_label: provider,
    region_label: region,
    distance_km: Number((Math.random() * 8 + 0.8).toFixed(1)),
    consumer_action: action,
    primary_action_label: action === 'buy' ? 'Comprar agora' : action === 'book' ? 'Agendar' : action === 'hire' ? 'Contratar' : 'Solicitar',
    verified_seller: true,
    metadata: {
      image_url: `${imageUrl}#company_type=${companyType}&company_category=${companyCategory}&business_activity=${businessActivity}`,
      video_url: demoVideoUrls[videoIndex % demoVideoUrls.length],
    },
  }
}

function buildFacets(offers: Offer[]): CatalogFacets {
  const companyTypeCounts = new Map<string, number>()
  const companyCategoryCounts = new Map<string, number>()
  const businessActivityCounts = new Map<string, number>()
  offers.forEach((offer) => {
    incrementMap(companyTypeCounts, getOfferMeta(offer, 'company_type'))
    incrementMap(companyCategoryCounts, getOfferMeta(offer, 'company_category'))
    incrementMap(businessActivityCounts, getOfferMeta(offer, 'business_activity'))
  })
  return {
    company_types: mapToFacetArray(companyTypeCounts, companyTypes),
    company_categories: mapToFacetArray(companyCategoryCounts, companyCategories),
    business_activities: mapToFacetArray(businessActivityCounts, businessActivities),
  }
}

function emptyFacets(): CatalogFacets {
  return { company_types: [], company_categories: [], business_activities: [] }
}

function defaultUsers(): DemoUser[] {
  return [
    { userId: 'usr-demo-001', email: 'cliente@valley.app', password: 'valley123', source: 'email' },
    { userId: 'usr-demo-google', email: 'google@valley.app', password: buildGooglePassword('google@valley.app'), source: 'google' },
  ]
}

function demoSessionFor(user: DemoUser, source: 'email' | 'google'): DemoSession {
  window.localStorage.setItem(DEMO_MODE_KEY, 'true')
  return { token: `demo-${slugify(user.email)}-${randomId(10)}`, userId: user.userId, email: user.email, source }
}

function validateEmail(email: string) {
  if (!email.includes('@')) {
    throw new Error('Informe um e-mail valido.')
  }
}

function buildCpf(value: string) {
  return `CPF-${slugify(value).replace(/[^a-z0-9]/g, '').slice(0, 11).padEnd(11, '0')}`
}

function buildGooglePassword(email: string) {
  return `valley-${slugify(email).slice(0, 12).padEnd(12, '0')}`
}

function buildSvgDataUri(title: string, subtitle: string, startColor: string, endColor: string) {
  const safeTitle = escapeXml(title.slice(0, 38))
  const safeSubtitle = escapeXml(subtitle.slice(0, 22))
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="${startColor}"/><stop offset="100%" stop-color="${endColor}"/></linearGradient></defs><rect width="1200" height="800" fill="url(#g)"/><circle cx="1050" cy="150" r="140" fill="rgba(255,255,255,0.18)"/><circle cx="180" cy="650" r="180" fill="rgba(255,255,255,0.12)"/><text x="80" y="140" fill="white" font-size="46" font-family="Segoe UI, Arial, sans-serif" font-weight="700">VALLEY</text><text x="80" y="220" fill="white" font-size="62" font-family="Segoe UI, Arial, sans-serif" font-weight="700">${safeTitle}</text><text x="80" y="300" fill="rgba(255,255,255,0.86)" font-size="34" font-family="Segoe UI, Arial, sans-serif">${safeSubtitle}</text></svg>`
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}

function escapeXml(value: string) {
  return value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&apos;')
}

function getOfferMeta(offer: Offer, key: 'company_type' | 'company_category' | 'business_activity') {
  const hash = offer.metadata?.image_url?.split('#')[1] ?? ''
  const params = new URLSearchParams(hash)
  return params.get(key) ?? ''
}

function incrementMap(map: Map<string, number>, key: string) {
  if (!key) return
  map.set(key, (map.get(key) ?? 0) + 1)
}

function mapToFacetArray(map: Map<string, number>, labels: Record<string, string>): FacetOption[] {
  return Array.from(map.entries()).map(([id, count]) => ({ id, label: labels[id] ?? id, count }))
}

async function getJson(path: string, token?: string) {
  return fetchJson(path, { method: 'GET' }, token)
}

async function postJson(path: string, body: unknown, token?: string) {
  return fetchJson(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }, token)
}

async function putJson(path: string, body: unknown, token?: string) {
  return fetchJson(path, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }, token)
}

async function fetchJson(path: string, init: RequestInit, token?: string) {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  headers.set('X-Valley-Api-Version', '1')
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  const response = await fetch(`${API_HUB_URL}${path}`, { ...init, headers })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = typeof payload?.detail === 'string' ? payload.detail : `Falha HTTP ${response.status}`
    throw new Error(detail)
  }
  return payload
}

function readStorage<T>(key: string, fallback: T): T {
  const raw = window.localStorage.getItem(key)
  if (!raw) {
    writeStorage(key, fallback)
    return fallback
  }
  try {
    return JSON.parse(raw) as T
  } catch {
    writeStorage(key, fallback)
    return fallback
  }
}

function writeStorage<T>(key: string, value: T) {
  window.localStorage.setItem(key, JSON.stringify(value))
}

function randomId(length: number) {
  return Math.random().toString(36).slice(2, 2 + length)
}

function slugify(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '-')
}

function normalizeOfferType(value: string): 'food' | 'product' | 'service' {
  if (value === 'food') return 'food'
  if (value === 'service' || value === 'appointment') return 'service'
  return 'product'
}

function moduleItem(id: string, title: string, summary: string, journey: string, media: string): ModuleShowcaseItem {
  return { id, title, summary, journey, media }
}

function isoDaysAgo(days: number) {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString()
}

function isoDaysFromNow(days: number) {
  const date = new Date()
  date.setDate(date.getDate() + days)
  date.setHours(14, 0, 0, 0)
  return date.toISOString()
}

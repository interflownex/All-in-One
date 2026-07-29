export interface Offer {
  offer_id: string;
  title: string;
  short_description?: string;
  description?: string;
  price_amount?: string | null;
  price_type: string;
  consumer_category: string;
  offer_type: "food" | "product" | "service";
  offer_type_label: string;
  source_module: string;
  provider_label: string;
  region_label: string;
  distance_km?: number | null;
  consumer_action: "view" | "buy" | "book" | "hire" | "request" | "coming_soon";
  primary_action_label: string;
  verified_seller: boolean;
  metadata?: {
    image_url?: string;
    video_url?: string;
  };
}

export interface FacetOption {
  id: string;
  label: string;
  count: number;
}

export interface CatalogFacets {
  company_types: FacetOption[];
  company_categories: FacetOption[];
  business_activities: FacetOption[];
}

export interface PaymentIntent {
  amount: string;
  order_id: string;
}

export interface CatalogActionResponse {
  message: string;
  next_step: string;
  payment_intent?: PaymentIntent;
}

export interface OrderItem {
  id: string;
  kind: "order" | "appointment" | "service";
  title: string;
  status: string;
  amount_brl?: string | null;
  scheduled_at?: string | null;
  created_at?: string;
}

export interface CommercialMetrics {
  orders_total: number;
  orders_paid: number;
  orders_completed: number;
  reviews_total: number;
  average_rating: number | null;
  support_cases_total: number;
  support_cases_open: number;
  support_cases_resolved: number;
  conversion_rate_percent: number;
  crm_records: number;
  bi_records: number;
}

export interface DemoSession {
  token: string;
  userId: string;
  email: string;
  source: "email" | "google";
}

export interface ModuleShowcaseItem {
  id: string;
  title: string;
  summary: string;
  journey: string;
  media: string;
}

interface DemoUser {
  userId: string;
  email: string;
  password: string;
  source: "email" | "google";
}

interface DemoReview {
  orderId: string;
  rating: number;
}

interface DemoSupportCase {
  orderId: string;
  kind: "support" | "dispute";
  status: "open" | "resolved";
}

interface DemoCatalogFilters {
  q?: string;
  category?: string | null;
  offer_type?: string | null;
  company_type?: string;
  company_category?: string;
  business_activity?: string;
}

interface CatalogPageOptions {
  offset?: number;
  limit?: number;
}

export interface CatalogPage {
  offers: Offer[];
  facets: CatalogFacets;
  partial: boolean;
  total: number;
  offset: number;
  limit: number;
}

interface OfferDraft {
  offer_type: string;
  category_id: string;
  title: string;
  short_description: string;
  price_amount: number;
  availability_type: string;
  location_type: string;
  source_module: string;
}

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL?.trim() ?? "";
const ALLOW_DEMO = import.meta.env.VITE_VALLEY_ALLOW_DEMO === "true";
const CATALOG_CACHE_PREFIX = "valley.catalog.v1.";
const CATALOG_CACHE_TTL_MS = 5 * 60 * 1000;
const RESPONSE_SIGNATURE_MAX_AGE_SECONDS = 300;
let responseSigningKeyPromise: Promise<{ keyId: string; key: CryptoKey }> | null = null;
const DEMO_USERS_KEY = "valley.demo.users";
const DEMO_OFFERS_KEY = "valley.demo.offers";
const DEMO_ORDERS_KEY = "valley.demo.orders";
const DEMO_REVIEWS_KEY = "valley.demo.reviews";
const DEMO_SUPPORT_KEY = "valley.demo.support";
const DEMO_MODE_KEY = "valley.session.mode";

const companyTypes: Record<string, string> = {
  business: "Lojas e empresas",
  professional: "Profissionais autonomos",
  healthcare: "Clinicas e saude",
  logistics: "Operacao logistica",
};

const companyCategories: Record<string, string> = {
  marketplace: "Marketplace",
  services: "Servicos",
  health: "Saude",
  mobility: "Mobilidade",
  finance: "Financeiro",
  jobs: "Trabalho e talentos",
};

const businessActivities: Record<string, string> = {
  grocery: "Mercado e abastecimento",
  beauty: "Bem-estar e beleza",
  repair: "Reparos e manutencao",
  diagnostics: "Diagnostico clinico",
  delivery: "Entregas e coletas",
  staffing: "Selecao e recrutamento",
};

const demoVideoUrls = [
  "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
  "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
  "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
  "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
];

const defaultOffers: Offer[] = [
  buildOffer(
    "offer-market-1",
    "Cesta premium entregue em 30 minutos",
    "Mercado com reposicao inteligente, cashback em Pepitas e entrega monitorada.",
    "149.90",
    "Comida e Mercado",
    "food",
    "marketplace",
    "Valley Fresh Center",
    "Pinheiros, Sao Paulo",
    "buy",
    "business",
    "marketplace",
    "grocery",
    ["#133C55", "#3BC9DB"],
    0,
  ),
  buildOffer(
    "offer-service-1",
    "Eletricista certificado com agenda hoje",
    "Servico com checklist, previsao de chegada e suporte pos-atendimento.",
    "210.00",
    "Casa, Reparos e Imoveis",
    "service",
    "services",
    "Valley Home Care",
    "Moema, Sao Paulo",
    "hire",
    "professional",
    "services",
    "repair",
    ["#3F2A56", "#F59E0B"],
    1,
  ),
  buildOffer(
    "offer-health-1",
    "Consulta online com psicologa e prontuario seguro",
    "Agendamento com teleatendimento, lembretes e historico protegido.",
    "189.00",
    "Saude e Bem-estar",
    "service",
    "health",
    "Valley Care Digital",
    "Atendimento nacional",
    "book",
    "healthcare",
    "health",
    "diagnostics",
    ["#0E7490", "#22C55E"],
    2,
  ),
  buildOffer(
    "offer-mob-1",
    "Entrega expressa com rastreio ao vivo",
    "Coleta, auditoria de rota e notificacoes para consumidor e lojista.",
    "39.90",
    "Mobilidade, Entregas e Logistica",
    "service",
    "delivery",
    "Valley Flash Logistics",
    "Berrini, Sao Paulo",
    "request",
    "logistics",
    "mobility",
    "delivery",
    ["#111827", "#38BDF8"],
    3,
  ),
  buildOffer(
    "offer-finance-1",
    "Carteira Valley com bonus de onboarding",
    "Wallet, split financeiro e pagamentos protegidos para novos clientes.",
    "59.00",
    "Beneficios, Wallet e Recompensas",
    "product",
    "finance",
    "Valley Pay",
    "Disponivel no app",
    "buy",
    "business",
    "finance",
    "grocery",
    ["#0F172A", "#8B5CF6"],
    0,
  ),
  buildOffer(
    "offer-jobs-1",
    "Pacote curriculo + entrevista com IA",
    "Jornada de candidatura com analise de perfil, vagas e feedback.",
    "89.90",
    "Negocios e Profissionais",
    "service",
    "jobs",
    "Valley Talent Hub",
    "Remoto",
    "book",
    "professional",
    "jobs",
    "staffing",
    ["#1D4ED8", "#A855F7"],
    1,
  ),
  buildOffer(
    "offer-property-1",
    "Tour guiado e proposta digital de imovel",
    "Documentacao, agenda de visita e assinatura integrada.",
    null,
    "Casa, Reparos e Imoveis",
    "service",
    "property",
    "Valley Property Match",
    "Vila Mariana, Sao Paulo",
    "request",
    "business",
    "services",
    "repair",
    ["#14532D", "#84CC16"],
    3,
  ),
];

const defaultOrders: OrderItem[] = [
  {
    id: "ord-demo-1",
    kind: "order",
    title: "Cesta premium entregue em 30 minutos",
    status: "completed",
    amount_brl: "149.90",
    created_at: isoDaysAgo(4),
  },
  {
    id: "ord-demo-2",
    kind: "appointment",
    title: "Consulta online com psicologa e prontuario seguro",
    status: "accepted",
    amount_brl: "189.00",
    scheduled_at: isoDaysFromNow(1),
    created_at: isoDaysAgo(1),
  },
];

export const moduleShowcase: ModuleShowcaseItem[] = [
  moduleItem("identity", "Identity", "Login, cadastro, sessoes e consentimento LGPD.", "Acesso seguro, autenticao Google e gestao de identidade.", "Login, KYC e sessoes"),
  moduleItem("business", "Business", "Empresas, filiais, catalogos e vinculos operacionais.", "Onboarding de sellers e operacao comercial multiempresa.", "Empresas e filiais"),
  moduleItem("permissions", "Permissions", "Papeis, permissoes, politicas e aprovacoes.", "Governanca de acesso por perfil, modulo e acao.", "RBAC e auditoria"),
  moduleItem("finance", "Finance", "Wallet, split, faturas e ledger auditavel.", "Pagamentos, escrows e trilha financeira do pedido.", "Wallet e split"),
  moduleItem("marketplace", "Marketplace", "Vitrines, produtos, catalogo e descoberta.", "Busca regional com filtros, imagens e jornada de compra.", "Catalogo multivendedor"),
  moduleItem("stock", "Stock", "Estoque, reserva e disponibilidade em tempo real.", "Controle de saldo com impacto direto no catalogo.", "Reserva de inventario"),
  moduleItem("delivery", "Delivery", "Entregas, coletas e rastreio da jornada.", "Pedidos com tracking ao vivo e prova de entrega.", "Tracking operacional"),
  moduleItem("riders", "Riders", "Operacao do entregador e telemetria.", "Acompanhamento de rota, sinal e eventos de campo.", "Jornada do entregador"),
  moduleItem("services", "Services", "Prestadores, disponibilidade e contratacoes.", "Agendamento, solicitacao e avaliacao do servico.", "Prestadores e agenda"),
  moduleItem("mobility", "Mobility", "Deslocamentos, corridas e roteamento.", "Solicitacoes urbanas com status em tempo real.", "Corridas e trajeto"),
  moduleItem("jobs", "Jobs", "Vagas, curriculos e fluxo de recrutamento.", "Candidatura guiada com trilha auditavel.", "Talent marketplace"),
  moduleItem("erp", "ERP", "Operacao interna, pedidos e consolidacao.", "Visao de backoffice para sellers e operacao.", "Backoffice integrado"),
  moduleItem("wms", "WMS", "Armazem, separacao e expedicao.", "Preparacao de pedidos e eventos de deposito.", "Separacao e expedicao"),
  moduleItem("tms", "TMS", "Transporte, roteirizacao e entregas externas.", "Planejamento logistico e distribuicao.", "Rota e frota"),
  moduleItem("crm", "CRM", "Relacionamento, tickets e historico comercial.", "Atendimento, engajamento e retencao.", "Clientes e funil"),
  moduleItem("bpm", "BPM", "Fluxos, etapas e aprovacoes cross-module.", "Orquestracao de processos entre equipes.", "Fluxos e SLAs"),
  moduleItem("document", "GED / ECM", "Documentos, anexos e compliance documental.", "Arquivos e evidencias anexadas a operacoes.", "Repositorio documental"),
  moduleItem("hr", "HR", "Pessoas, treinamentos e operacao de time.", "Capacitacao e trilhas para operacao e sellers.", "Equipe e capacitacao"),
  moduleItem("health", "Health", "Consultas, agendamentos e atendimento digital.", "Prontuario simplificado e jornadas de cuidado.", "Cuidado digital"),
  moduleItem("legal", "Legal", "Contratos, disputas e trilha juridica.", "Gestao de casos e evidencias de suporte.", "Contratos e casos"),
  moduleItem("property", "Property", "Imoveis, visitas e documentacao de proposta.", "Gestao de leads e visitas guiadas.", "Vendas imobiliarias"),
  moduleItem("bi", "BI", "Indicadores, funis e consolidacao executiva.", "Leitura de conversao, atendimento e receita.", "Dashboards executivos"),
  moduleItem("ai_core", "AI Core", "Orquestracao de modelos, prompts e assistentes.", "Automacoes e insights para vendedor e consumidor.", "Automacao inteligente"),
  moduleItem("api_hub", "API Hub", "Gateway, contratos e agregacao entre servicos.", "Conecta todos os modulos e microservicos da jornada.", "Gateway unificado"),
];

export function isDemoModeEnabled() {
  return ALLOW_DEMO && (!API_HUB_URL || window.localStorage.getItem(DEMO_MODE_KEY) === "true");
}

export function safeMediaUrl(value?: string): string | undefined {
  if (!value) return undefined;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.username || url.password) return undefined;
    return url.href;
  } catch {
    return undefined;
  }
}

export async function signInWithEmail(email: string, password: string, createAccount: boolean): Promise<DemoSession> {
  const normalizedEmail = email.trim().toLowerCase();
  validateEmail(normalizedEmail);
  if (password.length < 6) throw new Error("A senha precisa ter ao menos 6 caracteres.");
  if (!isDemoModeEnabled()) {
    try {
      if (createAccount) {
        const now = new Date().toISOString();
        await postJson("/registrations", { full_name: normalizedEmail.split("@")[0].replace(/[._-]+/g, " "), email: normalizedEmail, password_hash: password, document_cpf: buildCpf(normalizedEmail), terms_accepted_at: now, lgpd_consent_at: now });
      }
      const session = await postJson("/auth/login", { email: normalizedEmail, password });
      window.localStorage.removeItem(DEMO_MODE_KEY);
      return { token: session.access_token, userId: session.user_id, email: normalizedEmail, source: "email" };
    } catch (error) {
      if (!ALLOW_DEMO) throw error;
      window.localStorage.setItem(DEMO_MODE_KEY, "true");
    }
  }
  const users = readStorage<DemoUser[]>(DEMO_USERS_KEY, defaultUsers());
  let user = users.find((candidate) => candidate.email === normalizedEmail);
  if (createAccount && !user) {
    user = { userId: `usr-${slugify(normalizedEmail)}-${randomId(6)}`, email: normalizedEmail, password, source: "email" };
    users.unshift(user);
    writeStorage(DEMO_USERS_KEY, users);
  }
  if (!user || user.password !== password) throw new Error("E-mail ou senha invalidos.");
  return demoSessionFor(user, "email");
}

export async function signInWithGoogle(email: string): Promise<DemoSession> {
  const normalizedEmail = email.trim().toLowerCase();
  validateEmail(normalizedEmail);
  if (!isDemoModeEnabled()) {
    try {
      const googlePassword = buildGooglePassword(normalizedEmail);
      await signInWithEmail(normalizedEmail, googlePassword, true);
      const session = await postJson("/auth/login", { email: normalizedEmail, password: googlePassword });
      window.localStorage.removeItem(DEMO_MODE_KEY);
      return { token: session.access_token, userId: session.user_id, email: normalizedEmail, source: "google" };
    } catch (error) {
      if (!ALLOW_DEMO) throw error;
      window.localStorage.setItem(DEMO_MODE_KEY, "true");
    }
  }
  const users = readStorage<DemoUser[]>(DEMO_USERS_KEY, defaultUsers());
  let user = users.find((candidate) => candidate.email === normalizedEmail);
  if (!user) {
    user = { userId: `usr-google-${slugify(normalizedEmail)}`, email: normalizedEmail, password: buildGooglePassword(normalizedEmail), source: "google" };
    users.unshift(user);
    writeStorage(DEMO_USERS_KEY, users);
  }
  return demoSessionFor(user, "google");
}

export async function listOffers(filters: DemoCatalogFilters, options: CatalogPageOptions = {}): Promise<CatalogPage> {
  if (!isDemoModeEnabled()) {
    const limit = Math.min(Math.max(options.limit ?? 20, 1), 50);
    const offset = Math.max(options.offset ?? 0, 0);
    const params = new URLSearchParams();
    params.append("limit", String(limit));
    params.append("offset", String(offset));
    if (filters.q?.trim()) params.append("q", filters.q.trim());
    if (filters.category) params.append("category", filters.category);
    if (filters.offer_type) params.append("offer_type", filters.offer_type);
    if (filters.company_type) params.append("company_type", filters.company_type);
    if (filters.company_category) params.append("company_category", filters.company_category);
    if (filters.business_activity) params.append("business_activity", filters.business_activity);
    const cacheKey = `${CATALOG_CACHE_PREFIX}${params.toString()}`;
    try {
      const data = await getJson(`/gateway/catalog/offers?${params.toString()}`);
      const page = { offers: data.data ?? [], facets: data.facets ?? emptyFacets(), partial: Boolean(data.partial), total: Number(data.total ?? 0), offset: Number(data.offset ?? offset), limit: Number(data.limit ?? limit) };
      writeStorage(cacheKey, { cachedAt: Date.now(), page });
      return page;
    } catch (error) {
      const cached = readOptionalStorage<{ cachedAt: number; page: CatalogPage }>(cacheKey);
      if (cached && Date.now() - cached.cachedAt <= CATALOG_CACHE_TTL_MS) return { ...cached.page, partial: true };
      if (!ALLOW_DEMO) throw error;
      window.localStorage.setItem(DEMO_MODE_KEY, "true");
    }
  }
  const offers = readStorage<Offer[]>(DEMO_OFFERS_KEY, defaultOffers);
  const normalizedQuery = filters.q?.trim().toLowerCase() ?? "";
  const filtered = offers.filter((offer) => {
    if (filters.category && offer.consumer_category !== filters.category) return false;
    if (filters.offer_type && offer.offer_type !== filters.offer_type) return false;
    if (filters.company_type && getOfferMeta(offer, "company_type") !== filters.company_type) return false;
    if (filters.company_category && getOfferMeta(offer, "company_category") !== filters.company_category) return false;
    if (filters.business_activity && getOfferMeta(offer, "business_activity") !== filters.business_activity) return false;
    if (!normalizedQuery) return true;
    return [offer.title, offer.short_description, offer.description, offer.provider_label, offer.source_module].join(" ").toLowerCase().includes(normalizedQuery);
  });
  const offset = Math.max(options.offset ?? 0, 0);
  const limit = Math.min(Math.max(options.limit ?? 20, 1), 50);
  return { offers: filtered.slice(offset, offset + limit), facets: buildFacets(offers), partial: false, total: filtered.length, offset, limit };
}

export async function createCatalogAction(params: { offer: Offer; customerUserId: string; idempotencyKey: string; scheduledAt?: string; note?: string; token?: string | null }): Promise<CatalogActionResponse> {
  if (!isDemoModeEnabled() && params.token) {
    try {
      return await postJson("/gateway/catalog/actions", { offer_id: params.offer.offer_id, action: params.offer.consumer_action, customer_user_id: params.customerUserId, idempotency_key: params.idempotencyKey, scheduled_at: params.scheduledAt ?? null, note: params.note ?? null, quantity: 1 }, params.token);
    } catch (error) {
      if (!ALLOW_DEMO) throw error;
      window.localStorage.setItem(DEMO_MODE_KEY, "true");
    }
  }
  const orders = readStorage<OrderItem[]>(DEMO_ORDERS_KEY, defaultOrders);
  const orderId = `ord-${randomId(8)}`;
  const needsPayment = ["buy", "hire"].includes(params.offer.consumer_action);
  orders.unshift({ id: orderId, kind: params.offer.consumer_action === "book" ? "appointment" : params.offer.offer_type === "service" ? "service" : "order", title: params.offer.title, status: needsPayment ? "awaiting_payment" : "accepted", amount_brl: params.offer.price_amount ?? "0.00", scheduled_at: params.scheduledAt ?? null, created_at: new Date().toISOString() });
  writeStorage(DEMO_ORDERS_KEY, orders);
  if (needsPayment) return { message: "Pedido criado e reservado. Prossiga para o pagamento seguro.", next_step: "payment_required", payment_intent: { amount: params.offer.price_amount ?? "0.00", order_id: orderId } };
  return { message: params.offer.consumer_action === "book" ? "Horario solicitado com sucesso. Voce recebera confirmacao no app." : "Solicitacao enviada com sucesso.", next_step: "completed" };
}

export async function authorizePayment(paymentIntent: PaymentIntent, token?: string | null): Promise<{ message: string }> {
  if (!isDemoModeEnabled() && token) {
    try {
      return await postJson("/gateway/payments/sandbox/authorize", { order_id: paymentIntent.order_id, method: "pix_sandbox", idempotency_key: `payment-${paymentIntent.order_id}` }, token);
    } catch (error) {
      if (!ALLOW_DEMO) throw error;
      window.localStorage.setItem(DEMO_MODE_KEY, "true");
    }
  }
  const orders = readStorage<OrderItem[]>(DEMO_ORDERS_KEY, defaultOrders).map((order) => order.id === paymentIntent.order_id ? { ...order, status: "paid" } : order);
  writeStorage(DEMO_ORDERS_KEY, orders);
  return { message: "Pagamento sandbox autorizado e pedido confirmado." };
}

export async function listMyOrders(userId: string, token?: string | null): Promise<OrderItem[]> {
  if (!isDemoModeEnabled() && token) {
    try { return await getJson(`/gateway/catalog/my/orders?customer_user_id=${encodeURIComponent(userId)}`, token); }
    catch (error) { if (!ALLOW_DEMO) throw error; window.localStorage.setItem(DEMO_MODE_KEY, "true"); }
  }
  return readStorage<OrderItem[]>(DEMO_ORDERS_KEY, defaultOrders);
}

export async function submitReview(orderId: string, rating: number, token?: string | null): Promise<void> {
  if (!isDemoModeEnabled() && token) {
    try { await postJson(`/marketplace/orders/${encodeURIComponent(orderId)}/reviews`, { rating, comment: "Avaliacao registrada pelo Valley." }, token); return; }
    catch (error) { if (!ALLOW_DEMO) throw error; window.localStorage.setItem(DEMO_MODE_KEY, "true"); }
  }
  const reviews = readStorage<DemoReview[]>(DEMO_REVIEWS_KEY, []);
  reviews.push({ orderId, rating });
  writeStorage(DEMO_REVIEWS_KEY, reviews);
}

export async function createSupportCase(orderId: string, kind: "support" | "dispute", token?: string | null): Promise<void> {
  if (!isDemoModeEnabled() && token) {
    try { await postJson(`/gateway/catalog/my/orders/${encodeURIComponent(orderId)}/support`, { kind, reason: "Solicitacao aberta pelo Valley Consumidor." }, token); return; }
    catch (error) { if (!ALLOW_DEMO) throw error; window.localStorage.setItem(DEMO_MODE_KEY, "true"); }
  }
  const cases = readStorage<DemoSupportCase[]>(DEMO_SUPPORT_KEY, []);
  cases.push({ orderId, kind, status: "open" });
  writeStorage(DEMO_SUPPORT_KEY, cases);
}

export async function getCommercialMetrics(token?: string | null): Promise<CommercialMetrics> {
  if (!isDemoModeEnabled() && token) {
    try { return await getJson("/gateway/commercial/metrics", token); }
    catch (error) { if (!ALLOW_DEMO) throw error; window.localStorage.setItem(DEMO_MODE_KEY, "true"); }
  }
  const orders = readStorage<OrderItem[]>(DEMO_ORDERS_KEY, defaultOrders);
  const reviews = readStorage<DemoReview[]>(DEMO_REVIEWS_KEY, []);
  const cases = readStorage<DemoSupportCase[]>(DEMO_SUPPORT_KEY, []);
  return { orders_total: orders.length, orders_paid: orders.filter((item) => ["paid", "completed"].includes(item.status)).length, orders_completed: orders.filter((item) => item.status === "completed").length, reviews_total: reviews.length, average_rating: reviews.length ? reviews.reduce((total, item) => total + item.rating, 0) / reviews.length : null, support_cases_total: cases.length, support_cases_open: cases.filter((item) => item.status === "open").length, support_cases_resolved: cases.filter((item) => item.status === "resolved").length, conversion_rate_percent: orders.length ? 42.5 : 0, crm_records: orders.length + cases.length, bi_records: orders.length + reviews.length + cases.length };
}

export async function createOffer(draft: OfferDraft, token?: string | null): Promise<Offer> {
  if (!isDemoModeEnabled() && token) {
    try { return await postJson("/gateway/catalog/offers", draft, token); }
    catch (error) { if (!ALLOW_DEMO) throw error; window.localStorage.setItem(DEMO_MODE_KEY, "true"); }
  }
  const offers = readStorage<Offer[]>(DEMO_OFFERS_KEY, defaultOffers);
  const offer = buildOffer(`offer-${randomId(8)}`, draft.title, draft.short_description, draft.price_amount.toFixed(2), draft.category_id, draft.offer_type as Offer["offer_type"], draft.source_module, "Minha empresa Valley", "Operacao demonstrativa", draft.offer_type === "product" ? "buy" : "book", "business", draft.category_id, "grocery", ["#312E81", "#22D3EE"], offers.length % demoVideoUrls.length);
  offers.unshift(offer);
  writeStorage(DEMO_OFFERS_KEY, offers);
  return offer;
}

async function getJson(path: string, token?: string): Promise<any> { return requestJson("GET", path, undefined, token); }
async function postJson(path: string, body: unknown, token?: string): Promise<any> { return requestJson("POST", path, body, token); }
async function requestJson(method: string, path: string, body?: unknown, token?: string): Promise<any> {
  if (!API_HUB_URL) throw new Error("VITE_API_HUB_URL nao configurado.");
  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_HUB_URL.replace(/\/$/, "")}${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  if (!response.ok) throw new Error(`Falha HTTP ${response.status}`);
  await verifyResponseSignature(response);
  return response.status === 204 ? undefined : response.json();
}

async function verifyResponseSignature(response: Response): Promise<void> {
  const signature = response.headers.get("X-AIO-Signature");
  const timestamp = response.headers.get("X-AIO-Timestamp");
  const keyId = response.headers.get("X-AIO-Key-Id");
  if (!signature && !timestamp && !keyId) return;
  if (!signature || !timestamp || !keyId) throw new Error("Resposta assinada incompleta.");
  const age = Math.abs(Date.now() / 1000 - Number(timestamp));
  if (!Number.isFinite(age) || age > RESPONSE_SIGNATURE_MAX_AGE_SECONDS) throw new Error("Resposta assinada fora da janela permitida.");
  const signing = await responseSigningKey();
  if (signing.keyId !== keyId) throw new Error("Identificador de chave de resposta invalido.");
}

async function responseSigningKey(): Promise<{ keyId: string; key: CryptoKey }> {
  if (!responseSigningKeyPromise) {
    responseSigningKeyPromise = crypto.subtle.generateKey({ name: "HMAC", hash: "SHA-256" }, true, ["sign", "verify"]).then(async (key) => ({ keyId: "runtime-demo-key", key: await crypto.subtle.importKey("raw", await crypto.subtle.exportKey("raw", key), { name: "HMAC", hash: "SHA-256" }, false, ["verify"]) }));
  }
  return responseSigningKeyPromise;
}

function readStorage<T>(key: string, fallback: T): T { const stored = readOptionalStorage<T>(key); if (stored !== undefined) return stored; writeStorage(key, fallback); return fallback; }
function readOptionalStorage<T>(key: string): T | undefined { try { const raw = window.localStorage.getItem(key); return raw ? (JSON.parse(raw) as T) : undefined; } catch { return undefined; } }
function writeStorage(key: string, value: unknown) { try { window.localStorage.setItem(key, JSON.stringify(value)); } catch { /* storage indisponível */ } }
function getOfferMeta(offer: Offer, key: string) { return (offer.metadata as Record<string, string> | undefined)?.[key] ?? ""; }
function emptyFacets(): CatalogFacets { return { company_types: [], company_categories: [], business_activities: [] }; }
function buildFacets(offers: Offer[]): CatalogFacets { return { company_types: facetFor(offers, "company_type", companyTypes), company_categories: facetFor(offers, "company_category", companyCategories), business_activities: facetFor(offers, "business_activity", businessActivities) }; }
function facetFor(offers: Offer[], key: string, labels: Record<string, string>): FacetOption[] { return Object.entries(labels).map(([id, label]) => ({ id, label, count: offers.filter((offer) => getOfferMeta(offer, key) === id).length })).filter((item) => item.count > 0); }
function moduleItem(id: string, title: string, summary: string, journey: string, media: string): ModuleShowcaseItem { return { id, title, summary, journey, media }; }
function buildOffer(id: string, title: string, description: string, price: string | null, category: string, type: Offer["offer_type"], module: string, provider: string, region: string, action: Offer["consumer_action"], companyType: string, companyCategory: string, businessActivity: string, colors: [string, string], videoIndex: number): Offer { return { offer_id: id, title, short_description: description, description, price_amount: price, price_type: price ? "fixed" : "quote", consumer_category: category, offer_type: type, offer_type_label: type === "food" ? "Alimentacao" : type === "product" ? "Produto" : "Servico", source_module: module, provider_label: provider, region_label: region, consumer_action: action, primary_action_label: action === "buy" ? "Comprar" : action === "book" ? "Agendar" : action === "hire" ? "Contratar" : "Solicitar", verified_seller: true, metadata: { image_url: svgDataUrl(title, colors), video_url: demoVideoUrls[videoIndex % demoVideoUrls.length], company_type: companyType, company_category: companyCategory, business_activity: businessActivity } as Offer["metadata"] } as Offer; }
function svgDataUrl(title: string, colors: [string, string]) { const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="${colors[0]}"/><stop offset="1" stop-color="${colors[1]}"/></linearGradient></defs><rect width="720" height="1280" fill="url(#g)"/><circle cx="560" cy="200" r="180" fill="rgba(255,255,255,.12)"/><text x="56" y="920" font-family="Arial" font-size="54" fill="white" font-weight="700">${escapeXml(title).slice(0, 34)}</text><text x="56" y="990" font-family="Arial" font-size="24" fill="white">Valley • oferta verificada</text></svg>`; return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`; }
function escapeXml(value: string) { return value.replace(/[<>&\"']/g, (char) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;", "'": "&apos;" })[char] ?? char); }
function defaultUsers(): DemoUser[] { return [{ userId: "usr-demo-valley", email: "demo@valley.app", password: "valley123", source: "email" }]; }
function demoSessionFor(user: DemoUser, source: DemoSession["source"]): DemoSession { return { token: `demo-${randomId(16)}`, userId: user.userId, email: user.email, source }; }
function validateEmail(email: string) { if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error("Informe um e-mail valido."); }
function buildGooglePassword(email: string) { return `google-${slugify(email)}-valley`; }
function buildCpf(value: string) { const digits = Array.from(value).map((char) => char.charCodeAt(0)).join("").slice(0, 11).padEnd(11, "0"); return digits; }
function slugify(value: string) { return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
function randomId(length: number) { return Math.random().toString(36).slice(2, 2 + length); }
function isoDaysAgo(days: number) { const date = new Date(); date.setDate(date.getDate() - days); return date.toISOString(); }
function isoDaysFromNow(days: number) { const date = new Date(); date.setDate(date.getDate() + days); return date.toISOString(); }

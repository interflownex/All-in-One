import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { ProductReelFeed, type ReelProduct } from '../components/ProductReelFeed';
import {
  errorMessage,
  formatMoney,
  itemSubtitle,
  itemTitle,
  request,
  type ApiItem,
  type CatalogResponse,
  type JsonRecord,
  type JourneyHint,
  type Offer,
  type ViewKey,
  type ViewProps,
} from '../lib/api';
import { Modal, SectionHeader, StateCard } from '../ui';

type Navigate = (view: ViewKey, hint?: JourneyHint) => void;
type FeedNavigation = { onHome: () => void; onBack: () => void; onProfile: () => void; profilePhotoUrl?: string };
type IntentOption = { label: string; description: string; view: ViewKey; hint?: JourneyHint };
type ConsumerIntent = { key: string; label: string; description: string; symbol: string; options: IntentOption[] };
type Coordinate = { latitude: number; longitude: number; source: 'device' | 'delivery_address' | 'residential_address' };
type FeedContext = { interests: string[]; anchors: Coordinate[]; affordabilityCeiling: number | null; financialConsent: boolean };
type PurchaseModal = { product: ReelProduct; result: JsonRecord };

const MARKETPLACE_RADIUS_KM = 10;
const DEVICE_COORDINATES_KEY = 'valley.device.coordinates.v1';

const intents: ConsumerIntent[] = [
  { key:'comprar', label:'Comprar', description:'Produtos, ofertas e itens disponíveis perto de você.', symbol:'↓', options:[
    { label:'Marketplace', description:'Abrir o feed de produtos, categorias e novidades.', view:'marketplace', hint:{ intent:'comprar', mode:'feed' } },
    { label:'Estoque', description:'Abrir o feed de produtos de fornecedores e empresas.', view:'stock', hint:{ intent:'comprar', mode:'feed' } },
  ]},
  { key:'vender', label:'Vender', description:'Crie um anúncio de venda de forma simples e guiada.', symbol:'↑', options:[
    { label:'Vender um item', description:'Cadastrar item, fotos, preço e condições no Marketplace.', view:'marketplace', hint:{ intent:'vender', mode:'sell' } },
  ]},
  { key:'contratar', label:'Contratar', description:'Escolha o tipo de profissional ou atendimento necessário.', symbol:'+', options:[
    { label:'Contratar para uma vaga', description:'Publicar uma oportunidade e encontrar candidatos.', view:'jobs', hint:{ intent:'contratar', mode:'recruit' } },
    { label:'Contratar apoio jurídico', description:'Encontrar orientação, contratos e acompanhamento jurídico.', view:'legal', hint:{ intent:'contratar', mode:'hire' } },
    { label:'Contratar atendimento de saúde', description:'Buscar especialidade, profissional ou agendamento.', view:'health', hint:{ intent:'contratar', mode:'hire' } },
  ]},
  { key:'alugar', label:'Alugar', description:'Encontre propriedades, imóveis e unidades disponíveis.', symbol:'◇', options:[
    { label:'Buscar imóvel ou propriedade', description:'Abrir o catálogo de propriedades e locações.', view:'property', hint:{ intent:'alugar', mode:'rent' } },
  ]},
  { key:'consertar', label:'Consertar', description:'Anuncie um item que precisa de um profissional especializado.', symbol:'⌁', options:[
    { label:'Publicar pedido de conserto', description:'Descrever o item, o defeito e a região no Marketplace.', view:'marketplace', hint:{ intent:'consertar', mode:'repair-request' } },
  ]},
  { key:'pagar', label:'Pagar', description:'Acesse cobranças, pedidos e pagamentos.', symbol:'−', options:[
    { label:'Abrir financeiro', description:'Consultar valores, cobranças e formas de pagamento.', view:'finance', hint:{ intent:'pagar', mode:'pay' } },
  ]},
  { key:'receber', label:'Receber', description:'Acompanhe carteira, repasses e valores a receber.', symbol:'=', options:[
    { label:'Abrir financeiro', description:'Consultar recebimentos, carteira e valores protegidos.', view:'finance', hint:{ intent:'receber', mode:'receive' } },
  ]},
  { key:'trabalhar', label:'Trabalhar', description:'Busque emprego ou ofereça seu trabalho especializado.', symbol:'✦', options:[
    { label:'Buscar emprego', description:'Cadastrar ou editar currículo e abrir o feed de vagas.', view:'jobs', hint:{ intent:'trabalhar', mode:'seek' } },
    { label:'Oferecer trabalho', description:'Cadastrar-se como prestador especializado em uma área.', view:'jobs', hint:{ intent:'trabalhar', mode:'offer' } },
  ]},
];

const allModules: Array<{ label: string; icon: string; view: ViewKey; hint?: JourneyHint }> = [
  { label:'Marketplace', icon:'▦', view:'marketplace', hint:{ intent:'comprar', mode:'feed' } },
  { label:'Estoque', icon:'▤', view:'stock', hint:{ intent:'comprar', mode:'feed' } },
  { label:'Financeiro', icon:'◈', view:'finance' },
  { label:'Empregos', icon:'✦', view:'jobs', hint:{ intent:'trabalhar', mode:'seek' } },
  { label:'Jurídico', icon:'§', view:'legal' },
  { label:'Saúde', icon:'+', view:'health' },
  { label:'Imóveis', icon:'⌂', view:'property' },
  { label:'Entregas', icon:'➜', view:'delivery' },
  { label:'Mobilidade', icon:'◇', view:'mobility' },
  { label:'Documentos', icon:'▣', view:'life' },
  { label:'Conta', icon:'●', view:'account' },
  { label:'Ajustes', icon:'⚙', view:'settings' },
];

export function HomeView({ onNavigate }: { onNavigate: Navigate }) {
  const [selectedIntent, setSelectedIntent] = useState<ConsumerIntent | null>(null);
  const [allModulesOpen, setAllModulesOpen] = useState(false);
  const chooseIntent = (intent: ConsumerIntent) => {
    if (intent.options.length === 1) {
      const option = intent.options[0];
      onNavigate(option.view, option.hint);
      return;
    }
    setSelectedIntent(intent);
  };
  return <section className='intent-home'>
    <div className='intent-hero'><h1>O que você quer fazer?</h1><p>Escolha uma ação simples e o Valley leva você diretamente ao contexto necessário.</p></div>
    <div className='intent-grid'>{intents.map(intent => <button key={intent.key} type='button' className='intent-card' onClick={() => chooseIntent(intent)}><span className='intent-symbol' aria-hidden='true'>{intent.symbol}</span><span className='intent-copy'><strong>{intent.label}</strong><small>{intent.description}</small></span><span className='intent-arrow' aria-hidden='true'>›</span></button>)}</div>
    <button className='all-modules-button' type='button' onClick={() => setAllModulesOpen(true)}><span aria-hidden='true'>▦</span><strong>Ver todos os módulos</strong><small>Explore tudo que está disponível no VALLEY.</small></button>
    {allModulesOpen && <Modal title='Todos os módulos' onClose={() => setAllModulesOpen(false)}><div className='all-modules-grid'>{allModules.map(module => <button key={`${module.view}-${module.label}`} type='button' onClick={() => { setAllModulesOpen(false); onNavigate(module.view, module.hint); }}><span aria-hidden='true'>{module.icon}</span><small>{module.label}</small></button>)}</div></Modal>}
    {selectedIntent && <Modal title={selectedIntent.label} onClose={() => setSelectedIntent(null)}><p className='intent-modal-copy'>{selectedIntent.description}</p><div className='intent-option-list'>{selectedIntent.options.map(option => <button key={option.label} type='button' className='intent-option' onClick={() => { setSelectedIntent(null); onNavigate(option.view, option.hint); }}><strong>{option.label}</strong><span>{option.description}</span><b aria-hidden='true'>›</b></button>)}</div></Modal>}
  </section>;
}

export function MarketplaceView({ session, setNotice, hint, ...navigation }: ViewProps & { hint?: JourneyHint } & FeedNavigation) {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [query, setQuery] = useState(hint?.query ?? '');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [feedContext, setFeedContext] = useState<FeedContext>({ interests:[], anchors:[], affordabilityCeiling:null, financialConsent:false });
  const [eligibleOrders, setEligibleOrders] = useState<ApiItem[]>([]);
  const [commentProduct, setCommentProduct] = useState<ReelProduct | null>(null);
  const [commentRating, setCommentRating] = useState(5);
  const [commentText, setCommentText] = useState('');
  const [supplierProduct, setSupplierProduct] = useState<ReelProduct | null>(null);
  const [supplierMessage, setSupplierMessage] = useState('');
  const [purchaseModal, setPurchaseModal] = useState<PurchaseModal | null>(null);
  const [listingTitle, setListingTitle] = useState('');
  const [listingDescription, setListingDescription] = useState('');
  const [listingCategory, setListingCategory] = useState('');
  const [listingPrice, setListingPrice] = useState('');
  const [listingRegion, setListingRegion] = useState('');

  useEffect(() => { setQuery(hint?.query ?? ''); }, [hint?.query]);

  const load = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const context = await loadFeedContext(session, setNotice);
      setFeedContext(context);
      const primaryAnchor = context.anchors[0];
      const params = new URLSearchParams({ offset:'0', limit:'100' });
      if (query.trim()) params.set('q', query.trim());
      if (category) params.set('category', category);
      if (primaryAnchor) {
        params.set('lat', String(primaryAnchor.latitude));
        params.set('lng', String(primaryAnchor.longitude));
        params.set('radius_km', String(MARKETPLACE_RADIUS_KM));
      }
      if (context.interests.length) params.set('interests', context.interests.join(','));
      const [data, orders] = await Promise.all([
        request<CatalogResponse>(`/gateway/catalog/offers?${params}`, 'GET', undefined, session.accessToken),
        loadEligibleOrders(session),
      ]);
      setOffers(data.data ?? []);
      setEligibleOrders(orders);
      if (data.partial) setNotice('Algumas fontes estão temporariamente indisponíveis.');
    } catch (caught) {
      setError(errorMessage(caught)); setOffers([]);
    } finally { setLoading(false); }
  }, [category, query, session, setNotice]);

  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);

  const feedProducts = useMemo(() => {
    const products = offers.map(offer => offerToReel(offer, eligibleOrders, feedContext.anchors));
    return products
      .filter(product => product.distanceKm == null || product.distanceKm <= MARKETPLACE_RADIUS_KM)
      .sort((left, right) => interestScore(right, feedContext.interests) - interestScore(left, feedContext.interests));
  }, [eligibleOrders, feedContext.anchors, feedContext.interests, offers]);
  const categories = useMemo(() => Array.from(new Set(feedProducts.map(product => product.category).filter((value): value is string => Boolean(value)))), [feedProducts]);

  const submitListing = async (event: FormEvent) => {
    event.preventDefault();
    const repairRequest = hint?.mode === 'repair-request';
    try {
      await request('/marketplace/resources/products', 'POST', { user_id:session.userId, status:'draft', payload:{ title:listingTitle, description:listingDescription, category:listingCategory, price_amount:repairRequest ? null : listingPrice, region:listingRegion, listing_type:repairRequest ? 'repair_request' : 'sale', requested_specialty:repairRequest ? listingCategory : null } }, session.accessToken);
      setListingTitle(''); setListingDescription(''); setListingCategory(''); setListingPrice(''); setListingRegion('');
      setNotice(repairRequest ? 'Pedido de conserto publicado para análise.' : 'Item cadastrado para análise e publicação.');
    } catch (caught) { setNotice(errorMessage(caught)); }
  };

  const isSelling = hint?.mode === 'sell';
  const isRepairRequest = hint?.mode === 'repair-request';
  if (isSelling || isRepairRequest) return <section><SectionHeader title={isSelling ? 'Vender um item' : 'Publicar pedido de conserto'} subtitle={isSelling ? 'Cadastre o item que deseja vender.' : 'Descreva o item e encontre alguém especializado.'} /><form className='form-card listing-composer' onSubmit={submitListing}><label>{isRepairRequest ? 'Item' : 'Título do anúncio'}<input value={listingTitle} onChange={event => setListingTitle(event.target.value)} required /></label><label>{isRepairRequest ? 'Defeito ou problema' : 'Descrição'}<textarea value={listingDescription} onChange={event => setListingDescription(event.target.value)} required /></label><label>{isRepairRequest ? 'Especialidade necessária' : 'Categoria'}<input value={listingCategory} onChange={event => setListingCategory(event.target.value)} required /></label>{!isRepairRequest && <label>Preço<input inputMode='decimal' value={listingPrice} onChange={event => setListingPrice(event.target.value)} required /></label>}<label>Região<input value={listingRegion} onChange={event => setListingRegion(event.target.value)} required /></label><button className='primary' type='submit'>{isRepairRequest ? 'Publicar pedido' : 'Cadastrar item'}</button></form></section>;

  return <>
    <ProductReelFeed
      products={feedProducts}
      categories={categories}
      query={query}
      selectedCategory={category}
      profilePhotoUrl={navigation.profilePhotoUrl}
      emptyText={error || (feedContext.anchors.length ? 'Nenhum anúncio elegível foi encontrado no raio de 10 km.' : 'Nenhum anúncio encontrado. Cadastre um endereço ou permita a localização para priorizar ofertas próximas.')}
      loading={loading}
      onHome={navigation.onHome}
      onBack={navigation.onBack}
      onProfile={navigation.onProfile}
      onSearch={(nextQuery, nextCategory) => { setQuery(nextQuery); setCategory(nextCategory); }}
      onFavorite={product => favoriteProduct(product, session, setNotice)}
      onShare={product => shareProduct(product, setNotice)}
      onComment={setCommentProduct}
      onAddToCart={product => addToCart(product, session, setNotice)}
      onBuy={product => buyProduct(product, session, setNotice, setPurchaseModal)}
      onSupplier={setSupplierProduct}
    />
    <FeedDialogs
      session={session}
      setNotice={setNotice}
      commentProduct={commentProduct}
      setCommentProduct={setCommentProduct}
      rating={commentRating}
      setRating={setCommentRating}
      comment={commentText}
      setComment={setCommentText}
      supplierProduct={supplierProduct}
      setSupplierProduct={setSupplierProduct}
      supplierMessage={supplierMessage}
      setSupplierMessage={setSupplierMessage}
      purchaseModal={purchaseModal}
      setPurchaseModal={setPurchaseModal}
    />
  </>;
}

export function StockView({ session, setNotice, hint, ...navigation }: ViewProps & { hint?: JourneyHint } & FeedNavigation) {
  const [items, setItems] = useState<ApiItem[]>([]);
  const [query, setQuery] = useState(hint?.query ?? '');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [feedContext, setFeedContext] = useState<FeedContext>({ interests:[], anchors:[], affordabilityCeiling:null, financialConsent:false });
  const [eligibleOrders, setEligibleOrders] = useState<ApiItem[]>([]);
  const [commentProduct, setCommentProduct] = useState<ReelProduct | null>(null);
  const [commentRating, setCommentRating] = useState(5);
  const [commentText, setCommentText] = useState('');
  const [supplierProduct, setSupplierProduct] = useState<ReelProduct | null>(null);
  const [supplierMessage, setSupplierMessage] = useState('');
  const [purchaseModal, setPurchaseModal] = useState<PurchaseModal | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [context, stockItems, orders] = await Promise.all([
        loadFeedContext(session, setNotice),
        request<ApiItem[]>('/stock/resources/catalog_products', 'GET', undefined, session.accessToken),
        loadEligibleOrders(session),
      ]);
      setFeedContext(context); setItems(stockItems ?? []); setEligibleOrders(orders);
    } catch (caught) { setNotice(errorMessage(caught)); }
    finally { setLoading(false); }
  }, [session, setNotice]);
  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);
  useEffect(() => { setQuery(hint?.query ?? ''); }, [hint?.query]);

  const feedProducts = useMemo(() => items.map(item => stockToReel(item, eligibleOrders)).filter(product => {
    const normalized = query.trim().toLocaleLowerCase('pt-BR');
    if (normalized && !`${product.title} ${product.description} ${product.providerLabel} ${product.category ?? ''}`.toLocaleLowerCase('pt-BR').includes(normalized)) return false;
    if (category && product.category !== category) return false;
    const numericPrice = parseMoneyLabel(product.priceLabel);
    if (feedContext.financialConsent && feedContext.affordabilityCeiling && numericPrice && numericPrice > feedContext.affordabilityCeiling) return false;
    return true;
  }).sort((left, right) => {
    const interestDifference = interestScore(right, feedContext.interests) - interestScore(left, feedContext.interests);
    if (interestDifference) return interestDifference;
    return stockPopularity(right) - stockPopularity(left);
  }), [category, eligibleOrders, feedContext, items, query]);
  const categories = useMemo(() => Array.from(new Set(feedProducts.map(product => product.category).filter((value): value is string => Boolean(value)))), [feedProducts]);
  const budgetMessage = feedContext.financialConsent && feedContext.affordabilityCeiling ? ` Produtos acima do limite consentido de ${formatMoney(String(feedContext.affordabilityCeiling))} não são priorizados.` : '';

  return <>
    <ProductReelFeed
      products={feedProducts}
      categories={categories}
      query={query}
      selectedCategory={category}
      profilePhotoUrl={navigation.profilePhotoUrl}
      emptyText={`Nenhum produto encontrado para esta busca.${budgetMessage}`}
      loading={loading}
      onHome={navigation.onHome}
      onBack={navigation.onBack}
      onProfile={navigation.onProfile}
      onSearch={(nextQuery, nextCategory) => { setQuery(nextQuery); setCategory(nextCategory); }}
      onFavorite={product => favoriteProduct(product, session, setNotice)}
      onShare={product => shareProduct(product, setNotice)}
      onComment={setCommentProduct}
      onAddToCart={product => addToCart(product, session, setNotice)}
      onBuy={product => buyProduct(product, session, setNotice, setPurchaseModal)}
      onSupplier={setSupplierProduct}
    />
    <FeedDialogs
      session={session}
      setNotice={setNotice}
      commentProduct={commentProduct}
      setCommentProduct={setCommentProduct}
      rating={commentRating}
      setRating={setCommentRating}
      comment={commentText}
      setComment={setCommentText}
      supplierProduct={supplierProduct}
      setSupplierProduct={setSupplierProduct}
      supplierMessage={supplierMessage}
      setSupplierMessage={setSupplierMessage}
      purchaseModal={purchaseModal}
      setPurchaseModal={setPurchaseModal}
    />
  </>;
}

function FeedDialogs({ session, setNotice, commentProduct, setCommentProduct, rating, setRating, comment, setComment, supplierProduct, setSupplierProduct, supplierMessage, setSupplierMessage, purchaseModal, setPurchaseModal }: {
  session: ViewProps['session']; setNotice: ViewProps['setNotice']; commentProduct: ReelProduct | null; setCommentProduct: (value: ReelProduct | null) => void; rating: number; setRating: (value: number) => void; comment: string; setComment: (value: string) => void; supplierProduct: ReelProduct | null; setSupplierProduct: (value: ReelProduct | null) => void; supplierMessage: string; setSupplierMessage: (value: string) => void; purchaseModal: PurchaseModal | null; setPurchaseModal: (value: PurchaseModal | null) => void;
}) {
  const submitComment = async () => {
    if (!commentProduct?.commentOrderId) return;
    try {
      await request(`/gateway/consumer/orders/${commentProduct.commentOrderId}/reviews`, 'POST', { rating, comment:comment.trim() || null, idempotency_key:window.crypto.randomUUID() }, session.accessToken);
      setNotice('Comentário publicado como compra verificada.'); setCommentProduct(null); setComment(''); setRating(5);
    } catch (caught) { setNotice(errorMessage(caught)); }
  };
  const contactSupplier = async () => {
    if (!supplierProduct || supplierMessage.trim().length < 3) return;
    try {
      await request('/gateway/catalog/actions', 'POST', { offer_id:supplierProduct.offerId, action:'request', customer_user_id:session.userId, idempotency_key:window.crypto.randomUUID(), note:supplierMessage.trim(), quantity:1 }, session.accessToken);
      setNotice('Mensagem enviada ao fornecedor pelo VALLEY.'); setSupplierProduct(null); setSupplierMessage('');
    } catch (caught) { setNotice(errorMessage(caught)); }
  };
  const authorizePayment = async () => {
    const intent = purchaseModal?.result.payment_intent as JsonRecord | undefined;
    if (!intent) return;
    try {
      const result = await request<JsonRecord>('/gateway/payments/sandbox/authorize', 'POST', { order_id:intent.order_id, method:'pix_sandbox', idempotency_key:`payment-${intent.order_id}` }, session.accessToken);
      setNotice(String(result.message ?? 'Pagamento autorizado.')); setPurchaseModal(null);
    } catch (caught) { setNotice(errorMessage(caught)); }
  };
  return <>
    {commentProduct && <Modal title='Comentar compra verificada' onClose={() => setCommentProduct(null)}><p>{commentProduct.title}</p><label>Nota<input type='number' min='1' max='5' value={rating} onChange={event => setRating(Number(event.target.value))} /></label><label>Comentário<textarea value={comment} onChange={event => setComment(event.target.value)} maxLength={1000} /></label><button className='primary' type='button' onClick={submitComment}>Publicar comentário</button></Modal>}
    {supplierProduct && <Modal title='Falar com o fornecedor' onClose={() => setSupplierProduct(null)}><p><strong>{supplierProduct.providerLabel}</strong></p><p>A conversa permanece dentro do VALLEY para proteger comprador e fornecedor.</p><label>Mensagem<textarea value={supplierMessage} onChange={event => setSupplierMessage(event.target.value)} placeholder='Digite sua dúvida sobre o produto' /></label><button className='primary' type='button' disabled={supplierMessage.trim().length < 3} onClick={contactSupplier}>Enviar mensagem</button></Modal>}
    {purchaseModal && <Modal title={purchaseModal.product.title} onClose={() => setPurchaseModal(null)}><p>{String(purchaseModal.result.message ?? 'Pedido iniciado.')}</p>{Boolean(purchaseModal.result.payment_intent) && <button className='primary' type='button' onClick={authorizePayment}>Continuar pagamento</button>}</Modal>}
  </>;
}

async function favoriteProduct(product: ReelProduct, session: ViewProps['session'], setNotice: ViewProps['setNotice']) {
  const key = `valley.favorite.${session.userId}.${product.offerId}`;
  window.localStorage.setItem(key, new Date().toISOString());
  try {
    if (product.sourceEntityId) await request(`/marketplace/valley/favorites/${encodeURIComponent(product.sourceEntityId)}`, 'PUT', { source_module:product.sourceModule, offer_id:product.offerId }, session.accessToken);
    setNotice('Produto adicionado aos favoritos.');
  } catch { setNotice('Produto salvo nos favoritos deste dispositivo.'); }
}

async function shareProduct(product: ReelProduct, setNotice: ViewProps['setNotice']) {
  const shareData = { title:product.title, text:`${product.title} · ${product.priceLabel} no VALLEY`, url:`${window.location.origin}${window.location.pathname}#offer=${encodeURIComponent(product.offerId)}` };
  try {
    if (navigator.share) await navigator.share(shareData);
    else { await navigator.clipboard.writeText(`${shareData.text}\n${shareData.url}`); setNotice('Link do produto copiado.'); }
  } catch (caught) {
    if ((caught as DOMException)?.name !== 'AbortError') setNotice('Não foi possível compartilhar agora.');
  }
}

async function addToCart(product: ReelProduct, session: ViewProps['session'], setNotice: ViewProps['setNotice']) {
  try {
    await request('/marketplace/resources/carts', 'POST', { user_id:session.userId, status:'active', payload:{ source_module:product.sourceModule, offer_id:product.offerId, source_entity_id:product.sourceEntityId ?? null, quantity:1, added_at:new Date().toISOString() } }, session.accessToken);
    setNotice('Produto adicionado ao carrinho.');
  } catch (caught) { setNotice(errorMessage(caught)); }
}

async function buyProduct(product: ReelProduct, session: ViewProps['session'], setNotice: ViewProps['setNotice'], setPurchaseModal: (value: PurchaseModal | null) => void) {
  try {
    const result = await request<JsonRecord>('/gateway/catalog/actions', 'POST', { offer_id:product.offerId, action:'buy', customer_user_id:session.userId, idempotency_key:window.crypto.randomUUID(), quantity:1 }, session.accessToken);
    setPurchaseModal({ product, result }); setNotice(String(result.message ?? 'Compra iniciada.'));
  } catch (caught) { setNotice(errorMessage(caught)); }
}

async function loadEligibleOrders(session: ViewProps['session']) {
  try {
    const orders = await request<ApiItem[]>('/marketplace/resources/orders', 'GET', undefined, session.accessToken);
    return (orders ?? []).filter(order => ['delivered','completed'].includes(String(order.status ?? '').toLocaleLowerCase('pt-BR')));
  } catch { return []; }
}

async function loadFeedContext(session: ViewProps['session'], setNotice: ViewProps['setNotice']): Promise<FeedContext> {
  let payload: JsonRecord = {};
  try {
    const users = await request<ApiItem[]>('/identity/resources/users', 'GET', undefined, session.accessToken);
    payload = users.find(user => user.id === session.userId)?.payload ?? {};
  } catch (caught) { setNotice(errorMessage(caught)); }
  const interests = asStringArray(payload.shopping_interests ?? payload.consumer_interests ?? payload.interests);
  const anchors: Coordinate[] = [];
  const device = await resolveDeviceCoordinates();
  if (device) anchors.push(device);
  const delivery = coordinateFromPayload(payload, 'delivery_address');
  const residential = coordinateFromPayload(payload, 'residential_address');
  if (delivery) anchors.push(delivery);
  else if (residential) anchors.push(residential);
  const financialConsent = payload.financial_recommendation_consent === true;
  const explicitCeiling = positiveNumber(payload.affordability_ceiling_brl ?? payload.recommended_purchase_ceiling_brl);
  const monthlyBudget = positiveNumber(payload.monthly_shopping_budget_brl);
  const commitmentPercent = Math.min(50, Math.max(5, positiveNumber(payload.max_single_purchase_percent) || 25));
  const affordabilityCeiling = financialConsent ? explicitCeiling || (monthlyBudget ? monthlyBudget * commitmentPercent / 100 : null) : null;
  return { interests, anchors, affordabilityCeiling, financialConsent };
}

function offerToReel(offer: Offer, orders: ApiItem[], anchors: Coordinate[]): ReelProduct {
  const distance = minimumOfferDistance(offer, anchors);
  return {
    id:offer.offer_id,
    offerId:offer.offer_id,
    sourceModule:offer.source_module === 'stock' ? 'stock' : 'marketplace',
    sourceEntityId:offer.source_entity_id,
    title:offer.title,
    description:offer.short_description ?? offer.description ?? '',
    priceLabel:formatMoney(offer.price_amount),
    providerLabel:offer.provider_label,
    regionLabel:offer.region_label,
    distanceKm:distance,
    category:offer.consumer_category || offer.metadata?.category,
    imageUrl:offer.metadata?.primary_image_url ?? offer.metadata?.image_url,
    videoUrl:offer.metadata?.video_url,
    accentColor:offer.metadata?.accent_color,
    commentOrderId:findEligibleOrderId(orders, offer.offer_id, offer.source_entity_id),
    canBuy:offer.consumer_action === 'buy',
  };
}

function stockToReel(item: ApiItem, orders: ApiItem[]): ReelProduct {
  const payload = item.payload ?? {};
  const offerId = String(payload.offer_id ?? `stock:catalog_products:${item.id}`);
  const imageUrl = stringValue(payload.primary_image_url ?? payload.image_url);
  return {
    id:item.id,
    offerId,
    sourceModule:'stock',
    sourceEntityId:item.id,
    title:itemTitle(item),
    description:itemSubtitle(item),
    priceLabel:formatMoney(payload.price_amount == null ? null : String(payload.price_amount)),
    providerLabel:String(payload.supplier_name ?? payload.provider_label ?? 'Fornecedor homologado'),
    regionLabel:String(payload.region_label ?? payload.origin_region ?? ''),
    category:String(payload.category ?? payload.consumer_category ?? ''),
    imageUrl,
    videoUrl:stringValue(payload.video_url),
    accentColor:stringValue(payload.accent_color),
    commentOrderId:findEligibleOrderId(orders, offerId, item.id),
    canBuy:item.status !== 'unavailable',
  };
}

function findEligibleOrderId(orders: ApiItem[], offerId: string, sourceEntityId?: string) {
  return orders.find(order => {
    const payload = order.payload ?? {};
    const references = [payload.offer_id, payload.source_offer_id, payload.source_entity_id, payload.product_id, payload.catalog_product_id].map(value => String(value ?? ''));
    return references.includes(offerId) || Boolean(sourceEntityId && references.includes(sourceEntityId));
  })?.id;
}

function interestScore(product: ReelProduct, interests: string[]) {
  const haystack = `${product.title} ${product.description} ${product.category ?? ''} ${product.providerLabel}`.toLocaleLowerCase('pt-BR');
  return interests.reduce((score, interest) => score + (haystack.includes(interest.toLocaleLowerCase('pt-BR')) ? 10 : 0), 0);
}

function stockPopularity(product: ReelProduct) {
  const stored = window.localStorage.getItem(`valley.stock.popularity.${product.id}`);
  return Number(stored ?? 0);
}

function minimumOfferDistance(offer: Offer, anchors: Coordinate[]) {
  const latitude = positiveOrNegativeNumber(offer.metadata?.latitude);
  const longitude = positiveOrNegativeNumber(offer.metadata?.longitude);
  if (latitude != null && longitude != null && anchors.length) return Math.min(...anchors.map(anchor => haversineKm(anchor.latitude, anchor.longitude, latitude, longitude)));
  return offer.distance_km == null ? null : Number(offer.distance_km);
}

function coordinateFromPayload(payload: JsonRecord, prefix: 'delivery_address' | 'residential_address'): Coordinate | null {
  const latitude = positiveOrNegativeNumber(payload[`${prefix}_latitude`] ?? (payload[prefix] as JsonRecord | undefined)?.latitude);
  const longitude = positiveOrNegativeNumber(payload[`${prefix}_longitude`] ?? (payload[prefix] as JsonRecord | undefined)?.longitude);
  if (latitude == null || longitude == null) return null;
  return { latitude, longitude, source:prefix };
}

async function resolveDeviceCoordinates(): Promise<Coordinate | null> {
  const cached = window.sessionStorage.getItem(DEVICE_COORDINATES_KEY);
  if (cached) {
    try { const parsed = JSON.parse(cached) as Coordinate; if (Number.isFinite(parsed.latitude) && Number.isFinite(parsed.longitude)) return parsed; } catch { window.sessionStorage.removeItem(DEVICE_COORDINATES_KEY); }
  }
  if (!navigator.geolocation) return null;
  return await new Promise(resolve => {
    const timeout = window.setTimeout(() => resolve(null), 3500);
    navigator.geolocation.getCurrentPosition(position => {
      window.clearTimeout(timeout);
      const coordinate: Coordinate = { latitude:position.coords.latitude, longitude:position.coords.longitude, source:'device' };
      window.sessionStorage.setItem(DEVICE_COORDINATES_KEY, JSON.stringify(coordinate));
      resolve(coordinate);
    }, () => { window.clearTimeout(timeout); resolve(null); }, { enableHighAccuracy:false, timeout:3200, maximumAge:300000 });
  });
}

function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number) {
  const toRadians = (value: number) => value * Math.PI / 180;
  const deltaLat = toRadians(lat2 - lat1);
  const deltaLon = toRadians(lon2 - lon1);
  const value = Math.sin(deltaLat / 2) ** 2 + Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(deltaLon / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value));
}

function asStringArray(value: unknown) {
  if (Array.isArray(value)) return value.map(String).map(item => item.trim()).filter(Boolean);
  if (typeof value === 'string') return value.split(',').map(item => item.trim()).filter(Boolean);
  return [];
}
function positiveNumber(value: unknown) { const number = Number(value); return Number.isFinite(number) && number > 0 ? number : 0; }
function positiveOrNegativeNumber(value: unknown) { const number = Number(value); return Number.isFinite(number) ? number : null; }
function stringValue(value: unknown) { return typeof value === 'string' && value.trim() ? value.trim() : undefined; }
function parseMoneyLabel(value: string) { const normalized = value.replace(/[^0-9,.-]/g,'').replace(/\./g,'').replace(',','.'); const number = Number(normalized); return Number.isFinite(number) ? number : 0; }

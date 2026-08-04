import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { ProductFeed, type FeedProduct } from '../components/ProductFeed';
import {
  errorMessage,
  request,
  type ApiItem,
  type CatalogResponse,
  type JsonRecord,
  type JourneyHint,
  type Offer,
  type ViewProps,
} from '../lib/api';
import { Modal, SectionHeader, StateCard } from '../ui';

type FeedNavigationProps = {
  avatarDataUrl: string;
  onHome: () => void;
  onBack: () => void;
  onProfile: () => void;
};

type ConsumerOrder = {
  id: string;
  title?: string;
  status?: string;
  offer_id?: string;
  source_entity_id?: string;
  can_review?: boolean;
};

type UserShoppingContext = {
  interests: string[];
  affordabilityConsent: boolean;
  safeMonthlyLimit: number | null;
};

const completedStatuses = new Set(['completed', 'delivered', 'paid', 'received']);

function text(value: unknown) {
  return value == null ? '' : String(value);
}

function stringList(value: unknown) {
  if (Array.isArray(value)) return value.map(String).filter(Boolean);
  if (typeof value === 'string') return value.split(',').map(item => item.trim()).filter(Boolean);
  return [];
}

function normalizeOffer(offer: Offer): FeedProduct {
  const metadata = offer.metadata as (Offer['metadata'] & Record<string, unknown>) | undefined;
  return {
    id: offer.offer_id,
    offerId: offer.offer_id,
    sourceEntityId: offer.source_entity_id,
    sourceModule: offer.source_module,
    title: offer.title,
    description: offer.short_description ?? offer.description ?? '',
    category: offer.consumer_category,
    provider: offer.provider_label,
    region: offer.region_label,
    distanceKm: offer.distance_km,
    priceAmount: offer.price_amount,
    imageUrl: metadata?.image_url,
    videoUrl: metadata?.video_url,
    accentColor: text(metadata?.accent_color) || undefined,
  };
}

function normalizeStockItem(item: ApiItem): FeedProduct {
  const payload = item.payload ?? {};
  return {
    id: item.id,
    offerId: text(payload.offer_id) || `stock:catalog_products:${item.id}`,
    sourceEntityId: item.id,
    sourceModule: 'stock',
    title: text(payload.title ?? payload.name ?? item.id),
    description: text(payload.description ?? payload.short_description),
    category: text(payload.category ?? payload.consumer_category ?? 'Produtos'),
    provider: text(payload.supplier_name ?? payload.provider_label ?? 'Fornecedor homologado'),
    region: text(payload.region ?? payload.region_label ?? 'Entrega sob demanda'),
    distanceKm: payload.distance_km == null ? null : Number(payload.distance_km),
    priceAmount: payload.price_amount == null ? null : text(payload.price_amount),
    imageUrl: text(payload.image_url ?? payload.primary_image_url) || undefined,
    videoUrl: text(payload.video_url) || undefined,
    accentColor: text(payload.accent_color) || undefined,
  };
}

function orderMatches(order: ConsumerOrder, product: FeedProduct) {
  if (order.can_review === false) return false;
  if (order.offer_id && order.offer_id === product.offerId) return true;
  if (order.source_entity_id && order.source_entity_id === product.sourceEntityId) return true;
  return Boolean(order.title && order.title.trim().toLocaleLowerCase('pt-BR') === product.title.trim().toLocaleLowerCase('pt-BR'));
}

function getReviewOrder(orders: ConsumerOrder[], product: FeedProduct) {
  return orders.find(order => (order.can_review || completedStatuses.has((order.status ?? '').toLocaleLowerCase('pt-BR'))) && orderMatches(order, product));
}

function currentLocation() {
  return new Promise<{ lat: number; lng: number } | null>(resolve => {
    if (!navigator.geolocation) {
      resolve(null);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      position => resolve({ lat: position.coords.latitude, lng: position.coords.longitude }),
      () => resolve(null),
      { enableHighAccuracy: false, maximumAge: 300000, timeout: 5000 },
    );
  });
}

async function loadShoppingContext(session: ViewProps['session']): Promise<UserShoppingContext> {
  try {
    const users = await request<ApiItem[]>('/identity/resources/users', 'GET', undefined, session.accessToken);
    const payload = users.find(item => item.id === session.userId)?.payload ?? {};
    const interests = stringList(payload.shopping_interests ?? payload.interests ?? payload.favorite_categories);
    const consent = payload.purchase_power_consent === true;
    if (!consent) return { interests, affordabilityConsent: false, safeMonthlyLimit: null };

    const verifiedIncome = Number(payload.verified_monthly_income_brl ?? 0);
    const declaredIncome = Number(payload.declared_monthly_income_brl ?? 0);
    const income = verifiedIncome > 0 ? verifiedIncome : declaredIncome;
    const commitments = Math.max(0, Number(payload.monthly_fixed_commitments_brl ?? 0));
    const disposable = Math.max(0, income - commitments);
    const configuredPercent = Number(payload.max_purchase_commitment_percent ?? 20);
    const percent = Math.min(25, Math.max(5, configuredPercent)) / 100;
    return {
      interests,
      affordabilityConsent: true,
      safeMonthlyLimit: disposable > 0 ? disposable * percent : null,
    };
  } catch {
    return { interests: [], affordabilityConsent: false, safeMonthlyLimit: null };
  }
}

function interestScore(product: FeedProduct, interests: string[]) {
  const haystack = `${product.category} ${product.title} ${product.description}`.toLocaleLowerCase('pt-BR');
  return interests.reduce((score, interest) => score + (haystack.includes(interest.toLocaleLowerCase('pt-BR')) ? 1 : 0), 0);
}

function estimatedMonthlyCost(product: FeedProduct) {
  const price = Number(product.priceAmount ?? 0);
  return price > 0 ? price / 12 : 0;
}

function categoriesFor(products: FeedProduct[]) {
  return Array.from(new Set(products.map(product => product.category).filter(Boolean))).sort((left, right) => left.localeCompare(right, 'pt-BR'));
}

function SellerComposer({ session, setNotice, mode, onDone }: ViewProps & { mode: 'sell' | 'repair-request'; onDone: () => void }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [price, setPrice] = useState('');
  const [region, setRegion] = useState('');
  const repair = mode === 'repair-request';

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/marketplace/resources/products', 'POST', {
        user_id: session.userId,
        status: 'draft',
        payload: {
          title,
          description,
          category,
          price_amount: repair ? null : price,
          region,
          listing_type: repair ? 'repair_request' : 'sale',
          requested_specialty: repair ? category : null,
        },
      }, session.accessToken);
      setTitle(''); setDescription(''); setCategory(''); setPrice(''); setRegion('');
      setNotice(repair ? 'Pedido de conserto enviado para análise.' : 'Item enviado para análise e publicação.');
      onDone();
    } catch (error) {
      setNotice(errorMessage(error));
    }
  };

  return <section><SectionHeader title={repair ? 'Publicar pedido de conserto' : 'Vender um item'} subtitle={repair ? 'Descreva o item, o problema e a especialidade necessária.' : 'Cadastre fotos, descrição, preço e região do anúncio.'} />
    <form className='form-card listing-composer' onSubmit={submit}>
      <label>{repair ? 'Item que precisa de conserto' : 'Título do anúncio'}<input value={title} onChange={event => setTitle(event.target.value)} required /></label>
      <label>{repair ? 'Defeito ou problema' : 'Descrição'}<textarea value={description} onChange={event => setDescription(event.target.value)} required /></label>
      <label>{repair ? 'Especialidade necessária' : 'Categoria'}<input value={category} onChange={event => setCategory(event.target.value)} required /></label>
      {!repair && <label>Preço<input inputMode='decimal' value={price} onChange={event => setPrice(event.target.value)} required /></label>}
      <label>Região<input value={region} onChange={event => setRegion(event.target.value)} required /></label>
      <button className='primary' type='submit'>{repair ? 'Publicar pedido' : 'Cadastrar item'}</button>
    </form>
  </section>;
}

function FeedDialogs({
  commentProduct,
  supplierProduct,
  orders,
  session,
  setNotice,
  onCloseComment,
  onCloseSupplier,
}: {
  commentProduct: FeedProduct | null;
  supplierProduct: FeedProduct | null;
  orders: ConsumerOrder[];
  session: ViewProps['session'];
  setNotice: ViewProps['setNotice'];
  onCloseComment: () => void;
  onCloseSupplier: () => void;
}) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [message, setMessage] = useState('');

  const submitComment = async () => {
    if (!commentProduct) return;
    const order = getReviewOrder(orders, commentProduct);
    if (!order) {
      setNotice('Comentários são permitidos somente após a compra concluída.');
      return;
    }
    try {
      await request(`/gateway/consumer/orders/${order.id}/reviews`, 'POST', {
        rating,
        comment: comment.trim() || null,
        idempotency_key: window.crypto.randomUUID(),
      }, session.accessToken);
      setComment('');
      onCloseComment();
      setNotice('Comentário publicado para sua compra.');
    } catch (error) {
      setNotice(errorMessage(error));
    }
  };

  const submitSupplierMessage = async () => {
    if (!supplierProduct || message.trim().length < 5) return;
    try {
      await request('/crm/resources/activities', 'POST', {
        user_id: session.userId,
        status: 'requested',
        payload: {
          activity_type: 'supplier_message',
          offer_id: supplierProduct.offerId,
          source_module: supplierProduct.sourceModule,
          provider_label: supplierProduct.provider,
          message: message.trim(),
          channel: 'valley_in_app',
        },
      }, session.accessToken);
      setMessage('');
      onCloseSupplier();
      setNotice('Mensagem enviada ao fornecedor dentro do Valley.');
    } catch (error) {
      setNotice(errorMessage(error));
    }
  };

  return <>
    {commentProduct && <Modal title='Comentar compra' onClose={onCloseComment}><p>{commentProduct.title}</p><label>Nota<input type='number' min='1' max='5' value={rating} onChange={event => setRating(Number(event.target.value))} /></label><label>Comentário<textarea value={comment} onChange={event => setComment(event.target.value)} maxLength={1000} /></label><button className='primary' type='button' onClick={submitComment}>Publicar comentário</button></Modal>}
    {supplierProduct && <Modal title='Falar com o fornecedor' onClose={onCloseSupplier}><p>{supplierProduct.provider} · {supplierProduct.title}</p><label>Mensagem<textarea value={message} onChange={event => setMessage(event.target.value)} minLength={5} maxLength={1000} placeholder='Digite sua dúvida sobre o produto' /></label><button className='primary' type='button' disabled={message.trim().length < 5} onClick={submitSupplierMessage}>Enviar mensagem</button></Modal>}
  </>;
}

function useFeedActions(session: ViewProps['session'], setNotice: ViewProps['setNotice'], orders: ConsumerOrder[], reloadOrders: () => Promise<void>) {
  const [commentProduct, setCommentProduct] = useState<FeedProduct | null>(null);
  const [supplierProduct, setSupplierProduct] = useState<FeedProduct | null>(null);

  const favorite = async (product: FeedProduct) => {
    try {
      const entity = encodeURIComponent(product.sourceEntityId ?? product.offerId);
      await request(`/marketplace/valley/favorites/${entity}`, 'PUT', undefined, session.accessToken);
      setNotice('Produto adicionado aos favoritos.');
    } catch (error) { setNotice(errorMessage(error)); }
  };

  const addToCart = async (product: FeedProduct) => {
    try {
      await request('/marketplace/resources/carts', 'POST', {
        user_id: session.userId,
        status: 'active',
        payload: {
          offer_id: product.offerId,
          source_entity_id: product.sourceEntityId,
          source_module: product.sourceModule,
          title: product.title,
          quantity: 1,
        },
      }, session.accessToken);
      setNotice('Produto adicionado ao carrinho.');
    } catch (error) { setNotice(errorMessage(error)); }
  };

  const buy = async (product: FeedProduct) => {
    try {
      await request<JsonRecord>('/gateway/catalog/actions', 'POST', {
        offer_id: product.offerId,
        action: 'buy',
        customer_user_id: session.userId,
        idempotency_key: window.crypto.randomUUID(),
        quantity: 1,
      }, session.accessToken);
      setNotice('Pedido criado. Continue no Financeiro para concluir o pagamento.');
      await reloadOrders();
    } catch (error) { setNotice(errorMessage(error)); }
  };

  return {
    commentProduct,
    supplierProduct,
    canComment: (product: FeedProduct) => Boolean(getReviewOrder(orders, product)),
    favorite,
    addToCart,
    buy,
    openComment: setCommentProduct,
    openSupplier: setSupplierProduct,
    closeComment: () => setCommentProduct(null),
    closeSupplier: () => setSupplierProduct(null),
  };
}

export function MarketplaceView({ session, setNotice, hint, avatarDataUrl, onHome, onBack, onProfile }: ViewProps & { hint?: JourneyHint } & FeedNavigationProps) {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [orders, setOrders] = useState<ConsumerOrder[]>([]);
  const [shoppingContext, setShoppingContext] = useState<UserShoppingContext>({ interests: [], affordabilityConsent: false, safeMonthlyLimit: null });
  const [query, setQuery] = useState(hint?.query ?? '');
  const [appliedQuery, setAppliedQuery] = useState(hint?.query ?? '');
  const [category, setCategory] = useState('');
  const [coordinates, setCoordinates] = useState<{ lat: number; lng: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);

  const reloadOrders = useCallback(async () => {
    try {
      const data = await request<{ data?: ConsumerOrder[] }>('/gateway/consumer/orders', 'GET', undefined, session.accessToken);
      setOrders(data.data ?? []);
    } catch {
      setOrders([]);
    }
  }, [session.accessToken]);

  useEffect(() => {
    void currentLocation().then(setCoordinates);
    void loadShoppingContext(session).then(setShoppingContext);
    void reloadOrders();
  }, [reloadOrders, session]);

  const load = useCallback(async (append = false, offset = 0) => {
    if (append) setLoadingMore(true); else setLoading(true);
    setError('');
    const params = new URLSearchParams({ offset: String(offset), limit: '30', radius_km: '10', location_fallback: 'delivery_address,residential_address', ranking: 'interest_distance' });
    if (appliedQuery.trim()) params.set('q', appliedQuery.trim());
    if (category) params.set('category', category);
    if (coordinates) { params.set('lat', String(coordinates.lat)); params.set('lng', String(coordinates.lng)); }
    if (shoppingContext.interests.length) params.set('interests', shoppingContext.interests.join(','));
    try {
      const data = await request<CatalogResponse>(`/gateway/catalog/offers?${params}`);
      setOffers(current => append ? [...current, ...(data.data ?? [])] : (data.data ?? []));
      setTotal(data.total ?? 0);
    } catch (loadError) {
      setError(errorMessage(loadError));
      if (!append) setOffers([]);
    } finally {
      if (append) setLoadingMore(false); else setLoading(false);
    }
  }, [appliedQuery, category, coordinates, shoppingContext.interests]);

  useEffect(() => { const timer = window.setTimeout(() => { void load(false, 0); }, 0); return () => window.clearTimeout(timer); }, [load]);

  const products = useMemo(() => offers
    .filter(offer => offer.source_module !== 'stock')
    .map(normalizeOffer)
    .filter(product => product.distanceKm == null || product.distanceKm <= 10)
    .sort((left, right) => {
      const interestDifference = interestScore(right, shoppingContext.interests) - interestScore(left, shoppingContext.interests);
      if (interestDifference) return interestDifference;
      return (left.distanceKm ?? 999) - (right.distanceKm ?? 999);
    }), [offers, shoppingContext.interests]);

  const actions = useFeedActions(session, setNotice, orders, reloadOrders);
  const mode = hint?.mode;
  if (mode === 'sell' || mode === 'repair-request') {
    return <SellerComposer session={session} setNotice={setNotice} mode={mode} onDone={() => onHome()} />;
  }

  return <>
    <ProductFeed
      title='Marketplace'
      products={products}
      categories={categoriesFor(products)}
      activeCategory={category}
      query={query}
      avatarDataUrl={avatarDataUrl}
      loading={loading}
      error={error}
      hasMore={offers.length < total}
      loadingMore={loadingMore}
      canComment={actions.canComment}
      onHome={onHome}
      onBack={onBack}
      onProfile={onProfile}
      onQueryChange={setQuery}
      onSearch={() => setAppliedQuery(query.trim())}
      onCategoryChange={setCategory}
      onFavorite={product => void actions.favorite(product)}
      onComment={actions.openComment}
      onAddToCart={product => void actions.addToCart(product)}
      onBuy={product => void actions.buy(product)}
      onSupplier={actions.openSupplier}
      onLoadMore={() => void load(true, offers.length)}
    />
    <FeedDialogs commentProduct={actions.commentProduct} supplierProduct={actions.supplierProduct} orders={orders} session={session} setNotice={setNotice} onCloseComment={actions.closeComment} onCloseSupplier={actions.closeSupplier} />
  </>;
}

export function StockView({ session, setNotice, hint, avatarDataUrl, onHome, onBack, onProfile }: ViewProps & { hint?: JourneyHint } & FeedNavigationProps) {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [fallbackItems, setFallbackItems] = useState<ApiItem[]>([]);
  const [orders, setOrders] = useState<ConsumerOrder[]>([]);
  const [shoppingContext, setShoppingContext] = useState<UserShoppingContext>({ interests: [], affordabilityConsent: false, safeMonthlyLimit: null });
  const [query, setQuery] = useState(hint?.query ?? '');
  const [appliedQuery, setAppliedQuery] = useState(hint?.query ?? '');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const reloadOrders = useCallback(async () => {
    try {
      const data = await request<{ data?: ConsumerOrder[] }>('/gateway/consumer/orders', 'GET', undefined, session.accessToken);
      setOrders(data.data ?? []);
    } catch { setOrders([]); }
  }, [session.accessToken]);

  useEffect(() => {
    void loadShoppingContext(session).then(setShoppingContext);
    void reloadOrders();
  }, [reloadOrders, session]);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    const params = new URLSearchParams({ offset: '0', limit: '100', ranking: 'interest_affordability_best_sellers' });
    if (appliedQuery.trim()) params.set('q', appliedQuery.trim());
    if (category) params.set('category', category);
    if (shoppingContext.interests.length) params.set('interests', shoppingContext.interests.join(','));
    if (shoppingContext.affordabilityConsent && shoppingContext.safeMonthlyLimit != null) params.set('safe_monthly_commitment_max', shoppingContext.safeMonthlyLimit.toFixed(2));
    try {
      const [catalogResult, directResult] = await Promise.allSettled([
        request<CatalogResponse>(`/gateway/catalog/offers?${params}`),
        request<ApiItem[]>('/stock/resources/catalog_products', 'GET', undefined, session.accessToken),
      ]);
      setOffers(catalogResult.status === 'fulfilled' ? catalogResult.value.data ?? [] : []);
      setFallbackItems(directResult.status === 'fulfilled' ? directResult.value ?? [] : []);
      if (catalogResult.status === 'rejected' && directResult.status === 'rejected') throw catalogResult.reason;
    } catch (loadError) {
      setError(errorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }, [appliedQuery, category, session.accessToken, shoppingContext]);

  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);

  const products = useMemo(() => {
    const catalog = offers.filter(offer => offer.source_module === 'stock').map(normalizeOffer);
    const base = catalog.length ? catalog : fallbackItems.map(normalizeStockItem);
    const normalizedQuery = appliedQuery.toLocaleLowerCase('pt-BR');
    return base
      .filter(product => !normalizedQuery || `${product.title} ${product.description} ${product.category}`.toLocaleLowerCase('pt-BR').includes(normalizedQuery))
      .filter(product => !category || product.category === category)
      .filter(product => {
        if (!shoppingContext.affordabilityConsent || shoppingContext.safeMonthlyLimit == null) return true;
        const monthlyCost = estimatedMonthlyCost(product);
        return monthlyCost === 0 || monthlyCost <= shoppingContext.safeMonthlyLimit;
      })
      .sort((left, right) => {
        const interestDifference = interestScore(right, shoppingContext.interests) - interestScore(left, shoppingContext.interests);
        if (interestDifference) return interestDifference;
        const rightSales = Number((fallbackItems.find(item => item.id === right.sourceEntityId)?.payload ?? {}).sales_count ?? 0);
        const leftSales = Number((fallbackItems.find(item => item.id === left.sourceEntityId)?.payload ?? {}).sales_count ?? 0);
        return rightSales - leftSales;
      });
  }, [appliedQuery, category, fallbackItems, offers, shoppingContext]);

  const actions = useFeedActions(session, setNotice, orders, reloadOrders);
  return <>
    <ProductFeed
      title='Estoque'
      products={products}
      categories={categoriesFor(products)}
      activeCategory={category}
      query={query}
      avatarDataUrl={avatarDataUrl}
      loading={loading}
      error={error}
      canComment={actions.canComment}
      onHome={onHome}
      onBack={onBack}
      onProfile={onProfile}
      onQueryChange={setQuery}
      onSearch={() => setAppliedQuery(query.trim())}
      onCategoryChange={setCategory}
      onFavorite={product => void actions.favorite(product)}
      onComment={actions.openComment}
      onAddToCart={product => void actions.addToCart(product)}
      onBuy={product => void actions.buy(product)}
      onSupplier={actions.openSupplier}
    />
    <FeedDialogs commentProduct={actions.commentProduct} supplierProduct={actions.supplierProduct} orders={orders} session={session} setNotice={setNotice} onCloseComment={actions.closeComment} onCloseSupplier={actions.closeSupplier} />
    {!loading && products.length === 0 && shoppingContext.affordabilityConsent && shoppingContext.safeMonthlyLimit != null && <StateCard text='Nenhum produto encontrado dentro dos interesses e do limite mensal informado. Ajuste seus dados ou use a busca.' />}
  </>;
}

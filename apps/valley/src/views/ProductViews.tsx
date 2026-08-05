import {
  type FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  ProductFeed,
  type FeedFact,
  type FeedMedia,
  type FeedProduct,
} from '../components/ProductFeed';
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

type Coordinates = { lat: number; lng: number };

type ReviewOrder = {
  id: string;
  title?: string;
  status?: string;
  offer_id?: string;
  source_entity_id?: string;
  source_module?: string;
  can_review?: boolean;
};

type ShoppingContext = {
  ready: boolean;
  interests: string[];
  affordabilityConsent: boolean;
  safeMonthlyLimit: number | null;
  fallbackCoordinates: Coordinates | null;
};

type MarketplaceCatalogItem = {
  id: string;
  store_id?: string | null;
  store_name?: string | null;
  sku?: string | null;
  name?: string | null;
  description?: string | null;
  category?: string | null;
  subcategory?: string | null;
  brand?: string | null;
  price_brl?: string | null;
  currency?: string | null;
  image_url?: string | null;
  media?: unknown[];
  rating?: number | string | null;
  review_count?: number | string | null;
  in_stock?: boolean;
  stock_quantity?: number | null;
  distance_km?: number | null;
  sponsored?: boolean;
  published_at?: string | null;
  promotion?: Record<string, unknown> | null;
};

type MarketplaceCatalogResponse = {
  items?: MarketplaceCatalogItem[];
  total?: number;
};

const EMPTY_CONTEXT: ShoppingContext = {
  ready: false,
  interests: [],
  affordabilityConsent: false,
  safeMonthlyLimit: null,
  fallbackCoordinates: null,
};

function text(value: unknown) {
  return value == null ? '' : String(value);
}

function stringList(value: unknown) {
  if (Array.isArray(value)) return value.map(String).filter(Boolean);
  if (typeof value === 'string') {
    return value.split(',').map(item => item.trim()).filter(Boolean);
  }
  return [];
}

function numberOrNull(value: unknown) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function locationFrom(value: unknown): Coordinates | null {
  if (!value || typeof value !== 'object') return null;
  const record = value as Record<string, unknown>;
  const nested = record.location && typeof record.location === 'object'
    ? record.location as Record<string, unknown>
    : record;
  const lat = numberOrNull(nested.latitude ?? nested.lat);
  const lng = numberOrNull(nested.longitude ?? nested.lng ?? nested.lon);
  if (lat == null || lng == null) return null;
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) return null;
  return { lat, lng };
}

function isVideoUrl(url: string) {
  return /\.(mp4|webm|mov|m4v)(?:\?|$)/i.test(url);
}

function mediaFrom(
  rawMedia: unknown,
  primaryImage?: unknown,
  primaryVideo?: unknown,
): FeedMedia[] {
  const output: FeedMedia[] = [];
  const push = (item: FeedMedia) => {
    const normalized = item.url.trim();
    if (!normalized || output.some(existing => existing.url === normalized)) return;
    output.push({ ...item, url: normalized });
  };

  const videoUrl = text(primaryVideo);
  const imageUrl = text(primaryImage);
  if (videoUrl) {
    push({
      url: videoUrl,
      type: 'video',
      posterUrl: imageUrl || undefined,
    });
  }

  for (const candidate of Array.isArray(rawMedia) ? rawMedia : []) {
    if (typeof candidate === 'string') {
      push({
        url: candidate,
        type: isVideoUrl(candidate) ? 'video' : 'image',
      });
      continue;
    }
    if (!candidate || typeof candidate !== 'object') continue;
    const record = candidate as Record<string, unknown>;
    const url = text(record.url ?? record.src ?? record.media_url);
    if (!url) continue;
    const declaredType = text(
      record.type ?? record.kind ?? record.mime_type,
    ).toLocaleLowerCase('pt-BR');
    const type = declaredType.includes('video') || isVideoUrl(url)
      ? 'video'
      : 'image';
    push({
      url,
      type,
      posterUrl: text(record.poster_url ?? record.poster) || undefined,
      alt: text(record.alt ?? record.description) || undefined,
    });
  }

  if (imageUrl) push({ url: imageUrl, type: 'image' });
  return output;
}

function fact(label: string, value: unknown): FeedFact | null {
  if (value == null || value === '') return null;
  return { label, value: String(value) };
}

function compactFacts(items: Array<FeedFact | null>) {
  return items.filter((item): item is FeedFact => item !== null);
}

function normalizeMarketplaceItem(item: MarketplaceCatalogItem): FeedProduct {
  const promotion = item.promotion ?? {};
  const rating = numberOrNull(item.rating);
  const reviewCount = numberOrNull(item.review_count);
  const media = mediaFrom(item.media, item.image_url);
  return {
    id: item.id,
    offerId: `marketplace:products:${item.id}`,
    sourceEntityId: item.id,
    sourceModule: 'marketplace',
    title: text(item.name) || 'Produto sem título',
    description: text(item.description),
    fullDescription: text(item.description),
    category: text(item.category) || 'Produtos',
    provider: text(item.store_name) || 'Fornecedor verificado',
    region: 'Disponível em até 10 km',
    distanceKm: item.distance_km,
    priceAmount: item.price_brl,
    imageUrl: media.find(entry => entry.type === 'image')?.url,
    videoUrl: media.find(entry => entry.type === 'video')?.url,
    media,
    facts: compactFacts([
      fact('Categoria', item.category),
      fact('Subcategoria', item.subcategory),
      fact('Marca', item.brand),
      fact('SKU', item.sku),
      fact('Disponibilidade', item.in_stock === false ? 'Indisponível' : 'Disponível'),
      fact('Estoque informado', item.stock_quantity),
      fact('Moeda', item.currency || 'BRL'),
      fact('Avaliação', rating == null ? null : rating.toFixed(1)),
      fact('Quantidade de avaliações', reviewCount),
      fact('Distância', item.distance_km == null ? null : `${item.distance_km.toFixed(1)} km`),
      fact('Anúncio patrocinado', item.sponsored ? 'Sim' : null),
      fact('Publicado em', item.published_at),
    ]),
    supplier: {
      name: text(item.store_name) || 'Fornecedor verificado',
      verified: true,
      region: 'Atendimento pelo Marketplace Valley',
      rating,
      reviewCount,
      sourceLabel: 'Marketplace local Valley',
    },
    accentColor: text(promotion.accent_color) || undefined,
  };
}

function normalizeOffer(offer: Offer): FeedProduct {
  const metadata = (offer.metadata ?? {}) as Record<string, unknown>;
  const gallery = [
    ...(Array.isArray(metadata.media) ? metadata.media : []),
    ...(Array.isArray(metadata.gallery) ? metadata.gallery : []),
    ...(Array.isArray(metadata.images) ? metadata.images : []),
    ...(Array.isArray(metadata.videos) ? metadata.videos : []),
  ];
  const media = mediaFrom(
    gallery,
    metadata.primary_image_url ?? metadata.image_url,
    metadata.video_url,
  );
  const rating = numberOrNull(metadata.rating);
  const reviewCount = numberOrNull(metadata.review_count);
  return {
    id: offer.offer_id,
    offerId: offer.offer_id,
    sourceEntityId: offer.source_entity_id,
    sourceModule: offer.source_module,
    title: offer.title,
    description: offer.short_description ?? offer.description ?? '',
    fullDescription: offer.description ?? offer.short_description ?? '',
    category: offer.consumer_category,
    provider: offer.provider_label,
    region: offer.region_label,
    distanceKm: offer.distance_km,
    priceAmount: offer.price_amount,
    imageUrl: media.find(entry => entry.type === 'image')?.url,
    videoUrl: media.find(entry => entry.type === 'video')?.url,
    media,
    facts: compactFacts([
      fact('Categoria', offer.consumer_category),
      fact('Tipo de oferta', offer.offer_type_label),
      fact('Marca', metadata.brand),
      fact('Modelo', metadata.model),
      fact('SKU', metadata.sku),
      fact('Condição', metadata.condition),
      fact('Disponibilidade', metadata.availability),
      fact('Itens vendidos', metadata.sold_count),
      fact('Avaliação', rating == null ? null : rating.toFixed(1)),
      fact('Quantidade de avaliações', reviewCount),
      fact('Origem', offer.source_module === 'stock' ? 'Estoque Valley' : offer.source_module),
    ]),
    supplier: {
      name: offer.provider_label,
      verified: offer.verified_seller === true,
      region: offer.region_label,
      rating,
      reviewCount,
      sourceLabel: offer.source_module === 'stock'
        ? 'Fornecedor homologado do Estoque Valley'
        : 'Fornecedor cadastrado no Valley',
    },
    accentColor: text(metadata.accent_color) || undefined,
  };
}

function normalizeStockItem(item: ApiItem): FeedProduct {
  const payload = item.payload ?? {};
  const gallery = [
    ...(Array.isArray(payload.media) ? payload.media : []),
    ...(Array.isArray(payload.gallery) ? payload.gallery : []),
    ...(Array.isArray(payload.images) ? payload.images : []),
    ...(Array.isArray(payload.videos) ? payload.videos : []),
  ];
  const media = mediaFrom(
    gallery,
    payload.primary_image_url ?? payload.image_url,
    payload.video_url,
  );
  const rating = numberOrNull(payload.rating);
  const reviewCount = numberOrNull(payload.review_count);
  const provider = text(
    payload.supplier_name ?? payload.provider_label ?? 'Fornecedor homologado',
  );
  const region = text(
    payload.region ?? payload.region_label ?? 'Entrega sob demanda',
  );
  return {
    id: item.id,
    offerId: text(payload.offer_id) || `stock:catalog_products:${item.id}`,
    sourceEntityId: item.id,
    sourceModule: 'stock',
    title: text(payload.title ?? payload.name ?? item.id),
    description: text(payload.short_description ?? payload.description),
    fullDescription: text(payload.description ?? payload.short_description),
    category: text(payload.category ?? payload.consumer_category ?? 'Produtos'),
    provider,
    region,
    distanceKm: payload.distance_km == null ? null : Number(payload.distance_km),
    priceAmount: payload.price_amount == null
      ? payload.price_brl == null ? null : text(payload.price_brl)
      : text(payload.price_amount),
    imageUrl: media.find(entry => entry.type === 'image')?.url,
    videoUrl: media.find(entry => entry.type === 'video')?.url,
    media,
    facts: compactFacts([
      fact('Categoria', payload.category ?? payload.consumer_category),
      fact('Subcategoria', payload.subcategory),
      fact('Marca', payload.brand),
      fact('Modelo', payload.model),
      fact('SKU', payload.sku ?? payload.external_sku),
      fact('Condição', payload.condition),
      fact('Disponibilidade', payload.availability),
      fact('Prazo estimado', payload.delivery_estimate),
      fact('Itens vendidos', payload.sales_count),
      fact('Avaliação', rating == null ? null : rating.toFixed(1)),
      fact('Quantidade de avaliações', reviewCount),
    ]),
    supplier: {
      name: provider,
      verified: payload.supplier_status === 'approved'
        || payload.verified_supplier === true,
      region,
      rating,
      reviewCount,
      sourceLabel: 'Fornecedor homologado do Estoque Valley',
    },
    accentColor: text(payload.accent_color) || undefined,
  };
}

function reviewMatches(order: ReviewOrder, product: FeedProduct) {
  if (order.can_review !== true) return false;
  if (order.source_module && order.source_module !== product.sourceModule) return false;
  if (order.offer_id && order.offer_id === product.offerId) return true;
  if (order.source_entity_id && order.source_entity_id === product.sourceEntityId) {
    return true;
  }
  return Boolean(
    order.title
    && order.title.trim().toLocaleLowerCase('pt-BR')
      === product.title.trim().toLocaleLowerCase('pt-BR'),
  );
}

function eligibleOrder(orders: ReviewOrder[], product: FeedProduct) {
  return orders.find(order => reviewMatches(order, product));
}

function currentLocation() {
  return new Promise<Coordinates | null>(resolve => {
    if (!navigator.geolocation) {
      resolve(null);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      position => resolve({
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      }),
      () => resolve(null),
      {
        enableHighAccuracy: false,
        maximumAge: 300000,
        timeout: 5000,
      },
    );
  });
}

async function loadShoppingContext(
  session: ViewProps['session'],
): Promise<ShoppingContext> {
  try {
    const users = await request<ApiItem[]>(
      '/identity/resources/users',
      'GET',
      undefined,
      session.accessToken,
    );
    const payload = users.find(item => item.id === session.userId)?.payload ?? {};
    const interests = stringList(
      payload.shopping_interests
      ?? payload.interests
      ?? payload.favorite_categories,
    );
    const fallbackCoordinates = (
      locationFrom(payload.delivery_address)
      ?? locationFrom(payload.residential_address)
      ?? locationFrom(payload.address)
    );
    const consent = payload.purchase_power_consent === true;
    if (!consent) {
      return {
        ready: true,
        interests,
        affordabilityConsent: false,
        safeMonthlyLimit: null,
        fallbackCoordinates,
      };
    }

    const verifiedIncome = Number(payload.verified_monthly_income_brl ?? 0);
    const declaredIncome = Number(payload.declared_monthly_income_brl ?? 0);
    const income = verifiedIncome > 0 ? verifiedIncome : declaredIncome;
    const commitments = Math.max(
      0,
      Number(payload.monthly_fixed_commitments_brl ?? 0),
    );
    const disposable = Math.max(0, income - commitments);
    const configuredPercent = Number(payload.max_purchase_commitment_percent ?? 20);
    const percent = Math.min(25, Math.max(5, configuredPercent)) / 100;
    return {
      ready: true,
      interests,
      affordabilityConsent: true,
      safeMonthlyLimit: disposable > 0 ? disposable * percent : null,
      fallbackCoordinates,
    };
  } catch {
    return { ...EMPTY_CONTEXT, ready: true };
  }
}

async function loadReviewEligibility(
  session: ViewProps['session'],
): Promise<ReviewOrder[]> {
  try {
    const result = await request<ReviewOrder[]>(
      '/marketplace/valley/feed/review-eligibility',
      'GET',
      undefined,
      session.accessToken,
    );
    return Array.isArray(result) ? result : [];
  } catch {
    return [];
  }
}

function interestScore(product: FeedProduct, interests: string[]) {
  const haystack = `${product.category} ${product.title} ${product.description}`
    .toLocaleLowerCase('pt-BR');
  return interests.reduce(
    (score, interest) => score + (
      haystack.includes(interest.toLocaleLowerCase('pt-BR')) ? 1 : 0
    ),
    0,
  );
}

function monthlyCommitment(product: FeedProduct) {
  const price = Number(product.priceAmount ?? 0);
  return Number.isFinite(price) && price > 0 ? price : 0;
}

function categoriesFor(products: FeedProduct[]) {
  return Array.from(new Set(
    products.map(product => product.category).filter(Boolean),
  )).sort((left, right) => left.localeCompare(right, 'pt-BR'));
}

function isUuid(value: string | undefined) {
  return Boolean(
    value
    && /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value),
  );
}

function SellerComposer({
  session,
  setNotice,
  mode,
  onDone,
}: ViewProps & { mode: 'sell' | 'repair-request'; onDone: () => void }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [price, setPrice] = useState('');
  const [region, setRegion] = useState('');
  const repair = mode === 'repair-request';

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/crm/resources/leads', 'POST', {
        user_id: session.userId,
        status: 'requested',
        payload: {
          lead_type: repair
            ? 'consumer_marketplace_repair_request'
            : 'consumer_marketplace_listing',
          title,
          description,
          category,
          price_amount: repair ? null : price,
          region,
          requested_specialty: repair ? category : null,
          moderation_required: true,
          source_channel: 'valley_consumer',
        },
      }, session.accessToken);
      setTitle('');
      setDescription('');
      setCategory('');
      setPrice('');
      setRegion('');
      setNotice(
        repair
          ? 'Pedido de conserto enviado para análise e publicação.'
          : 'Anúncio enviado para análise e publicação.',
      );
      onDone();
    } catch (error) {
      setNotice(errorMessage(error));
    }
  };

  return <section>
    <SectionHeader
      title={repair ? 'Publicar pedido de conserto' : 'Vender um item'}
      subtitle={
        repair
          ? 'Descreva o item, o problema e a especialidade necessária.'
          : 'Cadastre descrição, preço e região para moderação do anúncio.'
      }
    />
    <form className='form-card listing-composer' onSubmit={submit}>
      <label>{repair ? 'Item que precisa de conserto' : 'Título do anúncio'}
        <input value={title} onChange={event => setTitle(event.target.value)} required />
      </label>
      <label>{repair ? 'Defeito ou problema' : 'Descrição'}
        <textarea value={description} onChange={event => setDescription(event.target.value)} required />
      </label>
      <label>{repair ? 'Especialidade necessária' : 'Categoria'}
        <input value={category} onChange={event => setCategory(event.target.value)} required />
      </label>
      {!repair && <label>Preço
        <input inputMode='decimal' value={price} onChange={event => setPrice(event.target.value)} required />
      </label>}
      <label>Região
        <input value={region} onChange={event => setRegion(event.target.value)} required />
      </label>
      <button className='primary' type='submit'>
        {repair ? 'Enviar pedido para análise' : 'Enviar anúncio para análise'}
      </button>
    </form>
  </section>;
}

function FeedDialogs({
  commentProduct,
  supplierProduct,
  reviewOrders,
  session,
  setNotice,
  onCloseComment,
  onCloseSupplier,
}: {
  commentProduct: FeedProduct | null;
  supplierProduct: FeedProduct | null;
  reviewOrders: ReviewOrder[];
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
    const order = eligibleOrder(reviewOrders, commentProduct);
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
          source_entity_id: supplierProduct.sourceEntityId,
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
    {commentProduct && <Modal title='Comentar compra' onClose={onCloseComment}>
      <p>{commentProduct.title}</p>
      <label>Nota
        <input type='number' min='1' max='5' value={rating} onChange={event => setRating(Number(event.target.value))} />
      </label>
      <label>Comentário
        <textarea value={comment} onChange={event => setComment(event.target.value)} maxLength={1000} />
      </label>
      <button className='primary' type='button' onClick={() => { void submitComment(); }}>
        Publicar comentário
      </button>
    </Modal>}

    {supplierProduct && <Modal title='Falar com o fornecedor' onClose={onCloseSupplier}>
      <p>{supplierProduct.provider} · {supplierProduct.title}</p>
      <p className='supplier-privacy-note'>
        A conversa permanece dentro do Valley. Dados externos de contato não são exibidos.
      </p>
      <label>Mensagem
        <textarea
          value={message}
          onChange={event => setMessage(event.target.value)}
          minLength={5}
          maxLength={1000}
          placeholder='Digite sua dúvida sobre o produto'
        />
      </label>
      <button
        className='primary'
        type='button'
        disabled={message.trim().length < 5}
        onClick={() => { void submitSupplierMessage(); }}
      >Enviar mensagem</button>
    </Modal>}
  </>;
}

function useFeedActions(
  session: ViewProps['session'],
  setNotice: ViewProps['setNotice'],
  reviewOrders: ReviewOrder[],
  reloadReviewOrders: () => Promise<void>,
) {
  const [commentProduct, setCommentProduct] = useState<FeedProduct | null>(null);
  const [supplierProduct, setSupplierProduct] = useState<FeedProduct | null>(null);

  const favorite = async (product: FeedProduct) => {
    try {
      if (product.sourceModule === 'marketplace' && isUuid(product.sourceEntityId)) {
        await request(
          `/marketplace/valley/favorites/${product.sourceEntityId}`,
          'PUT',
          undefined,
          session.accessToken,
        );
      } else {
        await request('/marketplace/resources/carts', 'POST', {
          user_id: session.userId,
          status: 'active',
          payload: {
            cart_type: 'favorites',
            source_module: product.sourceModule,
            items: [{
              offer_id: product.offerId,
              source_entity_id: product.sourceEntityId,
              title: product.title,
            }],
          },
        }, session.accessToken);
      }
      setNotice('Produto adicionado aos favoritos.');
    } catch (error) {
      setNotice(errorMessage(error));
    }
  };

  const addToCart = async (product: FeedProduct) => {
    try {
      if (product.sourceModule === 'marketplace' && isUuid(product.sourceEntityId)) {
        await request(
          `/marketplace/valley/cart/items/${product.sourceEntityId}`,
          'PUT',
          { quantity: 1 },
          session.accessToken,
        );
      } else {
        await request('/marketplace/resources/carts', 'POST', {
          user_id: session.userId,
          status: 'active',
          payload: {
            cart_type: 'cart',
            items: [{
              offer_id: product.offerId,
              source_entity_id: product.sourceEntityId,
              source_module: product.sourceModule,
              title: product.title,
              quantity: 1,
            }],
          },
        }, session.accessToken);
      }
      setNotice('Produto adicionado ao carrinho.');
    } catch (error) {
      setNotice(errorMessage(error));
    }
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
      await reloadReviewOrders();
    } catch (error) {
      setNotice(errorMessage(error));
    }
  };

  return {
    commentProduct,
    supplierProduct,
    canComment: (product: FeedProduct) => Boolean(eligibleOrder(reviewOrders, product)),
    favorite,
    addToCart,
    buy,
    openComment: setCommentProduct,
    openSupplier: setSupplierProduct,
    closeComment: () => setCommentProduct(null),
    closeSupplier: () => setSupplierProduct(null),
  };
}

export function MarketplaceView({
  session,
  setNotice,
  hint,
  avatarDataUrl,
  onHome,
  onBack,
  onProfile,
}: ViewProps & { hint?: JourneyHint } & FeedNavigationProps) {
  const [products, setProducts] = useState<FeedProduct[]>([]);
  const [reviewOrders, setReviewOrders] = useState<ReviewOrder[]>([]);
  const [context, setContext] = useState<ShoppingContext>(EMPTY_CONTEXT);
  const [deviceCoordinates, setDeviceCoordinates] = useState<Coordinates | null | undefined>(undefined);
  const [query, setQuery] = useState(hint?.query ?? '');
  const [appliedQuery, setAppliedQuery] = useState(hint?.query ?? '');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);

  const reloadReviewOrders = useCallback(async () => {
    setReviewOrders(await loadReviewEligibility(session));
  }, [session]);

  useEffect(() => {
    void currentLocation().then(setDeviceCoordinates);
    void loadShoppingContext(session).then(setContext);
    void reloadReviewOrders();
  }, [reloadReviewOrders, session]);

  const coordinates = deviceCoordinates ?? context.fallbackCoordinates;

  const load = useCallback(async (append = false, offset = 0) => {
    if (!context.ready || deviceCoordinates === undefined) return;
    if (!coordinates) {
      setProducts([]);
      setTotal(0);
      setError(
        'Ative a localização ou cadastre um endereço de entrega/residencial '
        + 'com coordenadas para ver ofertas em até 10 km.',
      );
      setLoading(false);
      return;
    }

    if (append) setLoadingMore(true);
    else setLoading(true);
    setError('');
    const params = new URLSearchParams({
      latitude: String(coordinates.lat),
      longitude: String(coordinates.lng),
      radius_km: '10',
      offset: String(offset),
      limit: '30',
      sort: 'relevance',
      in_stock_only: 'true',
    });
    if (appliedQuery.trim()) params.set('q', appliedQuery.trim());
    if (category) params.set('category', category);

    try {
      const data = await request<MarketplaceCatalogResponse>(
        `/marketplace/valley/marketplace/catalog?${params}`,
        'GET',
        undefined,
        session.accessToken,
      );
      const nextProducts = (data.items ?? [])
        .map(normalizeMarketplaceItem)
        .filter(product => product.distanceKm != null && product.distanceKm <= 10)
        .sort((left, right) => {
          const interestDifference = interestScore(right, context.interests)
            - interestScore(left, context.interests);
          if (interestDifference) return interestDifference;
          return (left.distanceKm ?? 10) - (right.distanceKm ?? 10);
        });
      setProducts(current => append ? [...current, ...nextProducts] : nextProducts);
      setTotal(data.total ?? nextProducts.length);
    } catch (loadError) {
      setError(errorMessage(loadError));
      if (!append) setProducts([]);
    } finally {
      if (append) setLoadingMore(false);
      else setLoading(false);
    }
  }, [
    appliedQuery,
    category,
    context.interests,
    context.ready,
    coordinates,
    deviceCoordinates,
    session.accessToken,
  ]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void load(false, 0); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const actions = useFeedActions(session, setNotice, reviewOrders, reloadReviewOrders);
  const mode = hint?.mode;
  if (mode === 'sell' || mode === 'repair-request') {
    return <SellerComposer session={session} setNotice={setNotice} mode={mode} onDone={onHome} />;
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
      hasMore={products.length < total}
      loadingMore={loadingMore}
      canComment={actions.canComment}
      onHome={onHome}
      onBack={onBack}
      onProfile={onProfile}
      onQueryChange={setQuery}
      onSearch={() => setAppliedQuery(query.trim())}
      onCategoryChange={setCategory}
      onFavorite={product => { void actions.favorite(product); }}
      onComment={actions.openComment}
      onAddToCart={product => { void actions.addToCart(product); }}
      onBuy={product => { void actions.buy(product); }}
      onSupplier={actions.openSupplier}
      onLoadMore={() => { void load(true, products.length); }}
    />
    <FeedDialogs
      commentProduct={actions.commentProduct}
      supplierProduct={actions.supplierProduct}
      reviewOrders={reviewOrders}
      session={session}
      setNotice={setNotice}
      onCloseComment={actions.closeComment}
      onCloseSupplier={actions.closeSupplier}
    />
  </>;
}

export function StockView({
  session,
  setNotice,
  hint,
  avatarDataUrl,
  onHome,
  onBack,
  onProfile,
}: ViewProps & { hint?: JourneyHint } & FeedNavigationProps) {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [fallbackItems, setFallbackItems] = useState<ApiItem[]>([]);
  const [reviewOrders, setReviewOrders] = useState<ReviewOrder[]>([]);
  const [context, setContext] = useState<ShoppingContext>(EMPTY_CONTEXT);
  const [query, setQuery] = useState(hint?.query ?? '');
  const [appliedQuery, setAppliedQuery] = useState(hint?.query ?? '');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const reloadReviewOrders = useCallback(async () => {
    setReviewOrders(await loadReviewEligibility(session));
  }, [session]);

  useEffect(() => {
    void loadShoppingContext(session).then(setContext);
    void reloadReviewOrders();
  }, [reloadReviewOrders, session]);

  const load = useCallback(async () => {
    if (!context.ready) return;
    setLoading(true);
    setError('');
    const params = new URLSearchParams({
      offset: '0',
      limit: '100',
      ranking: 'interest_affordability_best_sellers',
    });
    if (appliedQuery.trim()) params.set('q', appliedQuery.trim());
    if (category) params.set('category', category);
    if (context.interests.length) params.set('interests', context.interests.join(','));
    if (context.affordabilityConsent && context.safeMonthlyLimit != null) {
      params.set('safe_monthly_commitment_max', context.safeMonthlyLimit.toFixed(2));
    }

    try {
      const [catalogResult, directResult] = await Promise.allSettled([
        request<CatalogResponse>(`/gateway/catalog/offers?${params}`),
        request<ApiItem[]>(
          '/stock/resources/catalog_products',
          'GET',
          undefined,
          session.accessToken,
        ),
      ]);
      setOffers(
        catalogResult.status === 'fulfilled'
          ? catalogResult.value.data ?? []
          : [],
      );
      setFallbackItems(
        directResult.status === 'fulfilled'
          ? directResult.value ?? []
          : [],
      );
      if (catalogResult.status === 'rejected' && directResult.status === 'rejected') {
        throw catalogResult.reason;
      }
    } catch (loadError) {
      setError(errorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }, [appliedQuery, category, context, session.accessToken]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void load(); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const products = useMemo(() => {
    const catalog = offers
      .filter(offer => offer.source_module === 'stock')
      .map(normalizeOffer);
    const base = catalog.length ? catalog : fallbackItems.map(normalizeStockItem);
    const normalizedQuery = appliedQuery.toLocaleLowerCase('pt-BR');
    return base
      .filter(product => !normalizedQuery || (
        `${product.title} ${product.description} ${product.category}`
          .toLocaleLowerCase('pt-BR')
          .includes(normalizedQuery)
      ))
      .filter(product => !category || product.category === category)
      .filter(product => {
        if (!context.affordabilityConsent || context.safeMonthlyLimit == null) return true;
        const commitment = monthlyCommitment(product);
        return commitment === 0 || commitment <= context.safeMonthlyLimit;
      })
      .sort((left, right) => {
        const interestDifference = interestScore(right, context.interests)
          - interestScore(left, context.interests);
        if (interestDifference) return interestDifference;
        const rightSales = Number(
          (fallbackItems.find(item => item.id === right.sourceEntityId)?.payload ?? {}).sales_count ?? 0,
        );
        const leftSales = Number(
          (fallbackItems.find(item => item.id === left.sourceEntityId)?.payload ?? {}).sales_count ?? 0,
        );
        return rightSales - leftSales;
      });
  }, [appliedQuery, category, context, fallbackItems, offers]);

  const actions = useFeedActions(session, setNotice, reviewOrders, reloadReviewOrders);

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
      onFavorite={product => { void actions.favorite(product); }}
      onComment={actions.openComment}
      onAddToCart={product => { void actions.addToCart(product); }}
      onBuy={product => { void actions.buy(product); }}
      onSupplier={actions.openSupplier}
    />
    <FeedDialogs
      commentProduct={actions.commentProduct}
      supplierProduct={actions.supplierProduct}
      reviewOrders={reviewOrders}
      session={session}
      setNotice={setNotice}
      onCloseComment={actions.closeComment}
      onCloseSupplier={actions.closeSupplier}
    />
    {!loading
      && products.length === 0
      && context.affordabilityConsent
      && context.safeMonthlyLimit != null
      && <StateCard text={
        'Nenhum produto foi encontrado dentro dos interesses e do limite '
        + 'mensal autorizado. Ajuste seus dados ou use a busca.'
      } />}
  </>;
}

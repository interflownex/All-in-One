import {
  type CSSProperties,
  type FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { ValleyProfileAvatar } from './ValleyProfileAvatar';
import { formatMoney } from '../lib/api';

export type FeedMedia = {
  url: string;
  type: 'image' | 'video';
  posterUrl?: string;
  alt?: string;
};

export type FeedFact = {
  label: string;
  value: string;
};

export type FeedSupplierProfile = {
  name: string;
  verified?: boolean;
  region?: string;
  rating?: number | null;
  reviewCount?: number | null;
  sourceLabel?: string;
};

export type FeedProduct = {
  id: string;
  offerId: string;
  sourceEntityId?: string;
  sourceModule: string;
  title: string;
  description: string;
  fullDescription?: string;
  category: string;
  provider: string;
  region: string;
  distanceKm?: number | null;
  priceAmount?: string | null;
  imageUrl?: string;
  videoUrl?: string;
  media?: FeedMedia[];
  facts?: FeedFact[];
  supplier?: FeedSupplierProfile;
  accentColor?: string;
};

type ProductFeedProps = {
  title: string;
  products: FeedProduct[];
  categories: string[];
  activeCategory: string;
  query: string;
  avatarDataUrl: string;
  loading?: boolean;
  error?: string;
  hasMore?: boolean;
  loadingMore?: boolean;
  canComment: (product: FeedProduct) => boolean;
  onHome: () => void;
  onBack: () => void;
  onProfile: () => void;
  onQueryChange: (value: string) => void;
  onSearch: () => void;
  onCategoryChange: (value: string) => void;
  onFavorite: (product: FeedProduct) => void;
  onComment: (product: FeedProduct) => void;
  onAddToCart: (product: FeedProduct) => void;
  onBuy: (product: FeedProduct) => void;
  onSupplier: (product: FeedProduct) => void;
  onLoadMore?: () => void;
};

type IconName =
  | 'back'
  | 'close'
  | 'search'
  | 'heart'
  | 'share'
  | 'comment'
  | 'cart'
  | 'buy'
  | 'chat';

const paths: Record<IconName, string> = {
  back: 'M15 18l-6-6 6-6M9 12h10',
  close: 'M6 6l12 12M18 6 6 18',
  search: 'm21 21-4.35-4.35M19 11a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z',
  heart: 'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78Z',
  share: 'M18 8a3 3 0 1 0-2.83-4M6 14a3 3 0 1 0 0-4M18 20a3 3 0 1 0 0-4M8.59 11.51l6.83-3.02M8.59 12.49l6.83 3.02',
  comment: 'M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v8Z',
  cart: 'M3 4h2l2.2 10.2a2 2 0 0 0 2 1.6h7.9a2 2 0 0 0 1.95-1.55L21 7H7M12 9v5M9.5 11.5h5M10 20h.01M18 20h.01',
  buy: 'M6 8V6a6 6 0 0 1 12 0v2M4 8h16l-1 13H5L4 8ZM9 12h6',
  chat: 'M20 15a4 4 0 0 1-4 4H9l-5 3v-3.5A8 8 0 1 1 20 15ZM8 11h.01M12 11h.01M16 11h.01',
};

function Icon({ name }: { name: IconName }) {
  return <svg viewBox='0 0 24 24' aria-hidden='true'><path d={paths[name]} /></svg>;
}

function colorFor(product: FeedProduct) {
  if (product.accentColor && /^#[0-9a-f]{6}$/i.test(product.accentColor)) {
    return product.accentColor;
  }
  const palette = ['#5d2ce6', '#006d77', '#9c2f52', '#9a6700', '#185fa5', '#2d6a4f', '#7b2cbf'];
  const score = [...product.title].reduce(
    (total, character) => total + character.charCodeAt(0),
    0,
  );
  return palette[score % palette.length];
}

function mediaFor(product: FeedProduct): FeedMedia[] {
  const candidates: FeedMedia[] = [];
  if (product.videoUrl) {
    candidates.push({
      url: product.videoUrl,
      type: 'video',
      posterUrl: product.imageUrl,
      alt: product.title,
    });
  }
  for (const item of product.media ?? []) {
    if (item.url) candidates.push(item);
  }
  if (product.imageUrl) {
    candidates.push({ url: product.imageUrl, type: 'image', alt: product.title });
  }

  const seen = new Set<string>();
  return candidates.filter(item => {
    const key = item.url.trim();
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

async function shareProduct(product: FeedProduct) {
  const shareText = `${product.title} · ${product.provider}`;
  const shareData = {
    title: product.title,
    text: shareText,
    url: `${window.location.href.split('#')[0]}#offer=${encodeURIComponent(product.offerId)}`,
  };
  try {
    if (navigator.share) {
      await navigator.share(shareData);
      return;
    }
    await navigator.clipboard.writeText(`${shareText}\n${shareData.url}`);
  } catch (error) {
    if ((error as DOMException)?.name !== 'AbortError') throw error;
  }
}

function ActionButton({
  icon,
  label,
  onClick,
  disabled = false,
}: {
  icon: IconName;
  label: string;
  onClick: () => void;
  disabled?: boolean;
}) {
  return <button
    className='feed-action-button'
    type='button'
    aria-label={label}
    title={label}
    onClick={onClick}
    disabled={disabled}
  ><Icon name={icon} /></button>;
}

function ProductMediaCarousel({
  product,
  onOpenDetails,
  detailMode = false,
}: {
  product: FeedProduct;
  onOpenDetails?: () => void;
  detailMode?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const trackRef = useRef<HTMLDivElement | null>(null);
  const videoRefs = useRef<Array<HTMLVideoElement | null>>([]);
  const pointerMoved = useRef(false);
  const pointerStart = useRef({ x: 0, y: 0 });
  const [activeIndex, setActiveIndex] = useState(0);
  const [visible, setVisible] = useState(detailMode);
  const media = useMemo(() => mediaFor(product), [product]);

  useEffect(() => {
    if (detailMode) {
      setVisible(true);
      return;
    }
    const container = containerRef.current;
    if (!container || !('IntersectionObserver' in window)) {
      setVisible(true);
      return;
    }
    const observer = new IntersectionObserver(entries => {
      setVisible(entries.some(
        entry => entry.isIntersecting && entry.intersectionRatio >= 0.65,
      ));
    }, { threshold: [0.25, 0.65, 0.9] });
    observer.observe(container);
    return () => observer.disconnect();
  }, [detailMode]);

  useEffect(() => {
    videoRefs.current.forEach((video, index) => {
      if (!video) return;
      if (visible && index === activeIndex) {
        void video.play().catch(() => undefined);
      } else {
        video.pause();
      }
    });
  }, [activeIndex, visible]);

  const syncIndex = () => {
    const track = trackRef.current;
    if (!track || track.clientWidth <= 0) return;
    const nextIndex = Math.max(
      0,
      Math.min(media.length - 1, Math.round(track.scrollLeft / track.clientWidth)),
    );
    setActiveIndex(nextIndex);
  };

  const openDetails = () => {
    if (!pointerMoved.current) onOpenDetails?.();
  };

  return <div
    className={detailMode ? 'feed-media-layer detail-media-layer' : 'feed-media-layer'}
    ref={containerRef}
  >
    {media.length > 0
      ? <>
          <div
            className='feed-media-carousel'
            ref={trackRef}
            onScroll={syncIndex}
            onPointerDown={event => {
              pointerMoved.current = false;
              pointerStart.current = { x: event.clientX, y: event.clientY };
            }}
            onPointerMove={event => {
              const horizontal = Math.abs(event.clientX - pointerStart.current.x);
              const vertical = Math.abs(event.clientY - pointerStart.current.y);
              if (horizontal > 8 || vertical > 8) pointerMoved.current = true;
            }}
          >
            {media.map((item, index) => <div
              className='feed-media-slide'
              key={`${item.type}-${item.url}`}
              role={onOpenDetails ? 'button' : undefined}
              tabIndex={onOpenDetails ? 0 : undefined}
              aria-label={onOpenDetails ? `Abrir detalhes de ${product.title}` : undefined}
              onClick={openDetails}
              onKeyDown={event => {
                if (onOpenDetails && (event.key === 'Enter' || event.key === ' ')) {
                  event.preventDefault();
                  onOpenDetails();
                }
              }}
            >
              {item.type === 'video'
                ? <video
                    ref={element => { videoRefs.current[index] = element; }}
                    src={item.url}
                    poster={item.posterUrl ?? product.imageUrl}
                    loop
                    muted
                    playsInline
                    preload='metadata'
                  />
                : <img
                    src={item.url}
                    alt={item.alt ?? product.title}
                    loading={detailMode ? 'eager' : 'lazy'}
                  />}
            </div>)}
          </div>
          {media.length > 1 && <div
            className='feed-media-pagination'
            aria-label={`Mídia ${activeIndex + 1} de ${media.length}`}
          >
            {media.map((item, index) => <span
              key={`${item.url}-dot`}
              className={index === activeIndex ? 'active' : ''}
            />)}
          </div>}
        </>
      : <div
          className='feed-media-placeholder'
          role={onOpenDetails ? 'button' : undefined}
          tabIndex={onOpenDetails ? 0 : undefined}
          onClick={openDetails}
          onKeyDown={event => {
            if (onOpenDetails && (event.key === 'Enter' || event.key === ' ')) {
              onOpenDetails();
            }
          }}
        />}
  </div>;
}

function ProductDetailDialog({
  product,
  onClose,
  onAddToCart,
  onBuy,
  onSupplier,
}: {
  product: FeedProduct;
  onClose: () => void;
  onAddToCart: (product: FeedProduct) => void;
  onBuy: (product: FeedProduct) => void;
  onSupplier: (product: FeedProduct) => void;
}) {
  const supplier = product.supplier ?? {
    name: product.provider,
    region: product.region,
    sourceLabel: product.sourceModule === 'stock' ? 'Estoque Valley' : 'Marketplace Valley',
  };

  return <div
    className='product-detail-backdrop'
    role='presentation'
    onClick={event => {
      if (event.currentTarget === event.target) onClose();
    }}
  >
    <section
      className='product-detail-sheet'
      role='dialog'
      aria-modal='true'
      aria-label={`Detalhes de ${product.title}`}
    >
      <header className='product-detail-header'>
        <button type='button' onClick={onClose} aria-label='Fechar detalhes'>
          <Icon name='close' />
        </button>
        <h2>{product.title}</h2>
        <strong>{formatMoney(product.priceAmount)}</strong>
      </header>

      <div className='product-detail-media'>
        <ProductMediaCarousel product={product} detailMode />
      </div>

      <div className='product-detail-content'>
        <section>
          <h3>Descrição completa</h3>
          <p>{
            product.fullDescription
            || product.description
            || 'O anunciante ainda não informou uma descrição detalhada.'
          }</p>
        </section>

        {Boolean(product.facts?.length) && <section>
          <h3>Características e informações</h3>
          <dl className='product-detail-facts'>
            {product.facts?.map(fact => <div key={`${fact.label}-${fact.value}`}>
              <dt>{fact.label}</dt>
              <dd>{fact.value}</dd>
            </div>)}
          </dl>
        </section>}

        <section className='product-detail-supplier'>
          <h3>Fornecedor</h3>
          <div className='supplier-public-card'>
            <div>
              <strong>{supplier.name}</strong>
              <span>{supplier.verified ? 'Fornecedor verificado' : 'Fornecedor cadastrado'}</span>
            </div>
            {supplier.region && <span>{supplier.region}</span>}
            {supplier.rating != null && <span>
              Avaliação {supplier.rating.toFixed(1)}
              {supplier.reviewCount != null ? ` · ${supplier.reviewCount} avaliações` : ''}
            </span>}
            {supplier.sourceLabel && <small>{supplier.sourceLabel}</small>}
          </div>
          <p className='supplier-privacy-note'>
            Telefone, e-mail, redes sociais e outros dados externos de contato não são exibidos.
            A comunicação com o fornecedor acontece somente dentro do aplicativo Valley.
          </p>
        </section>
      </div>

      <footer className='product-detail-actions'>
        <button className='secondary' type='button' onClick={() => onSupplier(product)}>
          Falar no Valley
        </button>
        <button className='secondary' type='button' onClick={() => onAddToCart(product)}>
          Adicionar ao carrinho
        </button>
        <button className='primary' type='button' onClick={() => onBuy(product)}>
          Comprar
        </button>
      </footer>
    </section>
  </div>;
}

export function ProductFeed({
  title,
  products,
  categories,
  activeCategory,
  query,
  avatarDataUrl,
  loading,
  error,
  hasMore,
  loadingMore,
  canComment,
  onHome,
  onBack,
  onProfile,
  onQueryChange,
  onSearch,
  onCategoryChange,
  onFavorite,
  onComment,
  onAddToCart,
  onBuy,
  onSupplier,
  onLoadMore,
}: ProductFeedProps) {
  const [searchOpen, setSearchOpen] = useState(false);
  const [detailProduct, setDetailProduct] = useState<FeedProduct | null>(null);
  const activeCategories = useMemo(
    () => categories.filter(Boolean),
    [categories],
  );

  const submitSearch = (event: FormEvent) => {
    event.preventDefault();
    onSearch();
  };

  return <section className='immersive-product-feed' aria-label={title}>
    <header className='feed-toolbar'>
      <div className='feed-toolbar-left'>
        <button className='feed-logo-button' type='button' onClick={onHome} aria-label='Voltar para a Home Valley' title='Home'>
          <span className='feed-home-glow' />
          <img src='/assets/brand/valley-logo-official.png' alt='' aria-hidden='true' />
        </button>
        <button className='feed-toolbar-button' type='button' onClick={onBack} aria-label='Voltar para a tela anterior' title='Voltar'><Icon name='back' /></button>
        <button className='feed-toolbar-button' type='button' onClick={() => setSearchOpen(value => !value)} aria-label='Pesquisar produtos' title='Pesquisar'><Icon name='search' /></button>
      </div>
      <button className='feed-profile-button' type='button' onClick={onProfile} aria-label='Abrir meu perfil' title='Meu perfil'>
        <ValleyProfileAvatar src={avatarDataUrl} size='small' />
      </button>
    </header>

    {searchOpen && <form className='feed-search-drawer' onSubmit={submitSearch}>
      <label>Pesquisar item<input autoFocus type='search' value={query} onChange={event => onQueryChange(event.target.value)} placeholder='Digite produto, marca ou empresa' /></label>
      <button className='primary' type='submit'>Pesquisar</button>
      {activeCategories.length > 1 && <div className='feed-category-list' aria-label='Categorias disponíveis'>
        <button type='button' className={!activeCategory ? 'active' : ''} onClick={() => onCategoryChange('')}>Todas</button>
        {activeCategories.map(category => <button type='button' key={category} className={activeCategory === category ? 'active' : ''} onClick={() => onCategoryChange(category)}>{category}</button>)}
      </div>}
    </form>}

    <div className='vertical-product-feed'>
      {loading && <div className='feed-state'>Carregando anúncios...</div>}
      {error && <div className='feed-state error'>{error}</div>}
      {!loading && !error && products.length === 0 && <div className='feed-state'>Nenhum anúncio disponível para estes critérios.</div>}

      {products.map(product => {
        const style = { '--feed-accent': colorFor(product) } as CSSProperties;
        const reviewEnabled = canComment(product);
        return <article className='product-feed-item' key={product.id} style={style}>
          <ProductMediaCarousel
            product={product}
            onOpenDetails={() => setDetailProduct(product)}
          />
          <div className='feed-media-shade' />

          <div className='feed-title-frame' title={product.title}><h2>{product.title}</h2></div>

          <aside className='feed-action-rail' aria-label={`Ações para ${product.title}`}>
            <ActionButton icon='heart' label='Favoritar' onClick={() => onFavorite(product)} />
            <ActionButton icon='share' label='Compartilhar' onClick={() => void shareProduct(product)} />
            <ActionButton
              icon='comment'
              label={reviewEnabled ? 'Comentar compra' : 'Comentário disponível após compra concluída'}
              disabled={!reviewEnabled}
              onClick={() => onComment(product)}
            />
            <ActionButton icon='cart' label='Adicionar ao carrinho' onClick={() => onAddToCart(product)} />
            <ActionButton icon='buy' label='Comprar agora' onClick={() => onBuy(product)} />
            <ActionButton icon='chat' label='Falar com o fornecedor' onClick={() => onSupplier(product)} />
          </aside>

          <div className='feed-description-frame'>
            <p>{product.description || 'O anunciante ainda não informou uma descrição detalhada.'}</p>
            <div className='feed-product-meta'>
              <span>{product.provider}</span>
              <span>{product.region}{product.distanceKm != null ? ` · ${product.distanceKm.toFixed(1)} km` : ''}</span>
              <strong>{formatMoney(product.priceAmount)}</strong>
            </div>
          </div>
        </article>;
      })}

      {hasMore && onLoadMore && <div className='feed-load-more'>
        <button className='secondary' type='button' disabled={loadingMore} onClick={onLoadMore}>
          {loadingMore ? 'Carregando...' : 'Carregar mais ofertas'}
        </button>
      </div>}
    </div>

    {detailProduct && <ProductDetailDialog
      product={detailProduct}
      onClose={() => setDetailProduct(null)}
      onAddToCart={onAddToCart}
      onBuy={onBuy}
      onSupplier={product => {
        setDetailProduct(null);
        onSupplier(product);
      }}
    />}
  </section>;
}

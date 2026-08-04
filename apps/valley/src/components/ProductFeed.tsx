import { type CSSProperties, type FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { ValleyProfileAvatar } from './ValleyProfileAvatar';
import { formatMoney } from '../lib/api';

export type FeedProduct = {
  id: string;
  offerId: string;
  sourceEntityId?: string;
  sourceModule: string;
  title: string;
  description: string;
  category: string;
  provider: string;
  region: string;
  distanceKm?: number | null;
  priceAmount?: string | null;
  imageUrl?: string;
  videoUrl?: string;
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

type IconName = 'back' | 'search' | 'heart' | 'share' | 'comment' | 'cart' | 'buy' | 'chat';

const paths: Record<IconName, string> = {
  back: 'M15 18l-6-6 6-6M9 12h10',
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
  if (product.accentColor && /^#[0-9a-f]{6}$/i.test(product.accentColor)) return product.accentColor;
  const palette = ['#5d2ce6', '#006d77', '#9c2f52', '#9a6700', '#185fa5', '#2d6a4f', '#7b2cbf'];
  const score = [...product.title].reduce((total, character) => total + character.charCodeAt(0), 0);
  return palette[score % palette.length];
}

async function shareProduct(product: FeedProduct) {
  const shareText = `${product.title} · ${product.provider}`;
  const shareData = { title: product.title, text: shareText, url: `${window.location.href.split('#')[0]}#offer=${encodeURIComponent(product.offerId)}` };
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

function ActionButton({ icon, label, onClick, disabled = false }: { icon: IconName; label: string; onClick: () => void; disabled?: boolean }) {
  return <button className='feed-action-button' type='button' aria-label={label} title={label} onClick={onClick} disabled={disabled}><Icon name={icon} /></button>;
}

function ProductMedia({ product }: { product: FeedProduct }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    const video = videoRef.current;
    if (!container || !video || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver(entries => {
      const active = entries.some(entry => entry.isIntersecting && entry.intersectionRatio >= 0.65);
      if (active) void video.play().catch(() => undefined);
      else video.pause();
    }, { threshold: [0.25, 0.65, 0.9] });
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  return <div className='feed-media-layer' ref={containerRef}>
    {product.videoUrl
      ? <video ref={videoRef} src={product.videoUrl} poster={product.imageUrl} loop muted playsInline preload='metadata' />
      : product.imageUrl
        ? <img src={product.imageUrl} alt='' loading='lazy' />
        : <div className='feed-media-placeholder' aria-hidden='true' />}
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
  const activeCategories = useMemo(() => categories.filter(Boolean), [categories]);

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
          <ProductMedia product={product} />
          <div className='feed-media-shade' />

          <div className='feed-title-frame' title={product.title}><h2>{product.title}</h2></div>

          <aside className='feed-action-rail' aria-label={`Ações para ${product.title}`}>
            <ActionButton icon='heart' label='Favoritar' onClick={() => onFavorite(product)} />
            <ActionButton icon='share' label='Compartilhar' onClick={() => void shareProduct(product)} />
            <ActionButton icon='comment' label={reviewEnabled ? 'Comentar compra' : 'Comentário disponível após compra concluída'} disabled={!reviewEnabled} onClick={() => onComment(product)} />
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

      {hasMore && onLoadMore && <div className='feed-load-more'><button className='secondary' type='button' disabled={loadingMore} onClick={onLoadMore}>{loadingMore ? 'Carregando...' : 'Carregar mais'}</button></div>}
    </div>
  </section>;
}

import { type CSSProperties, type ReactNode, useEffect, useMemo, useRef, useState } from 'react';

export type ReelProduct = {
  id: string;
  offerId: string;
  sourceModule: 'marketplace' | 'stock';
  sourceEntityId?: string;
  title: string;
  description: string;
  priceLabel: string;
  providerLabel: string;
  regionLabel?: string;
  distanceKm?: number | null;
  category?: string;
  imageUrl?: string;
  videoUrl?: string;
  accentColor?: string;
  commentOrderId?: string;
  canBuy?: boolean;
};

type ProductReelFeedProps = {
  products: ReelProduct[];
  categories: string[];
  query: string;
  selectedCategory: string;
  profilePhotoUrl?: string;
  emptyText: string;
  loading?: boolean;
  onHome: () => void;
  onBack: () => void;
  onProfile: () => void;
  onSearch: (query: string, category: string) => void;
  onFavorite: (product: ReelProduct) => void | Promise<void>;
  onShare: (product: ReelProduct) => void | Promise<void>;
  onComment: (product: ReelProduct) => void;
  onAddToCart: (product: ReelProduct) => void | Promise<void>;
  onBuy: (product: ReelProduct) => void | Promise<void>;
  onSupplier: (product: ReelProduct) => void;
};

export function ProductReelFeed({
  products,
  categories,
  query,
  selectedCategory,
  profilePhotoUrl,
  emptyText,
  loading = false,
  onHome,
  onBack,
  onProfile,
  onSearch,
  onFavorite,
  onShare,
  onComment,
  onAddToCart,
  onBuy,
  onSupplier,
}: ProductReelFeedProps) {
  const [searchOpen, setSearchOpen] = useState(false);
  const [draftQuery, setDraftQuery] = useState(query);
  const [draftCategory, setDraftCategory] = useState(selectedCategory);

  useEffect(() => setDraftQuery(query), [query]);
  useEffect(() => setDraftCategory(selectedCategory), [selectedCategory]);

  const activeCategories = useMemo(() => categories.filter(Boolean), [categories]);
  const submitSearch = () => {
    onSearch(draftQuery.trim(), activeCategories.length > 1 ? draftCategory : '');
    setSearchOpen(false);
  };

  return <section className='product-reel-shell' aria-label='Feed vertical de produtos'>
    <div className='product-reel-nav'>
      <div className='product-reel-nav-left'>
        <button className='reel-logo-button' type='button' onClick={onHome} aria-label='Ir para a Home' title='Home'>
          <img src='/assets/brand/valley-logo-official.png' alt='' aria-hidden='true' />
        </button>
        <IconButton label='Voltar' onClick={onBack}><BackIcon /></IconButton>
        <IconButton label='Pesquisar' onClick={() => setSearchOpen(true)}><SearchIcon /></IconButton>
      </div>
      <button className='reel-profile-button' type='button' onClick={onProfile} aria-label='Abrir meu perfil' title='Meu perfil'>
        {profilePhotoUrl ? <img src={profilePhotoUrl} alt='' /> : <span aria-hidden='true'>V</span>}
      </button>
    </div>

    {searchOpen && <div className='reel-search-backdrop' role='presentation' onClick={() => setSearchOpen(false)}>
      <section className='reel-search-panel' role='dialog' aria-modal='true' aria-label='Pesquisar produtos' onClick={event => event.stopPropagation()}>
        <header><h2>Pesquisar</h2><IconButton label='Fechar pesquisa' onClick={() => setSearchOpen(false)}><CloseIcon /></IconButton></header>
        <label>Produto, marca ou fornecedor<input type='search' value={draftQuery} onChange={event => setDraftQuery(event.target.value)} placeholder='O que você procura?' autoFocus /></label>
        {activeCategories.length > 1 && <div className='reel-category-picker' aria-label='Categorias disponíveis'>
          <button type='button' className={!draftCategory ? 'active' : ''} onClick={() => setDraftCategory('')}>Tudo</button>
          {activeCategories.map(category => <button type='button' key={category} className={draftCategory === category ? 'active' : ''} onClick={() => setDraftCategory(category)}>{category}</button>)}
        </div>}
        <button className='primary' type='button' onClick={submitSearch}>Aplicar busca</button>
      </section>
    </div>}

    {loading && <div className='reel-state'><span className='reel-loader' />Carregando produtos...</div>}
    {!loading && !products.length && <div className='reel-state'>{emptyText}</div>}

    <div className='product-reel-list'>
      {products.map(product => <ProductReelCard
        key={product.id}
        product={product}
        onFavorite={onFavorite}
        onShare={onShare}
        onComment={onComment}
        onAddToCart={onAddToCart}
        onBuy={onBuy}
        onSupplier={onSupplier}
      />)}
    </div>
  </section>;
}

function ProductReelCard({
  product,
  onFavorite,
  onShare,
  onComment,
  onAddToCart,
  onBuy,
  onSupplier,
}: {
  product: ReelProduct;
  onFavorite: ProductReelFeedProps['onFavorite'];
  onShare: ProductReelFeedProps['onShare'];
  onComment: ProductReelFeedProps['onComment'];
  onAddToCart: ProductReelFeedProps['onAddToCart'];
  onBuy: ProductReelFeedProps['onBuy'];
  onSupplier: ProductReelFeedProps['onSupplier'];
}) {
  const accent = product.accentColor || accentFromId(product.id);
  const style = {
    '--reel-accent': accent,
    '--reel-panel': colorWithAlpha(accent, 0.72),
  } as CSSProperties;

  return <article className='product-reel-card' style={style}>
    <ProductMedia product={product} />
    <div className='reel-media-shade' />

    <div className='reel-title-frame' title={product.title}>
      <h2>{product.title}</h2>
    </div>

    <aside className='reel-action-rail' aria-label={`Ações para ${product.title}`}>
      <IconButton label='Favoritar' onClick={() => onFavorite(product)}><HeartIcon /></IconButton>
      <IconButton label='Compartilhar' onClick={() => onShare(product)}><ShareIcon /></IconButton>
      <IconButton
        label={product.commentOrderId ? 'Comentar' : 'Comentar disponível após a compra'}
        onClick={() => onComment(product)}
        disabled={!product.commentOrderId}
      ><CommentIcon /></IconButton>
      <IconButton label='Adicionar ao carrinho' onClick={() => onAddToCart(product)}><CartIcon /></IconButton>
      <IconButton label='Comprar' onClick={() => onBuy(product)} disabled={product.canBuy === false}><BuyIcon /></IconButton>
      <IconButton label='Falar com o fornecedor' onClick={() => onSupplier(product)}><SupplierIcon /></IconButton>
    </aside>

    <div className='reel-description-frame'>
      <p>{product.description || 'Descrição não informada pelo anunciante.'}</p>
      <div className='reel-product-meta'>
        <span>{product.providerLabel}</span>
        {product.regionLabel && <span>{product.regionLabel}</span>}
        {product.distanceKm != null && <span>{product.distanceKm.toFixed(1)} km</span>}
      </div>
      <strong>{product.priceLabel}</strong>
    </div>
  </article>;
}

function ProductMedia({ product }: { product: ReelProduct }) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const cardRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const node = cardRef.current;
    const video = videoRef.current;
    if (!node || !video || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver(entries => {
      const active = entries.some(entry => entry.isIntersecting && entry.intersectionRatio >= 0.65);
      if (active) void video.play().catch(() => undefined);
      else video.pause();
    }, { threshold: [0.25, 0.65, 0.9] });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return <div className='reel-media' ref={cardRef}>
    {product.videoUrl ? <video ref={videoRef} src={product.videoUrl} poster={product.imageUrl} muted loop playsInline preload='metadata' controls={false} /> : product.imageUrl ? <img src={product.imageUrl} alt='' loading='lazy' /> : <div className='reel-media-placeholder' aria-hidden='true'><span>VALLEY</span></div>}
  </div>;
}

function IconButton({ label, onClick, disabled = false, children }: { label: string; onClick: () => void; disabled?: boolean; children: ReactNode }) {
  return <button className='reel-icon-button' type='button' aria-label={label} title={label} onClick={onClick} disabled={disabled}>{children}</button>;
}

function accentFromId(id: string) {
  let hash = 0;
  for (const character of id) hash = (hash * 31 + character.charCodeAt(0)) >>> 0;
  return `hsl(${hash % 360} 74% 42%)`;
}

function colorWithAlpha(color: string, alpha: number) {
  if (color.startsWith('#') && /^#[0-9a-f]{6}$/i.test(color)) {
    const red = Number.parseInt(color.slice(1, 3), 16);
    const green = Number.parseInt(color.slice(3, 5), 16);
    const blue = Number.parseInt(color.slice(5, 7), 16);
    return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
  }
  return `color-mix(in srgb, ${color} ${Math.round(alpha * 100)}%, transparent)`;
}

function Svg({ children }: { children: ReactNode }) { return <svg viewBox='0 0 24 24' aria-hidden='true' focusable='false'>{children}</svg>; }
function BackIcon() { return <Svg><path d='M15 18l-6-6 6-6M9 12h11' /></Svg>; }
function SearchIcon() { return <Svg><circle cx='11' cy='11' r='7' /><path d='m20 20-4-4' /></Svg>; }
function CloseIcon() { return <Svg><path d='M6 6l12 12M18 6 6 18' /></Svg>; }
function HeartIcon() { return <Svg><path d='M20.8 4.6a5.4 5.4 0 0 0-7.6 0L12 5.8l-1.2-1.2a5.4 5.4 0 0 0-7.6 7.6L12 21l8.8-8.8a5.4 5.4 0 0 0 0-7.6Z' /></Svg>; }
function ShareIcon() { return <Svg><circle cx='18' cy='5' r='2.5' /><circle cx='6' cy='12' r='2.5' /><circle cx='18' cy='19' r='2.5' /><path d='m8.2 10.8 7.5-4.3M8.2 13.2l7.5 4.3' /></Svg>; }
function CommentIcon() { return <Svg><path d='M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z' /></Svg>; }
function CartIcon() { return <Svg><path d='M3 4h2l2.4 10.2a2 2 0 0 0 2 1.5h6.8a2 2 0 0 0 2-1.6L20 7H6' /><circle cx='10' cy='20' r='1.2' /><circle cx='17' cy='20' r='1.2' /></Svg>; }
function BuyIcon() { return <Svg><path d='M4 7h16v13H4zM8 7a4 4 0 0 1 8 0' /><path d='M9 12h6' /></Svg>; }
function SupplierIcon() { return <Svg><path d='M4 21v-8l8-5 8 5v8M9 21v-5h6v5M7 8V3h10v5' /></Svg>; }

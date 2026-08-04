import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
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
type IntentOption = { label: string; description: string; view: ViewKey; hint?: JourneyHint };
type ConsumerIntent = { key: string; label: string; description: string; symbol: string; options: IntentOption[] };

const intents: ConsumerIntent[] = [
  {
    key: 'comprar', label: 'Comprar', description: 'Produtos, ofertas e itens disponíveis perto de você.', symbol: '↓',
    options: [
      { label: 'Marketplace', description: 'Abrir o feed de produtos, categorias e novidades.', view: 'marketplace', hint: { intent: 'comprar', mode: 'feed' } },
      { label: 'Estoque', description: 'Abrir o feed de produtos de fornecedores e empresas.', view: 'stock', hint: { intent: 'comprar', mode: 'feed' } },
    ],
  },
  {
    key: 'vender', label: 'Vender', description: 'Crie um anúncio de venda de forma simples e guiada.', symbol: '↑',
    options: [{ label: 'Vender um item', description: 'Cadastrar item, fotos, preço e condições no Marketplace.', view: 'marketplace', hint: { intent: 'vender', mode: 'sell' } }],
  },
  {
    key: 'contratar', label: 'Contratar', description: 'Escolha o tipo de profissional ou atendimento necessário.', symbol: '+',
    options: [
      { label: 'Contratar para uma vaga', description: 'Publicar uma oportunidade e encontrar candidatos.', view: 'jobs', hint: { intent: 'contratar', mode: 'recruit' } },
      { label: 'Contratar apoio jurídico', description: 'Encontrar orientação, contratos e acompanhamento jurídico.', view: 'legal', hint: { intent: 'contratar', mode: 'hire' } },
      { label: 'Contratar atendimento de saúde', description: 'Buscar especialidade, profissional ou agendamento.', view: 'health', hint: { intent: 'contratar', mode: 'hire' } },
    ],
  },
  {
    key: 'alugar', label: 'Alugar', description: 'Encontre propriedades, imóveis e unidades disponíveis.', symbol: '◇',
    options: [{ label: 'Buscar imóvel ou propriedade', description: 'Abrir o catálogo de propriedades e locações.', view: 'property', hint: { intent: 'alugar', mode: 'rent' } }],
  },
  {
    key: 'consertar', label: 'Consertar', description: 'Anuncie um item que precisa de um profissional especializado.', symbol: '⌁',
    options: [{ label: 'Publicar pedido de conserto', description: 'Descrever o item, o defeito e a região no Marketplace.', view: 'marketplace', hint: { intent: 'consertar', mode: 'repair-request' } }],
  },
  {
    key: 'pagar', label: 'Pagar', description: 'Acesse cobranças, pedidos e pagamentos.', symbol: '−',
    options: [{ label: 'Abrir financeiro', description: 'Consultar valores, cobranças e formas de pagamento.', view: 'finance', hint: { intent: 'pagar', mode: 'pay' } }],
  },
  {
    key: 'receber', label: 'Receber', description: 'Acompanhe carteira, repasses e valores a receber.', symbol: '=',
    options: [{ label: 'Abrir financeiro', description: 'Consultar recebimentos, carteira e valores protegidos.', view: 'finance', hint: { intent: 'receber', mode: 'receive' } }],
  },
  {
    key: 'trabalhar', label: 'Trabalhar', description: 'Busque emprego ou ofereça seu trabalho especializado.', symbol: '✦',
    options: [
      { label: 'Buscar emprego', description: 'Cadastrar ou editar currículo e abrir o feed de vagas.', view: 'jobs', hint: { intent: 'trabalhar', mode: 'seek' } },
      { label: 'Oferecer trabalho', description: 'Cadastrar-se como prestador especializado em uma área.', view: 'jobs', hint: { intent: 'trabalhar', mode: 'offer' } },
    ],
  },
];

export function HomeView({ onNavigate }: { onNavigate: Navigate }) {
  const [selectedIntent, setSelectedIntent] = useState<ConsumerIntent | null>(null);
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
    <details className='utility-drawer'><summary>Outras utilidades</summary><div className='utility-links'><button type='button' onClick={() => onNavigate('delivery')}>Entregas</button><button type='button' onClick={() => onNavigate('mobility')}>Mobilidade</button><button type='button' onClick={() => onNavigate('life')}>Documentos</button><button type='button' onClick={() => onNavigate('settings')}>Ajustes</button></div></details>
    {selectedIntent && <Modal title={selectedIntent.label} onClose={() => setSelectedIntent(null)}><p className='intent-modal-copy'>{selectedIntent.description}</p><div className='intent-option-list'>{selectedIntent.options.map(option => <button key={option.label} type='button' className='intent-option' onClick={() => { setSelectedIntent(null); onNavigate(option.view, option.hint); }}><strong>{option.label}</strong><span>{option.description}</span><b aria-hidden='true'>›</b></button>)}</div></Modal>}
  </section>;
}

export function MarketplaceView({ session, setNotice, hint }: ViewProps & { hint?: JourneyHint }) {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState(hint?.query ?? '');
  const [appliedQuery, setAppliedQuery] = useState(hint?.query ?? '');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<Offer | null>(null);
  const [actionResult, setActionResult] = useState<JsonRecord | null>(null);
  const [listingTitle, setListingTitle] = useState('');
  const [listingDescription, setListingDescription] = useState('');
  const [listingCategory, setListingCategory] = useState('');
  const [listingPrice, setListingPrice] = useState('');
  const [listingRegion, setListingRegion] = useState('');

  useEffect(() => { const nextQuery = hint?.query ?? ''; setQuery(nextQuery); setAppliedQuery(nextQuery); }, [hint?.query]);
  const load = useCallback(async (append = false, offset = 0) => {
    if (append) setLoadingMore(true); else setLoading(true);
    setError('');
    const params = new URLSearchParams({ offset: String(offset), limit: '20' });
    if (appliedQuery.trim()) params.set('q', appliedQuery.trim());
    if (category) params.set('category', category);
    try {
      const data = await request<CatalogResponse>(`/gateway/catalog/offers?${params}`);
      setOffers(current => append ? [...current, ...(data.data ?? [])] : (data.data ?? []));
      setTotal(data.total ?? 0);
      if (data.partial) setNotice('Algumas fontes estão temporariamente indisponíveis.');
    } catch (err) { setError(errorMessage(err)); if (!append) setOffers([]); }
    finally { if (append) setLoadingMore(false); else setLoading(false); }
  }, [appliedQuery, category, setNotice]);
  useEffect(() => { const timer = window.setTimeout(() => { void load(false, 0); }, 0); return () => window.clearTimeout(timer); }, [load]);

  const categories = useMemo(() => Array.from(new Set(offers.map(item => item.consumer_category))).filter(Boolean), [offers]);
  const submitSearch = (event: FormEvent) => { event.preventDefault(); const normalized = query.trim(); if (normalized === appliedQuery) void load(false, 0); else setAppliedQuery(normalized); };
  const submitListing = async (event: FormEvent) => {
    event.preventDefault();
    const repairRequest = hint?.mode === 'repair-request';
    try {
      await request('/marketplace/resources/products', 'POST', {
        user_id: session.userId,
        status: 'draft',
        payload: {
          title: listingTitle,
          description: listingDescription,
          category: listingCategory,
          price_amount: repairRequest ? null : listingPrice,
          region: listingRegion,
          listing_type: repairRequest ? 'repair_request' : 'sale',
          requested_specialty: repairRequest ? listingCategory : null,
        },
      }, session.accessToken);
      setListingTitle(''); setListingDescription(''); setListingCategory(''); setListingPrice(''); setListingRegion('');
      setNotice(repairRequest ? 'Pedido de conserto publicado para análise.' : 'Item cadastrado para análise e publicação.');
      await load(false, 0);
    } catch (err) { setNotice(errorMessage(err)); }
  };
  const executeAction = async (offer: Offer) => {
    if (['view', 'coming_soon'].includes(offer.consumer_action)) { setSelected(offer); return; }
    try {
      const result = await request<JsonRecord>('/gateway/catalog/actions', 'POST', { offer_id: offer.offer_id, action: offer.consumer_action, customer_user_id: session.userId, idempotency_key: window.crypto.randomUUID(), quantity: 1 }, session.accessToken);
      setSelected(offer); setActionResult(result); setNotice(String(result.message ?? 'Solicitação registrada.'));
    } catch (err) { setNotice(errorMessage(err)); }
  };
  const pay = async () => {
    const paymentIntent = actionResult?.payment_intent as JsonRecord | undefined;
    if (!paymentIntent) return;
    try {
      const result = await request<JsonRecord>('/gateway/payments/sandbox/authorize', 'POST', { order_id: paymentIntent.order_id, method: 'pix_sandbox', idempotency_key: `payment-${paymentIntent.order_id}` }, session.accessToken);
      setNotice(String(result.message ?? 'Pagamento autorizado.')); setSelected(null); setActionResult(null);
    } catch (err) { setNotice(errorMessage(err)); }
  };
  const favorite = async (offer: Offer) => {
    if (!offer.source_entity_id) return;
    try { await request(`/marketplace/valley/favorites/${offer.source_entity_id}`, 'PUT', undefined, session.accessToken); setNotice('Favorito sincronizado com sua conta.'); }
    catch (err) { setNotice(errorMessage(err)); }
  };

  const isSelling = hint?.mode === 'sell';
  const isRepairRequest = hint?.mode === 'repair-request';
  const title = isSelling ? 'Vender um item' : isRepairRequest ? 'Publicar pedido de conserto' : 'Marketplace';
  const subtitle = isSelling ? 'Cadastre o item que deseja vender, com informações claras para os compradores.' : isRepairRequest ? 'Anuncie o item, descreva o defeito e encontre alguém especializado.' : 'Feed de atualizações, categorias, produtos e ofertas verificadas.';

  return <section className='media-surface'><SectionHeader title={title} subtitle={subtitle} />
    {(isSelling || isRepairRequest) && <form className='form-card listing-composer' onSubmit={submitListing}><h2>{isRepairRequest ? 'O que precisa ser consertado?' : 'O que você quer vender?'}</h2><label>{isRepairRequest ? 'Item' : 'Título do anúncio'}<input value={listingTitle} onChange={event => setListingTitle(event.target.value)} required /></label><label>{isRepairRequest ? 'Defeito ou problema' : 'Descrição'}<textarea value={listingDescription} onChange={event => setListingDescription(event.target.value)} required /></label><label>{isRepairRequest ? 'Especialidade necessária' : 'Categoria'}<input value={listingCategory} onChange={event => setListingCategory(event.target.value)} placeholder={isRepairRequest ? 'Ex.: eletrônica, mecânica, costura' : 'Ex.: casa, tecnologia, moda'} required /></label>{!isRepairRequest && <label>Preço<input inputMode='decimal' value={listingPrice} onChange={event => setListingPrice(event.target.value)} required /></label>}<label>Região<input value={listingRegion} onChange={event => setListingRegion(event.target.value)} required /></label><button className='primary' type='submit'>{isRepairRequest ? 'Publicar pedido de conserto' : 'Cadastrar item para vender'}</button></form>}
    <form className='search-panel search-panel-sticky' onSubmit={submitSearch}><label>Buscar produto, categoria ou empresa<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Digite o que procura' /></label><button className='primary' type='submit'>Buscar</button></form>
    <div className='chip-row'><button type='button' className={!category ? 'chip active' : 'chip'} onClick={() => setCategory('')}>Tudo</button>{categories.map(item => <button type='button' key={item} className={category === item ? 'chip active' : 'chip'} onClick={() => setCategory(item)}>{item}</button>)}</div>
    {loading && <StateCard text='Sincronizando catálogo...' />}{error && <StateCard text={error} tone='error' actionLabel='Tentar novamente' onAction={() => void load(false, 0)} />}{!loading && !error && !offers.length && <StateCard text='Nenhuma oferta encontrada para estes filtros.' />}
    <div className='offer-grid feed-grid'>{offers.map(offer => <article className='offer-card feed-card' key={offer.offer_id}>{offer.metadata?.image_url && <img src={offer.metadata.image_url} alt='' loading='lazy' />}{offer.metadata?.video_url && <video src={offer.metadata.video_url} preload='none' muted controls playsInline />}<span className='eyebrow'>{offer.offer_type_label} · {offer.source_module}</span><h2>{offer.title}</h2><p>{offer.short_description ?? offer.description}</p><small>{offer.provider_label} · {offer.region_label}{offer.distance_km != null ? ` · ${offer.distance_km.toFixed(1)} km` : ''}</small><strong>{formatMoney(offer.price_amount)}</strong><div className='button-row'><button type='button' className='secondary' onClick={() => setSelected(offer)}>Detalhes</button>{offer.source_entity_id && <button type='button' className='secondary' onClick={() => favorite(offer)}>Favoritar</button>}{offer.consumer_action !== 'coming_soon' && <button type='button' className='primary' onClick={() => executeAction(offer)}>{offer.primary_action_label}</button>}</div></article>)}</div>
    {!loading && offers.length < total && <button className='secondary load-more' type='button' disabled={loadingMore} onClick={() => void load(true, offers.length)}>{loadingMore ? 'Carregando mais ofertas...' : 'Carregar mais ofertas'}</button>}
    {selected && <Modal title={selected.title} onClose={() => { setSelected(null); setActionResult(null); }}><p>{selected.description ?? selected.short_description}</p><p><strong>{formatMoney(selected.price_amount)}</strong></p>{Boolean(actionResult?.payment_intent) && <button className='primary' type='button' onClick={pay}>Autorizar pagamento de homologação</button>}{!actionResult?.payment_intent && !['view', 'coming_soon'].includes(selected.consumer_action) && <button className='primary' type='button' onClick={() => executeAction(selected)}>{selected.primary_action_label}</button>}</Modal>}
  </section>;
}

export function StockView({ session, setNotice, hint }: ViewProps & { hint?: JourneyHint }) {
  const [items, setItems] = useState<ApiItem[]>([]);
  const [query, setQuery] = useState(hint?.query ?? '');
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true);
    try { setItems(await request<ApiItem[]>('/stock/resources/catalog_products', 'GET', undefined, session.accessToken) ?? []); }
    catch (err) { setNotice(errorMessage(err)); }
    finally { setLoading(false); }
  }, [session.accessToken, setNotice]);
  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);
  useEffect(() => { setQuery(hint?.query ?? ''); }, [hint?.query]);
  const filtered = useMemo(() => { const normalized = query.trim().toLocaleLowerCase('pt-BR'); if (!normalized) return items; return items.filter(item => `${itemTitle(item)} ${itemSubtitle(item)} ${JSON.stringify(item.payload ?? {})}`.toLocaleLowerCase('pt-BR').includes(normalized)); }, [items, query]);
  return <section className='media-surface'><SectionHeader title='Estoque' subtitle='Feed de produtos de fornecedores e empresas, com disponibilidade e busca direta.' actionLabel='Atualizar' onAction={load} /><div className='search-panel single-search search-panel-sticky'><label>Buscar no estoque<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Produto, código, fornecedor ou categoria' /></label></div>{loading && <StateCard text='Sincronizando estoque...' />}{!loading && !filtered.length && <StateCard text='Nenhum produto encontrado para esta busca.' />}<div className='offer-grid feed-grid'>{filtered.map(item => { const payload = item.payload ?? {}; const priceAmount = payload.price_amount == null ? null : String(payload.price_amount); return <article className='offer-card feed-card' key={item.id}><span className='eyebrow'>{item.status ?? 'disponível'}</span><h2>{itemTitle(item)}</h2><p>{itemSubtitle(item)}</p><small>{String(payload.supplier_name ?? payload.external_sku ?? payload.sku ?? 'Fornecedor não informado')}</small><strong>{formatMoney(priceAmount)}</strong><button type='button' className='primary' onClick={() => setNotice(`Produto ${itemTitle(item)} selecionado.`)}>Ver produto</button></article>; })}</div></section>;
}

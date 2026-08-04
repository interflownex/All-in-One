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
type ConsumerIntent = {
  key: string;
  label: string;
  description: string;
  symbol: string;
  options: IntentOption[];
};

const intents: ConsumerIntent[] = [
  {
    key: 'comprar',
    label: 'Comprar',
    description: 'Produtos, ofertas e itens disponíveis perto de você.',
    symbol: '↓',
    options: [
      { label: 'Marketplace', description: 'Entrar direto no feed de produtos e novidades.', view: 'marketplace', hint: { intent: 'comprar', mode: 'feed' } },
      { label: 'Estoque', description: 'Consultar produtos disponíveis por empresa e localização.', view: 'stock', hint: { intent: 'comprar', mode: 'browse' } },
    ],
  },
  {
    key: 'vender',
    label: 'Vender',
    description: 'Anuncie produtos ou organize o que sua empresa oferece.',
    symbol: '↑',
    options: [
      { label: 'Anunciar no Marketplace', description: 'Preparar um anúncio para o catálogo do Valley.', view: 'marketplace', hint: { intent: 'vender', mode: 'sell' } },
      { label: 'Cadastrar no Estoque', description: 'Registrar item, preço e disponibilidade.', view: 'stock', hint: { intent: 'vender', mode: 'sell' } },
    ],
  },
  {
    key: 'contratar',
    label: 'Contratar',
    description: 'Encontre profissionais, serviços ou pessoas para uma vaga.',
    symbol: '+',
    options: [
      { label: 'Contratar um serviço', description: 'Buscar profissionais e horários disponíveis.', view: 'services', hint: { intent: 'contratar', mode: 'hire' } },
      { label: 'Contratar para uma vaga', description: 'Criar ou acompanhar uma oportunidade de trabalho.', view: 'jobs', hint: { intent: 'contratar', mode: 'recruit' } },
    ],
  },
  {
    key: 'alugar',
    label: 'Alugar',
    description: 'Encontre ou anuncie itens, espaços e equipamentos para aluguel.',
    symbol: '◇',
    options: [
      { label: 'Buscar para alugar', description: 'Abrir resultados e ofertas de aluguel.', view: 'marketplace', hint: { intent: 'alugar', mode: 'feed', query: 'aluguel' } },
      { label: 'Anunciar para aluguel', description: 'Preparar uma oferta de aluguel.', view: 'marketplace', hint: { intent: 'alugar', mode: 'sell', query: 'aluguel' } },
    ],
  },
  {
    key: 'consertar',
    label: 'Consertar',
    description: 'Ache assistência, manutenção ou solicite um orçamento.',
    symbol: '⌁',
    options: [
      { label: 'Encontrar assistência', description: 'Buscar oficinas e profissionais de reparo.', view: 'services', hint: { intent: 'consertar', mode: 'hire', query: 'conserto' } },
      { label: 'Solicitar orçamento', description: 'Abrir uma solicitação de reparo.', view: 'services', hint: { intent: 'consertar', mode: 'request', query: 'reparo' } },
    ],
  },
  {
    key: 'pagar',
    label: 'Pagar',
    description: 'Pedidos, cobranças e pagamentos em um só lugar.',
    symbol: '−',
    options: [
      { label: 'Abrir pagamentos', description: 'Consultar pedidos e valores a pagar.', view: 'commerce', hint: { intent: 'pagar', mode: 'pay' } },
    ],
  },
  {
    key: 'receber',
    label: 'Receber',
    description: 'Acompanhe carteira, repasses e valores protegidos.',
    symbol: '=',
    options: [
      { label: 'Abrir recebimentos', description: 'Consultar carteira, escrow e histórico.', view: 'commerce', hint: { intent: 'receber', mode: 'receive' } },
    ],
  },
  {
    key: 'trabalhar',
    label: 'Trabalhar',
    description: 'Busque emprego ou cadastre-se para novas oportunidades.',
    symbol: '✦',
    options: [
      { label: 'Buscar emprego', description: 'Pesquisar vagas e acompanhar candidaturas.', view: 'jobs', hint: { intent: 'trabalhar', mode: 'seek' } },
      { label: 'Quero trabalhar', description: 'Criar seu cadastro profissional e demonstrar interesse.', view: 'jobs', hint: { intent: 'trabalhar', mode: 'offer' } },
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
    <div className='intent-hero'>
      <span className='intent-kicker'>O que você quer fazer agora?</span>
      <h1>Escolha uma intenção.</h1>
      <p>O Valley leva você ao lugar certo sem exigir que conheça nomes de módulos ou menus técnicos.</p>
    </div>
    <div className='intent-grid'>
      {intents.map(intent => <button key={intent.key} type='button' className='intent-card' onClick={() => chooseIntent(intent)}>
        <span className='intent-symbol' aria-hidden='true'>{intent.symbol}</span>
        <span className='intent-copy'><strong>{intent.label}</strong><small>{intent.description}</small></span>
        <span className='intent-arrow' aria-hidden='true'>›</span>
      </button>)}
    </div>
    <details className='utility-drawer'>
      <summary>Outras utilidades</summary>
      <div className='utility-links'>
        <button type='button' onClick={() => onNavigate('delivery')}>Entregas</button>
        <button type='button' onClick={() => onNavigate('mobility')}>Mobilidade</button>
        <button type='button' onClick={() => onNavigate('life')}>Saúde e documentos</button>
        <button type='button' onClick={() => onNavigate('settings')}>Ajustes</button>
      </div>
    </details>
    {selectedIntent && <Modal title={selectedIntent.label} onClose={() => setSelectedIntent(null)}>
      <p className='intent-modal-copy'>{selectedIntent.description}</p>
      <div className='intent-option-list'>
        {selectedIntent.options.map(option => <button key={option.label} type='button' className='intent-option' onClick={() => { setSelectedIntent(null); onNavigate(option.view, option.hint); }}>
          <strong>{option.label}</strong><span>{option.description}</span><b aria-hidden='true'>›</b>
        </button>)}
      </div>
    </Modal>}
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

  useEffect(() => {
    const nextQuery = hint?.query ?? '';
    setQuery(nextQuery);
    setAppliedQuery(nextQuery);
  }, [hint?.query]);

  const load = useCallback(async (append = false, offset = 0) => {
    if (append) setLoadingMore(true); else setLoading(true);
    setError('');
    const params = new URLSearchParams();
    params.append('offset', String(offset));
    params.append('limit', '20');
    if (appliedQuery.trim()) params.set('q', appliedQuery.trim());
    if (category) params.set('category', category);
    try {
      const data = await request<CatalogResponse>(`/gateway/catalog/offers?${params}`);
      setOffers(current => append ? [...current, ...(data.data ?? [])] : (data.data ?? []));
      setTotal(data.total ?? 0);
      if (data.partial) setNotice('Algumas fontes estão temporariamente indisponíveis.');
    } catch (err) {
      setError(errorMessage(err));
      if (!append) setOffers([]);
    } finally {
      if (append) setLoadingMore(false); else setLoading(false);
    }
  }, [appliedQuery, category, setNotice]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void load(false, 0); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const categories = useMemo(() => Array.from(new Set(offers.map(item => item.consumer_category))).filter(Boolean), [offers]);
  const submitSearch = (event: FormEvent) => {
    event.preventDefault();
    const normalized = query.trim();
    if (normalized === appliedQuery) void load(false, 0); else setAppliedQuery(normalized);
  };
  const executeAction = async (offer: Offer) => {
    if (['view', 'coming_soon'].includes(offer.consumer_action)) { setSelected(offer); return; }
    try {
      const result = await request<JsonRecord>('/gateway/catalog/actions', 'POST', { offer_id: offer.offer_id, action: offer.consumer_action, customer_user_id: session.userId, idempotency_key: window.crypto.randomUUID(), quantity: 1 }, session.accessToken);
      setSelected(offer); setActionResult(result); setNotice(String(result.message ?? 'Solicitação registrada.'));
    } catch (err) { setNotice(errorMessage(err)); }
  };
  const pay = async () => {
    const intent = actionResult?.payment_intent as JsonRecord | undefined;
    if (!intent) return;
    try {
      const result = await request<JsonRecord>('/gateway/payments/sandbox/authorize', 'POST', { order_id: intent.order_id, method: 'pix_sandbox', idempotency_key: `payment-${intent.order_id}` }, session.accessToken);
      setNotice(String(result.message ?? 'Pagamento autorizado.')); setSelected(null); setActionResult(null);
    } catch (err) { setNotice(errorMessage(err)); }
  };
  const favorite = async (offer: Offer) => {
    if (!offer.source_entity_id) return;
    try { await request(`/marketplace/valley/favorites/${offer.source_entity_id}`, 'PUT', undefined, session.accessToken); setNotice('Favorito sincronizado com sua conta.'); }
    catch (err) { setNotice(errorMessage(err)); }
  };

  const isSelling = hint?.mode === 'sell';
  return <section className='media-surface'><SectionHeader title={isSelling ? 'Vender no Marketplace' : 'Marketplace'} subtitle={isSelling ? 'Prepare sua oferta e acompanhe o catálogo em que ela será publicada.' : 'Feed de atualizações, categorias, produtos e ofertas verificadas.'} />
    {isSelling && <div className='context-banner'><strong>Modo vendedor</strong><span>O fluxo comercial completo será liberado conforme as permissões da empresa.</span></div>}
    <form className='search-panel search-panel-sticky' onSubmit={submitSearch}><label>Buscar produto, categoria ou empresa<input value={query} onChange={e => setQuery(e.target.value)} placeholder='Digite o que procura' /></label><button className='primary' type='submit'>Buscar</button></form>
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
  const [title, setTitle] = useState('');
  const [sku, setSku] = useState('');
  const [price, setPrice] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try { setItems(await request<ApiItem[]>('/stock/resources/inventory_items', 'GET', undefined, session.accessToken) ?? []); }
    catch (err) { setNotice(errorMessage(err)); }
    finally { setLoading(false); }
  }, [session.accessToken, setNotice]);

  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);
  useEffect(() => { setQuery(hint?.query ?? ''); }, [hint?.query]);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase('pt-BR');
    if (!normalized) return items;
    return items.filter(item => `${itemTitle(item)} ${itemSubtitle(item)} ${JSON.stringify(item.payload ?? {})}`.toLocaleLowerCase('pt-BR').includes(normalized));
  }, [items, query]);

  const create = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/stock/resources/inventory_items', 'POST', { user_id: session.userId, status: 'ACTIVE', payload: { title, sku, price_amount: price } }, session.accessToken);
      setTitle(''); setSku(''); setPrice(''); setNotice('Item enviado para o estoque.'); await load();
    } catch (err) { setNotice(errorMessage(err)); }
  };

  const isSelling = hint?.mode === 'sell';
  return <section><SectionHeader title={isSelling ? 'Cadastrar no Estoque' : 'Estoque'} subtitle='Consulte itens disponíveis por nome, código, empresa ou descrição.' actionLabel='Atualizar' onAction={load} />
    <div className='search-panel single-search'><label>Buscar no estoque<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Produto, SKU, empresa ou categoria' /></label></div>
    {isSelling && <form className='form-card compact-form' onSubmit={create}><h2>Novo item</h2><label>Produto<input value={title} onChange={event => setTitle(event.target.value)} required /></label><label>Código ou SKU<input value={sku} onChange={event => setSku(event.target.value)} required /></label><label>Preço<input inputMode='decimal' value={price} onChange={event => setPrice(event.target.value)} required /></label><button className='primary' type='submit'>Cadastrar item</button></form>}
    {loading && <StateCard text='Sincronizando estoque...' />}
    {!loading && !filtered.length && <StateCard text='Nenhum item encontrado para esta busca.' />}
    <div className='offer-grid'>{filtered.map(item => { const payload = item.payload ?? {}; const priceAmount = payload.price_amount == null ? null : String(payload.price_amount); return <article className='offer-card' key={item.id}><span className='eyebrow'>{item.status ?? 'disponível'}</span><h2>{itemTitle(item)}</h2><p>{itemSubtitle(item)}</p><small>{String(payload.sku ?? payload.code ?? 'Sem código informado')}</small><strong>{formatMoney(priceAmount)}</strong><button type='button' className='primary' onClick={() => setNotice(`Item ${itemTitle(item)} selecionado.`)}>Ver disponibilidade</button></article>; })}</div>
  </section>;
}

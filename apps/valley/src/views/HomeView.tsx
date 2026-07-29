import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { errorMessage, formatMoney, request, type CatalogResponse, type JsonRecord, type Offer, type ViewProps } from '../lib/api';
import { Modal, SectionHeader, StateCard } from '../ui';

export function HomeView({ session, setNotice }: ViewProps) {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState('');
  const [appliedQuery, setAppliedQuery] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<Offer | null>(null);
  const [actionResult, setActionResult] = useState<JsonRecord | null>(null);

  const load = useCallback(async (append = false, offset = 0) => {
    if (append) setLoadingMore(true); else setLoading(true);
    setError('');
    const params = new URLSearchParams();
    params.append("offset", String(offset));
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

  return <section><SectionHeader title='Descobrir no Valley' subtitle='Busca regional, categorias, ofertas verificadas e ações sincronizadas.' />
    <form className='search-panel' onSubmit={submitSearch}><label>O que você procura?<input value={query} onChange={e => setQuery(e.target.value)} placeholder='Produto, serviço ou profissional' /></label><button className='primary' type='submit'>Buscar</button></form>
    <div className='chip-row'><button type='button' className={!category ? 'chip active' : 'chip'} onClick={() => setCategory('')}>Tudo</button>{categories.map(item => <button type='button' key={item} className={category === item ? 'chip active' : 'chip'} onClick={() => setCategory(item)}>{item}</button>)}</div>
    {loading && <StateCard text='Sincronizando catálogo...' />}{error && <StateCard text={error} tone='error' actionLabel='Tentar novamente' onAction={() => void load(false, 0)} />}{!loading && !error && !offers.length && <StateCard text='Nenhuma oferta encontrada para estes filtros.' />}
    <div className='offer-grid'>{offers.map(offer => <article className='offer-card' key={offer.offer_id}>{offer.metadata?.image_url && <img src={offer.metadata.image_url} alt='' loading="lazy" />}{offer.metadata?.video_url && <video src={offer.metadata.video_url} preload="none" muted controls playsInline />}<span className='eyebrow'>{offer.offer_type_label} · {offer.source_module}</span><h2>{offer.title}</h2><p>{offer.short_description ?? offer.description}</p><small>{offer.provider_label} · {offer.region_label}{offer.distance_km != null ? ` · ${offer.distance_km.toFixed(1)} km` : ''}</small><strong>{formatMoney(offer.price_amount)}</strong><div className='button-row'><button type='button' className='secondary' onClick={() => setSelected(offer)}>Detalhes</button>{offer.source_entity_id && <button type='button' className='secondary' onClick={() => favorite(offer)}>Favoritar</button>}{offer.consumer_action !== 'coming_soon' && <button type='button' className='primary' onClick={() => executeAction(offer)}>{offer.primary_action_label}</button>}</div></article>)}</div>
    {!loading && offers.length < total && <button className='secondary load-more' type='button' disabled={loadingMore} onClick={() => void load(true, offers.length)}>{loadingMore ? 'Carregando mais ofertas...' : 'Carregar mais ofertas'}</button>}
    {selected && <Modal title={selected.title} onClose={() => { setSelected(null); setActionResult(null); }}><p>{selected.description ?? selected.short_description}</p><p><strong>{formatMoney(selected.price_amount)}</strong></p>{Boolean(actionResult?.payment_intent) && <button className='primary' type='button' onClick={pay}>Autorizar pagamento de homologação</button>}{!actionResult?.payment_intent && !['view', 'coming_soon'].includes(selected.consumer_action) && <button className='primary' type='button' onClick={() => executeAction(selected)}>{selected.primary_action_label}</button>}</Modal>}
  </section>;
}

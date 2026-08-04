import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import {
  errorMessage,
  formatMoney,
  itemSubtitle,
  itemTitle,
  request,
  type ApiItem,
  type JourneyHint,
  type ViewProps,
} from '../lib/api';
import { Metric, ResourceSummary, SectionHeader, StateCard } from '../ui';

function useResources(module: string, resource: string, token: string, setNotice: (message: string) => void) {
  const [items, setItems] = useState<ApiItem[]>([]);
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true);
    try { setItems(await request<ApiItem[]>(`/${module}/resources/${resource}`, 'GET', undefined, token) ?? []); }
    catch (error) { setNotice(errorMessage(error)); }
    finally { setLoading(false); }
  }, [module, resource, setNotice, token]);
  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);
  return { items, loading, load };
}

function searchable(items: ApiItem[], query: string) {
  const normalized = query.trim().toLocaleLowerCase('pt-BR');
  if (!normalized) return items;
  return items.filter(item => `${itemTitle(item)} ${itemSubtitle(item)} ${JSON.stringify(item.payload ?? {})}`.toLocaleLowerCase('pt-BR').includes(normalized));
}

export function FinanceView({ session, setNotice, hint }: ViewProps & { hint?: JourneyHint }) {
  const wallets = useResources('finance', 'wallets', session.accessToken, setNotice);
  const ledger = useResources('finance', 'ledger_entries', session.accessToken, setNotice);
  const escrows = useResources('finance', 'escrows', session.accessToken, setNotice);
  const invoices = useResources('finance', 'invoices', session.accessToken, setNotice);
  const [query, setQuery] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [counterparty, setCounterparty] = useState('');
  const mode = hint?.mode === 'receive' ? 'receive' : 'pay';
  const allItems = useMemo(() => [...ledger.items, ...escrows.items, ...invoices.items], [escrows.items, invoices.items, ledger.items]);
  const filtered = useMemo(() => searchable(allItems, query), [allItems, query]);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/finance/resources/invoices', 'POST', {
        user_id: session.userId,
        status: 'draft',
        payload: {
          direction: mode,
          amount_brl: amount,
          description,
          counterparty,
          idempotency_key: window.crypto.randomUUID(),
        },
      }, session.accessToken);
      setAmount(''); setDescription(''); setCounterparty('');
      setNotice(mode === 'pay' ? 'Pagamento preparado para validação.' : 'Cobrança preparada para recebimento.');
      await Promise.all([ledger.load(), escrows.load(), invoices.load()]);
    } catch (error) { setNotice(errorMessage(error)); }
  };
  return <section><SectionHeader title={mode === 'pay' ? 'Pagar' : 'Receber'} subtitle='Carteira, cobranças, pagamentos, repasses e valores protegidos.' actionLabel='Atualizar' onAction={() => void Promise.all([wallets.load(), ledger.load(), escrows.load(), invoices.load()])} />
    <div className='metric-grid'><Metric label='Carteiras' value={String(wallets.items.length)} /><Metric label='Movimentações' value={String(ledger.items.length)} /><Metric label='Valores protegidos' value={String(escrows.items.length)} /></div>
    <form className='form-card' onSubmit={submit}><h2>{mode === 'pay' ? 'Novo pagamento' : 'Novo recebimento'}</h2><label>{mode === 'pay' ? 'Quem vai receber' : 'Quem vai pagar'}<input value={counterparty} onChange={event => setCounterparty(event.target.value)} required /></label><label>Valor<input inputMode='decimal' value={amount} onChange={event => setAmount(event.target.value)} placeholder='R$' required /></label><label>Descrição<input value={description} onChange={event => setDescription(event.target.value)} required /></label><button className='primary' type='submit'>{mode === 'pay' ? 'Continuar pagamento' : 'Gerar cobrança'}</button></form>
    <div className='search-panel single-search'><label>Buscar no financeiro<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Descrição, valor, cobrança ou pagamento' /></label></div>
    {(wallets.loading || ledger.loading || escrows.loading || invoices.loading) && <StateCard text='Sincronizando financeiro...' />}
    {!filtered.length && !ledger.loading && !escrows.loading && !invoices.loading && <StateCard text='Nenhuma movimentação encontrada.' />}
    <div className='card-list compact'>{filtered.map(item => <article className='data-card' key={item.id}><div><span className='eyebrow'>{item.status ?? 'registrado'}</span><h3>{itemTitle(item)}</h3><p>{itemSubtitle(item)}</p>{item.payload?.amount_brl != null && <strong>{formatMoney(String(item.payload.amount_brl))}</strong>}</div></article>)}</div>
  </section>;
}

export function LegalView({ session, setNotice }: ViewProps & { hint?: JourneyHint }) {
  const cases = useResources('legal', 'cases', session.accessToken, setNotice);
  const contracts = useResources('legal', 'legal_contracts', session.accessToken, setNotice);
  const [query, setQuery] = useState('');
  const [subject, setSubject] = useState('');
  const [details, setDetails] = useState('');
  const [region, setRegion] = useState('');
  const filtered = useMemo(() => searchable([...cases.items, ...contracts.items], query), [cases.items, contracts.items, query]);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/legal/resources/cases', 'POST', { user_id: session.userId, status: 'requested', payload: { subject, description: details, region, source: 'valley_hire_legal' } }, session.accessToken);
      setSubject(''); setDetails(''); setRegion(''); setNotice('Solicitação jurídica registrada.'); await cases.load();
    } catch (error) { setNotice(errorMessage(error)); }
  };
  return <section><SectionHeader title='Contratar apoio jurídico' subtitle='Orientação, contratos e acompanhamento jurídico em uma jornada guiada.' actionLabel='Atualizar' onAction={() => void Promise.all([cases.load(), contracts.load()])} /><div className='search-panel single-search'><label>Buscar assunto jurídico<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Ex.: contrato, consumidor, imóvel, trabalho' /></label></div><form className='form-card' onSubmit={submit}><h2>Descreva o que precisa</h2><label>Assunto<input value={subject} onChange={event => setSubject(event.target.value)} required /></label><label>Detalhes<textarea value={details} onChange={event => setDetails(event.target.value)} required /></label><label>Região<input value={region} onChange={event => setRegion(event.target.value)} required /></label><button className='primary' type='submit'>Solicitar atendimento</button></form>{(cases.loading || contracts.loading) && <StateCard text='Sincronizando atendimentos...' />}{!filtered.length && !cases.loading && !contracts.loading && <StateCard text='Nenhum atendimento encontrado.' />}<ResourceSummary title='Atendimentos e contratos' items={filtered} /></section>;
}

export function HealthView({ session, setNotice }: ViewProps & { hint?: JourneyHint }) {
  const appointments = useResources('health', 'appointments', session.accessToken, setNotice);
  const [query, setQuery] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [region, setRegion] = useState('');
  const filtered = useMemo(() => searchable(appointments.items, query), [appointments.items, query]);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/health/resources/appointments', 'POST', { user_id: session.userId, status: 'requested', payload: { specialty, scheduled_at: scheduledAt, region, source: 'valley_hire_health' } }, session.accessToken);
      setSpecialty(''); setScheduledAt(''); setRegion(''); setNotice('Solicitação de atendimento registrada.'); await appointments.load();
    } catch (error) { setNotice(errorMessage(error)); }
  };
  return <section><SectionHeader title='Contratar atendimento de saúde' subtitle='Busque uma especialidade e solicite atendimento com segurança.' actionLabel='Atualizar' onAction={appointments.load} /><div className='search-panel single-search'><label>Buscar especialidade ou atendimento<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Ex.: clínica geral, odontologia, psicologia' /></label></div><form className='form-card' onSubmit={submit}><h2>Solicitar atendimento</h2><label>Especialidade<input value={specialty} onChange={event => setSpecialty(event.target.value)} required /></label><label>Data e hora preferida<input type='datetime-local' value={scheduledAt} onChange={event => setScheduledAt(event.target.value)} required /></label><label>Região<input value={region} onChange={event => setRegion(event.target.value)} required /></label><button className='primary' type='submit'>Buscar atendimento</button></form>{appointments.loading && <StateCard text='Sincronizando atendimentos...' />}{!filtered.length && !appointments.loading && <StateCard text='Nenhum atendimento encontrado.' />}<ResourceSummary title='Meus atendimentos' items={filtered} /></section>;
}

export function PropertyView({ session, setNotice }: ViewProps & { hint?: JourneyHint }) {
  const properties = useResources('property', 'properties', session.accessToken, setNotice);
  const units = useResources('property', 'units', session.accessToken, setNotice);
  const leases = useResources('property', 'leases', session.accessToken, setNotice);
  const [query, setQuery] = useState('');
  const [region, setRegion] = useState('');
  const [propertyType, setPropertyType] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [selectedProperty, setSelectedProperty] = useState<ApiItem | null>(null);
  const combined = useMemo(() => [...properties.items, ...units.items], [properties.items, units.items]);
  const filtered = useMemo(() => {
    const searched = searchable(combined, query);
    const normalizedRegion = region.trim().toLocaleLowerCase('pt-BR');
    const normalizedType = propertyType.trim().toLocaleLowerCase('pt-BR');
    const maximum = Number(maxPrice.replace(/[^0-9.,]/g, '').replace(',', '.')) || 0;
    return searched.filter(item => {
      const payload = item.payload ?? {};
      const itemRegion = String(payload.region ?? payload.city ?? payload.address ?? '').toLocaleLowerCase('pt-BR');
      const itemType = String(payload.property_type ?? payload.type ?? '').toLocaleLowerCase('pt-BR');
      const price = Number(String(payload.rent_amount ?? payload.price_amount ?? '0').replace(/[^0-9.,]/g, '').replace(',', '.')) || 0;
      if (normalizedRegion && !itemRegion.includes(normalizedRegion)) return false;
      if (normalizedType && !itemType.includes(normalizedType)) return false;
      if (maximum && price && price > maximum) return false;
      return true;
    });
  }, [combined, maxPrice, propertyType, query, region]);
  const requestLease = async () => {
    if (!selectedProperty) return;
    try {
      await request('/property/resources/leases', 'POST', { user_id: session.userId, status: 'requested', payload: { property_id: selectedProperty.id, source: 'valley_rent_intent' } }, session.accessToken);
      setSelectedProperty(null); setNotice('Interesse no aluguel registrado.'); await leases.load();
    } catch (error) { setNotice(errorMessage(error)); }
  };
  return <section className='media-surface'><SectionHeader title='Alugar imóvel ou propriedade' subtitle='Feed de imóveis, unidades e propriedades disponíveis para locação.' actionLabel='Atualizar' onAction={() => void Promise.all([properties.load(), units.load(), leases.load()])} /><div className='property-filters'><label>Buscar<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Imóvel, bairro ou característica' /></label><label>Região<input value={region} onChange={event => setRegion(event.target.value)} /></label><label>Tipo<input value={propertyType} onChange={event => setPropertyType(event.target.value)} placeholder='Casa, apartamento, sala' /></label><label>Valor máximo<input inputMode='decimal' value={maxPrice} onChange={event => setMaxPrice(event.target.value)} placeholder='R$' /></label></div>{(properties.loading || units.loading) && <StateCard text='Sincronizando imóveis...' />}{!filtered.length && !properties.loading && !units.loading && <StateCard text='Nenhum imóvel encontrado com estes filtros.' />}<div className='offer-grid feed-grid'>{filtered.map(item => { const payload = item.payload ?? {}; const price = payload.rent_amount ?? payload.price_amount; return <article className='offer-card feed-card' key={item.id}><span className='eyebrow'>{String(payload.property_type ?? payload.type ?? 'Imóvel')}</span><h2>{itemTitle(item)}</h2><p>{itemSubtitle(item)}</p><small>{String(payload.region ?? payload.city ?? payload.address ?? 'Região não informada')}</small><strong>{price == null ? 'Valor sob consulta' : formatMoney(String(price))}</strong><button className='primary' type='button' onClick={() => setSelectedProperty(item)}>Tenho interesse</button></article>; })}</div>{selectedProperty && <div className='context-banner'><strong>{itemTitle(selectedProperty)}</strong><span>Confirme para registrar seu interesse em alugar esta propriedade.</span><div className='button-row'><button className='secondary' type='button' onClick={() => setSelectedProperty(null)}>Cancelar</button><button className='primary' type='button' onClick={requestLease}>Confirmar interesse</button></div></div>}<ResourceSummary title='Meus interesses e locações' items={leases.items} /></section>;
}

import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { errorMessage, itemSubtitle, itemTitle, request, type ApiItem, type JourneyHint, type ViewProps } from '../lib/api';
import { ResourceSummary, SectionHeader, StateCard } from '../ui';

type Field = { key: string; label: string; type?: string };
function ResourceJourney({ title, subtitle, module, resource, session, setNotice, fields, embedded = false }: { title: string; subtitle: string; module: string; resource: string; session: ViewProps['session']; setNotice: ViewProps['setNotice']; fields: Field[]; embedded?: boolean }) {
  const [items, setItems] = useState<ApiItem[]>([]); const [values, setValues] = useState<Record<string, string>>({}); const [loading, setLoading] = useState(true); const [query, setQuery] = useState('');
  const load = useCallback(async () => { setLoading(true); try { setItems(await request<ApiItem[]>(`/${module}/resources/${resource}`, 'GET', undefined, session.accessToken) ?? []); } catch (err) { setNotice(errorMessage(err)); } finally { setLoading(false); } }, [module, resource, session.accessToken, setNotice]);
  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);
  const create = async (event: FormEvent) => { event.preventDefault(); try { await request(`/${module}/resources/${resource}`, 'POST', { user_id: session.userId, status: 'REQUESTED', payload: values }, session.accessToken); setValues({}); setNotice('Solicitação registrada no servidor.'); await load(); } catch (err) { setNotice(errorMessage(err)); } };
  const filteredItems = useMemo(() => { const normalized = query.trim().toLocaleLowerCase('pt-BR'); if (!normalized) return items; return items.filter(item => `${itemTitle(item)} ${itemSubtitle(item)} ${JSON.stringify(item.payload ?? {})}`.toLocaleLowerCase('pt-BR').includes(normalized)); }, [items, query]);
  return <div className={embedded ? 'embedded-journey' : ''}>{!embedded && <SectionHeader title={title} subtitle={subtitle} actionLabel='Atualizar' onAction={load} />}{embedded && <div className='inline-heading'><h2>{title}</h2><button type='button' className='secondary' onClick={load}>Atualizar</button></div>}<div className='search-panel single-search'><label>Buscar nesta tela<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Nome, tipo, local ou descrição' /></label></div><form className='form-card' onSubmit={create}>{fields.map(field => <label key={field.key}>{field.label}<input type={field.type ?? 'text'} value={values[field.key] ?? ''} onChange={e => setValues(current => ({ ...current, [field.key]: e.target.value }))} required /></label>)}<button className='primary' type='submit'>Enviar solicitação</button></form>{loading && <StateCard text='Sincronizando...' />}{!loading && !filteredItems.length && <StateCard text='Nenhum registro encontrado para esta busca.' />}<ResourceSummary title='Registros' items={filteredItems} /></div>;
}

export function ServicesView({ session, setNotice, hint }: ViewProps & { hint?: JourneyHint }) {
  const [providers, setProviders] = useState<ApiItem[]>([]); const [contracts, setContracts] = useState<ApiItem[]>([]); const [slots, setSlots] = useState<string[]>([]); const [date, setDate] = useState(() => new Date().toISOString().slice(0,10)); const [query, setQuery] = useState(hint?.query ?? '');
  const load = useCallback(async () => { try { const [p,c,s] = await Promise.all([request<ApiItem[]>('/services/resources/providers','GET',undefined,session.accessToken), request<ApiItem[]>('/services/resources/service_contracts','GET',undefined,session.accessToken), request<{ available_slots?: string[] }>(`/services/providers/mock-provider/time-slots?date=${date}`,'GET',undefined,session.accessToken)]); setProviders(p ?? []); setContracts(c ?? []); setSlots(s.available_slots ?? []); } catch (err) { setNotice(errorMessage(err)); } }, [date, session.accessToken, setNotice]);
  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);
  useEffect(() => { setQuery(hint?.query ?? ''); }, [hint?.query]);
  const filterItems = useCallback((items: ApiItem[]) => { const normalized = query.trim().toLocaleLowerCase('pt-BR'); if (!normalized) return items; return items.filter(item => `${itemTitle(item)} ${itemSubtitle(item)} ${JSON.stringify(item.payload ?? {})}`.toLocaleLowerCase('pt-BR').includes(normalized)); }, [query]);
  const filteredProviders = useMemo(() => filterItems(providers), [filterItems, providers]);
  const filteredContracts = useMemo(() => filterItems(contracts), [contracts, filterItems]);
  const reserve = async (slot: string) => { try { await request('/services/providers/mock-provider/reserve-slot','POST',{ slot, customer_id: session.userId },session.accessToken); setNotice(`Horário ${slot} reservado.`); await load(); } catch (err) { setNotice(errorMessage(err)); } };
  return <section><SectionHeader title={hint?.intent === 'consertar' ? 'Consertar e solicitar orçamento' : 'Contratar serviços'} subtitle='Encontre profissionais, oficinas, horários e contratos conectados ao servidor.' actionLabel='Atualizar' onAction={load} /><div className='search-panel single-search'><label>Buscar serviço ou profissional<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Ex.: eletricista, oficina, conserto de celular' /></label></div><div className='form-card'><label>Data da agenda<input type='date' value={date} onChange={e => setDate(e.target.value)} /></label><div className='slot-grid'>{slots.map(slot => <button type='button' key={slot} onClick={() => reserve(slot)}>{slot}</button>)}</div>{!slots.length && <StateCard text='Nenhum horário disponível nesta data.' />}</div><ResourceSummary title='Profissionais encontrados' items={filteredProviders} /><ResourceSummary title='Contratos encontrados' items={filteredContracts} />{!filteredProviders.length && !filteredContracts.length && <StateCard text='Nenhum serviço encontrado para esta busca.' />}</section>;
}

export function JobsView({ session, setNotice, hint }: ViewProps & { hint?: JourneyHint }) {
  const initialMode = hint?.mode === 'recruit' ? 'recruit' : hint?.mode === 'offer' ? 'offer' : 'seek';
  const [mode, setMode] = useState<'seek' | 'offer' | 'recruit'>(initialMode);
  const [vacancies, setVacancies] = useState<ApiItem[]>([]);
  const [applications, setApplications] = useState<ApiItem[]>([]);
  const [query, setQuery] = useState(hint?.query ?? '');
  const [vacancyId, setVacancyId] = useState('');
  const [note, setNote] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [vacancyData, applicationData] = await Promise.all([
        request<ApiItem[]>('/jobs/resources/vacancies', 'GET', undefined, session.accessToken),
        request<ApiItem[]>('/jobs/resources/applications', 'GET', undefined, session.accessToken),
      ]);
      setVacancies(vacancyData ?? []); setApplications(applicationData ?? []);
    } catch (err) { setNotice(errorMessage(err)); }
    finally { setLoading(false); }
  }, [session.accessToken, setNotice]);

  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);
  useEffect(() => { setMode(hint?.mode === 'recruit' ? 'recruit' : hint?.mode === 'offer' ? 'offer' : 'seek'); setQuery(hint?.query ?? ''); }, [hint?.mode, hint?.query]);

  const filteredVacancies = useMemo(() => { const normalized = query.trim().toLocaleLowerCase('pt-BR'); if (!normalized) return vacancies; return vacancies.filter(item => `${itemTitle(item)} ${itemSubtitle(item)} ${JSON.stringify(item.payload ?? {})}`.toLocaleLowerCase('pt-BR').includes(normalized)); }, [query, vacancies]);

  const apply = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/jobs/resources/applications', 'POST', { user_id: session.userId, status: 'REQUESTED', payload: { vacancy_id: vacancyId || null, note, profile_mode: mode } }, session.accessToken);
      setVacancyId(''); setNote(''); setNotice(mode === 'offer' ? 'Seu interesse profissional foi cadastrado.' : 'Candidatura enviada.'); await load();
    } catch (err) { setNotice(errorMessage(err)); }
  };

  const createVacancy = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/jobs/resources/vacancies', 'POST', { user_id: session.userId, status: 'OPEN', payload: { title: jobTitle, description, location } }, session.accessToken);
      setJobTitle(''); setDescription(''); setLocation(''); setNotice('Vaga cadastrada para análise e publicação.'); await load();
    } catch (err) { setNotice(errorMessage(err)); }
  };

  return <section><SectionHeader title='Trabalhar e contratar' subtitle='Busque emprego, cadastre seu interesse profissional ou publique uma oportunidade.' actionLabel='Atualizar' onAction={load} />
    <div className='segmented intent-segmented'><button type='button' className={mode === 'seek' ? 'active' : ''} onClick={() => setMode('seek')}>Buscar emprego</button><button type='button' className={mode === 'offer' ? 'active' : ''} onClick={() => setMode('offer')}>Quero trabalhar</button><button type='button' className={mode === 'recruit' ? 'active' : ''} onClick={() => setMode('recruit')}>Quero contratar</button></div>
    <div className='search-panel single-search'><label>Buscar vaga, empresa ou área<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder='Ex.: motorista, atendimento, tecnologia' /></label></div>
    {mode === 'recruit' ? <form className='form-card' onSubmit={createVacancy}><h2>Cadastrar oportunidade</h2><label>Título da vaga<input value={jobTitle} onChange={event => setJobTitle(event.target.value)} required /></label><label>Descrição<textarea value={description} onChange={event => setDescription(event.target.value)} required /></label><label>Local ou modalidade<input value={location} onChange={event => setLocation(event.target.value)} placeholder='Presencial, híbrido ou remoto' required /></label><button className='primary' type='submit'>Cadastrar vaga</button></form> : <form className='form-card' onSubmit={apply}><h2>{mode === 'offer' ? 'Cadastre seu interesse' : 'Candidatar-se'}</h2>{mode === 'seek' && <label>Código da vaga<input value={vacancyId} onChange={event => setVacancyId(event.target.value)} placeholder='Selecione ou informe a vaga' required /></label>}<label>Apresentação<textarea value={note} onChange={event => setNote(event.target.value)} placeholder='Conte brevemente sua experiência e disponibilidade' required /></label><button className='primary' type='submit'>{mode === 'offer' ? 'Cadastrar para trabalhar' : 'Enviar candidatura'}</button></form>}
    {loading && <StateCard text='Sincronizando oportunidades...' />}
    {!loading && !filteredVacancies.length && <StateCard text='Nenhuma vaga encontrada para esta busca.' />}
    <ResourceSummary title='Oportunidades' items={filteredVacancies} />
    <ResourceSummary title='Minhas candidaturas e cadastros' items={applications} />
  </section>;
}

export function DeliveryView({ session, setNotice }: ViewProps) { return <ResourceJourney title='Entregas e rastreamento' subtitle='Coleta, andamento e ocorrências sincronizadas.' module='delivery' resource='delivery_requests' session={session} setNotice={setNotice} fields={[{key:'origin',label:'Origem'},{key:'destination',label:'Destino'},{key:'note',label:'Observação'}]} />; }
export function MobilityView({ session, setNotice }: ViewProps) { const [tab,setTab] = useState<'rides'|'tickets'>('rides'); return <section><SectionHeader title='Mobilidade' subtitle='Corridas, rotas, bilhetes e acompanhamento.' /><div className='segmented'><button type='button' className={tab === 'rides' ? 'active' : ''} onClick={() => setTab('rides')}>Corridas</button><button type='button' className={tab === 'tickets' ? 'active' : ''} onClick={() => setTab('tickets')}>Bilhetes</button></div><ResourceJourney embedded title={tab === 'rides' ? 'Solicitar corrida' : 'Meus bilhetes'} subtitle='' module='mobility' resource={tab} session={session} setNotice={setNotice} fields={tab === 'rides' ? [{key:'origin',label:'Origem'},{key:'destination',label:'Destino'},{key:'passengers',label:'Passageiros',type:'number'}] : [{key:'route',label:'Linha ou rota'},{key:'quantity',label:'Quantidade',type:'number'}]} /></section>; }
export function LifeView({ session, setNotice }: ViewProps) { const [tab,setTab] = useState<'health'|'document'>('health'); const configs = { health:{title:'Saúde e consultas',module:'health',resource:'appointments',fields:[{key:'specialty',label:'Especialidade'},{key:'scheduled_at',label:'Data e hora',type:'datetime-local'}]}, document:{title:'Documentos',module:'document',resource:'documents',fields:[{key:'title',label:'Título'},{key:'document_type',label:'Tipo'},{key:'description',label:'Descrição'}]} } as const; const config = configs[tab]; return <section><SectionHeader title='Saúde e documentos' subtitle='Jornadas pessoais protegidas pelo mesmo All-in-One ID.' /><div className='segmented'><button type='button' className={tab === 'health' ? 'active' : ''} onClick={() => setTab('health')}>Saúde</button><button type='button' className={tab === 'document' ? 'active' : ''} onClick={() => setTab('document')}>Documentos</button></div><ResourceJourney embedded title={config.title} subtitle='' module={config.module} resource={config.resource} session={session} setNotice={setNotice} fields={[...config.fields]} /></section>; }

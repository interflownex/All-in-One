import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import {
  errorMessage,
  itemSubtitle,
  itemTitle,
  request,
  type ApiItem,
  type JourneyHint,
  type ViewProps,
} from '../lib/api';
import { ResourceSummary, SectionHeader, StateCard } from '../ui';

type Field = { key: string; label: string; type?: string };

type ResourceJourneyProps = {
  title: string;
  subtitle: string;
  module: string;
  resource: string;
  session: ViewProps['session'];
  setNotice: ViewProps['setNotice'];
  fields: Field[];
  embedded?: boolean;
};

function ResourceJourney({
  title,
  subtitle,
  module,
  resource,
  session,
  setNotice,
  fields,
  embedded = false,
}: ResourceJourneyProps) {
  const [items, setItems] = useState<ApiItem[]>([]);
  const [values, setValues] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setItems(await request<ApiItem[]>(
        `/${module}/resources/${resource}`,
        'GET',
        undefined,
        session.accessToken,
      ) ?? []);
    } catch (err) {
      setNotice(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [module, resource, session.accessToken, setNotice]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void load(); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const create = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request(`/${module}/resources/${resource}`, 'POST', {
        user_id: session.userId,
        status: 'REQUESTED',
        payload: values,
      }, session.accessToken);
      setValues({});
      setNotice('Solicitação registrada no servidor.');
      await load();
    } catch (err) {
      setNotice(errorMessage(err));
    }
  };

  const filteredItems = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase('pt-BR');
    if (!normalized) return items;
    return items.filter(item => (
      `${itemTitle(item)} ${itemSubtitle(item)} ${JSON.stringify(item.payload ?? {})}`
        .toLocaleLowerCase('pt-BR')
        .includes(normalized)
    ));
  }, [items, query]);

  return <div className={embedded ? 'embedded-journey' : ''}>
    {!embedded && <SectionHeader
      title={title}
      subtitle={subtitle}
      actionLabel='Atualizar'
      onAction={load}
    />}
    {embedded && <div className='inline-heading'>
      <h2>{title}</h2>
      <button type='button' className='secondary' onClick={load}>Atualizar</button>
    </div>}
    <div className='search-panel single-search'>
      <label>Buscar nesta tela
        <input
          type='search'
          value={query}
          onChange={event => setQuery(event.target.value)}
          placeholder='Nome, tipo, local ou descrição'
        />
      </label>
    </div>
    <form className='form-card' onSubmit={create}>
      {fields.map(field => <label key={field.key}>{field.label}
        <input
          type={field.type ?? 'text'}
          value={values[field.key] ?? ''}
          onChange={event => setValues(current => ({
            ...current,
            [field.key]: event.target.value,
          }))}
          required
        />
      </label>)}
      <button className='primary' type='submit'>Enviar solicitação</button>
    </form>
    {loading && <StateCard text='Sincronizando...' />}
    {!loading && !filteredItems.length && <StateCard text='Nenhum registro encontrado para esta busca.' />}
    <ResourceSummary title='Registros' items={filteredItems} />
  </div>;
}

export function ServicesView({
  session,
  setNotice,
  hint,
}: ViewProps & { hint?: JourneyHint }) {
  const [providers, setProviders] = useState<ApiItem[]>([]);
  const [contracts, setContracts] = useState<ApiItem[]>([]);
  const [slots, setSlots] = useState<string[]>([]);
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [query, setQuery] = useState(hint?.query ?? '');

  const load = useCallback(async () => {
    try {
      const [providerData, contractData, slotData] = await Promise.all([
        request<ApiItem[]>('/services/resources/providers', 'GET', undefined, session.accessToken),
        request<ApiItem[]>('/services/resources/service_contracts', 'GET', undefined, session.accessToken),
        request<{ available_slots?: string[] }>(
          `/services/providers/mock-provider/time-slots?date=${date}`,
          'GET',
          undefined,
          session.accessToken,
        ),
      ]);
      setProviders(providerData ?? []);
      setContracts(contractData ?? []);
      setSlots(slotData.available_slots ?? []);
    } catch (err) {
      setNotice(errorMessage(err));
    }
  }, [date, session.accessToken, setNotice]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void load(); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const filterItems = useCallback((items: ApiItem[]) => {
    const normalized = query.trim().toLocaleLowerCase('pt-BR');
    if (!normalized) return items;
    return items.filter(item => (
      `${itemTitle(item)} ${itemSubtitle(item)} ${JSON.stringify(item.payload ?? {})}`
        .toLocaleLowerCase('pt-BR')
        .includes(normalized)
    ));
  }, [query]);

  const filteredProviders = useMemo(
    () => filterItems(providers),
    [filterItems, providers],
  );
  const filteredContracts = useMemo(
    () => filterItems(contracts),
    [contracts, filterItems],
  );

  const reserve = async (slot: string) => {
    try {
      await request('/services/providers/mock-provider/reserve-slot', 'POST', {
        slot,
        customer_id: session.userId,
      }, session.accessToken);
      setNotice(`Horário ${slot} reservado.`);
      await load();
    } catch (err) {
      setNotice(errorMessage(err));
    }
  };

  return <section>
    <SectionHeader
      title='Contratar serviços'
      subtitle='Encontre profissionais, horários e contratos conectados ao servidor.'
      actionLabel='Atualizar'
      onAction={load}
    />
    <div className='search-panel single-search'>
      <label>Buscar serviço ou profissional
        <input
          type='search'
          value={query}
          onChange={event => setQuery(event.target.value)}
          placeholder='Ex.: eletricista, cuidador, designer'
        />
      </label>
    </div>
    <div className='form-card'>
      <label>Data da agenda
        <input type='date' value={date} onChange={event => setDate(event.target.value)} />
      </label>
      <div className='slot-grid'>
        {slots.map(slot => <button
          type='button'
          key={slot}
          onClick={() => { void reserve(slot); }}
        >{slot}</button>)}
      </div>
      {!slots.length && <StateCard text='Nenhum horário disponível nesta data.' />}
    </div>
    <ResourceSummary title='Profissionais encontrados' items={filteredProviders} />
    <ResourceSummary title='Contratos encontrados' items={filteredContracts} />
    {!filteredProviders.length && !filteredContracts.length && (
      <StateCard text='Nenhum serviço encontrado para esta busca.' />
    )}
  </section>;
}

export function DeliveryView({ session, setNotice }: ViewProps) {
  return <ResourceJourney
    title='Entregas e rastreamento'
    subtitle='Coleta, andamento e ocorrências sincronizadas.'
    module='delivery'
    resource='delivery_requests'
    session={session}
    setNotice={setNotice}
    fields={[
      { key: 'origin', label: 'Origem' },
      { key: 'destination', label: 'Destino' },
      { key: 'note', label: 'Observação' },
    ]}
  />;
}

export function MobilityView({ session, setNotice }: ViewProps) {
  const [tab, setTab] = useState<'rides' | 'tickets'>('rides');
  return <section>
    <SectionHeader
      title='Mobilidade'
      subtitle='Corridas, rotas, bilhetes e acompanhamento.'
    />
    <div className='segmented'>
      <button type='button' className={tab === 'rides' ? 'active' : ''} onClick={() => setTab('rides')}>Corridas</button>
      <button type='button' className={tab === 'tickets' ? 'active' : ''} onClick={() => setTab('tickets')}>Bilhetes</button>
    </div>
    <ResourceJourney
      embedded
      title={tab === 'rides' ? 'Solicitar corrida' : 'Meus bilhetes'}
      subtitle=''
      module='mobility'
      resource={tab}
      session={session}
      setNotice={setNotice}
      fields={tab === 'rides'
        ? [
            { key: 'origin', label: 'Origem' },
            { key: 'destination', label: 'Destino' },
            { key: 'passengers', label: 'Passageiros', type: 'number' },
          ]
        : [
            { key: 'route', label: 'Linha ou rota' },
            { key: 'quantity', label: 'Quantidade', type: 'number' },
          ]}
    />
  </section>;
}

export function LifeView({ session, setNotice }: ViewProps) {
  const [tab, setTab] = useState<'health' | 'document'>('health');
  const config = tab === 'health'
    ? {
        title: 'Saúde e consultas',
        module: 'health',
        resource: 'appointments',
        fields: [
          { key: 'specialty', label: 'Especialidade' },
          { key: 'scheduled_at', label: 'Data e hora', type: 'datetime-local' },
        ],
      }
    : {
        title: 'Documentos',
        module: 'document',
        resource: 'documents',
        fields: [
          { key: 'title', label: 'Título' },
          { key: 'document_type', label: 'Tipo' },
          { key: 'description', label: 'Descrição' },
        ],
      };

  return <section>
    <SectionHeader
      title='Saúde e documentos'
      subtitle='Jornadas pessoais protegidas pelo mesmo All-in-One ID.'
    />
    <div className='segmented'>
      <button type='button' className={tab === 'health' ? 'active' : ''} onClick={() => setTab('health')}>Saúde</button>
      <button type='button' className={tab === 'document' ? 'active' : ''} onClick={() => setTab('document')}>Documentos</button>
    </div>
    <ResourceJourney
      embedded
      title={config.title}
      subtitle=''
      module={config.module}
      resource={config.resource}
      session={session}
      setNotice={setNotice}
      fields={config.fields}
    />
  </section>;
}

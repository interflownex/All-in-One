import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { errorMessage, itemSubtitle, itemTitle, request, type ApiItem, type JourneyHint, type ViewProps } from '../lib/api';
import { ResourceSummary, SectionHeader, StateCard } from '../ui';

type Config = {
  title: string;
  subtitle: string;
  module: 'legal' | 'health' | 'property';
  resource: string;
  searchLabel: string;
  searchPlaceholder: string;
  formTitle: string;
  fields: { key: string; label: string; type?: string; placeholder?: string }[];
};

function IntentModuleView({ session, setNotice, hint, config }: ViewProps & { hint?: JourneyHint; config: Config }) {
  const [items, setItems] = useState<ApiItem[]>([]);
  const [query, setQuery] = useState(hint?.query ?? '');
  const [values, setValues] = useState<Record<string,string>>({});
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true);
    try { setItems(await request<ApiItem[]>(`/${config.module}/resources/${config.resource}`, 'GET', undefined, session.accessToken) ?? []); }
    catch (error) { setNotice(errorMessage(error)); }
    finally { setLoading(false); }
  }, [config.module, config.resource, session.accessToken, setNotice]);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => { setQuery(hint?.query ?? ''); }, [hint?.query]);
  const filtered = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase('pt-BR');
    if (!normalized) return items;
    return items.filter(item => `${itemTitle(item)} ${itemSubtitle(item)} ${JSON.stringify(item.payload ?? {})}`.toLocaleLowerCase('pt-BR').includes(normalized));
  }, [items, query]);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request(`/${config.module}/resources/${config.resource}`, 'POST', { user_id: session.userId, status: 'REQUESTED', payload: { ...values, valley_intent: hint?.intent ?? null } }, session.accessToken);
      setValues({}); setNotice('Solicitação registrada.'); await load();
    } catch (error) { setNotice(errorMessage(error)); }
  };
  return <section>
    <SectionHeader title={config.title} subtitle={config.subtitle} actionLabel='Atualizar' onAction={load} />
    <div className='search-panel single-search'><label>{config.searchLabel}<input type='search' value={query} onChange={event => setQuery(event.target.value)} placeholder={config.searchPlaceholder} /></label></div>
    <form className='form-card' onSubmit={submit}><h2>{config.formTitle}</h2>{config.fields.map(field => <label key={field.key}>{field.label}<input type={field.type ?? 'text'} value={values[field.key] ?? ''} onChange={event => setValues(current => ({ ...current, [field.key]: event.target.value }))} placeholder={field.placeholder} required /></label>)}<button className='primary' type='submit'>Continuar</button></form>
    {loading && <StateCard text='Sincronizando...' />}{!loading && !filtered.length && <StateCard text='Nenhum resultado encontrado para esta busca.' />}
    <ResourceSummary title='Resultados' items={filtered} />
  </section>;
}

export function LegalIntentView(props: ViewProps & { hint?: JourneyHint }) {
  return <IntentModuleView {...props} config={{ title:'Atendimento jurídico', subtitle:'Encontre apoio jurídico sem precisar conhecer o nome do módulo.', module:'legal', resource:'cases', searchLabel:'Buscar especialidade ou assunto', searchPlaceholder:'Ex.: consumidor, família, contrato', formTitle:'Solicitar atendimento', fields:[{key:'subject',label:'Assunto'},{key:'description',label:'Descreva o que precisa'}] }} />;
}
export function HealthIntentView(props: ViewProps & { hint?: JourneyHint }) {
  return <IntentModuleView {...props} config={{ title:'Saúde', subtitle:'Busque atendimento, profissional ou consulta.', module:'health', resource:'appointments', searchLabel:'Buscar profissional ou especialidade', searchPlaceholder:'Ex.: clínica geral, pediatria, psicologia', formTitle:'Solicitar consulta', fields:[{key:'specialty',label:'Especialidade'},{key:'scheduled_at',label:'Data e hora',type:'datetime-local'}] }} />;
}
export function PropertyIntentView(props: ViewProps & { hint?: JourneyHint }) {
  return <IntentModuleView {...props} config={{ title:'Imóveis e propriedades', subtitle:'Encontre opções para alugar por região, tipo e faixa de valor.', module:'property', resource:'properties', searchLabel:'Buscar imóvel ou região', searchPlaceholder:'Ex.: apartamento em Betim, casa, sala comercial', formTitle:'Registrar interesse', fields:[{key:'property_type',label:'Tipo de imóvel'},{key:'region',label:'Região desejada'},{key:'max_rent_brl',label:'Valor máximo',type:'number'}] }} />;
}

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { demoRecordsFor } from '../lib/demoData';
import ModuleDashboard from './ModuleDashboard';

interface SmartCRUDProps {
  module: string;
  entity: string;
  type: 'list' | 'form';
  title: string;
}

const API_HUB_URL = (import.meta as any).env?.VITE_API_HUB_URL ?? '';
const API_HUB_TOKEN = (import.meta as any).env?.VITE_API_HUB_TOKEN ?? '';

const LIVE_RESOURCE_ALIASES: Record<string, string> = {
  'identity:identity': 'users',
  'delivery:deliveryrequests': 'delivery_requests',
  'jobs:jobpostings': 'job_postings',
};

const liveResourceFor = (module: string, entity: string) =>
  LIVE_RESOURCE_ALIASES[`${module}:${entity}`] ?? entity;

const apiHeaders = (): Record<string, string> => (API_HUB_TOKEN ? { Authorization: `Bearer ${API_HUB_TOKEN}` } : {});

const actorIdFromToken = () => {
  try {
    const payload = JSON.parse(atob(API_HUB_TOKEN.split('.')[1] ?? ''));
    return payload.sub ?? '';
  } catch {
    return '';
  }
};

const normalizeData = (result: unknown): any[] => {
  if (Array.isArray(result)) return result;
  if (result && typeof result === 'object' && Array.isArray((result as any).data)) {
    return (result as any).data;
  }
  return [];
};

const displayNameFor = (item: any, title: string) =>
  item.name ||
  item.title ||
  item.payload?.name ||
  item.payload?.full_name ||
  item.payload?.label ||
  item.payload?.title ||
  item.payload?.service_type ||
  item.payload?.store_id ||
  `${title} #${item.id}`;

const SmartCRUD: React.FC<SmartCRUDProps> = ({ module, entity, type, title }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const editingRecord = (location.state as { record?: any } | null)?.record;
  const [data, setData] = useState<any[]>(() => API_HUB_TOKEN ? [] : demoRecordsFor(module, entity, title));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [notifications, setNotifications] = useState<string[]>([]);
  const [postApplication, setPostApplication] = useState<any | null>(null);
  const [actionFeedback, setActionFeedback] = useState('');
  const [actionState, setActionState] = useState<'idle' | 'running' | 'completed' | 'failed'>('idle');
  const [formData, setFormData] = useState({
    name: editingRecord ? displayNameFor(editingRecord, title) : '',
    description: editingRecord?.description ?? '',
    category: editingRecord?.category ?? 'Padrao',
  });
  const [formState, setFormState] = useState<'idle' | 'saving' | 'saved' | 'failed'>('idle');
  const [formFeedback, setFormFeedback] = useState('');
  const [selectedMedia, setSelectedMedia] = useState<any | null>(null);

  const resourceType = liveResourceFor(module, entity);
  const liveResourcePath = `/${module}/resources/${resourceType}`;
  const localStorageKey = `all-in-one:${module}:${resourceType}`;
  const isLiveApiHub = Boolean(API_HUB_TOKEN);
  const isJobsVacancyJourney = module === 'jobs' && resourceType === 'job_postings';

  const liveCollectionEndpoint = () => {
    if (isJobsVacancyJourney) {
      const search = query ? `?q=${encodeURIComponent(query)}` : '';
      return `${API_HUB_URL}/jobs/vacancies${search}`;
    }
    return `${API_HUB_URL}${liveResourcePath}?limit=3`;
  };

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const endpoint = isLiveApiHub
        ? liveCollectionEndpoint()
        : `${API_HUB_URL}/gateway/${module}/${entity}?q=${query}`;
      const response = await fetch(endpoint, { headers: apiHeaders() });
      if (!response.ok) throw new Error('Falha ao carregar dados.');
      const result = await response.json();
      const items = normalizeData(result);
      setData(items);
      if (isLiveApiHub && isJobsVacancyJourney) {
        setNotifications([
          `${items.length} vaga publicada encontrada na busca viva Jobs.`,
          query ? `Busca aplicada: ${query}` : 'Busca pronta para filtrar vagas publicadas.',
          'Notificacao Jobs: acompanhe candidatura e proximos passos nesta tela.',
        ]);
      }
    } catch (err) {
      const storedRecords = localStorage.getItem(localStorageKey);
      const localRecords = storedRecords === null ? demoRecordsFor(module, entity, title) : JSON.parse(storedRecords);
      if (storedRecords === null) localStorage.setItem(localStorageKey, JSON.stringify(localRecords));
      setError(isLiveApiHub ? 'API Hub vivo indisponivel para esta lista.' : '');
      const filteredLocalRecords = localRecords.filter((record: any) => !query || displayNameFor(record, title).toLocaleLowerCase('pt-BR').includes(query.toLocaleLowerCase('pt-BR')));
      setData(filteredLocalRecords);
    } finally {
      setLoading(false);
    }
  };

  const transitionResource = async (resourceId: string, action: string, reason: string) => {
    const response = await fetch(`${API_HUB_URL}${liveResourcePath}/${resourceId}/actions/${action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...apiHeaders() },
      body: JSON.stringify({ reason }),
    });
    if (!response.ok) {
      throw new Error(`Acao ${action} retornou HTTP ${response.status}.`);
    }
    return response.json();
  };

  const createLiveResource = async (path: string, payload: Record<string, unknown>) => {
    const actorId = actorIdFromToken();
    if (!actorId) throw new Error('Token sem usuario autenticado para executar a jornada.');
    const response = await fetch(`${API_HUB_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...apiHeaders() },
      body: JSON.stringify({ user_id: actorId, payload }),
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => null);
      throw new Error(detail?.detail ? `Criacao retornou HTTP ${response.status}: ${detail.detail}` : `Criacao retornou HTTP ${response.status}.`);
    }
    return response.json();
  };

  const runJourneyAction = async () => {
    const resource = data[0];
    if (!resource?.id) return;

    setActionState('running');
    setActionFeedback('Executando acao real via API Hub...');
    try {
      if (module === 'marketplace' && resourceType === 'orders') {
        const response = await fetch(`${API_HUB_URL}/gateway/payments/sandbox/authorize`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...apiHeaders() },
          body: JSON.stringify({
            order_id: resource.id,
            idempotency_key: `user-shell-payment-${resource.id}`,
          }),
        });
        if (!response.ok) {
          const detail = await response.json().catch(() => null);
          throw new Error(
            detail?.detail
              ? `Pagamento sandbox retornou HTTP ${response.status}: ${detail.detail}`
              : `Pagamento sandbox retornou HTTP ${response.status}.`,
          );
        }
        const paid = await response.json();
        setData((items) =>
          items.map((item) => (item.id === resource.id ? { ...item, status: paid.status ?? 'paid' } : item)),
        );
        setActionFeedback('Jornada concluida: pedido paid via API Hub vivo.');
      } else if (module === 'delivery' && resourceType === 'delivery_requests') {
        await transitionResource(resource.id, 'assign', 'entregador atribuido pelo shell User');
        await transitionResource(resource.id, 'pickup', 'pedido coletado pelo shell User');
        const completed = await transitionResource(resource.id, 'complete', 'entrega concluida pelo shell User');
        setData((items) => items.map((item) => (item.id === completed.id ? completed : item)));
        setActionFeedback('Jornada concluida: entrega completed via API Hub vivo.');
      } else if (module === 'jobs' && resourceType === 'job_postings') {
        const resume = await createLiveResource('/jobs/resources/resumes', {
          headline: 'Curriculo Playwright candidato',
          recruiter_visibility: 'business_recruiters',
        });
        const application = await createLiveResource('/jobs/resources/applications', {
          job_posting_id: resource.id,
          resume_id: resume.id,
        });
        setData((items) =>
          items.map((item) =>
            item.id === resource.id ? { ...item, status: application.status ?? 'submitted' } : item,
          ),
        );
        setPostApplication({
          applicationId: application.id,
          resumeId: resume.id,
          jobTitle: displayNameFor(resource, title),
          status: application.status ?? 'submitted',
        });
        setNotifications([
          'Notificacao Jobs: candidatura enviada com sucesso.',
          `Status da candidatura: ${application.status ?? 'submitted'}.`,
          'Proximo passo: acompanhe retorno da empresa e mantenha seu curriculo visivel.',
        ]);
        setActionFeedback('Jornada concluida: candidatura submitted via API Hub vivo.');
      }
      setActionState('completed');
    } catch (err) {
      setActionState('failed');
      setActionFeedback(err instanceof Error ? err.message : 'Falha ao executar acao real.');
    }
  };

  const canRunJourneyAction =
    isLiveApiHub &&
    data.length > 0 &&
    ((module === 'marketplace' && resourceType === 'orders') ||
      (module === 'delivery' && resourceType === 'delivery_requests') ||
      (module === 'jobs' && resourceType === 'job_postings'));

  useEffect(() => {
    if (type === 'list') {
      fetchData();
    }
  }, [module, entity, type, query]);

  const saveForm = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormState('saving');
    setFormFeedback('Salvando registro...');
    const payload = { ...formData, status: 'Ativo', updated_at: new Date().toISOString(), image: `/assets/demo/modules/${module}.webp`, video: '/assets/demo/platform-overview.mp4' };
    try {
      if (API_HUB_URL && API_HUB_TOKEN) {
        const endpoint = editingRecord?.id
          ? `${API_HUB_URL}/${module}/resources/${resourceType}/${editingRecord.id}`
          : `${API_HUB_URL}/${module}/resources/${resourceType}`;
        const response = await fetch(endpoint, {
          method: editingRecord?.id ? 'PUT' : 'POST',
          headers: { 'Content-Type': 'application/json', ...apiHeaders() },
          body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error(`API Hub retornou HTTP ${response.status}.`);
      } else {
        const storedRecords = localStorage.getItem(localStorageKey);
        const current = storedRecords === null ? demoRecordsFor(module, entity, title) : JSON.parse(storedRecords);
        const record = { id: editingRecord?.id ?? crypto.randomUUID(), ...payload, created_at: editingRecord?.created_at ?? payload.updated_at };
        const next = editingRecord?.id
          ? current.map((item: any) => item.id === editingRecord.id ? record : item)
          : [...current, record];
        localStorage.setItem(localStorageKey, JSON.stringify(next));
      }
      setFormState('saved');
      setFormFeedback('Registro salvo com sucesso. Retornando para a lista...');
      window.setTimeout(() => navigate(`/${module}/${entity}`), 450);
    } catch (error) {
      setFormState('failed');
      setFormFeedback(error instanceof Error ? error.message : 'Nao foi possivel salvar o registro.');
    }
  };

  const deleteRecord = async (record: any) => {
    if (!window.confirm(`Excluir ${displayNameFor(record, title)}?`)) return;
    setActionFeedback('Excluindo registro...');
    try {
      if (API_HUB_URL && API_HUB_TOKEN && !String(record.id).match(/^[123]$/)) {
        const response = await fetch(`${API_HUB_URL}${liveResourcePath}/${record.id}`, {
          method: 'DELETE',
          headers: apiHeaders(),
        });
        if (!response.ok) throw new Error(`API Hub retornou HTTP ${response.status}.`);
      }
      const current = JSON.parse(localStorage.getItem(localStorageKey) ?? '[]');
      localStorage.setItem(localStorageKey, JSON.stringify(current.filter((item: any) => item.id !== record.id)));
      setData((items) => items.filter((item) => item.id !== record.id));
      setActionState('completed');
      setActionFeedback('Registro excluido com sucesso.');
    } catch (error) {
      setActionState('failed');
      setActionFeedback(error instanceof Error ? error.message : 'Nao foi possivel excluir o registro.');
    }
  };

  if (type === 'form') {
    return (
      <div className="container">
        <form className="neo-form neo-brutalism" onSubmit={saveForm}>
          <h2 style={{ marginBottom: '24px', color: '#236cff' }}>{title} - {editingRecord ? 'Editar Registro' : 'Novo Registro'}</h2>
          <div className="field-group" style={{ display: 'grid', gap: '8px', marginBottom: '16px' }}>
            <label htmlFor="record-name" style={{ fontWeight: 800 }}>Nome / Identificador</label>
            <input id="record-name" type="text" className="neo-input" placeholder="Digite aqui..." required value={formData.name} onChange={(event) => setFormData((current) => ({ ...current, name: event.target.value }))} style={{ padding: '12px', border: '2px solid #11142a' }} />
          </div>
          <div className="field-group" style={{ display: 'grid', gap: '8px', marginBottom: '16px' }}>
            <label htmlFor="record-description" style={{ fontWeight: 800 }}>Descrição Detalhada</label>
            <textarea id="record-description" className="neo-input" placeholder="Informacoes adicionais..." value={formData.description} onChange={(event) => setFormData((current) => ({ ...current, description: event.target.value }))} style={{ padding: '12px', border: '2px solid #11142a', minHeight: '100px' }}></textarea>
          </div>
          <div className="field-group" style={{ display: 'grid', gap: '8px', marginBottom: '24px' }}>
            <label htmlFor="record-category" style={{ fontWeight: 800 }}>Categoria / Tipo</label>
            <select id="record-category" className="neo-input" value={formData.category} onChange={(event) => setFormData((current) => ({ ...current, category: event.target.value }))} style={{ padding: '12px', border: '2px solid #11142a' }}>
              <option value="Padrao">Padrao</option>
              <option value="Prioritario">Prioritario</option>
              <option value="Estrategico">Estrategico</option>
            </select>
          </div>
          {formFeedback ? <p className={`action-feedback ${formState === 'failed' ? 'error' : 'success'}`} role="status">{formFeedback}</p> : null}
          <div className="actions-row" style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button type="button" className="btn-secondary" onClick={() => navigate(-1)} style={{ padding: '10px 20px' }}>Cancelar</button>
            <button type="submit" className="btn-primary" disabled={formState === 'saving'} style={{ padding: '10px 20px' }}>{formState === 'saving' ? 'Salvando...' : 'Salvar Registro'}</button>
          </div>
        </form>
      </div>
    );
  }

  if (entity === module) {
    return <ModuleDashboard module={module} title={title} records={data} />;
  }

  return (
    <div className="container" style={{ position: 'relative' }}>
      <div style={{ position: 'fixed', bottom: '24px', right: '24px', opacity: 0.5, pointerEvents: 'none', zIndex: 100 }}>
        <img src="/assets/brand/all-in-one-logo-official.png" alt="Branding" style={{ height: '24px', width: 'auto' }} />
      </div>
      <section className="hero">

        <h1 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '12px' }}>{title}</h1>
        <p style={{ color: '#626b8e', fontSize: '1.1rem' }}>Gerenciamento inteligente do módulo {module.toUpperCase()}.</p>
      </section>

      <div className="filters-section" style={{ background: '#fff', padding: '24px', border: '3px solid #11142a', boxShadow: '6px 6px 0px #11142a', marginBottom: '32px' }}>
        <div className="search-row search-row-crud">
          <input 
            type="text" 
            placeholder={`Buscar em ${title}...`} 
            value={query} 
            onChange={(e) => setQuery(e.target.value)} 
            style={{ padding: '12px', border: '2px solid #11142a', borderRadius: '4px' }}
          />
          <button className="btn-primary" onClick={fetchData} style={{ padding: '0 24px' }}>Pesquisar</button>
          <button type="button" className="btn-secondary" onClick={() => navigate(`/${module}/${entity}-form`)} style={{ padding: '0 24px' }}>Novo registro</button>
        </div>
      </div>

      {error ? (
        <div className="notice" role="status">
          {error}
        </div>
      ) : null}

      {canRunJourneyAction ? (
        <section className="action-panel neo-brutalism" aria-label="Acao de jornada User" style={{ background: '#fff', padding: '20px', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 900, marginBottom: '12px' }}>Acao real API Hub</h2>
          <button className="btn-primary" type="button" onClick={runJourneyAction} disabled={actionState === 'running'} style={{ padding: '10px 20px' }}>
            Concluir jornada User
          </button>
          {actionFeedback ? (
            <p className={`journey-feedback ${actionState}`} style={{ marginTop: '12px', fontWeight: 800 }}>
              {actionFeedback}
            </p>
          ) : null}
        </section>
      ) : null}

      {isLiveApiHub && isJobsVacancyJourney ? (
        <section
          className="jobs-notifications neo-brutalism"
          aria-label="Busca notificacoes e pos-candidatura Jobs"
          style={{ background: '#fffdf3', padding: '20px', marginBottom: '24px' }}
        >
          <h2 style={{ fontSize: '1.25rem', fontWeight: 900, marginBottom: '12px' }}>Busca e notificacoes Jobs</h2>
          <ul style={{ margin: 0, paddingLeft: '20px', display: 'grid', gap: '8px' }}>
            {notifications.length > 0 ? notifications.map((message) => (
              <li key={message}>{message}</li>
            )) : (
              <li>Notificacao Jobs: use a busca para encontrar vagas publicadas.</li>
            )}
          </ul>
          {postApplication ? (
            <div className="post-application-card" style={{ marginTop: '16px', padding: '16px', border: '2px solid #11142a' }}>
              <h3 style={{ margin: 0, fontWeight: 900 }}>Pos-candidatura Jobs</h3>
              <p style={{ margin: '8px 0 0' }}>Vaga: {postApplication.jobTitle}</p>
              <p style={{ margin: '4px 0 0' }}>Status: {postApplication.status}</p>
              <p style={{ margin: '4px 0 0' }}>Candidatura: {postApplication.applicationId}</p>
              <p style={{ margin: '4px 0 0' }}>Curriculo: {postApplication.resumeId}</p>
            </div>
          ) : null}
        </section>
      ) : null}

      {loading ? (
        <div className="loader"></div>
      ) : (
        <div className="data-grid" style={{ display: 'grid', gap: '16px' }}>
          {data.length > 0 ? data.map((item: any) => (
            <div key={item.id} className="data-card neo-brutalism">
              {item.image ? <img className="data-card-media" src={item.image} alt="" loading="lazy" /> : null}
              <div className="data-card-copy">
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{displayNameFor(item, title)}</h3>
                <p style={{ fontSize: '0.9rem', color: '#626b8e' }}>ID: {item.id} | Criado em: {new Date(item.created_at).toLocaleDateString()}</p>
                {item.description ? <p className="data-card-description">{item.description}</p> : null}
              </div>
              <div className="data-card-actions">
                <span className="badge" style={{ background: item.status === 'Ativo' ? '#eef1ff' : '#fef3c7', color: item.status === 'Ativo' ? '#1a6fb3' : '#92400e', padding: '6px 12px', borderRadius: '4px', fontWeight: 700 }}>
                  {item.status || 'Disponível'}
                </span>
                <button type="button" className="btn-secondary" onClick={() => setSelectedMedia(item)} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Ver detalhes</button>
                <button type="button" className="btn-secondary" onClick={() => navigate(`/${module}/${entity}-form`, { state: { record: item } })} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Editar</button>
                <button type="button" className="btn-secondary danger" onClick={() => deleteRecord(item)} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Excluir</button>
              </div>
            </div>
          )) : (
            <div className="empty-state" style={{ textAlign: 'center', padding: '48px', border: '2px dashed #b8c5be' }}>
              <p>Nenhum registro encontrado para esta busca.</p>
            </div>
          )}
        </div>
      )}
      {selectedMedia ? (
        <div className="modal-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelectedMedia(null); }}>
          <section className="modal-content media-detail-modal" role="dialog" aria-modal="true" aria-labelledby="media-detail-title">
            <div className="modal-header"><h2 id="media-detail-title">{displayNameFor(selectedMedia, title)}</h2><button type="button" className="close-btn" aria-label="Fechar detalhes" onClick={() => setSelectedMedia(null)}>×</button></div>
            <div className="modal-body">
              {selectedMedia.video ? <video className="detail-video" src={selectedMedia.video} poster={selectedMedia.image} controls autoPlay muted loop /> : <img className="detail-image" src={selectedMedia.image} alt={displayNameFor(selectedMedia, title)} />}
              <p>{selectedMedia.description}</p>
              <dl className="detail-metadata"><div><dt>Status</dt><dd>{selectedMedia.status}</dd></div><div><dt>Regiao</dt><dd>{selectedMedia.region ?? 'Brasil'}</dd></div><div><dt>Categoria</dt><dd>{selectedMedia.category ?? 'Padrao'}</dd></div></dl>
            </div>
          </section>
        </div>
      ) : null}
    </div>
  );
};

export default SmartCRUD;

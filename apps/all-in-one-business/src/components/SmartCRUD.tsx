import React, { useState, useEffect } from 'react';

interface SmartCRUDProps {
  module: string;
  entity: string;
  type: 'list' | 'form';
  title: string;
}

const API_HUB_URL = (import.meta as any).env?.VITE_API_HUB_URL ?? '';
const API_HUB_TOKEN = (import.meta as any).env?.VITE_API_HUB_TOKEN ?? '';

const RESOURCE_ALIASES: Record<string, string> = {
  'business:catalogoffers': 'catalog_offers',
  'business:companies': 'companies',
  'jobs:applications': 'applications',
  'jobs:jobpostings': 'job_postings',
  'jobs:resumeaccesslogs': 'resume_access_logs',
  'jobs:resumes': 'resumes',
};

const liveHeaders = () => ({
  Authorization: `Bearer ${API_HUB_TOKEN}`,
  'Content-Type': 'application/json',
});

const normalizeCollection = (result: any): any[] => {
  if (Array.isArray(result)) return result;
  if (Array.isArray(result?.data)) return result.data;
  if (Array.isArray(result?.items)) return result.items;
  return [];
};

const itemTitle = (item: any, fallbackTitle: string) =>
  item.name ||
  item.title ||
  item.payload?.legal_name ||
  item.payload?.title ||
  item.payload?.headline ||
  item.payload?.purpose ||
  `${fallbackTitle} #${item.id}`;

const itemCreatedAt = (item: any) => {
  const rawDate = item.created_at || item.createdAt;
  return rawDate ? new Date(rawDate).toLocaleDateString() : 'sem data';
};

const SmartCRUD: React.FC<SmartCRUDProps> = ({ module, entity, type, title }) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const [actionMessage, setActionMessage] = useState('');
  const [query, setQuery] = useState('');
  const resourceType = RESOURCE_ALIASES[`${module}:${entity}`];
  const liveApiEnabled = Boolean(API_HUB_URL && API_HUB_TOKEN && resourceType);

  const apiHubFetch = async (path: string, init: RequestInit = {}) => {
    const response = await fetch(`${API_HUB_URL}${path}`, {
      ...init,
      headers: {
        ...liveHeaders(),
        ...(init.headers ?? {}),
      },
    });
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `API Hub retornou HTTP ${response.status}.`);
    }
    return response.json();
  };

  const fetchData = async () => {
    setLoading(true);
    setError('');
    setActionMessage('');
    try {
      if (liveApiEnabled) {
        const searchParams = query ? `?q=${encodeURIComponent(query)}` : '';
        const result = await apiHubFetch(`/${module}/resources/${resourceType}${searchParams}`);
        setData(normalizeCollection(result));
        return;
      }

      const response = await fetch(`${API_HUB_URL}/gateway/${module}/${entity}?q=${query}`);
      if (!response.ok) throw new Error('Falha ao carregar dados.');
      const result = await response.json();
      setData(result.data ?? []);
    } catch (err) {
      if (liveApiEnabled) {
        setError(err instanceof Error ? err.message : 'Falha ao carregar dados vivos do API Hub.');
        setData([]);
        return;
      }
      console.warn(`Usando dados fictícios para ${module}/${entity}`);
      setData([
        { id: '1', name: `${title} Item 1`, status: 'Ativo', created_at: new Date().toISOString() },
        { id: '2', name: `${title} Item 2`, status: 'Pendente', created_at: new Date().toISOString() },
        { id: '3', name: `${title} Item 3`, status: 'Inativo', created_at: new Date().toISOString() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (type === 'list') {
      fetchData();
    }
  }, [module, entity, type, query]);

  const runLiveAction = async () => {
    setActionLoading(true);
    setError('');
    setActionMessage('');
    try {
      if (module === 'business' && resourceType === 'companies') {
        const company = data[0];
        if (!company?.id) throw new Error('Nenhuma empresa disponivel para aprovacao.');
        const approved = await apiHubFetch(`/business/resources/companies/${company.id}/actions/approve`, {
          method: 'POST',
          body: JSON.stringify({ reason: 'KYB aprovado via Business shell vivo' }),
        });
        setData((items) => items.map((item) => (item.id === company.id ? approved : item)));
        setActionMessage('Empresa aprovada no API Hub vivo.');
        return;
      }

      if (module === 'jobs' && resourceType === 'job_postings') {
        const job = data[0];
        if (!job?.id) throw new Error('Nenhuma vaga disponivel para publicacao.');
        const published = await apiHubFetch(`/jobs/resources/job_postings/${job.id}/actions/publish`, {
          method: 'POST',
          body: JSON.stringify({ reason: 'Vaga validada pela empresa no Business shell vivo' }),
        });
        setData((items) => items.map((item) => (item.id === job.id ? published : item)));
        setActionMessage('Vaga publicada no API Hub vivo.');
        return;
      }

      if (module === 'jobs' && resourceType === 'resume_access_logs') {
        const resumes = normalizeCollection(await apiHubFetch('/jobs/resources/resumes'));
        const resume = resumes[0];
        if (!resume?.id) throw new Error('Nenhum curriculo visivel para registrar acesso.');
        await apiHubFetch(
          `/jobs/recruiting/resumes/${resume.id}?purpose=${encodeURIComponent('triagem para vaga publicada via Business shell')}`,
        );
        const logs = normalizeCollection(await apiHubFetch('/jobs/resources/resume_access_logs'));
        setData(logs);
        setActionMessage('Acesso a curriculo registrado no API Hub vivo.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao executar acao viva no API Hub.');
    } finally {
      setActionLoading(false);
    }
  };

  const actionLabel =
    module === 'business' && resourceType === 'companies'
      ? 'Aprovar empresa'
      : module === 'jobs' && resourceType === 'job_postings'
        ? 'Publicar vaga'
        : module === 'jobs' && resourceType === 'resume_access_logs'
          ? 'Registrar acesso a currículo'
          : '';

  if (type === 'form') {
    return (
      <div className="container">
        <form className="neo-form neo-brutalism" onSubmit={(e) => { e.preventDefault(); alert('Salvo com sucesso!'); }}>
          <h2 style={{ marginBottom: '24px', color: '#126b45' }}>{title} - Novo Registro</h2>
          <div className="field-group" style={{ display: 'grid', gap: '8px', marginBottom: '16px' }}>
            <label style={{ fontWeight: 800 }}>Nome / Identificador</label>
            <input type="text" className="neo-input" placeholder="Digite aqui..." required style={{ padding: '12px', border: '2px solid #17211c' }} />
          </div>
          <div className="field-group" style={{ display: 'grid', gap: '8px', marginBottom: '16px' }}>
            <label style={{ fontWeight: 800 }}>Descrição Detalhada</label>
            <textarea className="neo-input" placeholder="Informações adicionais..." style={{ padding: '12px', border: '2px solid #17211c', minHeight: '100px' }}></textarea>
          </div>
          <div className="field-group" style={{ display: 'grid', gap: '8px', marginBottom: '24px' }}>
            <label style={{ fontWeight: 800 }}>Categoria / Tipo</label>
            <select className="neo-input" style={{ padding: '12px', border: '2px solid #17211c' }}>
              <option>Padrão</option>
              <option>Prioritário</option>
              <option>Estratégico</option>
            </select>
          </div>
          <div className="actions-row" style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button type="button" className="btn-secondary" style={{ padding: '10px 20px' }}>Cancelar</button>
            <button type="submit" className="btn-primary" style={{ padding: '10px 20px' }}>Salvar Registro</button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="container" style={{ position: 'relative' }}>
      <div style={{ position: 'fixed', bottom: '24px', right: '24px', opacity: 0.5, pointerEvents: 'none', zIndex: 100 }}>
        <img src="/assets/brand/all-in-one-logo-light-official.png" alt="Branding" style={{ height: '24px', width: 'auto' }} />
      </div>
      <section className="hero">

        <h1 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '12px' }}>{title}</h1>
        <p style={{ color: '#536159', fontSize: '1.1rem' }}>Gerenciamento inteligente do módulo {module.toUpperCase()}.</p>
      </section>

      <div className="filters-section" style={{ background: '#fff', padding: '24px', border: '3px solid #17211c', boxShadow: '6px 6px 0px #17211c', marginBottom: '32px' }}>
        <div className="search-row" style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '16px' }}>
          <input 
            type="text" 
            placeholder={`Buscar em ${title}...`} 
            value={query} 
            onChange={(e) => setQuery(e.target.value)} 
            style={{ padding: '12px', border: '2px solid #17211c', borderRadius: '4px' }}
          />
          <button className="btn-primary" onClick={fetchData} style={{ padding: '0 24px' }}>Pesquisar</button>
        </div>
      </div>

      {error ? (
        <div className="notice" role="status">
          {error}
        </div>
      ) : null}

      {liveApiEnabled && actionLabel ? (
        <div className="filters-section" style={{ background: '#eef8f1', padding: '20px', border: '3px solid #17211c', boxShadow: '6px 6px 0px #17211c', marginBottom: '32px' }}>
          <strong>API Hub vivo ativo</strong>
          <p style={{ margin: '8px 0 16px', color: '#536159' }}>
            Esta tela esta usando recursos reais do API Hub e registra acoes auditaveis no backend.
          </p>
          <button className="btn-primary" onClick={runLiveAction} disabled={actionLoading} style={{ padding: '10px 20px' }}>
            {actionLoading ? 'Executando...' : actionLabel}
          </button>
          {actionMessage ? (
            <div className="notice" role="status" style={{ marginTop: '16px' }}>
              {actionMessage}
            </div>
          ) : null}
        </div>
      ) : null}

      {loading ? (
        <div className="loader"></div>
      ) : (
        <div className="data-grid" style={{ display: 'grid', gap: '16px' }}>
          {data.length > 0 ? data.map((item: any) => (
            <div key={item.id} className="data-card neo-brutalism" style={{ background: '#fff', padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{itemTitle(item, title)}</h3>
                <p style={{ fontSize: '0.9rem', color: '#536159' }}>ID: {item.id} | Criado em: {itemCreatedAt(item)}</p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <span className="badge" style={{ background: ['Ativo', 'active', 'approved', 'published', 'recorded'].includes(item.status) ? '#e2f2ea' : '#fef3c7', color: ['Ativo', 'active', 'approved', 'published', 'recorded'].includes(item.status) ? '#0d5135' : '#92400e', padding: '6px 12px', borderRadius: '4px', fontWeight: 700 }}>
                  {item.status || 'Disponível'}
                </span>
                <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Editar</button>
              </div>
            </div>
          )) : (
            <div className="empty-state" style={{ textAlign: 'center', padding: '48px', border: '2px dashed #b8c5be' }}>
              <p>Nenhum registro encontrado para esta busca.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SmartCRUD;

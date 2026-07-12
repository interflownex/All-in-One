import React, { useState, useEffect } from 'react';

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

const apiHeaders = () => (API_HUB_TOKEN ? { Authorization: `Bearer ${API_HUB_TOKEN}` } : {});

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
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [actionFeedback, setActionFeedback] = useState('');
  const [actionState, setActionState] = useState<'idle' | 'running' | 'completed' | 'failed'>('idle');

  const resourceType = liveResourceFor(module, entity);
  const liveResourcePath = `/${module}/resources/${resourceType}`;
  const isLiveApiHub = Boolean(API_HUB_TOKEN);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const endpoint = isLiveApiHub
        ? `${API_HUB_URL}${liveResourcePath}?limit=3`
        : `${API_HUB_URL}/gateway/${module}/${entity}?q=${query}`;
      const response = await fetch(endpoint, { headers: apiHeaders() });
      if (!response.ok) throw new Error('Falha ao carregar dados.');
      const result = await response.json();
      setData(normalizeData(result));
    } catch (err) {
      // Fallback para dados fictícios se a API falhar (para demonstração)
      console.warn(`Usando dados fictícios para ${module}/${entity}`);
      setError(isLiveApiHub ? 'API Hub vivo indisponivel para esta lista.' : '');
      setData([
        { id: '1', name: `${title} Item 1`, status: 'Ativo', created_at: new Date().toISOString() },
        { id: '2', name: `${title} Item 2`, status: 'Pendente', created_at: new Date().toISOString() },
        { id: '3', name: `${title} Item 3`, status: 'Inativo', created_at: new Date().toISOString() },
      ]);
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
      (module === 'delivery' && resourceType === 'delivery_requests'));

  useEffect(() => {
    if (type === 'list') {
      fetchData();
    }
  }, [module, entity, type, query]);

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
        <img src="/assets/brand/all-in-one-logo-official.png" alt="Branding" style={{ height: '24px', width: 'auto' }} />
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

      {loading ? (
        <div className="loader"></div>
      ) : (
        <div className="data-grid" style={{ display: 'grid', gap: '16px' }}>
          {data.length > 0 ? data.map((item: any) => (
            <div key={item.id} className="data-card neo-brutalism" style={{ background: '#fff', padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{displayNameFor(item, title)}</h3>
                <p style={{ fontSize: '0.9rem', color: '#536159' }}>ID: {item.id} | Criado em: {new Date(item.created_at).toLocaleDateString()}</p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <span className="badge" style={{ background: item.status === 'Ativo' ? '#e2f2ea' : '#fef3c7', color: item.status === 'Ativo' ? '#0d5135' : '#92400e', padding: '6px 12px', borderRadius: '4px', fontWeight: 700 }}>
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

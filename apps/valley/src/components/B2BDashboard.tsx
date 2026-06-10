import { useEffect, useState } from 'react';
import CalendarWidget from './CalendarWidget';
import OfferWizard from './OfferWizard';
import PepitaWidget from './PepitaWidget';

interface CommercialMetrics {
  orders_total: number
  orders_paid: number
  orders_completed: number
  reviews_total: number
  average_rating: number | null
  support_cases_total: number
  support_cases_open: number
  support_cases_resolved: number
  conversion_rate_percent: number
  crm_records: number
  bi_records: number
}

export default function B2BDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'calendar'>('overview');
  const [showWizard, setShowWizard] = useState(false);
  const [metrics, setMetrics] = useState<CommercialMetrics>({
    orders_total: 0,
    orders_paid: 0,
    orders_completed: 0,
    reviews_total: 0,
    average_rating: null,
    support_cases_total: 0,
    support_cases_open: 0,
    support_cases_resolved: 0,
    conversion_rate_percent: 0,
    crm_records: 0,
    bi_records: 0,
  });
  const [metricsError, setMetricsError] = useState('');

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_HUB_URL ?? ''}/gateway/insights/commercial`)
      .then(async res => {
        if (!res.ok) throw new Error(`Falha HTTP ${res.status}`)
        return res.json()
      })
      .then(data => {
        setMetrics({
          orders_total: data.orders_total ?? 0,
          orders_paid: data.orders_paid ?? 0,
          orders_completed: data.orders_completed ?? 0,
          reviews_total: data.reviews_total ?? 0,
          average_rating: data.average_rating ?? null,
          support_cases_total: data.support_cases_total ?? 0,
          support_cases_open: data.support_cases_open ?? 0,
          support_cases_resolved: data.support_cases_resolved ?? 0,
          conversion_rate_percent: data.conversion_rate_percent ?? 0,
          crm_records: data.crm_records ?? 0,
          bi_records: data.bi_records ?? 0,
        })
      })
      .catch(() => {
        setMetricsError('Indicadores comerciais indisponiveis no momento.')
      })
  }, [])

  return (
    <div className="b2b-dashboard" style={{ padding: '2rem', background: '#f8fafc', minHeight: '100vh' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', color: '#0f172a' }}>Painel do Lojista (B2B)</h1>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button 
            style={{ padding: '0.5rem 1rem', background: activeTab === 'overview' ? '#3b82f6' : '#e2e8f0', color: activeTab === 'overview' ? 'white' : '#0f172a', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            onClick={() => setActiveTab('overview')}
          >
            Visão Geral
          </button>
          <button 
            style={{ padding: '0.5rem 1rem', background: activeTab === 'calendar' ? '#3b82f6' : '#e2e8f0', color: activeTab === 'calendar' ? 'white' : '#0f172a', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            onClick={() => setActiveTab('calendar')}
          >
            Agenda
          </button>
          <button 
            style={{ padding: '0.5rem 1rem', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => setShowWizard(true)}
          >
            + Publicar Oferta
          </button>
        </div>
      </header>

      {activeTab === 'overview' && (
        <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3 style={{ color: '#64748b', fontSize: '0.875rem', textTransform: 'uppercase' }}>Pedidos e Conversao</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0f172a', margin: '0.5rem 0' }}>{metrics.orders_completed}</p>
            <span style={{ color: '#10b981', fontSize: '0.875rem' }}>{metrics.conversion_rate_percent.toFixed(2)}% de conversao</span>
          </div>
          
          <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3 style={{ color: '#64748b', fontSize: '0.875rem', textTransform: 'uppercase' }}>Suporte e Disputas</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0f172a', margin: '0.5rem 0' }}>{metrics.support_cases_total}</p>
            <span style={{ color: '#f59e0b', fontSize: '0.875rem' }}>{metrics.support_cases_open} em aberto</span>
          </div>

          <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3 style={{ color: '#64748b', fontSize: '0.875rem', textTransform: 'uppercase' }}>Avaliacoes</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0f172a', margin: '0.5rem 0' }}>{metrics.reviews_total}</p>
            <span style={{ color: '#3b82f6', fontSize: '0.875rem', cursor: 'pointer' }}>
              Media {metrics.average_rating ? metrics.average_rating.toFixed(2) : 'sem nota'}
            </span>
          </div>

          <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3 style={{ color: '#64748b', fontSize: '0.875rem', textTransform: 'uppercase' }}>CRM e BI</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0f172a', margin: '0.5rem 0' }}>{metrics.crm_records + metrics.bi_records}</p>
            <span style={{ color: '#0f172a', fontSize: '0.875rem' }}>{metrics.crm_records} CRM | {metrics.bi_records} BI</span>
          </div>

          <PepitaWidget onSelect={(amount) => console.log(`Recompensa selecionada: ${amount} Pepitas`)} />
        </div>
      )}

      {metricsError && activeTab === 'overview' && (
        <p style={{ marginTop: '1rem', color: '#b45309' }}>{metricsError}</p>
      )}

      {activeTab === 'calendar' && (
        <CalendarWidget />
      )}

      {showWizard && <OfferWizard onClose={() => setShowWizard(false)} />}
    </div>
  );
}

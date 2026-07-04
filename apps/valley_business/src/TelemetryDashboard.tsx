import { useCallback, useEffect, useState } from 'react'

interface TelemetryMetrics {
  status: string;
  pending: number;
  due: number;
  published: number;
  failed_retryable: number;
  max_retry_count: number;
  oldest_pending_age_seconds: number;
  error?: string;
}

const DEFAULT_API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? 'http://127.0.0.1:8100'

type TelemetryDashboardProps = {
  baseUrl?: string
}

export function TelemetryDashboard({ baseUrl = DEFAULT_API_HUB_URL }: TelemetryDashboardProps) {
  const [metrics, setMetrics] = useState<TelemetryMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true)

      const res = await fetch(`${baseUrl}/gateway/telemetry/outbox`)
      if (!res.ok) {
        throw new Error(`Erro HTTP: ${res.status}`)
      }
      const data = await res.json()
      setMetrics(data)
      setError(null)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }, [baseUrl])

  useEffect(() => {
    const initialFetch = setTimeout(fetchMetrics, 0)
    const interval = setInterval(fetchMetrics, 5000)
    return () => {
      clearTimeout(initialFetch)
      clearInterval(interval)
    }
  }, [fetchMetrics])

  return (
    <div className="glass-card" style={{ gridColumn: '1 / -1' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <h3 className="card-title" style={{ margin: 0 }}>Monitoramento de Eventos (Outbox)</h3>
          <p style={{ margin: '0.35rem 0 0', color: 'var(--text-muted)' }}>
            Fonte: {baseUrl}/gateway/telemetry/outbox
          </p>
        </div>
        <button className="btn-primary" style={{ width: 'auto', marginTop: 0 }} onClick={fetchMetrics} disabled={loading}>
          {loading ? 'Atualizando...' : 'Atualizar Agora'}
        </button>
      </div>

      {error && (
        <div style={{ background: 'rgba(231, 76, 60, 0.15)', color: '#e74c3c', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
          <strong>Erro de Conexão:</strong> {error}
        </div>
      )}

      {metrics && metrics.status === 'unhealthy' && (
        <div style={{ background: 'rgba(231, 76, 60, 0.15)', color: '#e74c3c', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
          <strong>Status Indisponível:</strong> {metrics.error}
        </div>
      )}

      <div className="grid-container" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
          <h4 style={{ color: 'var(--text-muted)', margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>Fila Pendente</h4>
          <p style={{ fontSize: '2rem', margin: 0, fontWeight: 600, color: metrics?.pending ? '#f1c40f' : 'white' }}>
            {metrics?.pending ?? '-'}
          </p>
        </div>

        <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
          <h4 style={{ color: 'var(--text-muted)', margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>Eventos Vencidos (Due)</h4>
          <p style={{ fontSize: '2rem', margin: 0, fontWeight: 600, color: metrics?.due ? '#e74c3c' : 'white' }}>
            {metrics?.due ?? '-'}
          </p>
        </div>

        <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
          <h4 style={{ color: 'var(--text-muted)', margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>Publicados com Sucesso</h4>
          <p style={{ fontSize: '2rem', margin: 0, fontWeight: 600, color: '#2ecc71' }}>
            {metrics?.published ?? '-'}
          </p>
        </div>

        <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
          <h4 style={{ color: 'var(--text-muted)', margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>Falhas (Em Retry)</h4>
          <p style={{ fontSize: '2rem', margin: 0, fontWeight: 600, color: metrics?.failed_retryable ? '#e67e22' : 'white' }}>
            {metrics?.failed_retryable ?? '-'}
          </p>
        </div>

        <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
          <h4 style={{ color: 'var(--text-muted)', margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>Max Retry Count</h4>
          <p style={{ fontSize: '2rem', margin: 0, fontWeight: 600 }}>
            {metrics?.max_retry_count ?? '-'}
          </p>
        </div>

        <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
          <h4 style={{ color: 'var(--text-muted)', margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>Idade do Mais Antigo</h4>
          <p style={{ fontSize: '2rem', margin: 0, fontWeight: 600 }}>
            {metrics?.oldest_pending_age_seconds !== undefined ? `${metrics.oldest_pending_age_seconds.toFixed(1)}s` : '-'}
          </p>
        </div>
      </div>
    </div>
  )
}

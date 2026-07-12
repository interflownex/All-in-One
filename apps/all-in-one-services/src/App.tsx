import { useEffect, useState } from 'react'

const stages = [
  'Prestador aprovado',
  'Visita agendada',
  'Orcamento revisado',
  'Contrato e escrow',
  'Evidencia entregue',
]

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? ''
const API_HUB_TOKEN = import.meta.env.VITE_API_HUB_TOKEN ?? ''

const endpoints = [
  { label: 'Prestadores', path: '/services/resources/providers', fallback: '4 prestadores elegiveis' },
  { label: 'Contratos', path: '/services/resources/service_contracts', fallback: '2 contratos em andamento' },
  { label: 'Escrows', path: '/finance/resources/escrows', fallback: '1 escrow simulado' },
  { label: 'Evidencias', path: '/document/resources/documents', fallback: '3 evidencias previstas' },
]

type ApiCard = {
  label: string
  path: string
  status: 'online' | 'fallback'
  summary: string
}

async function fetchEndpoint(path: string) {
  if (!API_HUB_URL) throw new Error('VITE_API_HUB_URL ausente')
  const response = await fetch(`${API_HUB_URL}${path}?limit=3`, {
    headers: API_HUB_TOKEN ? { Authorization: `Bearer ${API_HUB_TOKEN}` } : {},
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  const payload = await response.json()
  if (Array.isArray(payload)) return payload
  return Array.isArray(payload?.data) ? payload.data : []
}

function App() {
  const [cards, setCards] = useState<ApiCard[]>(
    endpoints.map(endpoint => ({
      label: endpoint.label,
      path: endpoint.path,
      status: 'fallback',
      summary: endpoint.fallback,
    })),
  )

  useEffect(() => {
    let active = true
    Promise.all(
      endpoints.map(async endpoint => {
        try {
          const data = await fetchEndpoint(endpoint.path)
          return {
            label: endpoint.label,
            path: endpoint.path,
            status: 'online' as const,
            summary: `${data.length} registro(s) retornado(s) pelo API Hub`,
          }
        } catch {
          return {
            label: endpoint.label,
            path: endpoint.path,
            status: 'fallback' as const,
            summary: endpoint.fallback,
          }
        }
      }),
    ).then(nextCards => {
      if (active) setCards(nextCards)
    })
    return () => {
      active = false
    }
  }, [])

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">All-in-One Services</p>
        <h1>Servicos com visita, contrato, escrow e evidencia em uma linha clara.</h1>
        <p>
          Shell dedicado para prestadores e operadores acompanharem a jornada de
          ponta a ponta antes da expansao Playwright.
        </p>
      </section>

      <section className="timeline" aria-label="Jornada prioritaria">
        {stages.map((stage, index) => (
          <article key={stage}>
            <strong>{String(index + 1).padStart(2, '0')}</strong>
            <span>{stage}</span>
          </article>
        ))}
      </section>

      <section className="panel">
        <h2>Conexao API Hub</h2>
        <div className="api-grid">
          {cards.map(card => (
            <article className="api-card" key={card.path}>
              <strong>{card.label}</strong>
              <code>{card.path}</code>
              <span className={card.status}>{card.status === 'online' ? 'online' : 'fallback'}</span>
              <p>{card.summary}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}

export default App

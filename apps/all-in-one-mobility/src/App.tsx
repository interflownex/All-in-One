import { useEffect, useState } from 'react'

const cards = [
  ['Corrida', 'Solicitacao, aceite e conclusao com status operacional.'],
  ['Ticket', 'Compra e historico de bilhetes vinculados ao usuario.'],
  ['QR/NFC', 'Validacao local para preparar a integracao fisica real.'],
  ['Historico', 'Linha do tempo para suporte e auditoria da jornada.'],
]

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? ''

const endpoints = [
  { label: 'Corridas', path: '/mobility/resources/rides', fallback: '2 corridas em simulacao' },
  { label: 'Tickets', path: '/mobility/resources/tickets', fallback: '4 tickets emitidos' },
  { label: 'Riders', path: '/riders/resources/rider_profiles', fallback: '3 riders elegiveis' },
  { label: 'Wallets', path: '/finance/resources/wallets', fallback: '1 wallet vinculada' },
]

type ApiCard = {
  label: string
  path: string
  status: 'online' | 'fallback'
  summary: string
}

async function fetchEndpoint(path: string) {
  if (!API_HUB_URL) throw new Error('VITE_API_HUB_URL ausente')
  const response = await fetch(`${API_HUB_URL}${path}?limit=3`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  const payload = await response.json()
  return Array.isArray(payload?.data) ? payload.data : []
}

function App() {
  const [apiCards, setApiCards] = useState<ApiCard[]>(
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
      if (active) setApiCards(nextCards)
    })
    return () => {
      active = false
    }
  }, [])

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">All-in-One Mobility</p>
        <h1>Corridas, tickets e validacao QR/NFC prontos para virar E2E.</h1>
        <p>
          Shell dedicado para passageiros e operadores acompanharem mobilidade
          sem depender ainda de mapas, ETA ou validadores fisicos reais.
        </p>
      </section>

      <section className="cards" aria-label="Jornada prioritaria">
        {cards.map(([title, text]) => (
          <article key={title}>
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </section>

      <section className="panel">
        <h2>Conexao API Hub</h2>
        <div className="api-grid">
          {apiCards.map(card => (
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

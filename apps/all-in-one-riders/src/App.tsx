import { useEffect, useState } from 'react'

const steps = [
  ['01', 'Candidatura', 'Cadastro do perfil, CNH, veiculo e aceite dos termos.'],
  ['02', 'Aprovacao', 'Fila operacional para documentos, antifraude e ativacao.'],
  ['03', 'Corridas', 'Entrega ou corrida com coleta, destino, rota e ocorrencias.'],
  ['04', 'Ganhos', 'Resumo financeiro e repasse via Finance sem expor saldo bruto.'],
]

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? ''
const API_HUB_TOKEN = import.meta.env.VITE_API_HUB_TOKEN ?? ''

const endpoints = [
  { label: 'Perfis', path: '/riders/resources/rider_profiles', fallback: '2 candidatos em triagem' },
  { label: 'Veiculos', path: '/riders/resources/vehicles', fallback: '1 veiculo pronto para vistoria' },
  { label: 'Entregas', path: '/delivery/resources/delivery_requests', fallback: '3 entregas simuladas' },
  { label: 'Corridas', path: '/mobility/resources/rides', fallback: '1 corrida em aceite' },
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
        <p className="eyebrow">All-in-One Riders</p>
        <h1>Candidatura, operacao em campo e ganhos em uma trilha auditavel.</h1>
        <p>
          Shell dedicado para levar candidatura, documentos, veiculos,
          entregas/corridas e ganhos ao Playwright sem misturar a experiencia
          Valley Rider.
        </p>
      </section>

      <section className="grid" aria-label="Jornada prioritaria">
        {steps.map(([number, title, text]) => (
          <article className="card" key={number}>
            <span>{number}</span>
            <h2>{title}</h2>
            <p>{text}</p>
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

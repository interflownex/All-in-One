import { useEffect, useState } from 'react'

const journey = [
  'Consentimento LGPD',
  'Paciente e profissional',
  'Agenda clinica',
  'Prontuario protegido',
  'Consulta e retorno',
]

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? ''
const API_HUB_TOKEN = import.meta.env.VITE_API_HUB_TOKEN ?? ''

const endpoints = [
  { label: 'Pacientes', path: '/health/resources/patients', fallback: '2 pacientes protegidos' },
  { label: 'Agendas', path: '/health/resources/appointments', fallback: '3 consultas previstas' },
  { label: 'Consentimentos', path: '/identity/resources/consents', fallback: '1 consentimento pendente' },
  { label: 'Documentos', path: '/document/resources/documents', fallback: '2 documentos clinicos' },
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
        <p className="eyebrow">All-in-One Health</p>
        <h1>Saude operacional com consentimento, agenda e prontuario protegido.</h1>
        <p>
          Shell dedicado para validar a jornada paciente, agenda, prontuario
          e consulta antes de conectar telemedicina e provedores reais.
        </p>
      </section>

      <section className="journey" aria-label="Jornada prioritaria">
        {journey.map(item => <article key={item}>{item}</article>)}
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

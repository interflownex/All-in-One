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

type ApiResource = {
  id: string
  status?: string
  payload?: Record<string, unknown>
}

type JourneyState = 'idle' | 'running' | 'completed' | 'failed'

const apiHeaders = () => (API_HUB_TOKEN ? { Authorization: `Bearer ${API_HUB_TOKEN}` } : {})

async function fetchEndpoint(path: string): Promise<ApiResource[]> {
  if (!API_HUB_URL) throw new Error('VITE_API_HUB_URL ausente')
  const response = await fetch(`${API_HUB_URL}${path}?limit=3`, {
    headers: apiHeaders(),
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  const payload = await response.json()
  if (Array.isArray(payload)) return payload
  return Array.isArray(payload?.data) ? payload.data : []
}

async function transitionRiderProfile(profileId: string, action: 'submit' | 'approve' | 'activate', reason: string) {
  const response = await fetch(`${API_HUB_URL}/riders/resources/rider_profiles/${profileId}/actions/${action}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...apiHeaders(),
    },
    body: JSON.stringify({ reason }),
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json() as Promise<ApiResource>
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
  const [profile, setProfile] = useState<ApiResource | null>(null)
  const [journeyState, setJourneyState] = useState<JourneyState>('idle')
  const [journeyMessage, setJourneyMessage] = useState('Pronto para submeter documentos, aprovar cadastro e ativar rider.')

  useEffect(() => {
    let active = true
    Promise.all(
      endpoints.map(async endpoint => {
        try {
          const data = await fetchEndpoint(endpoint.path)
          if (endpoint.path.endsWith('/rider_profiles') && data[0]) {
            setProfile(data[0])
          }
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

  async function completeRiderJourney() {
    if (!profile?.id) {
      setJourneyState('failed')
      setJourneyMessage('Nenhum perfil retornado pelo API Hub para executar a jornada.')
      return
    }
    setJourneyState('running')
    setJourneyMessage('Submetendo documentos do rider...')
    try {
      const submitted = await transitionRiderProfile(profile.id, 'submit', 'documentos enviados pelo Playwright')
      setProfile(submitted)
      const approved = await transitionRiderProfile(profile.id, 'approve', 'compliance aprovou cadastro com MFA')
      setProfile(approved)
      const active = await transitionRiderProfile(profile.id, 'activate', 'rider liberado para operacao')
      setProfile(active)
      setJourneyState('completed')
      setJourneyMessage('Jornada concluida: rider active e pronto para operacao.')
    } catch {
      setJourneyState('failed')
      setJourneyMessage('Nao foi possivel concluir a jornada Riders pelo API Hub.')
    }
  }

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

      <section className="action-panel" aria-label="Acao de jornada Riders">
        <div>
          <p className="eyebrow">Jornada executavel</p>
          <h2>Submeter, aprovar e ativar rider</h2>
          <p>
            Usa o perfil retornado pelo API Hub para validar documentos, aprovar
            com contexto compliance/MFA e liberar a operacao.
          </p>
        </div>
        <dl>
          <div>
            <dt>Perfil</dt>
            <dd>{profile?.id ? profile.id.slice(0, 8) : 'aguardando API Hub'}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{profile?.status ?? 'fallback'}</dd>
          </div>
        </dl>
        <button type="button" onClick={completeRiderJourney} disabled={journeyState === 'running'}>
          {journeyState === 'running' ? 'Executando...' : 'Concluir jornada Riders'}
        </button>
        <p className={`journey-feedback ${journeyState}`}>{journeyMessage}</p>
      </section>
    </main>
  )
}

export default App

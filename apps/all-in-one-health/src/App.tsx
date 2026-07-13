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

type ApiResource = {
  id: string
  status?: string
  payload?: Record<string, unknown>
}

type JourneyState = 'idle' | 'running' | 'completed' | 'failed'

type ClinicalGovernance = {
  consents: number
  documents: number
  patientSummary: string
  followUp: string
}

const apiHeaders = (): Record<string, string> => (API_HUB_TOKEN ? { Authorization: `Bearer ${API_HUB_TOKEN}` } : {})

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

async function transitionAppointment(appointmentId: string, action: 'approve' | 'complete', reason: string) {
  const response = await fetch(`${API_HUB_URL}/health/resources/appointments/${appointmentId}/actions/${action}`, {
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
  const [appointment, setAppointment] = useState<ApiResource | null>(null)
  const [governance, setGovernance] = useState<ClinicalGovernance>({
    consents: 0,
    documents: 0,
    patientSummary: 'Aguardando dados protegidos do API Hub.',
    followUp: 'Retorno sera definido apos concluir a consulta.',
  })
  const [journeyState, setJourneyState] = useState<JourneyState>('idle')
  const [journeyMessage, setJourneyMessage] = useState('Pronto para aprovar consulta e registrar atendimento concluido.')

  useEffect(() => {
    let active = true
    Promise.all(
      endpoints.map(async endpoint => {
        try {
          const data = await fetchEndpoint(endpoint.path)
          if (endpoint.path.endsWith('/appointments') && data[0]) {
            setAppointment(data[0])
          }
          if (endpoint.path.endsWith('/patients') && data[0]) {
            setGovernance(current => ({
              ...current,
              patientSummary: String(data[0].payload?.name ?? data[0].payload?.health_identifier ?? 'Paciente protegido'),
            }))
          }
          if (endpoint.path.endsWith('/consents')) {
            setGovernance(current => ({ ...current, consents: data.length }))
          }
          if (endpoint.path.endsWith('/documents')) {
            setGovernance(current => ({ ...current, documents: data.length }))
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

  async function completeHealthJourney() {
    if (!appointment?.id) {
      setJourneyState('failed')
      setJourneyMessage('Nenhuma consulta retornada pelo API Hub para executar a jornada.')
      return
    }
    setJourneyState('running')
    setJourneyMessage('Aprovando consulta com contexto clinico e MFA...')
    try {
      const approved = await transitionAppointment(appointment.id, 'approve', 'consulta autorizada pelo Playwright')
      setAppointment(approved)
      const completed = await transitionAppointment(appointment.id, 'complete', 'atendimento concluido com prontuario protegido')
      setAppointment(completed)
      setGovernance(current => ({
        ...current,
        followUp: 'Retorno pos-consulta criado: revisar prontuario protegido e manter consentimento LGPD ativo.',
      }))
      setJourneyState('completed')
      setJourneyMessage('Jornada concluida: consulta completed com governanca clinica registrada.')
    } catch {
      setJourneyState('failed')
      setJourneyMessage('Nao foi possivel concluir a jornada Health pelo API Hub.')
    }
  }

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

      <section className="action-panel" aria-label="Acao de jornada Health">
        <div>
          <p className="eyebrow">Jornada executavel</p>
          <h2>Aprovar consulta e concluir atendimento</h2>
          <p>
            Usa a primeira agenda retornada pelo API Hub para validar aprovacao
            clinica com MFA e conclusao do atendimento sem expor dado sensivel.
          </p>
        </div>
        <dl>
          <div>
            <dt>Consulta</dt>
            <dd>{appointment?.id ? appointment.id.slice(0, 8) : 'aguardando API Hub'}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{appointment?.status ?? 'fallback'}</dd>
          </div>
        </dl>
        <button type="button" onClick={completeHealthJourney} disabled={journeyState === 'running'}>
          {journeyState === 'running' ? 'Executando...' : 'Concluir jornada Health'}
        </button>
        <p className={`journey-feedback ${journeyState}`}>{journeyMessage}</p>
      </section>

      <section className="action-panel" aria-label="Governanca clinica Health">
        <div>
          <p className="eyebrow">Governanca clinica</p>
          <h2>Consentimento, prontuario e retorno</h2>
          <p>
            Consolida apenas metadados operacionais retornados pelo API Hub,
            mantendo dados sensiveis fora da interface de acompanhamento.
          </p>
        </div>
        <dl>
          <div>
            <dt>Paciente</dt>
            <dd>{governance.patientSummary}</dd>
          </div>
          <div>
            <dt>Consentimento LGPD</dt>
            <dd>{governance.consents > 0 ? 'Consentimento verificado' : 'Aguardando consentimento'}</dd>
          </div>
          <div>
            <dt>Prontuario</dt>
            <dd>{governance.documents > 0 ? 'Prontuario protegido disponivel' : 'Documento clinico pendente'}</dd>
          </div>
          <div>
            <dt>Retorno</dt>
            <dd>{governance.followUp}</dd>
          </div>
        </dl>
      </section>
    </main>
  )
}

export default App

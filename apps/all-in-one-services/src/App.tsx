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

type ApiResource = {
  id: string
  status?: string
  payload?: Record<string, unknown>
}

type JourneyState = 'idle' | 'running' | 'completed' | 'failed'

type ServiceEvidence = {
  provider: string
  escrows: number
  documents: number
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

async function transitionContract(contractId: string, action: 'accept' | 'complete', reason: string, payload = {}) {
  const response = await fetch(`${API_HUB_URL}/services/resources/service_contracts/${contractId}/actions/${action}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...apiHeaders(),
    },
    body: JSON.stringify({ reason, payload }),
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
  const [contract, setContract] = useState<ApiResource | null>(null)
  const [evidence, setEvidence] = useState<ServiceEvidence>({
    provider: 'Aguardando prestador do API Hub.',
    escrows: 0,
    documents: 0,
    followUp: 'Aguardando conclusao do atendimento.',
  })
  const [journeyState, setJourneyState] = useState<JourneyState>('idle')
  const [journeyMessage, setJourneyMessage] = useState('Pronto para aceitar contrato, reter escrow e anexar evidencia.')

  useEffect(() => {
    let active = true
    Promise.all(
      endpoints.map(async endpoint => {
        try {
          const data = await fetchEndpoint(endpoint.path)
          if (endpoint.path.endsWith('/service_contracts') && data[0]) {
            setContract(data[0])
          }
          if (endpoint.path.endsWith('/providers') && data[0]) {
            setEvidence(current => ({
              ...current,
              provider: String(data[0].payload?.name ?? data[0].payload?.category ?? 'Prestador validado'),
            }))
          }
          if (endpoint.path.endsWith('/escrows')) {
            setEvidence(current => ({ ...current, escrows: data.length }))
          }
          if (endpoint.path.endsWith('/documents')) {
            setEvidence(current => ({ ...current, documents: data.length }))
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

  async function completeServiceJourney() {
    if (!contract?.id) {
      setJourneyState('failed')
      setJourneyMessage('Nenhum contrato retornado pelo API Hub para executar a jornada.')
      return
    }
    setJourneyState('running')
    setJourneyMessage('Aceitando contrato e confirmando escrow...')
    try {
      const held = await transitionContract(contract.id, 'accept', 'orcamento aceito com escrow')
      setContract(held)
      const completed = await transitionContract(contract.id, 'complete', 'servico executado com evidencia', {
        evidence_hash: 'phase4-playwright-evidence',
      })
      setContract(completed)
      setEvidence(current => ({
        ...current,
        followUp: 'Pos-atendimento criado: liberar escrow apos conferencia da evidencia e registrar satisfacao do cliente.',
      }))
      setJourneyState('completed')
      setJourneyMessage('Jornada concluida: contrato completed com evidencia anexada.')
    } catch {
      setJourneyState('failed')
      setJourneyMessage('Nao foi possivel concluir a jornada pelo API Hub.')
    }
  }

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

      <section className="action-panel" aria-label="Acao de jornada Services">
        <div>
          <p className="eyebrow">Jornada executavel</p>
          <h2>Aceitar contrato e concluir evidencia</h2>
          <p>
            Usa o primeiro contrato retornado pelo API Hub para simular aceite,
            escrow retido e entrega com evidencia auditavel.
          </p>
        </div>
        <dl>
          <div>
            <dt>Contrato</dt>
            <dd>{contract?.id ? contract.id.slice(0, 8) : 'aguardando API Hub'}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{contract?.status ?? 'fallback'}</dd>
          </div>
        </dl>
        <button type="button" onClick={completeServiceJourney} disabled={journeyState === 'running'}>
          {journeyState === 'running' ? 'Executando...' : 'Concluir jornada Services'}
        </button>
        <p className={`journey-feedback ${journeyState}`}>{journeyMessage}</p>
      </section>

      <section className="action-panel" aria-label="Pos-atendimento Services">
        <div>
          <p className="eyebrow">Pos-atendimento</p>
          <h2>Escrow, evidencia e retorno do cliente</h2>
          <p>
            Consolida metadados operacionais do API Hub para acompanhar a
            liberacao financeira e a prova de execucao sem expor documentos.
          </p>
        </div>
        <dl>
          <div>
            <dt>Prestador</dt>
            <dd>{evidence.provider}</dd>
          </div>
          <div>
            <dt>Escrow</dt>
            <dd>{evidence.escrows > 0 ? 'Escrow operacional vinculado' : 'Escrow pendente'}</dd>
          </div>
          <div>
            <dt>Evidencia</dt>
            <dd>{evidence.documents > 0 ? 'Evidencia documental disponivel' : 'Evidencia pendente'}</dd>
          </div>
          <div>
            <dt>Retorno</dt>
            <dd>{evidence.followUp}</dd>
          </div>
        </dl>
      </section>
    </main>
  )
}

export default App

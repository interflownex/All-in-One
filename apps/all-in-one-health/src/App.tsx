import { useEffect, useState, type FormEvent } from 'react'
import './index.css'

type TabKey = 'dashboard' | 'pacientes' | 'agenda' | 'prontuario' | 'telemedicina'

type GatewayStatus = {
  service?: string
  status?: string
  security?: string
  rate_limit?: string
  routes?: string[]
}

type CommercialInsights = {
  orders_total?: number
  orders_paid?: number
  orders_completed?: number
  reviews_total?: number
  average_rating?: number | null
  support_cases_total?: number
  support_cases_open?: number
  support_cases_resolved?: number
  conversion_rate_percent?: number
  source?: string
}

type ModuleHealth = {
  module?: string
  service?: string
  status?: string
  storage?: string
  version?: string
}

type HealthPatient = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    full_name?: string
    health_identifier?: string
    city?: string
    primary_care?: string
    insurance_plan?: string
    next_visit?: string
  }
}

type HealthAppointment = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    patient_id?: string
    patient_name?: string
    specialty?: string
    scheduled_at?: string
    mode?: string
    channel?: string
    telemedicine?: boolean
  }
}

type HealthRecord = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    patient_id?: string
    patient_name?: string
    record_type?: string
    provider?: string
    summary?: string
    confidentiality?: string
  }
}

type Prescription = {
  id: string
  status?: string
  created_at?: string
  payload?: {
    patient_id?: string
    patient_name?: string
    medication?: string
    dosage?: string
    issued_by?: string
    refills?: string
  }
}

type Snapshot = {
  gateway: GatewayStatus
  commercial: CommercialInsights
  moduleHealth: ModuleHealth
  patients: HealthPatient[]
  appointments: HealthAppointment[]
  records: HealthRecord[]
  prescriptions: Prescription[]
}

type AppointmentDraft = {
  patient_id: string
  patient_name: string
  specialty: string
  scheduled_at: string
  mode: string
  channel: string
}

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? 'http://127.0.0.1:8100'
const HEALTH_URL = import.meta.env.VITE_HEALTH_URL ?? 'http://127.0.0.1:8112'

const FALLBACK_GATEWAY: GatewayStatus = {
  service: 'api_hub',
  status: 'operational',
  security: 'gateway-signed',
  rate_limit: '60rpm',
  routes: ['/gateway/status', '/gateway/insights/commercial'],
}

const FALLBACK_COMMERCIAL: CommercialInsights = {
  orders_total: 12,
  orders_paid: 10,
  orders_completed: 9,
  reviews_total: 3,
  average_rating: 4.8,
  support_cases_total: 1,
  support_cases_open: 0,
  support_cases_resolved: 1,
  conversion_rate_percent: 18,
  source: 'fallback',
}

const FALLBACK_HEALTH: ModuleHealth = {
  module: 'health',
  service: 'health',
  status: 'healthy',
  storage: 'postgres',
  version: 'baseline',
}

const FALLBACK_PATIENTS: HealthPatient[] = [
  {
    id: 'patient-1',
    status: 'active',
    created_at: '2026-07-04T09:00:00Z',
    payload: {
      full_name: 'Ana Souza',
      health_identifier: 'SUS-998877',
      city: 'Sao Paulo',
      primary_care: 'Clinica geral',
      insurance_plan: 'All-in-One Care',
      next_visit: '2026-07-08T14:00:00Z',
    },
  },
  {
    id: 'patient-2',
    status: 'monitoring',
    created_at: '2026-07-04T11:00:00Z',
    payload: {
      full_name: 'Carlos Lima',
      health_identifier: 'SUS-554433',
      city: 'Campinas',
      primary_care: 'Cardiologia',
      insurance_plan: 'Premium Care',
      next_visit: '2026-07-09T10:30:00Z',
    },
  },
]

const FALLBACK_APPOINTMENTS: HealthAppointment[] = [
  {
    id: 'appointment-1',
    status: 'confirmed',
    created_at: '2026-07-04T12:00:00Z',
    payload: {
      patient_id: 'patient-1',
      patient_name: 'Ana Souza',
      specialty: 'telemedicina',
      scheduled_at: '2026-07-08T14:00:00Z',
      mode: 'video',
      channel: 'portal',
      telemedicine: true,
    },
  },
  {
    id: 'appointment-2',
    status: 'scheduled',
    created_at: '2026-07-04T13:00:00Z',
    payload: {
      patient_id: 'patient-2',
      patient_name: 'Carlos Lima',
      specialty: 'cardiologia',
      scheduled_at: '2026-07-09T10:30:00Z',
      mode: 'presencial',
      channel: 'clinic',
      telemedicine: false,
    },
  },
]

const FALLBACK_RECORDS: HealthRecord[] = [
  {
    id: 'record-1',
    status: 'available',
    created_at: '2026-07-04T14:00:00Z',
    payload: {
      patient_id: 'patient-1',
      patient_name: 'Ana Souza',
      record_type: 'consulta',
      provider: 'Dra. Marina',
      summary: 'Evolucao favoravel e acompanhamento remoto.',
      confidentiality: 'restricted',
    },
  },
  {
    id: 'record-2',
    status: 'available',
    created_at: '2026-07-04T14:30:00Z',
    payload: {
      patient_id: 'patient-2',
      patient_name: 'Carlos Lima',
      record_type: 'exame',
      provider: 'Dra. Paula',
      summary: 'Exames com encaminhamento para telemedicina.',
      confidentiality: 'restricted',
    },
  },
]

const FALLBACK_PRESCRIPTIONS: Prescription[] = [
  {
    id: 'prescription-1',
    status: 'issued',
    created_at: '2026-07-04T15:00:00Z',
    payload: {
      patient_id: 'patient-1',
      patient_name: 'Ana Souza',
      medication: 'Vitamina D',
      dosage: '1 comp. ao dia',
      issued_by: 'Dra. Marina',
      refills: '2',
    },
  },
  {
    id: 'prescription-2',
    status: 'issued',
    created_at: '2026-07-04T15:30:00Z',
    payload: {
      patient_id: 'patient-2',
      patient_name: 'Carlos Lima',
      medication: 'Beta bloqueador',
      dosage: '1 comp. pela manha',
      issued_by: 'Dra. Paula',
      refills: '1',
    },
  },
]

const TAB_CONTENT: Record<TabKey, { label: string; detail: string }> = {
  dashboard: { label: 'Dashboard', detail: 'visao clinica consolidada' },
  pacientes: { label: 'Pacientes', detail: 'cadastro e acompanhamento' },
  agenda: { label: 'Agenda', detail: 'consultas e telemedicina' },
  prontuario: { label: 'Prontuario', detail: 'historico e prescricoes' },
  telemedicina: { label: 'Telemedicina', detail: 'canal remoto seguro' },
}

function getStoredActorId() {
  const key = 'all-in-one-health.demo-user-id'
  const stored = window.localStorage.getItem(key)
  if (stored) return stored
  const generated = window.crypto.randomUUID()
  window.localStorage.setItem(key, generated)
  return generated
}

function formatDateTime(value?: string | null) {
  if (!value) return 'Sem agendamento'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(parsed)
}

function unwrapCollection<T>(payload: unknown, fallback: T[]) {
  if (Array.isArray(payload)) return payload as T[]
  if (payload && typeof payload === 'object') {
    const data = (payload as { data?: T[] }).data
    if (Array.isArray(data) && data.length > 0) return data
  }
  return fallback
}

function mergeHeaders(extra: HeadersInit | undefined, actorId: string) {
  return {
    'Content-Type': 'application/json',
    'X-Actor-User-Id': actorId,
    ...(extra ?? {}),
  }
}

async function fetchJson<T>(url: string, actorId: string, signal: AbortSignal, init: RequestInit = {}) {
  try {
    const response = await fetch(url, {
      ...init,
      signal,
      headers: mergeHeaders(init.headers, actorId),
    })
    if (!response.ok) return null
    return (await response.json()) as T
  } catch {
    return null
  }
}

function buildAppointmentSeed(fallbackPatient: HealthPatient): AppointmentDraft {
  return {
    patient_id: fallbackPatient.id,
    patient_name: fallbackPatient.payload?.full_name ?? 'Paciente Demo',
    specialty: fallbackPatient.payload?.primary_care ?? 'Clinica geral',
    scheduled_at: new Date(Date.now() + 60 * 60 * 1000).toISOString().slice(0, 16),
    mode: 'telemedicina',
    channel: 'portal',
  }
}

export default function App() {
  const actorId = getStoredActorId()
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard')
  const [search, setSearch] = useState('')
  const [snapshot, setSnapshot] = useState<Snapshot>({
    gateway: FALLBACK_GATEWAY,
    commercial: FALLBACK_COMMERCIAL,
    moduleHealth: FALLBACK_HEALTH,
    patients: FALLBACK_PATIENTS,
    appointments: FALLBACK_APPOINTMENTS,
    records: FALLBACK_RECORDS,
    prescriptions: FALLBACK_PRESCRIPTIONS,
  })
  const [statusMessage, setStatusMessage] = useState<string | null>(null)
  const [statusError, setStatusError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [appointmentDraft, setAppointmentDraft] = useState<AppointmentDraft>(
    buildAppointmentSeed(FALLBACK_PATIENTS[0]),
  )

  useEffect(() => {
    const controller = new AbortController()

    async function load() {
      const [
        gateway,
        commercial,
        moduleHealth,
        patients,
        appointments,
        records,
        prescriptions,
      ] = await Promise.all([
        fetchJson<GatewayStatus>(`${API_HUB_URL}/gateway/status`, actorId, controller.signal),
        fetchJson<CommercialInsights>(`${API_HUB_URL}/gateway/insights/commercial`, actorId, controller.signal),
        fetchJson<ModuleHealth>(`${HEALTH_URL}/health`, actorId, controller.signal),
        fetchJson<unknown>(`${HEALTH_URL}/resources/patients`, actorId, controller.signal),
        fetchJson<unknown>(`${HEALTH_URL}/resources/appointments`, actorId, controller.signal),
        fetchJson<unknown>(`${HEALTH_URL}/resources/medical_records`, actorId, controller.signal),
        fetchJson<unknown>(`${HEALTH_URL}/resources/prescriptions`, actorId, controller.signal),
      ])

      const patientList = unwrapCollection(patients, FALLBACK_PATIENTS)
      setSnapshot({
        gateway: gateway ?? FALLBACK_GATEWAY,
        commercial: commercial ?? FALLBACK_COMMERCIAL,
        moduleHealth: moduleHealth ?? FALLBACK_HEALTH,
        patients: patientList,
        appointments: unwrapCollection(appointments, FALLBACK_APPOINTMENTS),
        records: unwrapCollection(records, FALLBACK_RECORDS),
        prescriptions: unwrapCollection(prescriptions, FALLBACK_PRESCRIPTIONS),
      })
      setAppointmentDraft((current) => (current.patient_id ? current : buildAppointmentSeed(patientList[0] ?? FALLBACK_PATIENTS[0])))
    }

    void load()
    return () => controller.abort()
  }, [actorId])

  const query = search.trim().toLowerCase()
  const filteredPatients = snapshot.patients.filter((item) => {
    const haystack = [
      item.id,
      item.status,
      item.payload?.full_name,
      item.payload?.health_identifier,
      item.payload?.city,
      item.payload?.primary_care,
      item.payload?.insurance_plan,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return !query || haystack.includes(query)
  })
  const filteredAppointments = snapshot.appointments.filter((item) => {
    const haystack = [
      item.id,
      item.status,
      item.payload?.patient_name,
      item.payload?.specialty,
      item.payload?.mode,
      item.payload?.channel,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return !query || haystack.includes(query)
  })
  const filteredRecords = snapshot.records.filter((item) => {
    const haystack = [
      item.id,
      item.status,
      item.payload?.patient_name,
      item.payload?.record_type,
      item.payload?.provider,
      item.payload?.summary,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return !query || haystack.includes(query)
  })
  const filteredPrescriptions = snapshot.prescriptions.filter((item) => {
    const haystack = [
      item.id,
      item.status,
      item.payload?.patient_name,
      item.payload?.medication,
      item.payload?.issued_by,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return !query || haystack.includes(query)
  })

  async function handleAppointmentSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setStatusMessage(null)
    setStatusError(null)

    try {
      const response = await fetch(`${HEALTH_URL}/resources/appointments`, {
        method: 'POST',
        headers: mergeHeaders(undefined, actorId),
        body: JSON.stringify({
          user_id: actorId,
          payload: appointmentDraft,
        }),
      })

      if (!response.ok) {
        throw new Error('Nao foi possivel agendar a consulta.')
      }

      const payload = (await response.json()) as { id?: string; status?: string }
      setStatusMessage(`Consulta agendada com sucesso${payload.id ? `: ${payload.id}` : ''}.`)
      setActiveTab('agenda')
    } catch (error) {
      setStatusError(error instanceof Error ? error.message : 'Falha inesperada ao agendar consulta.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="health-shell">
      <aside className="health-sidebar">
        <div className="brand-block">
          <div className="brand-mark">H</div>
          <div>
            <div className="brand-name">All-in-One Health</div>
            <div className="brand-subtitle">pacientes, agenda e telemedicina</div>
          </div>
        </div>

        <div className="gateway-chip">
          <span className="status-dot" />
          <div>
            <strong>{snapshot.gateway.security ?? 'gateway-signed'}</strong>
            <p>
              {snapshot.gateway.status ?? 'operacional'} • {snapshot.moduleHealth.storage ?? 'postgres'}
            </p>
          </div>
        </div>

        <nav className="nav-stack" aria-label="Secoes do Health">
          {(Object.keys(TAB_CONTENT) as TabKey[]).map((key) => (
            <button
              key={key}
              type="button"
              className={`nav-pill ${activeTab === key ? 'active' : ''}`}
              onClick={() => setActiveTab(key)}
            >
              <strong>{TAB_CONTENT[key].label}</strong>
              <span>{TAB_CONTENT[key].detail}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-note">
          <strong>Atendimento coordenado</strong>
          <p>
            O shell Health consome o API Hub, o Identity baseline e os recursos do modulo com um
            identificador persistente no navegador.
          </p>
        </div>
      </aside>

      <main className="health-main">
        <section className="hero-panel">
          <div>
            <span className="eyebrow">Saude integrada em tempo real</span>
            <h1>Consultas, prontuarios e telemedicina em uma unica superficie.</h1>
            <p className="hero-copy">
              O app Health conecta pacientes, agenda, prontuarios e prescricoes sobre os
              endpoints versionados do All-in-One, com fallback visual para demo e dados reais
              quando o backend esta disponivel.
            </p>
          </div>

          <div className="hero-side">
            <div className="search-box">
              <span>Buscar paciente, consulta ou prontuario</span>
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Ex.: Ana Souza, telemedicina, consulta"
              />
            </div>

            <div className="hero-status">
              <div>
                <span className="muted">Rede clinica</span>
                <strong>{snapshot.moduleHealth.status ?? 'healthy'}</strong>
              </div>
              <div>
                <span className="muted">Conversao comercial</span>
                <strong>{snapshot.commercial.conversion_rate_percent ?? 0}%</strong>
              </div>
            </div>
          </div>
        </section>

        {statusMessage ? <div className="success-box">{statusMessage}</div> : null}
        {statusError ? <div className="warning-box">{statusError}</div> : null}

        <section className="metric-grid">
          <article className="metric-card highlight">
            <span>Pacientes ativos</span>
            <strong>{filteredPatients.length}</strong>
            <small>
              {snapshot.moduleHealth.version ?? 'baseline'} • {snapshot.moduleHealth.storage ?? 'postgres'}
            </small>
          </article>
          <article className="metric-card">
            <span>Consultas agendadas</span>
            <strong>{filteredAppointments.length}</strong>
            <small>agenda clinica e telemedicina</small>
          </article>
          <article className="metric-card">
            <span>Prontuarios visiveis</span>
            <strong>{filteredRecords.length}</strong>
            <small>auditoria e confidencialidade</small>
          </article>
          <article className="metric-card">
            <span>Prescricoes emitidas</span>
            <strong>{filteredPrescriptions.length}</strong>
            <small>canal medico autorizado</small>
          </article>
          <article className="metric-card">
            <span>Gateway</span>
            <strong>{snapshot.gateway.status ?? 'operational'}</strong>
            <small>{snapshot.gateway.rate_limit ?? '60rpm'}</small>
          </article>
        </section>

        <section className="content-grid">
          {activeTab === 'dashboard' ? (
            <>
              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Visao clinica</span>
                    <h2>Fila de cuidado e telemedicina</h2>
                  </div>
                  <span className="section-note">Fonte {snapshot.gateway.service ?? 'api_hub'}</span>
                </div>
                <div className="timeline">
                  {filteredAppointments.slice(0, 3).map((item) => (
                    <div key={item.id} className="timeline-item">
                      <span className="timeline-time">{formatDateTime(item.payload?.scheduled_at)}</span>
                      <div>
                        <strong>{item.payload?.patient_name ?? item.id}</strong>
                        <p>
                          {item.payload?.specialty ?? 'consulta'} • {item.payload?.mode ?? 'telemedicina'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </article>

              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Indicadores</span>
                    <h2>Atividade e confianca</h2>
                  </div>
                </div>
                <div className="insight-stack">
                  <div className="insight-row">
                    <span>Ordens pagas</span>
                    <strong>{snapshot.commercial.orders_paid ?? 0}</strong>
                  </div>
                  <div className="insight-row">
                    <span>Avaliacao media</span>
                    <strong>{snapshot.commercial.average_rating ?? 0}</strong>
                  </div>
                  <div className="insight-row">
                    <span>Casos abertos</span>
                    <strong>{snapshot.commercial.support_cases_open ?? 0}</strong>
                  </div>
                </div>
              </article>
            </>
          ) : null}

          {activeTab === 'pacientes' ? (
            <article className="content-card span-two">
              <div className="section-head">
                <div>
                  <span className="section-label">Base assistida</span>
                  <h2>Pacientes e linhas de cuidado</h2>
                </div>
                <span className="section-note">Busca local e fallback de demo</span>
              </div>
              <div className="card-grid">
                {filteredPatients.map((patient) => (
                  <div key={patient.id} className="info-card">
                    <span>{patient.status ?? 'active'}</span>
                    <strong>{patient.payload?.full_name ?? patient.id}</strong>
                    <p>{patient.payload?.health_identifier ?? 'Sem identificador'}</p>
                    <small>
                      {patient.payload?.city ?? 'Cidade nao informada'} •{' '}
                      {patient.payload?.primary_care ?? 'Clinica geral'}
                    </small>
                    <small>Plano: {patient.payload?.insurance_plan ?? 'Basico'}</small>
                  </div>
                ))}
              </div>
            </article>
          ) : null}

          {activeTab === 'agenda' ? (
            <>
              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Nova consulta</span>
                    <h2>Agendamento rapido</h2>
                  </div>
                </div>
                <form className="stack-form" onSubmit={handleAppointmentSubmit}>
                  <label>
                    <span>Paciente</span>
                    <input
                      value={appointmentDraft.patient_name}
                      onChange={(event) =>
                        setAppointmentDraft((current) => ({ ...current, patient_name: event.target.value }))
                      }
                      placeholder="Nome do paciente"
                    />
                  </label>
                  <label>
                    <span>ID do paciente</span>
                    <input
                      value={appointmentDraft.patient_id}
                      onChange={(event) =>
                        setAppointmentDraft((current) => ({ ...current, patient_id: event.target.value }))
                      }
                      placeholder="patient-1"
                    />
                  </label>
                  <label>
                    <span>Especialidade</span>
                    <input
                      value={appointmentDraft.specialty}
                      onChange={(event) =>
                        setAppointmentDraft((current) => ({ ...current, specialty: event.target.value }))
                      }
                      placeholder="clinica geral"
                    />
                  </label>
                  <label>
                    <span>Data e hora</span>
                    <input
                      type="datetime-local"
                      value={appointmentDraft.scheduled_at}
                      onChange={(event) =>
                        setAppointmentDraft((current) => ({ ...current, scheduled_at: event.target.value }))
                      }
                    />
                  </label>
                  <label>
                    <span>Canal</span>
                    <input
                      value={appointmentDraft.channel}
                      onChange={(event) =>
                        setAppointmentDraft((current) => ({ ...current, channel: event.target.value }))
                      }
                      placeholder="portal"
                    />
                  </label>
                  <button type="submit" className="primary-button" disabled={submitting}>
                    {submitting ? 'Agendando...' : 'Agendar consulta'}
                  </button>
                </form>
              </article>

              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Agenda viva</span>
                    <h2>Consultas confirmadas</h2>
                  </div>
                </div>
                <div className="timeline">
                  {filteredAppointments.map((appointment) => (
                    <div key={appointment.id} className="timeline-item">
                      <span className="timeline-time">{formatDateTime(appointment.payload?.scheduled_at)}</span>
                      <div>
                        <strong>{appointment.payload?.patient_name ?? appointment.id}</strong>
                        <p>
                          {appointment.payload?.specialty ?? 'consulta'} •{' '}
                          {appointment.payload?.mode ?? 'presencial'}
                        </p>
                        <small>{appointment.payload?.channel ?? 'portal'}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </article>
            </>
          ) : null}

          {activeTab === 'prontuario' ? (
            <>
              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Prontuarios</span>
                    <h2>Historico clinico protegido</h2>
                  </div>
                </div>
                <div className="card-grid">
                  {filteredRecords.map((record) => (
                    <div key={record.id} className="info-card accent">
                      <span>{record.payload?.confidentiality ?? 'restricted'}</span>
                      <strong>{record.payload?.patient_name ?? record.id}</strong>
                      <p>{record.payload?.record_type ?? 'registro clinico'}</p>
                      <small>{record.payload?.summary ?? 'Sem resumo'}</small>
                      <small>{record.payload?.provider ?? 'Profissional nao informado'}</small>
                    </div>
                  ))}
                </div>
              </article>

              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Prescricoes</span>
                    <h2>Saida medica segura</h2>
                  </div>
                </div>
                <div className="card-grid">
                  {filteredPrescriptions.map((prescription) => (
                    <div key={prescription.id} className="info-card">
                      <span>{prescription.status ?? 'issued'}</span>
                      <strong>{prescription.payload?.patient_name ?? prescription.id}</strong>
                      <p>{prescription.payload?.medication ?? 'Medicamento'}</p>
                      <small>{prescription.payload?.dosage ?? 'Dose nao informada'}</small>
                      <small>{prescription.payload?.issued_by ?? 'Profissional nao informado'}</small>
                    </div>
                  ))}
                </div>
              </article>
            </>
          ) : null}

          {activeTab === 'telemedicina' ? (
            <>
              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Telemedicina</span>
                    <h2>Canal remoto e triagem</h2>
                  </div>
                </div>
                <div className="callout-card">
                  <strong>Pronto para atendimento remoto</strong>
                  <p>
                    A jornada de telemedicina usa o mesmo identificador do navegador, o API Hub e
                    os recursos do modulo Health para orquestrar consulta, prescricao e
                    acompanhamento.
                  </p>
                  <div className="callout-actions">
                    <button type="button" className="secondary-button" onClick={() => setActiveTab('agenda')}>
                      Ver agenda
                    </button>
                    <button type="button" className="secondary-button" onClick={() => setActiveTab('prontuario')}>
                      Abrir prontuario
                    </button>
                  </div>
                </div>
              </article>

              <article className="content-card">
                <div className="section-head">
                  <div>
                    <span className="section-label">Identidade</span>
                    <h2>Contexto ativo do paciente</h2>
                  </div>
                </div>
                <div className="stack-note">
                  <strong>{actorId}</strong>
                  <p>
                    O shell Health persiste um UUID demo no navegador e envia o cabeçalho
                    X-Actor-User-Id em todas as chamadas ao backend.
                  </p>
                </div>
              </article>
            </>
          ) : null}
        </section>
      </main>
    </div>
  )
}

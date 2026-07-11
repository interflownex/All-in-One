const journey = [
  'Consentimento LGPD',
  'Paciente e profissional',
  'Agenda clinica',
  'Prontuario protegido',
  'Consulta e retorno',
]

const endpoints = ['/gateway/health', '/gateway/identity', '/gateway/document']

function App() {
  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">All-in-One Health</p>
        <h1>Saude operacional com consentimento, agenda e prontuario protegido.</h1>
        <p>
          Shell dedicado para validar a jornada paciente -> agenda -> prontuario
          -> consulta antes de conectar telemedicina e provedores reais.
        </p>
      </section>

      <section className="journey" aria-label="Jornada prioritaria">
        {journey.map(item => <article key={item}>{item}</article>)}
      </section>

      <section className="panel">
        <h2>Contratos API Hub</h2>
        <div className="chips">
          {endpoints.map(endpoint => <code key={endpoint}>{endpoint}</code>)}
        </div>
      </section>
    </main>
  )
}

export default App

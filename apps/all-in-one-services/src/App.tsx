const stages = [
  'Prestador aprovado',
  'Visita agendada',
  'Orcamento revisado',
  'Contrato e escrow',
  'Evidencia entregue',
]

const endpoints = ['/gateway/services', '/gateway/finance', '/gateway/document']

function App() {
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
        <h2>Contratos API Hub</h2>
        <div className="chips">
          {endpoints.map(endpoint => <code key={endpoint}>{endpoint}</code>)}
        </div>
      </section>
    </main>
  )
}

export default App

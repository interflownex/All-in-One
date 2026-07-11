const cards = [
  ['Corrida', 'Solicitacao, aceite e conclusao com status operacional.'],
  ['Ticket', 'Compra e historico de bilhetes vinculados ao usuario.'],
  ['QR/NFC', 'Validacao local para preparar a integracao fisica real.'],
  ['Historico', 'Linha do tempo para suporte e auditoria da jornada.'],
]

const endpoints = ['/gateway/mobility', '/gateway/riders', '/gateway/finance']

function App() {
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
        <h2>Contratos API Hub</h2>
        <div className="chips">
          {endpoints.map(endpoint => <code key={endpoint}>{endpoint}</code>)}
        </div>
      </section>
    </main>
  )
}

export default App

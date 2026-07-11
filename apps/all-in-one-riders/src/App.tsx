const steps = [
  ['01', 'Candidatura', 'Cadastro do perfil, CNH, veiculo e aceite dos termos.'],
  ['02', 'Aprovacao', 'Fila operacional para documentos, antifraude e ativacao.'],
  ['03', 'Corridas', 'Entrega ou corrida com coleta, destino, rota e ocorrencias.'],
  ['04', 'Ganhos', 'Resumo financeiro e repasse via Finance sem expor saldo bruto.'],
]

const endpoints = ['/gateway/riders', '/gateway/delivery', '/gateway/mobility', '/gateway/finance']

function App() {
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
        <h2>Contratos API Hub</h2>
        <div className="chips">
          {endpoints.map(endpoint => <code key={endpoint}>{endpoint}</code>)}
        </div>
      </section>
    </main>
  )
}

export default App

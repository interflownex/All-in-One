import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

type DashboardRecord = {
  id: string
  name?: string
  title?: string
  status?: string
  region?: string
  value?: number
  created_at?: string
}

type ModuleDashboardProps = {
  module: string
  title: string
  records: DashboardRecord[]
}

const MODULE_OPERATIONS: Record<string, Array<[string, string]>> = {
  identity: [['Usuarios', 'users'], ['Documentos', 'documents'], ['Biometria', 'biometrics'], ['Sessoes', 'sessions'], ['Verificacoes', 'identityverifications'], ['Consentimentos', 'consentrecords']],
  business: [['Empresas', 'companies'], ['Filiais', 'branches'], ['Documentos', 'companydocuments'], ['Membros', 'usercompanymemberships'], ['Ofertas', 'catalogoffers']],
  permissions: [['Perfis', 'roles'], ['Permissoes', 'permissions'], ['Usuarios e perfis', 'userroles'], ['Politicas', 'accesspolicies'], ['Alcadas', 'approvallimits']],
  finance: [['Carteiras', 'wallets'], ['Lancamentos', 'ledgerentries'], ['Escrows', 'escrows'], ['Splits', 'splits'], ['Faturas', 'invoices'], ['Wallet ledger', 'walletledger']],
  marketplace: [['Lojas', 'stores'], ['Produtos', 'products'], ['Carrinhos', 'carts'], ['Pedidos', 'orders'], ['Avaliacoes', 'reviews'], ['Disputas', 'disputes'], ['Pepitas', 'pepitagrants']],
  stock: [['Fornecedores', 'suppliers'], ['Catalogo', 'catalogproducts'], ['Regras de preco', 'pricerules'], ['Pedidos', 'supplierorders'], ['Cotacoes', 'discountquotes']],
  delivery: [['Solicitacoes', 'deliveryrequests'], ['Cotacoes', 'quotes'], ['Atribuicoes', 'assignments'], ['Comprovantes', 'proofs'], ['Seguros', 'insuranceoptions']],
  riders: [['Perfis', 'riderprofiles'], ['Documentos', 'riderdocuments'], ['Veiculos', 'vehicles'], ['Avaliacoes', 'riderreviews']],
  services: [['Prestadores', 'providers'], ['Visitas', 'visits'], ['Orcamentos', 'quotes'], ['Contratos', 'servicecontracts'], ['Evidencias', 'evidence']],
  mobility: [['Corridas', 'rides'], ['Rotas', 'routes'], ['Paradas', 'stops'], ['Bilhetes', 'tickets'], ['Tarifas', 'farerules']],
  jobs: [['Curriculos', 'resumes'], ['Experiencias', 'employmentrecords'], ['Documentos', 'resumedocuments'], ['Vagas', 'jobpostings'], ['Candidaturas', 'applications'], ['Logs de acesso', 'resumeaccesslogs']],
  erp: [['Contas', 'accounts'], ['Contas a pagar', 'payables'], ['Contas a receber', 'receivables'], ['Centros de custo', 'costcenters'], ['Documentos fiscais', 'fiscaldocuments']],
  wms: [['Armazens', 'warehouses'], ['Enderecos', 'bins'], ['Inventario', 'inventory'], ['Ondas de picking', 'pickingwaves'], ['Expedicoes', 'shipments']],
  tms: [['Transportadoras', 'carriers'], ['Fretes', 'freights'], ['Rotas', 'routes'], ['Comprovantes', 'proofsofdelivery'], ['Auditorias', 'freightaudits']],
  crm: [['Leads', 'leads'], ['Oportunidades', 'opportunities'], ['Atividades', 'activities'], ['Campanhas', 'campaigns']],
  bpm: [['Processos', 'processes'], ['Instancias', 'workflowinstances'], ['Tarefas', 'tasks'], ['Politicas de SLA', 'slapolicies']],
  document: [['Pastas', 'folders'], ['Documentos', 'documents'], ['Versoes', 'versions'], ['Retencao', 'retentionpolicies']],
  hr: [['Colaboradores', 'employees'], ['Folhas', 'payrollruns'], ['Candidatos', 'candidates'], ['Cursos', 'courses'], ['Saude ocupacional', 'occupationalrecords']],
  health: [['Pacientes', 'patients'], ['Agendamentos', 'appointments'], ['Prontuarios', 'medicalrecords'], ['Prescricoes', 'prescriptions'], ['Leitos', 'beds']],
  vision: [['Dispositivos', 'devices'], ['Streams', 'streams'], ['Gravacoes', 'recordings'], ['Alertas', 'motionalerts']],
  legal: [['Processos', 'cases'], ['Prazos', 'deadlines'], ['Audiencias', 'hearings'], ['Contratos', 'legalcontracts']],
  property: [['Imoveis', 'properties'], ['Unidades', 'units'], ['Locacoes', 'leases'], ['Assembleias', 'assemblies'], ['Manutencoes', 'maintenanceorders']],
  bi: [['Datasets', 'datasets'], ['Dashboards', 'dashboards'], ['Indicadores', 'indicators'], ['Exportacoes', 'exports']],
  ai_core: [['Memorias de IA', 'aimemories'], ['Moderacao', 'moderationdecisions'], ['Execucoes de modelos', 'modelruns']],
  api_hub: [['Clientes', 'apiclients'], ['Chaves', 'apikeys'], ['Webhooks', 'webhooks'], ['Integracoes', 'integrationruns']],
}

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })

const ModuleDashboard = ({ module, title, records }: ModuleDashboardProps) => {
  const [updatedAt, setUpdatedAt] = useState(() => new Date())
  const operations = MODULE_OPERATIONS[module] ?? []
  const metrics = useMemo(() => {
    const completed = records.filter((record) => ['Concluido', 'Aprovado'].includes(record.status ?? '')).length
    const active = records.filter((record) => record.status === 'Ativo').length
    return [
      ['Registros monitorados', records.length.toString(), '+12% no periodo'],
      ['Operacoes ativas', active.toString(), 'fluxos em andamento'],
      ['Taxa de conclusao', `${Math.round((completed / Math.max(records.length, 1)) * 100)}%`, 'SLA demonstrativo'],
      ['Volume processado', currency.format(records.reduce((total, record) => total + (record.value ?? 0), 0)), 'base ficticia coerente'],
    ]
  }, [records])

  const exportReport = () => {
    const rows = [['id', 'nome', 'status', 'regiao', 'valor'], ...records.map((record) => [record.id, record.name ?? record.title ?? '', record.status ?? '', record.region ?? '', String(record.value ?? '')])]
    const csv = rows.map((row) => row.map((cell) => `"${cell.replaceAll('"', '""')}"`).join(';')).join('\n')
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `all-in-one-${module}-relatorio.csv`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <main className="module-dashboard container">
      <section className="dashboard-heading">
        <div><p className="dashboard-kicker">Central operacional · dados demonstrativos</p><h1>{title}</h1><p>Visao executiva e atalhos para todas as operacoes do modulo.</p></div>
        <div className="dashboard-toolbar"><button type="button" className="btn-secondary" onClick={() => setUpdatedAt(new Date())}>Atualizar indicadores</button><button type="button" className="btn-primary" onClick={exportReport}>Exportar relatorio</button></div>
      </section>

      <section className="dashboard-metrics" aria-label="Indicadores do modulo">
        {metrics.map(([label, value, detail], index) => <article key={label}><span>{String(index + 1).padStart(2, '0')}</span><p>{label}</p><strong>{value}</strong><small>{detail}</small></article>)}
      </section>

      <div className="dashboard-grid">
        <section className="dashboard-panel dashboard-flow"><div className="panel-heading"><div><p className="dashboard-kicker">Fluxo operacional</p><h2>Desempenho por status</h2></div><small>Atualizado {updatedAt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</small></div>
          {['Ativo', 'Em analise', 'Concluido', 'Agendado', 'Aprovado'].map((status, index) => { const count = records.filter((record) => record.status === status).length; return <div className="status-bar" key={status}><span>{status}</span><div><i style={{ width: `${Math.max(12, count * 10 + index * 4)}%` }} /></div><strong>{count}</strong></div> })}
        </section>
        <section className="dashboard-panel"><div className="panel-heading"><div><p className="dashboard-kicker">Navegacao</p><h2>Operacoes do modulo</h2></div><small>{operations.length} areas</small></div><div className="operation-grid">{operations.map(([label, path]) => <Link key={path} to={`/${module}/${path}`}><span>↗</span><strong>{label}</strong><small>Abrir operacao</small></Link>)}</div></section>
      </div>

      <section className="dashboard-panel dashboard-activity"><div className="panel-heading"><div><p className="dashboard-kicker">Atividade recente</p><h2>Ultimos registros</h2></div><Link to={operations[0] ? `/${module}/${operations[0][1]}` : '/'}>Ver operacao completa →</Link></div>
        <div className="activity-table" role="table"><div className="activity-row activity-header" role="row"><span>Registro</span><span>Regiao</span><span>Status</span><span>Valor</span></div>{records.slice(0, 10).map((record) => <div className="activity-row" role="row" key={record.id}><strong>{record.name ?? record.title}</strong><span>{record.region}</span><span><i className="status-dot" />{record.status}</span><span>{currency.format(record.value ?? 0)}</span></div>)}</div>
      </section>
    </main>
  )
}

export default ModuleDashboard

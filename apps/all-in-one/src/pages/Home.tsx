import { Link } from "react-router-dom";
import "./Home.css";

const experiences = [
  [
    "01",
    "◉",
    "Pessoas",
    "Compras, mobilidade, servicos, financas, saude e carreira em uma jornada unica.",
  ],
  ["02", "◆", "Empresas", "Gestao integrada de clientes, estoque, documentos, pessoas e operacao."],
  [
    "03",
    "↗",
    "Entregadores",
    "Trabalho, rotas, entregas, ganhos e seguranca em uma unica experiencia.",
  ],
  ["04", "✦", "Prestadores", "Oferta de servicos, agenda, execucao e relacionamento com clientes."],
  [
    "05",
    "⌑",
    "Saude",
    "Cuidado conectado, acesso simples e informacoes organizadas com seguranca.",
  ],
  ["06", "◎", "Mobilidade", "Rotas, viagens, tarifas e operacao integradas ao mesmo ecossistema."],
] as const;

const modules = [
  ["identity", "Identidade", "◉", "Usuarios, sessoes, verificacoes e consentimentos."],
  ["business", "Business", "◆", "Empresas, equipes, unidades e conformidade KYB."],
  ["permissions", "Permissoes", "⌘", "Funcoes, politicas RBAC/ABAC e escopos de acesso."],
  ["finance", "Financeiro", "R$", "Wallets, ledger, recebimentos, escrow e conciliacoes."],
  ["marketplace", "Marketplace", "▣", "Lojas, produtos, pedidos, avaliacoes e disputas."],
  ["stock", "STOCK", "▤", "Catálogo curado, fornecedores homologados, pedido sob demanda e tracking."],
  ["delivery", "Delivery", "↗", "Solicitacoes, cotacoes, seguros e comprovantes."],
  ["riders", "Riders", "◈", "Perfis, documentos, veiculos e avaliacoes."],
  ["services", "Servicos", "✦", "Solicitacoes, prestadores, agenda e execucao."],
  ["mobility", "Mobilidade", "◎", "Rotas, paradas, viagens, tarifas e bilhetes."],
  ["jobs", "Jobs", "⌑", "Vagas, curriculos, candidaturas e CTPS Digital."],
  ["erp", "ERP", "▦", "Contas, recebiveis, centros de custo e documentos fiscais."],
  ["wms", "WMS", "▥", "Enderecos, movimentacoes, picking e inventarios."],
  ["tms", "TMS", "⇄", "Cargas, transportadoras, rotas e acompanhamento."],
  ["crm", "CRM", "◇", "Leads, oportunidades, atividades e campanhas."],
  ["bpm", "BPM", "⟳", "Processos, tarefas, instancias e politicas de SLA."],
  ["document", "Documentos", "▧", "Arquivos, versoes, retencao e compartilhamento seguro."],
  ["hr", "RH", "♙", "Colaboradores, vinculos, jornadas e desenvolvimento."],
  ["health", "Saude", "✚", "Jornadas de cuidado, agendamentos e servicos de saude."],
  ["legal", "Legal", "§", "Contratos, politicas, obrigacoes e registros legais."],
  ["property", "Propriedades", "⌂", "Imoveis, unidades, contratos e manutencao."],
  ["bi", "BI", "▥", "Metricas, analises e paineis de toda a operacao."],
  ["ai_core", "Nucleo de IA", "✧", "Assistentes, memorias consentidas e automacoes inteligentes."],
  ["api_hub", "API Hub", "{ }", "APIs, chaves, contratos e observabilidade."],
] as const;

const Home = () => (
  <div className="aio-home" id="inicio">
    <header className="aio-topbar">
      <a className="aio-brand" href="#inicio" aria-label="All in One - inicio">
        <img src="/assets/brand/all-in-one-logo-official.png" alt="All in One" />
      </a>
      <nav aria-label="Navegacao principal">
        <a href="#experiencias">Experiencias</a>
        <a href="#modulos">Modulos</a>
        <a href="#arquitetura">Plataforma</a>
      </nav>
      <a className="aio-nav-cta" href="#modulos">
        Explorar
      </a>
    </header>

    <section className="aio-hero">
      <div className="aio-aurora aio-aurora-one" />
      <div className="aio-aurora aio-aurora-two" />
      <div className="aio-hero-copy">
        <p className="aio-eyebrow">
          <span /> Ecossistema digital integrado
        </p>
        <h1>
          Todos os sistemas.
          <br />
          <em>Uma unica plataforma.</em>
        </h1>
        <p className="aio-lead">
          O All in One conecta pessoas, empresas, entregadores, prestadores e operacoes em uma
          experiencia modular, segura e inteligente.
        </p>
        <div className="aio-actions">
          <a className="aio-primary" href="#experiencias">
            Conhecer a plataforma <span>↗</span>
          </a>
          <a className="aio-secondary" href="#arquitetura">
            Ver como funciona
          </a>
        </div>
        <div className="aio-stats" aria-label="Resumo da plataforma">
          <div>
            <strong>24</strong>
            <span>microservicos</span>
          </div>
          <div>
            <strong>175</strong>
            <span>telas Stitch</span>
          </div>
          <div>
            <strong>1</strong>
            <span>identidade</span>
          </div>
        </div>
      </div>
      <div className="aio-hero-mark" aria-hidden="true">
        <div className="aio-orbit aio-orbit-one" />
        <div className="aio-orbit aio-orbit-two" />
        <img src="/assets/brand/all-in-one-logo-official.png" alt="" />
      </div>
    </section>

    <section className="aio-section" id="experiencias">
      <div className="aio-section-heading">
        <p className="aio-eyebrow">
          <span /> Um ecossistema, varias jornadas
        </p>
        <h2>Uma experiencia para cada forma de fazer.</h2>
        <p>
          A mesma identidade conecta todas as superficies sem fragmentar dados, contexto ou
          seguranca.
        </p>
      </div>
      <div className="aio-surface-grid">
        {experiences.map(([number, icon, title, description]) => (
          <article className="aio-surface-card" key={title}>
            <span className="aio-card-index">{number}</span>
            <div className="aio-surface-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{description}</p>
            <a href="#modulos">
              Ver modulos <span>→</span>
            </a>
          </article>
        ))}
      </div>
    </section>

    <section className="aio-section aio-module-section" id="modulos">
      <div className="aio-section-heading compact">
        <p className="aio-eyebrow">
          <span /> Plataforma modular
        </p>
        <h2>24 capacidades que trabalham como uma só.</h2>
        <p>Cada card abre diretamente o dashboard Stitch funcional do modulo.</p>
      </div>
      <div className="aio-module-grid">
        {modules.map(([slug, title, icon, description], index) => (
          <article className="aio-module-card" key={slug}>
            <div className="aio-module-card-top">
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{title}</strong>
              <i>{icon}</i>
            </div>
            <p>{description}</p>
            <Link to={`/${slug}`}>
              Abrir dashboard <span>→</span>
            </Link>
          </article>
        ))}
      </div>
    </section>

    <section className="aio-architecture" id="arquitetura">
      <div>
        <p className="aio-eyebrow">
          <span /> Base preparada para crescer
        </p>
        <h2>
          Dados conectados.
          <br />
          Operacoes independentes.
        </h2>
        <p>
          Uma identidade central organiza permissoes e contexto. Cada dominio evolui por APIs e
          eventos, mantendo auditoria, seguranca e consistencia.
        </p>
        <ul>
          <li>
            <i>01</i>
            <span>
              <strong>Identidade unica</strong> para pessoas, empresas e operacoes.
            </span>
          </li>
          <li>
            <i>02</i>
            <span>
              <strong>Arquitetura modular</strong> com servicos especializados.
            </span>
          </li>
          <li>
            <i>03</i>
            <span>
              <strong>Seguranca por padrao</strong> com autorizacao e auditoria.
            </span>
          </li>
        </ul>
      </div>
      <div className="aio-architecture-visual" aria-label="Diagrama da arquitetura All in One">
        <div className="aio-core">
          <img src="/assets/brand/all-in-one-logo-official.png" alt="All in One" />
        </div>
        <span className="node one">Identidade</span>
        <span className="node two">Eventos</span>
        <span className="node three">APIs</span>
        <span className="node four">Dados</span>
      </div>
    </section>

    <footer className="aio-footer">
      <img src="/assets/brand/all-in-one-logo-official.png" alt="All in One" />
      <p>Todos os sistemas. Uma unica plataforma.</p>
      <a href="#inicio">Voltar ao inicio ↑</a>
    </footer>
  </div>
);

export default Home;

import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { BrandLogo } from './BrandLogo';

type NavigationScreen = {
  title: string;
  path: string;
  kind: 'visao_geral' | 'lista' | 'formulario' | 'configuracao' | 'relatorio';
};

type NavigationModule = {
  slug: string;
  title: string;
  category: 'Operacao' | 'Gestao' | 'Dados' | 'Configuracoes';
  state: 'mandatory' | 'active' | 'recommended';
  screens: NavigationScreen[];
};

const modulesData: NavigationModule[] = [
  {
    slug: 'business',
    title: 'Empresas',
    category: 'Configuracoes',
    state: 'mandatory',
    screens: [
      { title: 'Visao geral da empresa', path: '/business/business', kind: 'visao_geral' },
      { title: 'Empresas cadastradas', path: '/business/companies', kind: 'lista' },
      { title: 'Cadastrar empresa', path: '/business/companies-form', kind: 'formulario' },
      { title: 'Filiais', path: '/business/branches', kind: 'lista' },
      { title: 'Documentos da empresa', path: '/business/companydocuments', kind: 'lista' },
      { title: 'Ofertas do catalogo', path: '/business/catalogoffers', kind: 'lista' },
      { title: 'Usuarios da empresa', path: '/business/usercompanymemberships', kind: 'configuracao' },
    ],
  },
  {
    slug: 'permissions',
    title: 'Permissoes',
    category: 'Configuracoes',
    state: 'mandatory',
    screens: [
      { title: 'Papeis de acesso', path: '/permissions/roles', kind: 'configuracao' },
      { title: 'Permissoes', path: '/permissions/permissions', kind: 'configuracao' },
      { title: 'Usuarios e papeis', path: '/permissions/userroles', kind: 'configuracao' },
      { title: 'Politicas de acesso', path: '/permissions/accesspolicies', kind: 'configuracao' },
      { title: 'Alcadas de aprovacao', path: '/permissions/approvallimits', kind: 'configuracao' },
    ],
  },
  {
    slug: 'finance',
    title: 'Financeiro',
    category: 'Gestao',
    state: 'active',
    screens: [
      { title: 'Visao financeira', path: '/finance/finance', kind: 'visao_geral' },
      { title: 'Carteiras', path: '/finance/wallets', kind: 'lista' },
      { title: 'Lancamentos do livro-razão', path: '/finance/ledgerentries', kind: 'lista' },
      { title: 'Faturas', path: '/finance/invoices', kind: 'lista' },
      { title: 'Split de pagamento', path: '/finance/splits', kind: 'lista' },
      { title: 'Escrow', path: '/finance/escrows', kind: 'lista' },
    ],
  },
  {
    slug: 'marketplace',
    title: 'Marketplace',
    category: 'Operacao',
    state: 'active',
    screens: [
      { title: 'Visao do marketplace', path: '/marketplace/marketplace', kind: 'visao_geral' },
      { title: 'Lojas', path: '/marketplace/stores', kind: 'lista' },
      { title: 'Produtos', path: '/marketplace/products', kind: 'lista' },
      { title: 'Cadastrar produto', path: '/marketplace/products-form', kind: 'formulario' },
      { title: 'Pedidos', path: '/marketplace/orders', kind: 'lista' },
      { title: 'Avaliacoes', path: '/marketplace/reviews', kind: 'lista' },
      { title: 'Disputas', path: '/marketplace/disputes', kind: 'lista' },
    ],
  },
  {
    slug: 'erp',
    title: 'ERP',
    category: 'Gestao',
    state: 'recommended',
    screens: [
      { title: 'Visao do ERP', path: '/erp/erp', kind: 'visao_geral' },
      { title: 'Contas', path: '/erp/accounts', kind: 'lista' },
      { title: 'Centros de custo', path: '/erp/costcenters', kind: 'lista' },
      { title: 'Contas a pagar', path: '/erp/payables', kind: 'lista' },
      { title: 'Contas a receber', path: '/erp/receivables', kind: 'lista' },
      { title: 'Documentos fiscais', path: '/erp/fiscaldocuments', kind: 'relatorio' },
    ],
  },
  {
    slug: 'stock',
    title: 'Estoque',
    category: 'Operacao',
    state: 'recommended',
    screens: [
      { title: 'Visao de estoque', path: '/stock/stock', kind: 'visao_geral' },
      { title: 'Produtos de catalogo', path: '/stock/catalogproducts', kind: 'lista' },
      { title: 'Fornecedores', path: '/stock/suppliers', kind: 'lista' },
      { title: 'Regras de preco', path: '/stock/pricerules', kind: 'lista' },
      { title: 'Pedidos a fornecedores', path: '/stock/supplierorders', kind: 'lista' },
    ],
  },
  {
    slug: 'delivery',
    title: 'Entregas',
    category: 'Operacao',
    state: 'recommended',
    screens: [
      { title: 'Visao de entregas', path: '/delivery/delivery', kind: 'visao_geral' },
      { title: 'Solicitacoes de entrega', path: '/delivery/deliveryrequests', kind: 'lista' },
      { title: 'Cotacoes', path: '/delivery/quotes', kind: 'lista' },
      { title: 'Atribuicoes', path: '/delivery/assignments', kind: 'lista' },
      { title: 'Comprovantes', path: '/delivery/proofs', kind: 'lista' },
    ],
  },
  {
    slug: 'jobs',
    title: 'Vagas e candidatos',
    category: 'Gestao',
    state: 'recommended',
    screens: [
      { title: 'Visao de vagas', path: '/jobs/jobs', kind: 'visao_geral' },
      { title: 'Vagas', path: '/jobs/jobpostings', kind: 'lista' },
      { title: 'Publicar vaga', path: '/jobs/jobpostings-form', kind: 'formulario' },
      { title: 'Candidaturas', path: '/jobs/applications', kind: 'lista' },
      { title: 'Curriculos', path: '/jobs/resumes', kind: 'lista' },
    ],
  },
  {
    slug: 'bi',
    title: 'Analises e indicadores',
    category: 'Dados',
    state: 'recommended',
    screens: [
      { title: 'Visao de indicadores', path: '/bi/bi', kind: 'visao_geral' },
      { title: 'Paineis', path: '/bi/dashboards', kind: 'relatorio' },
      { title: 'Indicadores', path: '/bi/indicators', kind: 'relatorio' },
      { title: 'Conjuntos de dados', path: '/bi/datasets', kind: 'lista' },
      { title: 'Exportacoes', path: '/bi/exports', kind: 'lista' },
    ],
  },
  {
    slug: 'api_hub',
    title: 'Integracoes e APIs',
    category: 'Configuracoes',
    state: 'recommended',
    screens: [
      { title: 'Visao de integracoes', path: '/api_hub/api_hub', kind: 'visao_geral' },
      { title: 'Clientes de API', path: '/api_hub/apiclients', kind: 'configuracao' },
      { title: 'Chaves de API', path: '/api_hub/apikeys', kind: 'configuracao' },
      { title: 'Webhooks', path: '/api_hub/webhooks', kind: 'configuracao' },
      { title: 'Execucoes de integracao', path: '/api_hub/integrationruns', kind: 'relatorio' },
    ],
  },
];

const categoryOrder: NavigationModule['category'][] = ['Operacao', 'Gestao', 'Dados', 'Configuracoes'];
const visibleStates: NavigationModule['state'][] = ['mandatory', 'active', 'recommended'];

const statusLabel: Record<NavigationModule['state'], string> = {
  mandatory: 'Obrigatorio',
  active: 'Ativo',
  recommended: 'Recomendado',
};

const Navigation: React.FC = () => {
  const [openModule, setOpenModule] = useState<string | null>('business');
  const [filter, setFilter] = useState('');

  const groupedModules = useMemo(() => {
    const normalizedFilter = filter.trim().toLowerCase();
    const visibleModules = modulesData
      .filter(module => visibleStates.includes(module.state))
      .filter(module => {
        if (!normalizedFilter) return true;
        return module.title.toLowerCase().includes(normalizedFilter) || module.screens.some(screen => screen.title.toLowerCase().includes(normalizedFilter));
      });

    return categoryOrder.map(category => ({
      category,
      modules: visibleModules.filter(module => module.category === category),
    })).filter(group => group.modules.length > 0);
  }, [filter]);

  return (
    <nav className="side-nav" aria-label="Navegacao principal do painel empresarial">
      <div className="nav-header" style={{ padding: '24px 16px', borderBottom: '2px solid #17211c', marginBottom: '16px', background: '#126b45' }}>
        <Link to="/" className="logo-container" style={{ display: 'flex', flexDirection: 'column', gap: '8px', textDecoration: 'none' }}>
          <BrandLogo alt="All-in-One" maxWidth={120} />
          <div style={{ color: '#fff', fontSize: '14px', fontWeight: 900, letterSpacing: '1px', textTransform: 'uppercase' }}>Unidade empresarial</div>
        </Link>
      </div>

      <div className="nav-section">
        <h3>Painel administrativo</h3>
        <label style={{ display: 'block', padding: '0 16px 12px' }}>
          <span style={{ display: 'block', fontSize: '12px', fontWeight: 800, marginBottom: '6px', color: '#536159' }}>Buscar modulo ou tela</span>
          <input
            aria-label="Buscar modulo ou tela"
            value={filter}
            onChange={event => setFilter(event.target.value)}
            placeholder="Ex.: produtos, financeiro, vagas"
            style={{ width: '100%', border: '2px solid #17211c', borderRadius: '10px', padding: '10px 12px', fontSize: '14px' }}
          />
        </label>

        {groupedModules.map(group => (
          <section key={group.category} aria-labelledby={`nav-${group.category}`}>
            <h4 id={`nav-${group.category}`} style={{ padding: '12px 16px 6px', margin: 0, fontSize: '12px', color: '#536159', textTransform: 'uppercase', letterSpacing: '1px' }}>{group.category}</h4>
            <ul>
              {group.modules.map(module => (
                <li key={module.slug} className="nav-item-group" style={{ marginBottom: '4px' }}>
                  <button
                    type="button"
                    className={`module-link ${openModule === module.slug ? 'active' : ''}`}
                    onClick={() => setOpenModule(openModule === module.slug ? null : module.slug)}
                    aria-expanded={openModule === module.slug}
                    style={{
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      width: '100%',
                      padding: '12px 16px',
                      fontWeight: 700,
                      border: '2px solid transparent',
                      background: openModule === module.slug ? '#e2f2ea' : 'transparent',
                      borderColor: openModule === module.slug ? '#17211c' : 'transparent',
                      boxShadow: openModule === module.slug ? '4px 4px 0px #17211c' : 'none',
                      color: '#17211c',
                      textAlign: 'left',
                    }}
                  >
                    <span className="title" style={{ flex: 1 }}>{module.title}</span>
                    <span style={{ marginRight: '8px', fontSize: '10px', color: '#536159' }}>{statusLabel[module.state]}</span>
                    <span style={{ fontSize: '10px' }}>{openModule === module.slug ? '▼' : '▶'}</span>
                  </button>
                  {openModule === module.slug && (
                    <ul className="sub-menu" style={{ listStyle: 'none', padding: '8px 0', background: '#f9fafa', borderLeft: '2px solid #17211c', marginLeft: '24px' }}>
                      {module.screens.map(screen => (
                        <li key={screen.path}>
                          <Link to={screen.path} style={{ fontSize: '13px', padding: '8px 16px', display: 'block', color: '#536159', textDecoration: 'none' }}>
                            {screen.title}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </nav>
  );
};

export default Navigation;

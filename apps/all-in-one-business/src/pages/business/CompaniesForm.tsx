import React, { useMemo, useState } from 'react';
import {
  type BusinessKind,
  type BusinessClassificationInput,
  recommendBusinessModules,
} from '../../modules/moduleRecommendationRules';
import { applyBusinessModuleRecommendations, businessModulesApiEnabled } from '../../modules/businessModuleApi';

const DEMO_COMPANY_ID = '00000000-0000-4000-8000-000000000001';

const businessKindOptions: Array<{ value: BusinessKind; label: string }> = [
  { value: 'physical_store', label: 'Loja física' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'dropshipping', label: 'Dropshipping' },
  { value: 'restaurant', label: 'Restaurante' },
  { value: 'services_provider', label: 'Prestadora de serviços' },
  { value: 'carrier', label: 'Transportadora' },
  { value: 'clinic', label: 'Clínica' },
  { value: 'industry', label: 'Indústria' },
  { value: 'office', label: 'Escritório administrativo' },
  { value: 'autonomous', label: 'Autônomo' },
  { value: 'rider', label: 'Entregador' },
  { value: 'driver_partner', label: 'Motorista parceiro' },
];

const stateLabel = {
  mandatory: 'Obrigatório',
  active: 'Ativo automático',
  recommended: 'Recomendado',
  optional: 'Opcional',
  hidden: 'Oculto',
  disabled: 'Desativado',
  blocked_by_plan: 'Bloqueado pelo plano',
};

const stateTone: Record<string, string> = {
  mandatory: '#126b45',
  active: '#19764c',
  recommended: '#946200',
  optional: '#536159',
  hidden: '#6b7280',
  disabled: '#991b1b',
  blocked_by_plan: '#7c2d12',
};

const fieldStyle: React.CSSProperties = { padding: '12px', border: '2px solid #17211c', borderRadius: 4, width: '100%' };
const labelStyle: React.CSSProperties = { fontWeight: 800, display: 'grid', gap: 8 };

const CompaniesForm: React.FC = () => {
  const [form, setForm] = useState<BusinessClassificationInput & {
    legalName: string;
    tradeName: string;
    cnpj: string;
    companySize: string;
    branchCount: string;
    employeeCount: string;
    businessDescription: string;
  }>({
    legalName: '',
    tradeName: '',
    cnpj: '',
    companySize: 'micro',
    branchCount: '1',
    employeeCount: '1-5',
    businessDescription: '',
    businessKind: 'ecommerce',
    hasPhysicalStock: true,
    sellsOnline: true,
    performsDelivery: true,
    hiresPeople: false,
    issuesFiscalDocuments: true,
    operatesFleet: false,
    hasWarehouse: false,
  });

  const [savedMessage, setSavedMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [saving, setSaving] = useState(false);
  const recommendations = useMemo(() => recommendBusinessModules(form), [form]);
  const activeCount = recommendations.filter(module => ['mandatory', 'active'].includes(module.state)).length;
  const recommendedCount = recommendations.filter(module => module.state === 'recommended').length;
  const hiddenCount = recommendations.filter(module => module.state === 'hidden').length;

  const update = <K extends keyof typeof form>(key: K, value: (typeof form)[K]) => {
    setSavedMessage('');
    setErrorMessage('');
    setForm(current => ({ ...current, [key]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setErrorMessage('');
    try {
      if (businessModulesApiEnabled) {
        const result = await applyBusinessModuleRecommendations(DEMO_COMPANY_ID, form);
        setSavedMessage(`Cadastro enviado ao back-end. ${result.modules.length} módulos foram classificados, aplicados e auditados para a empresa.`);
        return;
      }
      setSavedMessage('Cadastro validado localmente. Configure VITE_API_HUB_URL e VITE_API_HUB_TOKEN para aplicar a classificação e os módulos no back-end Business.');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Não foi possível aplicar os módulos no back-end. Seus dados foram preservados.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container">
      <section className="hero a1-module-hero" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: '2.3rem', fontWeight: 900, marginBottom: 12 }}>Cadastre-se</h1>
        <p style={{ color: '#536159', fontSize: '1.05rem' }}>
          Informe os dados principais da empresa. O sistema classifica o perfil operacional e seleciona automaticamente os módulos adequados, ocultando o que não fizer sentido para a operação inicial.
        </p>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(320px, 0.8fr)', gap: 24, alignItems: 'start' }}>
        <form className="neo-form neo-brutalism" onSubmit={handleSubmit} style={{ background: '#fff', padding: 24, border: '3px solid #17211c', boxShadow: '6px 6px 0 #17211c' }}>
          <h2 style={{ marginBottom: 20, color: '#126b45' }}>Dados essenciais</h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 16, marginBottom: 16 }}>
            <label style={labelStyle}>Razão social
              <input value={form.legalName} onChange={event => update('legalName', event.target.value)} required placeholder="Ex.: Brasil Desconto Tecnologia Ltda." style={fieldStyle} />
            </label>
            <label style={labelStyle}>Nome fantasia
              <input value={form.tradeName} onChange={event => update('tradeName', event.target.value)} placeholder="Ex.: Brasil Desconto" style={fieldStyle} />
            </label>
            <label style={labelStyle}>CNPJ
              <input value={form.cnpj} onChange={event => update('cnpj', event.target.value)} required inputMode="numeric" placeholder="00.000.000/0000-00" style={fieldStyle} />
            </label>
            <label style={labelStyle}>Tipo de empresa
              <select value={form.businessKind} onChange={event => update('businessKind', event.target.value as BusinessKind)} style={fieldStyle}>
                {businessKindOptions.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
            </label>
            <label style={labelStyle}>CNAE principal
              <input value={form.cnaePrimary ?? ''} onChange={event => update('cnaePrimary', event.target.value)} placeholder="Ex.: 47.89-0-99" style={fieldStyle} />
            </label>
            <label style={labelStyle}>Porte
              <select value={form.companySize} onChange={event => update('companySize', event.target.value)} style={fieldStyle}>
                <option value="micro">Microempresa</option>
                <option value="small">Pequena empresa</option>
                <option value="medium">Média empresa</option>
                <option value="large">Grande empresa</option>
              </select>
            </label>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 16, marginBottom: 20 }}>
            <label style={labelStyle}>Filiais
              <input value={form.branchCount} onChange={event => update('branchCount', event.target.value)} inputMode="numeric" style={fieldStyle} />
            </label>
            <label style={labelStyle}>Funcionários
              <select value={form.employeeCount} onChange={event => update('employeeCount', event.target.value)} style={fieldStyle}>
                <option value="1-5">1 a 5</option>
                <option value="6-20">6 a 20</option>
                <option value="21-100">21 a 100</option>
                <option value="101+">101 ou mais</option>
              </select>
            </label>
          </div>

          <h2 style={{ margin: '24px 0 16px', color: '#126b45' }}>Operação</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 12, marginBottom: 20 }}>
            {[
              ['hasPhysicalStock', 'Possui estoque físico'],
              ['sellsOnline', 'Vende pela internet'],
              ['performsDelivery', 'Realiza entregas'],
              ['hiresPeople', 'Contrata pessoas'],
              ['issuesFiscalDocuments', 'Emite documentos fiscais'],
              ['operatesFleet', 'Opera frota própria ou terceira'],
              ['hasWarehouse', 'Possui armazém ou centro de distribuição'],
            ].map(([key, label]) => (
              <label key={key} style={{ display: 'flex', gap: 10, alignItems: 'center', fontWeight: 700 }}>
                <input type="checkbox" checked={Boolean(form[key as keyof typeof form])} onChange={event => update(key as keyof typeof form, event.target.checked as never)} />
                {label}
              </label>
            ))}
          </div>

          <label style={{ ...labelStyle, marginBottom: 20 }}>Descrição da atividade
            <textarea value={form.businessDescription} onChange={event => update('businessDescription', event.target.value)} placeholder="Explique o que a empresa vende, entrega, produz ou administra." style={{ ...fieldStyle, minHeight: 120 }} />
          </label>

          {savedMessage && <div role="status" style={{ background: '#e2f2ea', border: '2px solid #126b45', padding: 12, marginBottom: 16, fontWeight: 700 }}>{savedMessage}</div>}
          {errorMessage && <div role="alert" style={{ background: '#fee2e2', border: '2px solid #991b1b', padding: 12, marginBottom: 16, fontWeight: 700 }}>{errorMessage}</div>}

          <div className="actions-row" style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
            <button type="button" className="btn-secondary" style={{ padding: '10px 20px' }}>Salvar rascunho</button>
            <button type="submit" className="btn-primary" disabled={saving} style={{ padding: '10px 20px' }}>
              {saving ? 'Aplicando módulos...' : 'Cadastre-se'}
            </button>
          </div>
        </form>

        <aside className="a1-card" style={{ background: '#fff', padding: 20, border: '3px solid #17211c', boxShadow: '6px 6px 0 #17211c' }}>
          <h2 style={{ color: '#126b45', marginBottom: 12 }}>Módulos sugeridos</h2>
          <p style={{ color: '#536159', fontSize: 13, marginBottom: 12 }}>
            {businessModulesApiEnabled ? 'Integração com back-end Business habilitada.' : 'Prévia local ativa; back-end será usado quando o API Hub estiver configurado.'}
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginBottom: 16 }}>
            <strong>{activeCount}<br /><span style={{ color: '#536159', fontSize: 12 }}>ativos</span></strong>
            <strong>{recommendedCount}<br /><span style={{ color: '#536159', fontSize: 12 }}>recomendados</span></strong>
            <strong>{hiddenCount}<br /><span style={{ color: '#536159', fontSize: 12 }}>ocultos</span></strong>
          </div>
          <div style={{ display: 'grid', gap: 10 }}>
            {recommendations.map(module => (
              <div key={module.moduleSlug} className="a1-card" style={{ border: '2px solid #17211c', padding: 12, background: module.state === 'hidden' ? '#f9fafa' : '#fff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                  <strong>{module.titlePtBr}</strong>
                  <span style={{ color: stateTone[module.state], fontWeight: 900 }}>{stateLabel[module.state]}</span>
                </div>
                <p style={{ margin: '8px 0 0', color: '#536159', fontSize: 13 }}>{module.explanationPtBr}</p>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
};

export default CompaniesForm;

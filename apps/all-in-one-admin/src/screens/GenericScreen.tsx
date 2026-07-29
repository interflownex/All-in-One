import { Icon } from "../icons";
import type { ScreenId } from "../types";

const content: Record<Exclude<ScreenId, "overview" | "approvals" | "modules">, { title: string; description: string; icon: "building" | "pulse" | "shield" | "chart" | "settings"; actions: string[] }> = {
  companies: { title: "Empresas e unidades", description: "Template para cadastro, KYB, planos, unidades e relacionamento institucional.", icon: "building", actions: ["Cadastrar empresa", "Revisar KYB", "Gerenciar unidades"] },
  operations: { title: "Operações em tempo real", description: "Template para filas, incidentes, jobs, integrações e saúde operacional.", icon: "pulse", actions: ["Abrir incidente", "Consultar jobs", "Ver integrações"] },
  security: { title: "Segurança e conformidade", description: "Template para acessos, auditoria, segredos, políticas e eventos sensíveis.", icon: "shield", actions: ["Revisar acessos", "Exportar auditoria", "Abrir política"] },
  reports: { title: "Relatórios executivos", description: "Template para indicadores, filtros, exportações e relatórios agendados.", icon: "chart", actions: ["Criar relatório", "Exportar CSV", "Agendar envio"] },
  settings: { title: "Configurações administrativas", description: "Template para ambientes, notificações, integrações e preferências do Admin.", icon: "settings", actions: ["Configurar ambiente", "Editar notificações", "Gerenciar integrações"] },
};

export function GenericScreen({ screen }: { screen: Exclude<ScreenId, "overview" | "approvals" | "modules"> }) {
  const item = content[screen];
  return (
    <div className="screen-stack">
      <section className="intro-row"><div><h2>{item.title}</h2><p>{item.description}</p></div><button className="primary-button" type="button"><Icon name={item.icon} size={17} />Ação principal</button></section>
      <section className="generic-layout">
        <article className="panel generic-hero"><div className="generic-hero__icon"><Icon name={item.icon} size={34} /></div><div><span>Template funcional</span><h3>Estrutura pronta para receber dados reais</h3><p>Os controles abaixo demonstram hierarquia, densidade, estados e responsividade sem simular uma operação produtiva.</p></div></article>
        <div className="generic-actions">{item.actions.map((action, index) => <button type="button" key={action}><span>{String(index + 1).padStart(2, "0")}</span><strong>{action}</strong><Icon name="arrow" size={17} /></button>)}</div>
      </section>
      <section className="state-grid">
        <article className="panel state-card"><span className="state-card__visual state-card__visual--loading" /><h4>Carregamento</h4><p>Esqueleto discreto, sem salto de layout.</p></article>
        <article className="panel state-card"><span className="state-card__visual state-card__visual--empty"><Icon name={item.icon} size={25} /></span><h4>Estado vazio</h4><p>Orienta a primeira ação com clareza.</p></article>
        <article className="panel state-card"><span className="state-card__visual state-card__visual--error">!</span><h4>Erro recuperável</h4><p>Explica o problema e oferece nova tentativa.</p></article>
        <article className="panel state-card"><span className="state-card__visual state-card__visual--success"><Icon name="check" size={25} /></span><h4>Sucesso</h4><p>Confirma a ação e mantém rastreabilidade.</p></article>
      </section>
    </div>
  );
}

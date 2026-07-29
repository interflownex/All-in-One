import { useMemo, useState } from "react";
import { approvals as initialApprovals } from "../data";
import { Icon } from "../icons";
import { StatusBadge } from "../components/StatusBadge";
import type { Approval } from "../types";

export function Approvals() {
  const [items, setItems] = useState(initialApprovals);
  const [selectedId, setSelectedId] = useState(initialApprovals[0].id);
  const [filter, setFilter] = useState<"Todos" | Approval["status"]>("Todos");
  const selected = items.find((item) => item.id === selectedId) ?? items[0];
  const filtered = useMemo(() => filter === "Todos" ? items : items.filter((item) => item.status === filter), [items, filter]);

  const updateStatus = (status: Approval["status"]) => {
    setItems((current) => current.map((item) => item.id === selected.id ? { ...item, status } : item));
  };

  return (
    <div className="screen-stack">
      <section className="intro-row"><div><h2>Fila de aprovações</h2><p>Revise solicitações críticas com contexto, trilha e decisão registrada.</p></div><button className="primary-button" type="button"><Icon name="chart" size={17} />Exportar fila</button></section>
      <div className="filter-tabs" role="tablist" aria-label="Filtrar aprovações">
        {(["Todos", "Pendente", "Em análise", "Aprovado"] as const).map((item) => <button role="tab" aria-selected={filter === item} className={filter === item ? "filter-tab filter-tab--active" : "filter-tab"} onClick={() => setFilter(item)} key={item} type="button">{item}</button>)}
      </div>
      <section className="approval-layout">
        <div className="approval-queue panel">
          <div className="queue-search"><Icon name="search" size={17} /><input placeholder="Buscar solicitação…" aria-label="Buscar solicitação" /></div>
          <div className="approval-queue__items">
            {filtered.map((approval) => (
              <button key={approval.id} type="button" onClick={() => setSelectedId(approval.id)} className={selected?.id === approval.id ? "approval-card approval-card--selected" : "approval-card"}>
                <div className="approval-card__top"><span>{approval.id}</span><span>{approval.age}</span></div>
                <strong>{approval.title}</strong>
                <p>{approval.subtitle}</p>
                <div className="approval-card__bottom"><span>{approval.type}</span><StatusBadge status={approval.status} /></div>
              </button>
            ))}
          </div>
        </div>
        {selected && (
          <article className="approval-detail panel">
            <div className="approval-detail__hero">
              <div className="approval-detail__icon"><Icon name={selected.type === "Empresa" ? "building" : selected.type === "Módulo" ? "grid" : selected.type === "Financeiro" ? "money" : "shield"} size={24} /></div>
              <div><span>{selected.id} · {selected.type}</span><h3>{selected.title}</h3><p>{selected.subtitle}</p></div>
            </div>
            <div className="detail-grid">
              <div><span>Prioridade</span><strong>{selected.priority}</strong></div>
              <div><span>Recebida</span><strong>{selected.age}</strong></div>
              <div><span>Status atual</span><StatusBadge status={selected.status} /></div>
              <div><span>Risco</span><strong>Baixo</strong></div>
            </div>
            <div className="audit-timeline">
              <h4>Trilha de auditoria</h4>
              <div><i /><p><strong>Solicitação criada</strong><span>Dados recebidos e validados no contrato inicial.</span></p><time>18:22</time></div>
              <div><i /><p><strong>Verificação automática</strong><span>Nenhum conflito crítico encontrado.</span></p><time>18:24</time></div>
              <div><i className="audit-timeline__pending" /><p><strong>Decisão administrativa</strong><span>Aguardando ação com justificativa.</span></p><time>agora</time></div>
            </div>
            <label className="decision-field"><span>Justificativa da decisão</span><textarea placeholder="Registre a evidência e o motivo da decisão." /></label>
            <div className="approval-actions"><button type="button" className="secondary-button" onClick={() => updateStatus("Em análise")}>Manter em análise</button><button type="button" className="primary-button" onClick={() => updateStatus("Aprovado")}><Icon name="check" size={17} />Aprovar</button></div>
          </article>
        )}
      </section>
    </div>
  );
}

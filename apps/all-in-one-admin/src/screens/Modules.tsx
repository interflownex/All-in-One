import { useMemo, useState } from "react";
import { modules as initialModules } from "../data";
import { Icon } from "../icons";
import { StatusBadge } from "../components/StatusBadge";

export function Modules() {
  const [records, setRecords] = useState(initialModules);
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => records.filter((item) => `${item.name} ${item.slug} ${item.audience}`.toLowerCase().includes(query.toLowerCase())), [query, records]);

  const toggle = (slug: string) => setRecords((current) => current.map((item) => item.slug === slug ? { ...item, enabled: !item.enabled } : item));

  return (
    <div className="screen-stack">
      <section className="intro-row"><div><h2>Governança de módulos</h2><p>Visibilidade, saúde e ativação sob uma fonte central de verdade.</p></div><button className="primary-button" type="button"><Icon name="grid" size={17} />Novo plano de ativação</button></section>
      <section className="module-summary">
        <div><span>Ativos</span><strong>{records.filter((item) => item.enabled).length}</strong></div>
        <div><span>Em homologação</span><strong>{records.filter((item) => item.status === "Homologação").length}</strong></div>
        <div><span>Bloqueados</span><strong>{records.filter((item) => item.status === "Bloqueado").length}</strong></div>
        <div><span>Saúde média</span><strong>{Math.round(records.reduce((sum, item) => sum + item.health, 0) / records.length)}%</strong></div>
      </section>
      <section className="panel modules-panel">
        <div className="module-toolbar"><div className="queue-search"><Icon name="search" size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar módulo…" aria-label="Buscar módulo" /></div><button className="select-button" type="button">Todos os públicos <Icon name="arrow" size={14} /></button></div>
        <div className="table-scroll">
          <table className="modules-table">
            <thead><tr><th>Módulo</th><th>Público</th><th>Status</th><th>Saúde</th><th>Incidentes</th><th>Disponível</th><th aria-label="Ações" /></tr></thead>
            <tbody>{filtered.map((module) => (
              <tr key={module.slug}>
                <td><div className="module-name"><span>{module.name.slice(0, 2).toUpperCase()}</span><div><strong>{module.name}</strong><small>{module.slug}</small></div></div></td>
                <td>{module.audience}</td>
                <td><StatusBadge status={module.status} /></td>
                <td><div className="health"><div><i style={{ width: `${module.health}%` }} /></div><span>{module.health}%</span></div></td>
                <td><span className={module.incidents > 0 ? "incident incident--active" : "incident"}>{module.incidents}</span></td>
                <td><button type="button" role="switch" aria-checked={module.enabled} aria-label={`${module.enabled ? "Desativar" : "Ativar"} ${module.name}`} className={module.enabled ? "toggle toggle--active" : "toggle"} onClick={() => toggle(module.slug)}><span /></button></td>
                <td><button className="icon-button icon-button--small" type="button" aria-label={`Abrir ${module.name}`}><Icon name="arrow" size={16} /></button></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

import { activity, approvals } from "../data";
import { Icon } from "../icons";
import { MetricCard } from "../components/MetricCard";
import { StatusBadge } from "../components/StatusBadge";

export function Dashboard({ onOpenApprovals }: { onOpenApprovals: () => void }) {
  return (
    <div className="screen-stack">
      <section className="intro-row">
        <div>
          <h2>Operação em um só lugar</h2>
          <p>Acompanhe saúde, aprovações e evolução dos módulos ativos.</p>
        </div>
        <div className="prototype-note"><span />Protótipo navegável</div>
      </section>

      <section className="metrics-grid" aria-label="Indicadores principais">
        <MetricCard label="Empresas ativas" value="2.340" delta="8,2% no período" icon="building" tone="green" />
        <MetricCard label="Usuários verificados" value="18.492" delta="5,1% no período" icon="users" tone="blue" />
        <MetricCard label="Pedidos processados" value="12.845" delta="11,4% no período" icon="orders" tone="violet" />
        <MetricCard label="Volume transacionado" value="R$ 1,28 mi" delta="6,7% no período" icon="money" tone="amber" />
      </section>

      <section className="dashboard-grid">
        <article className="panel panel--chart">
          <div className="panel__header">
            <div><p>Atividade operacional</p><h3>Evolução dos últimos 30 dias</h3></div>
            <button type="button" className="select-button">30 dias <Icon name="arrow" size={14} /></button>
          </div>
          <div className="chart-area" aria-label="Gráfico demonstrativo de atividade operacional">
            <div className="chart-axis"><span>12k</span><span>8k</span><span>4k</span><span>0</span></div>
            <svg viewBox="0 0 640 210" role="img" aria-label="Tendência ascendente de atividade">
              <defs>
                <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#39d98a" stopOpacity="0.32" />
                  <stop offset="100%" stopColor="#39d98a" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path className="chart-grid-line" d="M0 28H640M0 80H640M0 132H640M0 184H640" />
              <path className="chart-area-fill" d="M0 168 C55 150 72 158 110 132 S180 116 220 124 S288 89 325 104 S390 76 430 82 S505 48 550 62 S605 24 640 30 L640 210 L0 210 Z" />
              <path className="chart-line" d="M0 168 C55 150 72 158 110 132 S180 116 220 124 S288 89 325 104 S390 76 430 82 S505 48 550 62 S605 24 640 30" />
            </svg>
            <div className="chart-labels"><span>1 jul</span><span>8 jul</span><span>15 jul</span><span>22 jul</span><span>28 jul</span></div>
          </div>
        </article>

        <article className="panel panel--activity">
          <div className="panel__header"><div><p>Tempo real</p><h3>Atividades recentes</h3></div><button className="icon-button icon-button--small" type="button" aria-label="Mais opções"><Icon name="more" size={18} /></button></div>
          <div className="activity-list">
            {activity.map((item) => (
              <div className="activity-row" key={item.title}>
                <span className={`activity-row__marker activity-row__marker--${item.tone}`} />
                <div><strong>{item.title}</strong><small>{item.detail}</small></div>
                <time>{item.time}</time>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="panel approvals-preview">
        <div className="panel__header">
          <div><p>Fila de decisão</p><h3>Aprovações prioritárias</h3></div>
          <button className="text-button" type="button" onClick={onOpenApprovals}>Ver todas <Icon name="arrow" size={15} /></button>
        </div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>Solicitação</th><th>Tipo</th><th>Prioridade</th><th>Tempo</th><th>Status</th><th aria-label="Ações" /></tr></thead>
            <tbody>
              {approvals.slice(0, 3).map((approval) => (
                <tr key={approval.id}>
                  <td><strong>{approval.title}</strong><small>{approval.id}</small></td>
                  <td>{approval.type}</td>
                  <td><span className={`priority priority--${approval.priority.toLowerCase().replace("é", "e")}`}>{approval.priority}</span></td>
                  <td>{approval.age}</td>
                  <td><StatusBadge status={approval.status} /></td>
                  <td><button className="icon-button icon-button--small" type="button" aria-label={`Abrir ${approval.id}`}><Icon name="arrow" size={16} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

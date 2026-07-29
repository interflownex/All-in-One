import { Icon } from "../icons";
import type { IconName } from "../types";

type MetricCardProps = {
  label: string;
  value: string;
  delta: string;
  icon: IconName;
  tone?: "green" | "blue" | "violet" | "amber";
};

export function MetricCard({ label, value, delta, icon, tone = "green" }: MetricCardProps) {
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <div className="metric-card__header">
        <span>{label}</span>
        <span className="metric-card__icon"><Icon name={icon} size={18} /></span>
      </div>
      <strong>{value}</strong>
      <div className="metric-card__delta"><Icon name="trend" size={14} />{delta}</div>
    </article>
  );
}

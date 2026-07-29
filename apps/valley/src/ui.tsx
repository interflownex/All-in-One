import type { ApiItem } from './lib/api';
import { itemSubtitle, itemTitle } from './lib/api';

export function SectionHeader({ title, subtitle, actionLabel, onAction }: { title: string; subtitle: string; actionLabel?: string; onAction?: () => void }) {
  return <header className='section-header'><div><h1>{title}</h1><p>{subtitle}</p></div>{actionLabel && onAction && <button className='secondary' type='button' onClick={onAction}>{actionLabel}</button>}</header>;
}
export function StateCard({ text, tone, actionLabel, onAction }: { text: string; tone?: 'error'; actionLabel?: string; onAction?: () => void }) {
  return <div className={`state-card ${tone ?? ''}`}><p>{text}</p>{actionLabel && onAction && <button className='secondary' type='button' onClick={onAction}>{actionLabel}</button>}</div>;
}
export function Metric({ label, value }: { label: string; value: string }) { return <div className='metric'><strong>{value}</strong><span>{label}</span></div>; }
export function ResourceSummary({ title, items }: { title: string; items: ApiItem[] }) {
  if (!items.length) return null;
  return <div className='resource-section'><h2>{title}</h2><div className='card-list compact'>{items.map(item => <article className='data-card' key={item.id}><div><span className='eyebrow'>{item.status ?? 'sincronizado'}</span><h3>{itemTitle(item)}</h3><p>{itemSubtitle(item)}</p></div></article>)}</div></div>;
}
export function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  return <div className='modal-backdrop' role='presentation'><section className='modal' role='dialog' aria-modal='true' aria-label={title}><header><h2>{title}</h2><button type='button' onClick={onClose} aria-label='Fechar'>×</button></header><div>{children}</div></section></div>;
}

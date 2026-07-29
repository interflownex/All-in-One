export function StatusBadge({ status }: { status: string }) {
  const slug = status.toLowerCase().replaceAll(" ", "-").replace("ç", "c").replace("ã", "a");
  return <span className={`status-badge status-badge--${slug}`}>{status}</span>;
}

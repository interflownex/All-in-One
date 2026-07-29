export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`brand ${compact ? "brand--compact" : ""}`}>
      <img
        className="brand__logo"
        src="/brand/all-in-one-logo-official.png"
        alt="All in One"
      />
      {!compact && (
        <div className="brand__copy">
          <strong>A1 Admin</strong>
          <span>Centro de comando</span>
        </div>
      )}
    </div>
  );
}

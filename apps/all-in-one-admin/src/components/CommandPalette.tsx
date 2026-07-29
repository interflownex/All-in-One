import { navigation } from "../data";
import { Icon } from "../icons";
import type { ScreenId } from "../types";

export function CommandPalette({
  open,
  onClose,
  onNavigate,
}: {
  open: boolean;
  onClose: () => void;
  onNavigate: (screen: ScreenId) => void;
}) {
  if (!open) return null;
  return (
    <div className="command-overlay" role="presentation" onMouseDown={onClose}>
      <section className="command-palette" role="dialog" aria-modal="true" aria-label="Busca rápida" onMouseDown={(event) => event.stopPropagation()}>
        <div className="command-palette__input">
          <Icon name="search" size={20} />
          <input autoFocus placeholder="Buscar tela ou ação…" aria-label="Buscar tela ou ação" />
          <kbd>Esc</kbd>
        </div>
        <p>Acesso rápido</p>
        <div className="command-palette__list">
          {navigation.slice(0, 6).map((item) => (
            <button key={item.id} type="button" onClick={() => { onNavigate(item.id); onClose(); }}>
              <span><Icon name={item.icon} size={18} />{item.label}</span>
              <Icon name="arrow" size={15} />
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}

import { navigation } from "../data";
import { Icon } from "../icons";
import type { ScreenId } from "../types";
import { Brand } from "./Brand";

type TopbarProps = {
  active: ScreenId;
  onOpenCommand: () => void;
};

export function Topbar({ active, onOpenCommand }: TopbarProps) {
  const item = navigation.find((entry) => entry.id === active);
  return (
    <header className="topbar">
      <div className="topbar__mobile-brand"><Brand compact /></div>
      <div>
        <p className="topbar__context">Administração do ecossistema</p>
        <h1>{item?.label ?? "Visão geral"}</h1>
      </div>
      <div className="topbar__actions">
        <button className="command-button" type="button" onClick={onOpenCommand}>
          <Icon name="search" size={17} />
          <span>Buscar</span>
          <kbd>⌘ K</kbd>
        </button>
        <button className="icon-button" type="button" aria-label="Notificações">
          <Icon name="bell" size={19} />
          <span className="notification-dot" />
        </button>
        <button className="profile-button" type="button" aria-label="Abrir perfil do administrador">
          <span className="avatar">AN</span>
          <span className="profile-button__copy"><strong>Admin</strong><small>Super Admin</small></span>
          <Icon name="arrow" size={15} />
        </button>
      </div>
    </header>
  );
}

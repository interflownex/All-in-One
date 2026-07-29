import { navigation } from "../data";
import { Icon } from "../icons";
import type { ScreenId } from "../types";
import { Brand } from "./Brand";

type SidebarProps = {
  active: ScreenId;
  onNavigate: (screen: ScreenId) => void;
};

export function Sidebar({ active, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar" aria-label="Navegação principal">
      <Brand />
      <nav className="sidebar__nav">
        {navigation.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${active === item.id ? "nav-item--active" : ""}`}
            onClick={() => onNavigate(item.id)}
            type="button"
            aria-current={active === item.id ? "page" : undefined}
          >
            <Icon name={item.icon} size={19} />
            <span>{item.label}</span>
            {item.id === "approvals" && <span className="nav-item__count">4</span>}
          </button>
        ))}
      </nav>
      <div className="sidebar__footer">
        <div className="environment-pill">
          <span className="environment-pill__dot" />
          Ambiente de protótipo
        </div>
        <p>Dados demonstrativos, sem operação produtiva.</p>
      </div>
    </aside>
  );
}

import { navigation } from "../data";
import { Icon } from "../icons";
import type { ScreenId } from "../types";

const primary = ["overview", "approvals", "modules", "operations", "settings"] as ScreenId[];

export function MobileNav({ active, onNavigate }: { active: ScreenId; onNavigate: (screen: ScreenId) => void }) {
  return (
    <nav className="mobile-nav" aria-label="Navegação móvel">
      {primary.map((id) => {
        const item = navigation.find((entry) => entry.id === id)!;
        return (
          <button
            key={id}
            type="button"
            className={active === id ? "mobile-nav__item mobile-nav__item--active" : "mobile-nav__item"}
            onClick={() => onNavigate(id)}
            aria-current={active === id ? "page" : undefined}
          >
            <Icon name={item.icon} size={19} />
            <span>{item.shortLabel}</span>
            {id === "approvals" && <i>4</i>}
          </button>
        );
      })}
    </nav>
  );
}

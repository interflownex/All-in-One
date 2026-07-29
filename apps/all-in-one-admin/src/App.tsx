import { useEffect, useState } from "react";
import { CommandPalette } from "./components/CommandPalette";
import { MobileNav } from "./components/MobileNav";
import { Sidebar } from "./components/Sidebar";
import { Topbar } from "./components/Topbar";
import { Approvals } from "./screens/Approvals";
import { Dashboard } from "./screens/Dashboard";
import { GenericScreen } from "./screens/GenericScreen";
import { Modules } from "./screens/Modules";
import type { ScreenId } from "./types";
import "./styles.css";

export default function App() {
  const [screen, setScreen] = useState<ScreenId>("overview");
  const [commandOpen, setCommandOpen] = useState(false);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandOpen(true);
      }
      if (event.key === "Escape") setCommandOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const renderScreen = () => {
    if (screen === "overview") return <Dashboard onOpenApprovals={() => setScreen("approvals")} />;
    if (screen === "approvals") return <Approvals />;
    if (screen === "modules") return <Modules />;
    return <GenericScreen screen={screen} />;
  };

  return (
    <div className="app-shell">
      <Sidebar active={screen} onNavigate={setScreen} />
      <div className="workspace">
        <Topbar active={screen} onOpenCommand={() => setCommandOpen(true)} />
        <main className="content" id="main-content">{renderScreen()}</main>
      </div>
      <MobileNav active={screen} onNavigate={setScreen} />
      <CommandPalette open={commandOpen} onClose={() => setCommandOpen(false)} onNavigate={setScreen} />
    </div>
  );
}

import { useLayout, useOpenExternal } from "skybridge/web";
import { useToolInfo } from "../helpers.js";

const FALLBACK_APP_URL = "https://84e9680fcfa2a84551.v2.appdeploy.ai/";

const contextMarks: Record<string, string> = {
  PERSONAL: "PF",
  RIDER: "RI",
  BUSINESS: "PJ",
  ONE_SERVICE: "OS",
  PDV: "PDV",
};

export default function ValleyContexts() {
  const { output } = useToolInfo<"valley_list_contexts">();
  const { theme } = useLayout();
  const openExternal = useOpenExternal();
  const dark = theme === "dark";
  const contexts = output?.contexts ?? [];
  const appUrl = output?.appUrl ?? FALLBACK_APP_URL;

  const page = dark ? "#020617" : "#f8fafc";
  const panel = dark ? "#0f172a" : "#ffffff";
  const border = dark ? "#1e293b" : "#dbe4ee";
  const text = dark ? "#f8fafc" : "#0f172a";
  const muted = dark ? "#94a3b8" : "#475569";
  const accent = "#67e8f9";
  const accentText = "#082f49";

  return (
    <main
      style={{
        boxSizing: "border-box",
        width: "100%",
        maxWidth: 920,
        margin: "0 auto",
        padding: 20,
        borderRadius: 24,
        border: `1px solid ${border}`,
        background: page,
        color: text,
        fontFamily:
          '"Avenir Next", "Montserrat", "Trebuchet MS", system-ui, sans-serif',
      }}
    >
      <header
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: 16,
          marginBottom: 18,
        }}
      >
        <div>
          <div
            style={{
              marginBottom: 8,
              color: dark ? accent : "#0369a1",
              fontSize: 12,
              fontWeight: 800,
              letterSpacing: "0.16em",
              textTransform: "uppercase",
            }}
          >
            Valley Universal
          </div>
          <h1 style={{ margin: 0, fontSize: 26, lineHeight: 1.1 }}>
            Um aplicativo, cinco contextos
          </h1>
          <p
            style={{
              maxWidth: 680,
              margin: "10px 0 0",
              color: muted,
              fontSize: 14,
              lineHeight: 1.55,
            }}
          >
            Escolha o caminho que deseja conhecer. A disponibilidade real é
            confirmada pelo Valley depois da autenticação.
          </p>
        </div>
        <div
          aria-label="Identidade Valley"
          style={{
            display: "grid",
            flex: "0 0 auto",
            width: 48,
            height: 48,
            placeItems: "center",
            borderRadius: 16,
            background: accent,
            color: accentText,
            fontWeight: 900,
            letterSpacing: "0.08em",
          }}
        >
          V
        </div>
      </header>

      <section
        aria-label="Contextos do Valley"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 12,
        }}
      >
        {contexts.map((context) => (
          <article
            key={context.id}
            style={{
              display: "flex",
              minHeight: 128,
              flexDirection: "column",
              gap: 10,
              padding: 16,
              borderRadius: 18,
              border: `1px solid ${border}`,
              background: panel,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 10,
              }}
            >
              <strong style={{ fontSize: 17 }}>{context.label}</strong>
              <span
                style={{
                  display: "grid",
                  minWidth: 36,
                  height: 30,
                  padding: "0 8px",
                  placeItems: "center",
                  borderRadius: 10,
                  background: dark ? "#164e63" : "#cffafe",
                  color: dark ? "#cffafe" : "#155e75",
                  fontSize: 11,
                  fontWeight: 900,
                }}
              >
                {contextMarks[context.id] ?? context.id.slice(0, 2)}
              </span>
            </div>
            <span style={{ color: muted, fontSize: 12, fontWeight: 700 }}>
              {context.audience}
            </span>
            <p
              style={{
                margin: 0,
                color: muted,
                fontSize: 13,
                lineHeight: 1.45,
              }}
            >
              {context.purpose}
            </p>
          </article>
        ))}
      </section>

      <footer
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 14,
          marginTop: 18,
          paddingTop: 18,
          borderTop: `1px solid ${border}`,
        }}
      >
        <p
          style={{
            flex: "1 1 360px",
            margin: 0,
            color: muted,
            fontSize: 12,
            lineHeight: 1.5,
          }}
        >
          {output?.authorizationNotice ??
            "A escolha visual não concede acesso. O backend valida perfil, vínculo e situação cadastral."}
        </p>
        <button
          type="button"
          onClick={() => openExternal(appUrl, { redirectUrl: false })}
          style={{
            minHeight: 44,
            padding: "0 18px",
            border: 0,
            borderRadius: 14,
            background: accent,
            color: accentText,
            cursor: "pointer",
            fontWeight: 900,
          }}
        >
          Abrir Valley
        </button>
      </footer>
    </main>
  );
}

import { useEffect, useState } from "react";

const cards = [
  ["Corrida", "Solicitacao, aceite e conclusao com status operacional."],
  ["Ticket", "Compra e historico de bilhetes vinculados ao usuario."],
  ["QR/NFC", "Validacao local para preparar a integracao fisica real."],
  ["Historico", "Linha do tempo para suporte e auditoria da jornada."],
];

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? "";
const API_HUB_TOKEN = import.meta.env.VITE_API_HUB_TOKEN ?? "";

const endpoints = [
  { label: "Corridas", path: "/mobility/resources/rides", fallback: "2 corridas em simulacao" },
  { label: "Tickets", path: "/mobility/resources/tickets", fallback: "4 tickets emitidos" },
  { label: "Riders", path: "/riders/resources/rider_profiles", fallback: "3 riders elegiveis" },
  { label: "Wallets", path: "/finance/resources/wallets", fallback: "1 wallet vinculada" },
];

type ApiCard = {
  label: string;
  path: string;
  status: "online" | "fallback";
  summary: string;
};

type ApiResource = {
  id: string;
  status?: string;
  payload?: Record<string, unknown>;
};

type JourneyState = "idle" | "running" | "completed" | "failed";

type MobilityOperations = {
  route: string;
  rider: string;
  ticket: string;
  wallet: string;
  receipt: string;
};

const apiHeaders = (): Record<string, string> =>
  API_HUB_TOKEN ? { Authorization: `Bearer ${API_HUB_TOKEN}` } : {};

const pointSummary = (point: unknown) => {
  if (!point || typeof point !== "object") return "ponto nao informado";
  const coordinates = point as Record<string, unknown>;
  return `${coordinates.lat ?? "?"} / ${coordinates.lng ?? "?"}`;
};

async function fetchEndpoint(path: string): Promise<ApiResource[]> {
  if (!API_HUB_URL) throw new Error("VITE_API_HUB_URL ausente");
  const response = await fetch(`${API_HUB_URL}${path}?limit=3`, {
    headers: apiHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const payload = await response.json();
  if (Array.isArray(payload)) return payload;
  return Array.isArray(payload?.data) ? payload.data : [];
}

async function transitionResource(
  path: string,
  resourceId: string,
  action: string,
  reason: string,
  payload = {},
) {
  const response = await fetch(`${API_HUB_URL}${path}/${resourceId}/actions/${action}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...apiHeaders(),
    },
    body: JSON.stringify({ reason, payload }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json() as Promise<ApiResource>;
}

function App() {
  const [apiCards, setApiCards] = useState<ApiCard[]>(
    endpoints.map((endpoint) => ({
      label: endpoint.label,
      path: endpoint.path,
      status: "fallback",
      summary: endpoint.fallback,
    })),
  );
  const [ride, setRide] = useState<ApiResource | null>(null);
  const [ticket, setTicket] = useState<ApiResource | null>(null);
  const [operations, setOperations] = useState<MobilityOperations>({
    route: "Aguardando rota do API Hub.",
    rider: "Aguardando operador elegivel.",
    ticket: "Aguardando ticket QR/NFC.",
    wallet: "Aguardando wallet vinculada.",
    receipt: "Comprovante liberado apos corrida completed e ticket used.",
  });
  const [journeyState, setJourneyState] = useState<JourneyState>("idle");
  const [journeyMessage, setJourneyMessage] = useState(
    "Pronto para aceitar corrida, concluir trajeto e usar ticket QR/NFC.",
  );

  useEffect(() => {
    let active = true;
    Promise.all(
      endpoints.map(async (endpoint) => {
        try {
          const data = await fetchEndpoint(endpoint.path);
          if (endpoint.path.endsWith("/rides") && data[0]) {
            setRide(data[0]);
            setOperations((current) => ({
              ...current,
              route: `Rota viva ${pointSummary(data[0].payload?.origin)} -> ${pointSummary(data[0].payload?.destination)}`,
            }));
          }
          if (endpoint.path.endsWith("/tickets") && data[0]) {
            setTicket(data[0]);
            setOperations((current) => ({
              ...current,
              ticket: `Ticket ${data[0].payload?.route_code ?? "sem rota"} com QR/NFC tokenizado`,
            }));
          }
          if (endpoint.path.endsWith("/rider_profiles") && data[0]) {
            setOperations((current) => ({
              ...current,
              rider: String(
                data[0].payload?.name ?? data[0].payload?.wallet_id ?? "Rider elegivel",
              ),
            }));
          }
          if (endpoint.path.endsWith("/wallets") && data[0]) {
            setOperations((current) => ({
              ...current,
              wallet: String(
                data[0].payload?.label ?? data[0].payload?.wallet_type ?? "Wallet vinculada",
              ),
            }));
          }
          return {
            label: endpoint.label,
            path: endpoint.path,
            status: "online" as const,
            summary: `${data.length} registro(s) retornado(s) pelo API Hub`,
          };
        } catch {
          return {
            label: endpoint.label,
            path: endpoint.path,
            status: "fallback" as const,
            summary: endpoint.fallback,
          };
        }
      }),
    ).then((nextCards) => {
      if (active) setApiCards(nextCards);
    });
    return () => {
      active = false;
    };
  }, []);

  async function completeMobilityJourney() {
    if (!ride?.id || !ticket?.id) {
      setJourneyState("failed");
      setJourneyMessage("Corrida ou ticket ausente no API Hub para executar a jornada.");
      return;
    }
    setJourneyState("running");
    setJourneyMessage("Aceitando corrida e validando embarque...");
    try {
      const acceptedRide = await transitionResource(
        "/mobility/resources/rides",
        ride.id,
        "accept",
        "motorista aceitou corrida",
      );
      setRide(acceptedRide);
      const completedRide = await transitionResource(
        "/mobility/resources/rides",
        ride.id,
        "complete",
        "corrida concluida com rota validada",
      );
      setRide(completedRide);
      const usedTicket = await transitionResource(
        "/mobility/resources/tickets",
        ticket.id,
        "use",
        "ticket validado por QR NFC",
        {
          validation_mode: "qr_nfc",
        },
      );
      setTicket(usedTicket);
      setOperations((current) => ({
        ...current,
        receipt:
          "Comprovante pos-corrida criado: rota concluida, ticket usado e wallet pronta para conciliacao.",
      }));
      setJourneyState("completed");
      setJourneyMessage("Jornada concluida: corrida completed e ticket used.");
    } catch {
      setJourneyState("failed");
      setJourneyMessage("Nao foi possivel concluir a jornada Mobility pelo API Hub.");
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">All-in-One Mobility</p>
        <h1>Corridas, tickets e validacao QR/NFC prontos para virar E2E.</h1>
        <p>
          Shell dedicado para passageiros e operadores acompanharem mobilidade sem depender ainda de
          mapas, ETA ou validadores fisicos reais.
        </p>
      </section>

      <section className="cards" aria-label="Jornada prioritaria">
        {cards.map(([title, text]) => (
          <article key={title}>
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </section>

      <section className="panel">
        <h2>Conexao API Hub</h2>
        <div className="api-grid">
          {apiCards.map((card) => (
            <article className="api-card" key={card.path}>
              <strong>{card.label}</strong>
              <code>{card.path}</code>
              <span className={card.status}>
                {card.status === "online" ? "online" : "fallback"}
              </span>
              <p>{card.summary}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="action-panel" aria-label="Acao de jornada Mobility">
        <div>
          <p className="eyebrow">Jornada executavel</p>
          <h2>Concluir corrida e validar ticket</h2>
          <p>
            Usa a corrida e o ticket retornados pelo API Hub para simular aceite, conclusao de
            trajeto e validacao QR/NFC.
          </p>
        </div>
        <dl>
          <div>
            <dt>Corrida</dt>
            <dd>{ride?.status ?? "fallback"}</dd>
          </div>
          <div>
            <dt>Ticket</dt>
            <dd>{ticket?.status ?? "fallback"}</dd>
          </div>
        </dl>
        <button
          type="button"
          onClick={completeMobilityJourney}
          disabled={journeyState === "running"}
        >
          {journeyState === "running" ? "Executando..." : "Concluir jornada Mobility"}
        </button>
        <p className={`journey-feedback ${journeyState}`}>{journeyMessage}</p>
      </section>

      <section className="action-panel" aria-label="Pos-corrida Mobility">
        <div>
          <p className="eyebrow">Pos-corrida</p>
          <h2>Rota, QR/NFC e conciliacao</h2>
          <p>
            Consolida rota, operador, ticket tokenizado e wallet para suporte, auditoria antifraude
            e conciliacao financeira sem expor token bruto.
          </p>
        </div>
        <dl>
          <div>
            <dt>Rota</dt>
            <dd>{operations.route}</dd>
          </div>
          <div>
            <dt>Operador</dt>
            <dd>{operations.rider}</dd>
          </div>
          <div>
            <dt>Ticket QR/NFC</dt>
            <dd>{operations.ticket}</dd>
          </div>
          <div>
            <dt>Wallet</dt>
            <dd>{operations.wallet}</dd>
          </div>
          <div>
            <dt>Comprovante</dt>
            <dd>{operations.receipt}</dd>
          </div>
        </dl>
      </section>
    </main>
  );
}

export default App;

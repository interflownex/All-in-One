import React, { useMemo, useState } from "react";
import {
  type BusinessKind,
  type ModuleRecommendation,
  recommendBusinessModules,
} from "../../modules/moduleRecommendationRules";
import {
  applyBusinessModuleRecommendations,
  businessModulesApiEnabled,
  getCompanyModuleChangeImpact,
  patchCompanyModule,
} from "../../modules/businessModuleApi";

const DEMO_COMPANY_ID = "00000000-0000-4000-8000-000000000001";

const businessKindOptions: Array<{ value: BusinessKind; label: string }> = [
  { value: "physical_store", label: "Loja física" },
  { value: "ecommerce", label: "E-commerce" },
  { value: "dropshipping", label: "Dropshipping" },
  { value: "restaurant", label: "Restaurante" },
  { value: "services_provider", label: "Prestadora de serviços" },
  { value: "carrier", label: "Transportadora" },
  { value: "clinic", label: "Clínica" },
  { value: "industry", label: "Indústria" },
  { value: "office", label: "Escritório administrativo" },
];

const stateLabel = {
  mandatory: "Obrigatório",
  active: "Ativo",
  recommended: "Recomendado",
  optional: "Opcional",
  hidden: "Oculto",
  disabled: "Desativado",
  blocked_by_plan: "Bloqueado pelo plano",
};

const statusColor: Record<string, string> = {
  mandatory: "#126b45",
  active: "#19764c",
  recommended: "#946200",
  optional: "#536159",
  hidden: "#6b7280",
  disabled: "#991b1b",
  blocked_by_plan: "#7c2d12",
};

type ManualState = Record<string, ModuleRecommendation["state"]>;

const BusinessPermissions: React.FC = () => {
  const [businessKind, setBusinessKind] = useState<BusinessKind>("ecommerce");
  const [query, setQuery] = useState("");
  const [manualStates, setManualStates] = useState<ManualState>({});
  const [auditTrail, setAuditTrail] = useState<string[]>([
    "Tela aberta: configuração de módulos pronta para auditoria.",
  ]);
  const [showImpact, setShowImpact] = useState<ModuleRecommendation | null>(null);
  const [impactText, setImpactText] = useState("");
  const [apiStatus, setApiStatus] = useState(
    businessModulesApiEnabled
      ? "Back-end Business habilitado."
      : "Modo local: configure VITE_API_HUB_URL e VITE_API_HUB_TOKEN para persistir no back-end.",
  );
  const [actionLoading, setActionLoading] = useState(false);

  const classification = useMemo(
    () => ({
      businessKind,
      hasPhysicalStock: true,
      sellsOnline: ["ecommerce", "dropshipping", "physical_store"].includes(businessKind),
      performsDelivery: ["ecommerce", "restaurant"].includes(businessKind),
      hiresPeople: !["autonomous"].includes(businessKind),
      issuesFiscalDocuments: true,
      operatesFleet: ["carrier", "industry"].includes(businessKind),
      hasWarehouse: ["carrier", "industry", "ecommerce"].includes(businessKind),
    }),
    [businessKind],
  );

  const recommendations = useMemo(() => recommendBusinessModules(classification), [classification]);

  const modules = recommendations
    .map((module) => ({ ...module, state: manualStates[module.moduleSlug] ?? module.state }))
    .filter((module) =>
      `${module.titlePtBr} ${module.explanationPtBr}`.toLowerCase().includes(query.toLowerCase()),
    );

  const counts = {
    active: modules.filter((module) => ["mandatory", "active"].includes(module.state)).length,
    recommended: modules.filter((module) => module.state === "recommended").length,
    hidden: modules.filter((module) => module.state === "hidden").length,
  };

  const changeModuleState = async (
    module: ModuleRecommendation,
    state: ModuleRecommendation["state"],
  ) => {
    if (module.state === "mandatory" && state !== "mandatory") return;
    setActionLoading(true);
    setApiStatus("Aplicando alteração...");
    try {
      if (businessModulesApiEnabled) {
        await patchCompanyModule(
          DEMO_COMPANY_ID,
          module.moduleSlug,
          state,
          `Alteração manual para ${stateLabel[state]} via tela de módulos e recursos.`,
        );
        setApiStatus("Alteração persistida no back-end Business.");
      } else {
        setApiStatus(
          "Alteração aplicada localmente. Back-end será usado quando o API Hub estiver configurado.",
        );
      }
      setManualStates((current) => ({ ...current, [module.moduleSlug]: state }));
      setAuditTrail((current) => [
        `${new Date().toLocaleString("pt-BR")}: ${module.titlePtBr} alterado para ${stateLabel[state]}.`,
        ...current,
      ]);
      setShowImpact(null);
      setImpactText("");
    } catch (error) {
      setApiStatus(
        error instanceof Error ? error.message : "Falha ao persistir alteração no back-end.",
      );
    } finally {
      setActionLoading(false);
    }
  };

  const resetToRecommended = async () => {
    setActionLoading(true);
    setApiStatus("Restaurando recomendações...");
    try {
      if (businessModulesApiEnabled) {
        const result = await applyBusinessModuleRecommendations(DEMO_COMPANY_ID, classification);
        setApiStatus(
          `Recomendações restauradas no back-end. ${result.modules.length} módulos sincronizados.`,
        );
      } else {
        setApiStatus("Recomendações restauradas localmente.");
      }
      setManualStates({});
      setAuditTrail((current) => [
        `${new Date().toLocaleString("pt-BR")}: recomendações automáticas restauradas.`,
        ...current,
      ]);
    } catch (error) {
      setApiStatus(error instanceof Error ? error.message : "Falha ao restaurar recomendações.");
    } finally {
      setActionLoading(false);
    }
  };

  const openImpact = async (module: ModuleRecommendation) => {
    setShowImpact(module);
    setImpactText(
      "Dados preservados. A alteração registra auditoria e afeta apenas navegação e operações futuras.",
    );
    if (!businessModulesApiEnabled) return;
    try {
      const impact = await getCompanyModuleChangeImpact(
        DEMO_COMPANY_ID,
        module.moduleSlug,
        "hidden",
      );
      setImpactText(String(impact.explanation ?? "Impacto consultado no back-end Business."));
    } catch (error) {
      setImpactText(
        error instanceof Error ? error.message : "Não foi possível consultar impacto no back-end.",
      );
    }
  };

  return (
    <div className="container">
      <section className="hero" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: "2.3rem", fontWeight: 900, marginBottom: 12 }}>
          Configurações › Empresa › Módulos e recursos
        </h1>
        <p style={{ color: "#536159", fontSize: "1.05rem" }}>
          Ative, oculte ou desative módulos conforme o perfil da empresa. Módulos obrigatórios
          preservam identidade, empresa, permissões e auditoria.
        </p>
      </section>

      <div
        role="status"
        style={{
          background: "#e2f2ea",
          border: "2px solid #126b45",
          padding: 12,
          marginBottom: 16,
          fontWeight: 700,
        }}
      >
        {apiStatus}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
          gap: 16,
          marginBottom: 24,
        }}
      >
        <div className="metric-card neo-brutalism" style={{ background: "#fff", padding: 18 }}>
          <strong style={{ fontSize: 28 }}>{counts.active}</strong>
          <br />
          ativos
        </div>
        <div className="metric-card neo-brutalism" style={{ background: "#fff", padding: 18 }}>
          <strong style={{ fontSize: 28 }}>{counts.recommended}</strong>
          <br />
          recomendados
        </div>
        <div className="metric-card neo-brutalism" style={{ background: "#fff", padding: 18 }}>
          <strong style={{ fontSize: 28 }}>{counts.hidden}</strong>
          <br />
          ocultos
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "280px minmax(0, 1fr)",
          gap: 24,
          alignItems: "start",
        }}
      >
        <aside
          className="neo-brutalism"
          style={{ background: "#fff", padding: 20, border: "3px solid #17211c" }}
        >
          <label style={{ display: "grid", gap: 8, fontWeight: 800, marginBottom: 16 }}>
            Perfil da empresa
            <select
              value={businessKind}
              onChange={(event) => setBusinessKind(event.target.value as BusinessKind)}
              style={{ padding: 12, border: "2px solid #17211c" }}
            >
              {businessKindOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label style={{ display: "grid", gap: 8, fontWeight: 800, marginBottom: 16 }}>
            Buscar módulo
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Ex.: financeiro, estoque, BI"
              style={{ padding: 12, border: "2px solid #17211c" }}
            />
          </label>
          <button
            type="button"
            className="btn-secondary"
            disabled={actionLoading}
            onClick={resetToRecommended}
            style={{ width: "100%", padding: 12 }}
          >
            Restaurar recomendação automática
          </button>

          <h2 style={{ margin: "24px 0 12px", color: "#126b45" }}>Auditoria</h2>
          <ol style={{ color: "#536159", paddingLeft: 18, display: "grid", gap: 8, fontSize: 13 }}>
            {auditTrail.slice(0, 5).map((entry) => (
              <li key={entry}>{entry}</li>
            ))}
          </ol>
        </aside>

        <main style={{ display: "grid", gap: 14 }}>
          {modules.map((module) => (
            <article
              key={module.moduleSlug}
              className="neo-brutalism"
              style={{ background: "#fff", padding: 18, border: "3px solid #17211c" }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 16,
                  alignItems: "start",
                }}
              >
                <div>
                  <h2 style={{ margin: 0, color: "#126b45" }}>{module.titlePtBr}</h2>
                  <strong style={{ color: statusColor[module.state] }}>
                    {stateLabel[module.state]}
                  </strong>
                  <p style={{ color: "#536159", marginTop: 8 }}>{module.explanationPtBr}</p>
                  <p style={{ color: "#536159", fontSize: 13 }}>
                    Dependências: {module.dependencies.join(", ") || "sem dependência adicional"}
                  </p>
                </div>
                <div
                  style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}
                >
                  <button
                    type="button"
                    className="btn-primary"
                    disabled={actionLoading || module.state === "mandatory"}
                    onClick={() => changeModuleState(module, "active")}
                    style={{ padding: "8px 12px" }}
                  >
                    Ativar
                  </button>
                  <button
                    type="button"
                    className="btn-secondary"
                    disabled={actionLoading || module.state === "mandatory"}
                    onClick={() => changeModuleState(module, "hidden")}
                    style={{ padding: "8px 12px" }}
                  >
                    Ocultar
                  </button>
                  <button
                    type="button"
                    className="btn-secondary"
                    disabled={module.state === "mandatory"}
                    onClick={() => openImpact(module)}
                    style={{ padding: "8px 12px" }}
                  >
                    Ver impacto
                  </button>
                </div>
              </div>
            </article>
          ))}
        </main>
      </div>

      {showImpact && (
        <div
          role="dialog"
          aria-modal="true"
          className="neo-brutalism"
          style={{
            position: "fixed",
            inset: "auto 24px 24px auto",
            maxWidth: 420,
            background: "#fff",
            padding: 20,
            border: "3px solid #17211c",
            boxShadow: "8px 8px 0 #17211c",
            zIndex: 20,
          }}
        >
          <h2 style={{ color: "#126b45" }}>Impacto em {showImpact.titlePtBr}</h2>
          <p>{impactText}</p>
          <button
            type="button"
            className="btn-primary"
            onClick={() => changeModuleState(showImpact, "hidden")}
            style={{ padding: "10px 16px", marginRight: 8 }}
          >
            Confirmar ocultação
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => setShowImpact(null)}
            style={{ padding: "10px 16px" }}
          >
            Cancelar
          </button>
        </div>
      )}
    </div>
  );
};

export default BusinessPermissions;

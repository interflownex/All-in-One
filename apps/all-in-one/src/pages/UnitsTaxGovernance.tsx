import React, { useMemo, useState } from "react";
import type { FormEvent } from "react";

const API_HUB_URL = (import.meta as any).env?.VITE_API_HUB_URL ?? "";
const API_HUB_TOKEN = (import.meta as any).env?.VITE_API_HUB_TOKEN ?? "";

type Feedback = { kind: "idle" | "loading" | "success" | "error"; message: string };

const headers = () => ({
  "Content-Type": "application/json",
  ...(API_HUB_TOKEN
    ? { Authorization: `Bearer ${API_HUB_TOKEN}` }
    : { "X-Actor-User-Id": "operador-local-governanca" }),
});

const activeWindow = () => {
  const start = new Date(Date.now() - 60_000).toISOString();
  const end = new Date(Date.now() + 86_400_000).toISOString();
  return { start, end };
};

const UnitsTaxGovernance: React.FC = () => {
  const window = useMemo(activeWindow, []);
  const [tab, setTab] = useState<"units" | "tax">("units");
  const [unit, setUnit] = useState({
    quantity: "1",
    multiplier: "12",
    divisor: "1",
    precision: "3",
    rounding_mode: "half_up",
    source_dimension: "package",
    target_dimension: "unit",
    density: "",
    approved: false,
  });
  const [tax, setTax] = useState({
    taxable_base: "100.00",
    rate: "0.18",
    base_reduction: "0.00",
    precision: "2",
    rounding_mode: "half_up",
    legal_basis: "",
    approved: false,
  });
  const [unitFeedback, setUnitFeedback] = useState<Feedback>({ kind: "idle", message: "" });
  const [taxFeedback, setTaxFeedback] = useState<Feedback>({ kind: "idle", message: "" });

  const request = async (path: string, payload: object) => {
    const response = await fetch(`${API_HUB_URL}${path}`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok)
      throw new Error(result.detail ?? "Não foi possível validar o cálculo no backend.");
    return result;
  };

  const submitUnit = async (event: FormEvent) => {
    event.preventDefault();
    if (!unit.approved) {
      setUnitFeedback({
        kind: "error",
        message: "A conversão precisa ser homologada antes do cálculo.",
      });
      return;
    }
    setUnitFeedback({ kind: "loading", message: "Validando no backend…" });
    try {
      const result = await request("/stock/calculations/unit-conversion", {
        ...unit,
        precision: Number(unit.precision),
        density: unit.density || null,
        effective_from: window.start,
        effective_to: window.end,
      });
      setUnitFeedback({
        kind: "success",
        message: `Resultado homologado: ${result.converted_quantity}`,
      });
    } catch (error) {
      setUnitFeedback({
        kind: "error",
        message: error instanceof Error ? error.message : "Erro inesperado.",
      });
    }
  };

  const submitTax = async (event: FormEvent) => {
    event.preventDefault();
    if (!tax.legal_basis.trim()) {
      setTaxFeedback({ kind: "error", message: "Informe o fundamento legal da regra fiscal." });
      return;
    }
    if (!tax.approved) {
      setTaxFeedback({
        kind: "error",
        message: "A regra fiscal precisa ser homologada antes do cálculo.",
      });
      return;
    }
    setTaxFeedback({ kind: "loading", message: "Recalculando no backend…" });
    try {
      const result = await request("/erp/calculations/tax", {
        ...tax,
        precision: Number(tax.precision),
        effective_from: window.start,
        effective_to: window.end,
      });
      setTaxFeedback({
        kind: "success",
        message: `Base reduzida: ${result.reduced_base} · Tributo: ${result.tax_amount}`,
      });
    } catch (error) {
      setTaxFeedback({
        kind: "error",
        message: error instanceof Error ? error.message : "Erro inesperado.",
      });
    }
  };

  return (
    <section className="governance-page">
      <div className="governance-hero">
        <div>
          <span className="eyebrow">Governança operacional</span>
          <h1>Unidades e regras fiscais</h1>
          <p>
            Simule conversões e tributos com vigência, precisão e homologação. O resultado oficial é
            sempre recalculado no backend.
          </p>
        </div>
        <div className="governance-kpis" aria-label="Indicadores de governança">
          <article>
            <strong>12</strong>
            <span>casas decimais suportadas</span>
          </article>
          <article>
            <strong>UTC</strong>
            <span>vigência autoritativa</span>
          </article>
          <article>
            <strong>100%</strong>
            <span>cálculo no backend</span>
          </article>
        </div>
      </div>

      <div className="governance-tabs" role="tablist" aria-label="Áreas de governança">
        <button
          className={tab === "units" ? "active" : ""}
          onClick={() => setTab("units")}
          role="tab"
        >
          Conversão de unidades
        </button>
        <button className={tab === "tax" ? "active" : ""} onClick={() => setTab("tax")} role="tab">
          Cálculo fiscal
        </button>
      </div>

      {tab === "units" ? (
        <form className="governance-card" onSubmit={submitUnit} noValidate>
          <header>
            <div>
              <h2>Regra de conversão</h2>
              <p>Exemplo: 1 caixa equivale a 12 unidades.</p>
            </div>
            <span className="status-chip">Vigência ativa</span>
          </header>
          <div className="governance-grid">
            <label>
              Quantidade de origem
              <input
                required
                inputMode="decimal"
                value={unit.quantity}
                onChange={(e) => setUnit((v) => ({ ...v, quantity: e.target.value }))}
              />
            </label>
            <label>
              Multiplicador
              <input
                required
                inputMode="decimal"
                value={unit.multiplier}
                onChange={(e) => setUnit((v) => ({ ...v, multiplier: e.target.value }))}
              />
            </label>
            <label>
              Divisor
              <input
                required
                inputMode="decimal"
                value={unit.divisor}
                onChange={(e) => setUnit((v) => ({ ...v, divisor: e.target.value }))}
              />
            </label>
            <label>
              Precisão
              <input
                required
                type="number"
                min="0"
                max="12"
                value={unit.precision}
                onChange={(e) => setUnit((v) => ({ ...v, precision: e.target.value }))}
              />
            </label>
            <label>
              Dimensão de origem
              <select
                value={unit.source_dimension}
                onChange={(e) => setUnit((v) => ({ ...v, source_dimension: e.target.value }))}
              >
                <option value="package">Embalagem</option>
                <option value="unit">Unidade</option>
                <option value="mass">Massa</option>
                <option value="volume">Volume</option>
              </select>
            </label>
            <label>
              Dimensão de destino
              <select
                value={unit.target_dimension}
                onChange={(e) => setUnit((v) => ({ ...v, target_dimension: e.target.value }))}
              >
                <option value="unit">Unidade</option>
                <option value="package">Embalagem</option>
                <option value="mass">Massa</option>
                <option value="volume">Volume</option>
              </select>
            </label>
            <label>
              Densidade contextual (se necessária)
              <input
                inputMode="decimal"
                value={unit.density}
                onChange={(e) => setUnit((v) => ({ ...v, density: e.target.value }))}
                placeholder="Ex.: 0.998"
              />
            </label>
            <label>
              Arredondamento
              <select
                value={unit.rounding_mode}
                onChange={(e) => setUnit((v) => ({ ...v, rounding_mode: e.target.value }))}
              >
                <option value="half_up">Metade para cima</option>
                <option value="half_even">Metade par</option>
                <option value="floor">Para baixo</option>
                <option value="ceiling">Para cima</option>
              </select>
            </label>
          </div>
          <label className="approval-check">
            <input
              type="checkbox"
              checked={unit.approved}
              onChange={(e) => setUnit((v) => ({ ...v, approved: e.target.checked }))}
            />{" "}
            Confirmo que a regra foi homologada
          </label>
          <footer>
            <button
              className="btn-primary"
              type="submit"
              disabled={unitFeedback.kind === "loading"}
            >
              Validar conversão
            </button>
            <output className={`governance-feedback ${unitFeedback.kind}`} aria-live="polite">
              {unitFeedback.message}
            </output>
          </footer>
        </form>
      ) : (
        <form className="governance-card" onSubmit={submitTax} noValidate>
          <header>
            <div>
              <h2>Regra tributária</h2>
              <p>Alíquota e redução devem ser informadas como fração decimal.</p>
            </div>
            <span className="status-chip fiscal">Revisão fiscal</span>
          </header>
          <div className="governance-grid">
            <label>
              Base tributável
              <input
                required
                inputMode="decimal"
                value={tax.taxable_base}
                onChange={(e) => setTax((v) => ({ ...v, taxable_base: e.target.value }))}
              />
            </label>
            <label>
              Alíquota
              <input
                required
                inputMode="decimal"
                value={tax.rate}
                onChange={(e) => setTax((v) => ({ ...v, rate: e.target.value }))}
              />
            </label>
            <label>
              Redução da base
              <input
                required
                inputMode="decimal"
                value={tax.base_reduction}
                onChange={(e) => setTax((v) => ({ ...v, base_reduction: e.target.value }))}
              />
            </label>
            <label>
              Precisão
              <input
                required
                type="number"
                min="0"
                max="12"
                value={tax.precision}
                onChange={(e) => setTax((v) => ({ ...v, precision: e.target.value }))}
              />
            </label>
            <label className="wide">
              Fundamento legal
              <input
                required
                value={tax.legal_basis}
                onChange={(e) => setTax((v) => ({ ...v, legal_basis: e.target.value }))}
                placeholder="Lei, convênio ou norma aplicável"
              />
            </label>
            <label>
              Arredondamento
              <select
                value={tax.rounding_mode}
                onChange={(e) => setTax((v) => ({ ...v, rounding_mode: e.target.value }))}
              >
                <option value="half_up">Metade para cima</option>
                <option value="half_even">Metade par</option>
                <option value="floor">Para baixo</option>
                <option value="ceiling">Para cima</option>
              </select>
            </label>
          </div>
          <label className="approval-check">
            <input
              type="checkbox"
              checked={tax.approved}
              onChange={(e) => setTax((v) => ({ ...v, approved: e.target.checked }))}
            />{" "}
            Confirmo que a regra fiscal foi homologada
          </label>
          <footer>
            <button className="btn-primary" type="submit" disabled={taxFeedback.kind === "loading"}>
              Calcular tributo
            </button>
            <output className={`governance-feedback ${taxFeedback.kind}`} aria-live="polite">
              {taxFeedback.message}
            </output>
          </footer>
        </form>
      )}
    </section>
  );
};

export default UnitsTaxGovernance;

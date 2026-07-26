import React, { useEffect, useMemo, useState } from "react";
import {
  completeAliExpressOauth,
  getAliExpressAuthorizeUrl,
  listStockIntegrationAudit,
  listStockIntegrationRuns,
  listStockProviders,
  saveStockProviderSecrets,
  stockIntegrationApiEnabled,
  syncStockProvider,
  testStockProvider,
  updateStockProvider,
  type StockIntegrationAudit,
  type StockIntegrationRun,
  type StockProviderConfig,
  type StockProviderSecrets,
  type StockProviderSlug,
  type StockProviderState,
  type StockSyncResource,
} from "../../modules/stockIntegrationApi";

const PROVIDER_ORDER: StockProviderSlug[] = ["cj_dropshipping", "aliexpress"];
const SYNC_RESOURCES: Array<{ key: StockSyncResource; label: string }> = [
  { key: "products", label: "Produtos" },
  { key: "inventory", label: "Estoque" },
  { key: "prices", label: "Preços" },
  { key: "orders", label: "Pedidos" },
  { key: "tracking", label: "Rastreamento" },
];

const cardStyle: React.CSSProperties = {
  border: "2px solid #17211c",
  borderRadius: 14,
  background: "#fff",
  boxShadow: "5px 5px 0 #17211c",
  padding: 20,
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  border: "2px solid #17211c",
  borderRadius: 9,
  padding: "11px 12px",
  background: "#fff",
  color: "#17211c",
};

const labelStyle: React.CSSProperties = {
  display: "grid",
  gap: 6,
  fontWeight: 800,
  fontSize: 13,
};

const buttonStyle: React.CSSProperties = {
  border: "2px solid #17211c",
  borderRadius: 9,
  padding: "11px 15px",
  fontWeight: 900,
  cursor: "pointer",
  boxShadow: "3px 3px 0 #17211c",
};

const cloneConfig = (config: StockProviderConfig): StockProviderConfig => ({
  ...config,
  secret_env: { ...config.secret_env },
  mapping_rules: { ...config.mapping_rules },
  provider_options: { ...config.provider_options },
});

const formatDate = (value?: string) => {
  if (!value) return "Sem registro";
  return new Date(value).toLocaleString("pt-BR");
};

const StockOverview: React.FC = () => {
  const [providers, setProviders] = useState<StockProviderState[]>([]);
  const [selectedSlug, setSelectedSlug] = useState<StockProviderSlug>("cj_dropshipping");
  const [draft, setDraft] = useState<StockProviderConfig | null>(null);
  const [secrets, setSecrets] = useState<StockProviderSecrets>({});
  const [resources, setResources] = useState<StockSyncResource[]>(["products"]);
  const [runs, setRuns] = useState<StockIntegrationRun[]>([]);
  const [audit, setAudit] = useState<StockIntegrationAudit[]>([]);
  const [oauthCode, setOauthCode] = useState("");
  const [query, setQuery] = useState("");
  const [productId, setProductId] = useState("");
  const [trackingNumber, setTrackingNumber] = useState("");
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const selected = useMemo(
    () => providers.find((provider) => provider.provider === selectedSlug) ?? null,
    [providers, selectedSlug],
  );

  const load = async () => {
    if (!stockIntegrationApiEnabled) return;
    setBusy("load");
    setError("");
    try {
      const [providerList, runList, auditList] = await Promise.all([
        listStockProviders(),
        listStockIntegrationRuns(25),
        listStockIntegrationAudit(40),
      ]);
      setProviders(providerList.sort((a, b) => PROVIDER_ORDER.indexOf(a.provider) - PROVIDER_ORDER.indexOf(b.provider)));
      setRuns(runList);
      setAudit(auditList);
      const current = providerList.find((provider) => provider.provider === selectedSlug) ?? providerList[0];
      if (current) {
        setSelectedSlug(current.provider);
        setDraft(cloneConfig(current.config));
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Não foi possível carregar as integrações.");
    } finally {
      setBusy("");
    }
  };

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    if (selected) {
      setDraft(cloneConfig(selected.config));
      setSecrets({});
      setMessage("");
      setError("");
    }
  }, [selectedSlug, selected?.config.updated_at]);

  const replaceProvider = (next: StockProviderState) => {
    setProviders((items) => items.map((item) => (item.provider === next.provider ? next : item)));
    setDraft(cloneConfig(next.config));
  };

  const runAction = async (name: string, action: () => Promise<void>) => {
    setBusy(name);
    setMessage("");
    setError("");
    try {
      await action();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "A operação não pôde ser concluída.");
    } finally {
      setBusy("");
    }
  };

  const updateDraft = <K extends keyof StockProviderConfig>(key: K, value: StockProviderConfig[K]) => {
    setDraft((current) => (current ? { ...current, [key]: value } : current));
  };

  const saveConfiguration = () =>
    runAction("config", async () => {
      if (!draft) return;
      const next = await updateStockProvider(selectedSlug, {
        enabled: draft.enabled,
        environment: draft.environment,
        api_base_url: draft.api_base_url,
        authorization_url: draft.authorization_url,
        token_url: draft.token_url,
        refresh_url: draft.refresh_url,
        callback_url: draft.callback_url,
        webhook_url: draft.webhook_url,
        secret_env: draft.secret_env,
        auto_sync_products: draft.auto_sync_products,
        auto_sync_inventory: draft.auto_sync_inventory,
        auto_sync_prices: draft.auto_sync_prices,
        auto_sync_orders: draft.auto_sync_orders,
        auto_sync_tracking: draft.auto_sync_tracking,
        auto_publish_products: draft.auto_publish_products,
        schedule_minutes: draft.schedule_minutes,
        timeout_seconds: draft.timeout_seconds,
        retry_attempts: draft.retry_attempts,
        rate_limit_per_minute: draft.rate_limit_per_minute,
        max_products_per_run: draft.max_products_per_run,
        source_currency: draft.source_currency,
        target_currency: draft.target_currency,
        default_country: draft.default_country,
        default_warehouse: draft.default_warehouse,
        markup_percent: draft.markup_percent,
        connection_test_path: draft.connection_test_path,
        mapping_rules: draft.mapping_rules,
        provider_options: draft.provider_options,
      });
      replaceProvider(next);
      setMessage("Configuração persistida no backend do STOCK.");
      await refreshHistory();
    });

  const saveCredentials = () =>
    runAction("secrets", async () => {
      const clean = Object.fromEntries(
        Object.entries(secrets).filter(([, value]) => typeof value === "string" && value.trim()),
      ) as StockProviderSecrets;
      if (Object.keys(clean).length === 0) {
        throw new Error("Informe ao menos uma credencial para salvar.");
      }
      const next = await saveStockProviderSecrets(selectedSlug, clean);
      replaceProvider(next);
      setSecrets({});
      setMessage("Credenciais enviadas ao cofre criptografado. Os valores não serão exibidos novamente.");
      await refreshHistory();
    });

  const refreshHistory = async () => {
    const [runList, auditList] = await Promise.all([
      listStockIntegrationRuns(25),
      listStockIntegrationAudit(40),
    ]);
    setRuns(runList);
    setAudit(auditList);
  };

  const testConnection = () =>
    runAction("test", async () => {
      const result = await testStockProvider(selectedSlug);
      setMessage(`Teste concluído: ${result.status}.`);
      await load();
    });

  const sync = (dryRun: boolean) =>
    runAction(dryRun ? "dry-run" : "sync", async () => {
      const result = await syncStockProvider(selectedSlug, {
        resources,
        dry_run: dryRun,
        query: query || undefined,
        product_id: productId || undefined,
        tracking_number: trackingNumber || undefined,
        limit: Math.min(draft?.max_products_per_run ?? 20, 100),
      });
      setMessage(
        dryRun
          ? `Plano de sincronização validado: ${result.status}.`
          : `Prévia de integração executada: ${result.status}.`,
      );
      await refreshHistory();
    });

  const openAliExpressAuthorization = () =>
    runAction("oauth-url", async () => {
      const result = await getAliExpressAuthorizeUrl();
      const opened = window.open(result.authorization_url, "_blank", "noopener,noreferrer");
      if (!opened) {
        setMessage(`Copie e abra este endereço: ${result.authorization_url}`);
      } else {
        setMessage("A autorização do AliExpress foi aberta em uma nova aba.");
      }
    });

  const completeOauth = () =>
    runAction("oauth-code", async () => {
      if (!oauthCode.trim()) throw new Error("Informe o código OAuth retornado pelo AliExpress.");
      const next = await completeAliExpressOauth(oauthCode.trim());
      replaceProvider(next);
      setOauthCode("");
      setMessage("OAuth concluído e tokens armazenados no cofre criptografado.");
      await refreshHistory();
    });

  if (!stockIntegrationApiEnabled) {
    return (
      <div className="container" style={{ maxWidth: 1100 }}>
        <section style={{ ...cardStyle, background: "#fff4d6" }}>
          <h1>Central STOCK, CJ Dropshipping e AliExpress</h1>
          <p>
            A tela está implementada, mas este painel ainda não recebeu as variáveis públicas de conexão
            com o API Hub.
          </p>
          <div style={{ display: "grid", gap: 8, marginTop: 18 }}>
            <code>VITE_API_HUB_URL=https://endereco-do-api-hub</code>
            <code>VITE_API_HUB_TOKEN=token-administrativo-com-MFA</code>
          </div>
          <p style={{ marginTop: 18 }}>
            As chaves da CJ e do AliExpress nunca devem ser colocadas nessas variáveis do navegador. Elas
            são enviadas ao cofre do backend ou configuradas diretamente no gerenciador de segredos.
          </p>
        </section>
      </div>
    );
  }

  if (!selected || !draft) {
    return <div className="container">{busy ? "Carregando integrações..." : "Nenhuma integração encontrada."}</div>;
  }

  const providerRuns = runs.filter((run) => run.provider === selectedSlug);
  const providerAudit = audit.filter((item) => item.provider === selectedSlug);
  const secretFields = selectedSlug === "cj_dropshipping"
    ? [
        ["api_key", "CJ API Key"],
        ["access_token", "Access Token opcional"],
        ["refresh_token", "Refresh Token opcional"],
        ["webhook_secret", "Segredo de webhook"],
      ]
    : [
        ["app_key", "AliExpress App Key"],
        ["app_secret", "AliExpress App Secret"],
        ["access_token", "Access Token opcional"],
        ["refresh_token", "Refresh Token opcional"],
        ["webhook_secret", "Segredo de webhook"],
      ];

  return (
    <div className="container" style={{ maxWidth: 1380, paddingBottom: 80 }}>
      <header
        style={{
          ...cardStyle,
          background: "#126b45",
          color: "#fff",
          marginBottom: 24,
        }}
      >
        <p style={{ fontWeight: 900, textTransform: "uppercase", letterSpacing: 1.4 }}>
          STOCK · Integrações de fornecedores
        </p>
        <h1 style={{ color: "#fff", margin: "8px 0" }}>CJ Dropshipping e AliExpress</h1>
        <p style={{ maxWidth: 850, color: "#e2f2ea" }}>
          Configure credenciais, OAuth, catálogos, estoque, preços, pedidos, rastreamento,
          sincronizações e webhooks. As credenciais ficam somente no backend criptografado.
        </p>
      </header>

      {message && (
        <div role="status" style={{ ...cardStyle, background: "#dcfce7", marginBottom: 18 }}>
          {message}
        </div>
      )}
      {error && (
        <div role="alert" style={{ ...cardStyle, background: "#fee2e2", marginBottom: 18 }}>
          <strong>Não foi possível concluir:</strong> {error}
        </div>
      )}

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: 18, marginBottom: 24 }}>
        {providers.map((provider) => (
          <button
            type="button"
            key={provider.provider}
            onClick={() => setSelectedSlug(provider.provider)}
            style={{
              ...cardStyle,
              cursor: "pointer",
              textAlign: "left",
              background: selectedSlug === provider.provider ? "#e2f2ea" : "#fff",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <strong style={{ fontSize: 20 }}>{provider.display_name}</strong>
              <span
                style={{
                  border: "2px solid #17211c",
                  borderRadius: 999,
                  padding: "4px 9px",
                  background: provider.ready_for_connection ? "#bbf7d0" : "#fef3c7",
                  fontSize: 12,
                  fontWeight: 900,
                }}
              >
                {provider.ready_for_connection ? "Pronto" : "Configuração pendente"}
              </span>
            </div>
            <p style={{ color: "#536159", marginBottom: 0 }}>
              {provider.config.enabled ? "Ativo" : "Desativado"} · {provider.config.environment}
            </p>
          </button>
        ))}
      </section>

      <section style={{ ...cardStyle, marginBottom: 24 }}>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: 14 }}>
          <div>
            <h2 style={{ margin: 0 }}>{selected.display_name}</h2>
            <p style={{ marginBottom: 0, color: "#536159" }}>
              Autenticação: {selected.auth_kind} · Atualizado em {formatDate(draft.updated_at)}
            </p>
          </div>
          <a href={selected.docs_url} target="_blank" rel="noreferrer" style={{ ...buttonStyle, background: "#fff" }}>
            Documentação oficial
          </a>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12, marginTop: 20 }}>
          {Object.entries(selected.secret_status).map(([name, configured]) => (
            <div key={name} style={{ border: "2px solid #17211c", borderRadius: 9, padding: 12, background: configured ? "#dcfce7" : "#fef3c7" }}>
              <strong>{name}</strong>
              <div>{configured ? "Configurado" : "Pendente"}</div>
            </div>
          ))}
        </div>
        {selected.missing_requirements.length > 0 && (
          <p style={{ marginTop: 16, fontWeight: 800 }}>
            Pendências: {selected.missing_requirements.join(", ")}.
          </p>
        )}
      </section>

      <section style={{ ...cardStyle, marginBottom: 24 }}>
        <h2>1. Configuração geral e endpoints</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: 16 }}>
          <label style={labelStyle}>
            Integração ativa
            <select
              value={draft.enabled ? "true" : "false"}
              onChange={(event) => updateDraft("enabled", event.target.value === "true")}
              style={inputStyle}
            >
              <option value="false">Desativada</option>
              <option value="true">Ativa</option>
            </select>
          </label>
          <label style={labelStyle}>
            Ambiente
            <select
              value={draft.environment}
              onChange={(event) => updateDraft("environment", event.target.value as "sandbox" | "production")}
              style={inputStyle}
            >
              <option value="sandbox">Sandbox / homologação</option>
              <option value="production">Produção</option>
            </select>
          </label>
          <label style={labelStyle}>
            URL base da API
            <input value={draft.api_base_url} onChange={(event) => updateDraft("api_base_url", event.target.value)} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            URL de autorização
            <input value={draft.authorization_url ?? ""} onChange={(event) => updateDraft("authorization_url", event.target.value || null)} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            URL de token
            <input value={draft.token_url ?? ""} onChange={(event) => updateDraft("token_url", event.target.value || null)} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            URL de renovação
            <input value={draft.refresh_url ?? ""} onChange={(event) => updateDraft("refresh_url", event.target.value || null)} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Callback OAuth
            <input value={draft.callback_url ?? ""} onChange={(event) => updateDraft("callback_url", event.target.value || null)} style={inputStyle} placeholder="https://.../oauth/callback" />
          </label>
          <label style={labelStyle}>
            Webhook público
            <input value={draft.webhook_url ?? ""} onChange={(event) => updateDraft("webhook_url", event.target.value || null)} style={inputStyle} placeholder="https://.../stock/integrations/webhooks/..." />
          </label>
          <label style={labelStyle}>
            Caminho para teste
            <input value={draft.connection_test_path ?? ""} onChange={(event) => updateDraft("connection_test_path", event.target.value || null)} style={inputStyle} />
          </label>
        </div>
      </section>

      <section style={{ ...cardStyle, marginBottom: 24 }}>
        <h2>2. Cofre de credenciais</h2>
        <p style={{ color: "#536159" }}>
          Os campos abaixo são enviados uma única vez ao backend. O navegador não guarda nem recupera os valores.
          A alteração exige sessão administrativa com MFA.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: 16 }}>
          {secretFields.map(([name, label]) => (
            <label key={name} style={labelStyle}>
              {label}
              <input
                type="password"
                autoComplete="new-password"
                value={(secrets as Record<string, string | undefined>)[name] ?? ""}
                onChange={(event) => setSecrets((current) => ({ ...current, [name]: event.target.value }))}
                style={inputStyle}
                placeholder="Não exibido após salvar"
              />
            </label>
          ))}
        </div>

        <h3 style={{ marginTop: 24 }}>Nomes das variáveis no gerenciador de segredos</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: 16 }}>
          {Object.entries(draft.secret_env).map(([name, envName]) => (
            <label key={name} style={labelStyle}>
              {name}
              <input
                value={envName}
                onChange={(event) => updateDraft("secret_env", { ...draft.secret_env, [name]: event.target.value })}
                style={inputStyle}
              />
            </label>
          ))}
        </div>
        <button
          type="button"
          disabled={Boolean(busy)}
          onClick={saveCredentials}
          style={{ ...buttonStyle, background: "#17211c", color: "#fff", marginTop: 18 }}
        >
          {busy === "secrets" ? "Salvando no cofre..." : "Salvar credenciais no cofre"}
        </button>
      </section>

      <section style={{ ...cardStyle, marginBottom: 24 }}>
        <h2>3. Sincronização, limites e regras comerciais</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 16 }}>
          <label style={labelStyle}>
            Intervalo automático em minutos
            <input type="number" min={5} max={10080} value={draft.schedule_minutes} onChange={(event) => updateDraft("schedule_minutes", Number(event.target.value))} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Timeout em segundos
            <input type="number" min={3} max={120} value={draft.timeout_seconds} onChange={(event) => updateDraft("timeout_seconds", Number(event.target.value))} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Tentativas automáticas
            <input type="number" min={0} max={10} value={draft.retry_attempts} onChange={(event) => updateDraft("retry_attempts", Number(event.target.value))} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Limite por minuto
            <input type="number" min={1} max={1000} value={draft.rate_limit_per_minute} onChange={(event) => updateDraft("rate_limit_per_minute", Number(event.target.value))} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Máximo de produtos por execução
            <input type="number" min={1} max={1000} value={draft.max_products_per_run} onChange={(event) => updateDraft("max_products_per_run", Number(event.target.value))} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Moeda de origem
            <input maxLength={3} value={draft.source_currency} onChange={(event) => updateDraft("source_currency", event.target.value.toUpperCase())} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Moeda de destino
            <input maxLength={3} value={draft.target_currency} onChange={(event) => updateDraft("target_currency", event.target.value.toUpperCase())} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            País padrão
            <input maxLength={2} value={draft.default_country} onChange={(event) => updateDraft("default_country", event.target.value.toUpperCase())} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Armazém padrão
            <input value={draft.default_warehouse ?? ""} onChange={(event) => updateDraft("default_warehouse", event.target.value || null)} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Markup padrão (%)
            <input type="number" min={0} max={1000} step="0.01" value={draft.markup_percent} onChange={(event) => updateDraft("markup_percent", Number(event.target.value))} style={inputStyle} />
          </label>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(230px,1fr))", gap: 10, marginTop: 20 }}>
          {[
            ["auto_sync_products", "Sincronizar produtos"],
            ["auto_sync_inventory", "Sincronizar estoque"],
            ["auto_sync_prices", "Sincronizar preços"],
            ["auto_sync_orders", "Sincronizar pedidos"],
            ["auto_sync_tracking", "Sincronizar rastreamento"],
            ["auto_publish_products", "Publicar automaticamente"],
          ].map(([key, label]) => (
            <label key={key} style={{ display: "flex", gap: 10, alignItems: "center", border: "2px solid #17211c", borderRadius: 9, padding: 12, fontWeight: 800 }}>
              <input
                type="checkbox"
                checked={Boolean(draft[key as keyof StockProviderConfig])}
                onChange={(event) => updateDraft(key as keyof StockProviderConfig, event.target.checked as never)}
              />
              {label}
            </label>
          ))}
        </div>

        <h3 style={{ marginTop: 24 }}>Mapeamento para o catálogo interno</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 14 }}>
          {Object.entries(draft.mapping_rules).map(([target, source]) => (
            <label key={target} style={labelStyle}>
              {target}
              <input
                value={source}
                onChange={(event) => updateDraft("mapping_rules", { ...draft.mapping_rules, [target]: event.target.value })}
                style={inputStyle}
              />
            </label>
          ))}
        </div>

        <button
          type="button"
          disabled={Boolean(busy)}
          onClick={saveConfiguration}
          style={{ ...buttonStyle, background: "#126b45", color: "#fff", marginTop: 20 }}
        >
          {busy === "config" ? "Salvando..." : "Salvar todas as configurações"}
        </button>
      </section>

      {selectedSlug === "aliexpress" && (
        <section style={{ ...cardStyle, background: "#fff7ed", marginBottom: 24 }}>
          <h2>4. Autorização OAuth do AliExpress</h2>
          <p>
            Salve primeiro o App Key, App Secret e a Callback URL. Depois abra a autorização do vendedor.
            Ao retornar, informe o código recebido para trocar por tokens no backend.
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            <button type="button" disabled={Boolean(busy)} onClick={openAliExpressAuthorization} style={{ ...buttonStyle, background: "#fb923c" }}>
              Abrir autorização do AliExpress
            </button>
            <input value={oauthCode} onChange={(event) => setOauthCode(event.target.value)} placeholder="Código OAuth retornado" style={{ ...inputStyle, maxWidth: 420 }} />
            <button type="button" disabled={Boolean(busy)} onClick={completeOauth} style={{ ...buttonStyle, background: "#17211c", color: "#fff" }}>
              Concluir OAuth
            </button>
          </div>
        </section>
      )}

      <section style={{ ...cardStyle, marginBottom: 24 }}>
        <h2>{selectedSlug === "aliexpress" ? "5" : "4"}. Teste e sincronização controlada</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 18 }}>
          {SYNC_RESOURCES.map((resource) => (
            <label key={resource.key} style={{ display: "flex", alignItems: "center", gap: 7, border: "2px solid #17211c", borderRadius: 999, padding: "7px 11px", fontWeight: 800 }}>
              <input
                type="checkbox"
                checked={resources.includes(resource.key)}
                onChange={(event) =>
                  setResources((current) =>
                    event.target.checked
                      ? [...new Set([...current, resource.key])]
                      : current.filter((item) => item !== resource.key),
                  )
                }
              />
              {resource.label}
            </label>
          ))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(230px,1fr))", gap: 14 }}>
          <label style={labelStyle}>
            Pesquisa de produto
            <input value={query} onChange={(event) => setQuery(event.target.value)} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            ID de produto para estoque
            <input value={productId} onChange={(event) => setProductId(event.target.value)} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Código de rastreamento
            <input value={trackingNumber} onChange={(event) => setTrackingNumber(event.target.value)} style={inputStyle} />
          </label>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 20 }}>
          <button type="button" disabled={Boolean(busy)} onClick={testConnection} style={{ ...buttonStyle, background: "#bfdbfe" }}>
            {busy === "test" ? "Testando..." : "Testar conexão"}
          </button>
          <button type="button" disabled={Boolean(busy) || resources.length === 0} onClick={() => sync(true)} style={{ ...buttonStyle, background: "#fef3c7" }}>
            Validar plano sem importar
          </button>
          <button type="button" disabled={Boolean(busy) || resources.length === 0} onClick={() => sync(false)} style={{ ...buttonStyle, background: "#126b45", color: "#fff" }}>
            Executar prévia pela API
          </button>
        </div>
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(360px,1fr))", gap: 20 }}>
        <div style={cardStyle}>
          <h2>Execuções recentes</h2>
          <div style={{ display: "grid", gap: 10 }}>
            {providerRuns.length === 0 ? (
              <p>Nenhuma execução registrada.</p>
            ) : (
              providerRuns.map((run) => (
                <article key={run.id} style={{ border: "2px solid #17211c", borderRadius: 9, padding: 12 }}>
                  <strong>{run.kind} · {run.status}</strong>
                  <div>{formatDate(run.completed_at)}</div>
                  <small>{run.resources?.join(", ") || "Sem recursos listados"}</small>
                </article>
              ))
            )}
          </div>
        </div>
        <div style={cardStyle}>
          <h2>Auditoria</h2>
          <div style={{ display: "grid", gap: 10 }}>
            {providerAudit.length === 0 ? (
              <p>Nenhuma alteração registrada.</p>
            ) : (
              providerAudit.map((item) => (
                <article key={item.id} style={{ border: "2px solid #17211c", borderRadius: 9, padding: 12 }}>
                  <strong>{item.action}</strong>
                  <div>{item.actor}</div>
                  <small>{formatDate(item.created_at)}</small>
                </article>
              ))
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default StockOverview;

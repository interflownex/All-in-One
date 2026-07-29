import { McpServer } from "skybridge/server";
import { z } from "zod";

const VALLEY_APP_URL = "https://84e9680fcfa2a84551.v2.appdeploy.ai/";

const contexts = [
  {
    id: "PERSONAL",
    label: "Pessoal",
    audience: "Pessoa Física (B2C)",
    purpose: "Compras, carteira, benefícios, pedidos e serviços do cotidiano.",
  },
  {
    id: "RIDER",
    label: "Rider",
    audience: "Riders, entregadores e motoristas",
    purpose: "Entregas, corridas, rotas, disponibilidade, ganhos e repasses.",
  },
  {
    id: "BUSINESS",
    label: "Business",
    audience: "Pessoa Jurídica (B2B)",
    purpose: "Empresa, catálogo, pedidos, equipe, estoque e operação comercial.",
  },
  {
    id: "ONE_SERVICE",
    label: "One Service",
    audience: "Profissionais e empresas prestadoras",
    purpose: "Agenda, visitas, propostas, contratos, evidências e recebimentos.",
  },
  {
    id: "PDV",
    label: "PDV",
    audience: "Operadores, supervisores e gestores autorizados",
    purpose: "Vendas, caixa, pedidos, estoque e sincronização operacional.",
  },
] as const;

const server = new McpServer({
  name: "valley-universal",
  version: "1.0.0",
})
  .registerTool(
    {
      name: "valley_list_contexts",
      description:
        "Lista os contextos públicos do Valley Universal e explica a finalidade de cada um. Não concede acesso.",
      inputSchema: {},
    },
    async () => ({
      content: [
        {
          type: "text" as const,
          text: "O Valley Universal possui cinco contextos de usuário. A disponibilidade real depende da autenticação e das permissões do backend.",
        },
      ],
      structuredContent: {
        contexts,
        authorizationNotice:
          "Selecionar ou mencionar um contexto não concede permissão. O Valley valida perfil, vínculo e situação cadastral após o login.",
      },
    }),
  )
  .registerTool(
    {
      name: "valley_get_release_status",
      description:
        "Consulta o estado público das entregas web/PWA, Android e MCP do Valley Universal.",
      inputSchema: {},
    },
    async () => ({
      content: [
        {
          type: "text" as const,
          text: "A versão web/PWA está publicada. O contêiner Android e o workflow do APK estão versionados. O endpoint MCP está preparado para implantação separada.",
        },
      ],
      structuredContent: {
        web: {
          status: "published",
          url: VALLEY_APP_URL,
          capabilities: [
            "responsive web",
            "PWA install",
            "Google authentication",
            "context switching",
            "admin boundary",
          ],
        },
        android: {
          status: "source-and-ci-versioned",
          module: "apps/valley-android/universal",
        },
        mcp: {
          status: "scaffold-versioned",
          accessMode: "read-only",
        },
      },
    }),
  )
  .registerTool(
    {
      name: "valley_open_app",
      description:
        "Retorna a URL oficial do Valley Universal e orienta a pessoa a escolher um contexto dentro do aplicativo.",
      inputSchema: {
        context: z
          .enum(["PERSONAL", "RIDER", "BUSINESS", "ONE_SERVICE", "PDV"])
          .optional()
          .describe("Contexto que a pessoa pretende utilizar."),
      },
    },
    async ({ context }) => {
      const selected = context
        ? contexts.find((item) => item.id === context)
        : undefined;
      return {
        content: [
          {
            type: "text" as const,
            text: selected
              ? `Abra o Valley e, após entrar, selecione o contexto ${selected.label}. O acesso depende das permissões da conta.`
              : "Abra o Valley, entre com sua conta e escolha um dos contextos autorizados.",
          },
        ],
        structuredContent: {
          url: VALLEY_APP_URL,
          requestedContext: selected ?? null,
          authorizationNotice:
            "Esta ferramenta não autentica, não concede papéis e não contorna homologações.",
        },
      };
    },
  );

export type AppType = typeof server;

await server.run();

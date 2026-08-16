import { fileURLToPath } from "node:url";
import path from "node:path";

const scriptPath = fileURLToPath(import.meta.url);

export function validatePagesProject(
  response,
  { projectName, expectedBranch = "main" } = {},
) {
  if (!projectName) {
    throw new Error("Identificador do projeto Pages não informado.");
  }
  if (!response || response.success !== true || !response.result) {
    throw new Error("Projeto Pages não encontrado ou resposta remota inválida.");
  }

  const project = response.result;
  if (project.name !== projectName) {
    throw new Error("Projeto Pages retornado não corresponde ao destino esperado.");
  }
  if (project.production_branch !== expectedBranch) {
    throw new Error(
      `Branch de produção remota inválida: esperado ${expectedBranch}.`,
    );
  }

  return project;
}

if (process.argv[1] && path.resolve(process.argv[1]) === scriptPath) {
  process.stdin.setEncoding("utf8");
  let input = "";
  for await (const chunk of process.stdin) {
    input += chunk;
  }
  const payload = JSON.parse(input);
  validatePagesProject(payload, {
    projectName: process.env.PAGES_PROJECT,
    expectedBranch: process.env.EXPECTED_PRODUCTION_BRANCH ?? "main",
  });
  console.log("Estado remoto do projeto Pages validado com sucesso.");
}

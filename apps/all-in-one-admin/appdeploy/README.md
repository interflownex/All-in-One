# Registro da aplicação publicada do AIO Admin

Registro técnico da aplicação funcional publicada no AppDeploy.

- App ID: `9135635066da434181`;
- URL: `https://9135635066da434181.v2.appdeploy.ai/`;
- versão funcional: `2.0.0`;
- público: Equipe Técnica e gestão administrativa;
- classificação: `Pendências > Técnico > Equipe Técnica`.

## Segurança

O backend exige autenticação Google e allowlist administrativa. O padrão sintético de QA do AppDeploy é aceito exclusivamente pelo ambiente isolado de testes automatizados. Dados administrativos não são públicos.

## Estado entregue

O AppDeploy concluiu cinco testes ponta a ponta: login/dashboard, persistência de empresa, aprovação móvel, proteção de módulo obrigatório e recuperação após falha do servidor.

A interface-base versionada permanece em `apps/all-in-one-admin`, e o instalador Android usa a aplicação publicada como fonte operacional sincronizada.

# GOAL #126 — Ícone empresarial dinâmico

**Classificação:** Pendências / Técnico  
**Público-alvo:** Pessoa Jurídica (B2B), Pessoa Física (B2C) e Equipe Técnica  
**Status:** arquitetura aprovada; fundação executada em branch; ativação visual bloqueada até inclusão dos frames oficiais.

## Decisão aprovada

O Android não terá o ícone principal do APK substituído silenciosamente. O Valley e o Valley Rider usarão a API oficial de atalhos fixados para adicionar à tela inicial um ícone composto por:

- moldura oficial Valley ou Valley Rider;
- aro e estrela preservados;
- logomarca aprovada da empresa no centro;
- nome Valley ou Valley Rider na parte inferior.

Selfies e imagens pessoais são proibidas. Quando o launcher não oferecer suporte, o ícone padrão permanece disponível.

## Entregas desta rodada

- ponte Flutter `CompanyLauncherShortcut`;
- composição local em bitmap adaptativo;
- ponte Android nativa via `MethodChannel`;
- `ShortcutManager.requestPinShortcut` com confirmação do sistema;
- vínculo do atalho ao `companyId`;
- instalação automática da ponte na plataforma Android efêmera;
- validação determinística no configurador do build;
- testes de contrato contra técnicas não aprovadas.

## Bloqueio visual obrigatório

A funcionalidade não deve ser exposta na interface antes de serem versionados e aprovados estes ativos transparentes:

```text
apps/valley-flutter/assets/brand/valley-shortcut-frame.png
apps/valley-flutter/assets/brand/valley-rider-shortcut-frame.png
```

Não gerar placeholders e não derivar uma moldura nova sem autorização de marca.

## Contrato de integração

O backend deverá fornecer apenas logomarcas com estado `APPROVED`, acompanhadas de `companyId`, `logoVersion` e `logoHash`. A abertura pelo atalho não substitui autenticação, autorização, vínculo empresarial ou RBAC.

## Critérios para ativação

- [x] arquitetura Android oficial definida;
- [x] ponte Flutter implementada;
- [x] ponte Android implementada;
- [x] fallback preservado;
- [x] testes de contrato adicionados;
- [ ] frames oficiais aprovados e versionados;
- [ ] chamada de UI conectada ao cadastro empresarial;
- [ ] resposta do backend com logo aprovada;
- [ ] homologação em Pixel, Samsung, Motorola e Xiaomi;
- [ ] feature flag habilitada após homologação.

## Rollback

A remoção ou desativação da chamada de UI interrompe novas solicitações de atalho sem afetar o ícone padrão do APK nem o acesso normal ao aplicativo.

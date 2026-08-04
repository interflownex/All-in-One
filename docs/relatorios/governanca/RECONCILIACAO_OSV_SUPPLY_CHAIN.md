# Reconciliação OSV-Scanner e segurança da cadeia de suprimentos

## Classificação

- Projeto: All in One + Valley
- Pasta lógica: Pendências
- Assunto: Técnico
- Público-alvo: Equipe Técnica

## Decisão

O workflow OSV-Scanner permanece fixado no commit oficial correspondente à versão 2.3.8:

```text
8dc09193bb540e09b23da07ad7e30bd33bf87018
```

A referência mutável `google/osv-scanner-action@main`, introduzida diretamente na branch principal, não é adotada.

## Justificativa

- referências mutáveis podem alterar código executado sem mudança no repositório consumidor;
- o commit fixado já executou com sucesso nos pull requests atuais;
- a atualização futura deve apontar para outra versão ou SHA revisado;
- dependências de workflow devem ser reproduzíveis e auditáveis.

## Regra mandatória

Nenhuma action externa de segurança pode usar `@main`, `@master` ou outra branch mutável. Versões principais somente são aceitas quando a política do repositório permitir explicitamente e houver proteção adicional; para reusable workflows de segurança, o padrão é SHA completo revisado.

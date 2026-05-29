# Preferencia obrigatoria de idioma

- Todas as respostas, alertas, erros, orientacoes, perguntas e opcoes devem ser escritos em portugues do Brasil.
- Essa regra vale para este workspace (`all-in-one`) e deve prevalecer sobre respostas em ingles quando nao houver conflito tecnico ou legal.
- Codigos, nomes de arquivos, comandos, identificadores, logs e mensagens externas devem permanecer no idioma/formato original quando isso preservar precisao tecnica.

# Sincronizacao Git obrigatoria

- Ao concluir cada atividade que altere arquivos neste workspace, executar sincronizacao Git automatica com `git add`, `git commit` e `git push`.
- O comando padrao e:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/git_auto_sync.ps1 -Activity "<descricao da atividade>"
```

- A politica persistente fica em `config/autonomy/git_auto_sync_policy.json`.
- Neste checkout, o push automatico deve usar o remoto `fork` quando `origin` nao aceitar escrita.
- Nao criar commit vazio quando nao houver mudancas.
- Se houver merge ou rebase em andamento, parar e reportar o bloqueio em portugues do Brasil.

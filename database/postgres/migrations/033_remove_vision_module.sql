-- Remoção definitiva do módulo Vision do escopo ativo do All-in-One.
-- Antes de aplicar em produção, confirme que qualquer dado necessário foi exportado.
BEGIN;
DROP SCHEMA IF EXISTS vision CASCADE;
COMMIT;

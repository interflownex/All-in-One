BEGIN;

ALTER TABLE compliance.catalog_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance.catalog_versions FORCE ROW LEVEL SECURITY;

ALTER TABLE compliance.field_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance.field_registry FORCE ROW LEVEL SECURITY;

COMMENT ON TABLE compliance.catalog_versions IS
    'Versões físicas do catálogo regulatório executável All in One + Valley. RLS forçada sem políticas permissivas até definição e homologação das roles de aplicação.';

COMMENT ON TABLE compliance.field_registry IS
    'Registro físico versionado dos campos, finalidades, bases, controles e retenção. RLS forçada sem políticas permissivas até definição e homologação das roles de aplicação.';

COMMIT;

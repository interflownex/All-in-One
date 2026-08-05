BEGIN;

ALTER TABLE compliance.field_registry NO FORCE ROW LEVEL SECURITY;
ALTER TABLE compliance.field_registry DISABLE ROW LEVEL SECURITY;

ALTER TABLE compliance.catalog_versions NO FORCE ROW LEVEL SECURITY;
ALTER TABLE compliance.catalog_versions DISABLE ROW LEVEL SECURITY;

COMMENT ON TABLE compliance.catalog_versions IS
    'Versões físicas do catálogo regulatório executável All in One + Valley.';

COMMENT ON TABLE compliance.field_registry IS
    'Registro físico versionado dos campos, finalidades, bases, controles e retenção.';

COMMIT;

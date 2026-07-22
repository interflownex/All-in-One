BEGIN;

DROP TABLE IF EXISTS forms.form_billing_events;
DROP TABLE IF EXISTS forms.form_submission_values;
DROP TABLE IF EXISTS forms.form_submissions;
DROP TABLE IF EXISTS forms.form_publications;
DROP TABLE IF EXISTS forms.form_homologations;
DROP TABLE IF EXISTS forms.form_permissions;
DROP TABLE IF EXISTS forms.form_calculations;
DROP TABLE IF EXISTS forms.form_validations;
ALTER TABLE IF EXISTS forms.form_fields DROP CONSTRAINT IF EXISTS form_fields_visibility_fk;
ALTER TABLE IF EXISTS forms.form_blocks DROP CONSTRAINT IF EXISTS form_blocks_visibility_fk;
DROP TABLE IF EXISTS forms.form_visibility_rules;
DROP TABLE IF EXISTS forms.form_fields;
DROP TABLE IF EXISTS forms.form_blocks;
ALTER TABLE IF EXISTS forms.form_definitions DROP CONSTRAINT IF EXISTS form_definitions_current_version_fk;
DROP TABLE IF EXISTS forms.form_versions;
DROP TABLE IF EXISTS forms.form_definitions;
DROP TABLE IF EXISTS forms.field_bindings;
DROP TABLE IF EXISTS forms.field_catalog;
DROP FUNCTION IF EXISTS forms.reject_published_child_mutation();
DROP FUNCTION IF EXISTS forms.reject_published_version_mutation();
DROP SCHEMA IF EXISTS forms;

COMMIT;

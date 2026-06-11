BEGIN;

-- 1. IDENTITY
INSERT INTO identity.users (
    id, full_name, cpf_document, birth_date, email, phone_e164, 
    password_hash, face_hash, terms_accepted_at, lgpd_consent_at, status, liveness_score
) VALUES 
('10000000-0000-0000-0000-000000000001', 'Administrador Sistema', '11122233344', '1980-01-01', 'admin@valley.com', '+5511911111111', 'hash', 'face_admin', NOW(), NOW(), 'active', 0.99),
('10000000-0000-0000-0000-000000000002', 'João Silva', '22233344455', '1985-05-20', 'joao@gmail.com', '+5511922222222', 'hash', 'face_joao', NOW(), NOW(), 'active', 0.98),
('10000000-0000-0000-0000-000000000003', 'Maria Oliveira', '33344455566', '1992-11-03', 'maria@outlook.com', '+5511933333333', 'hash', 'face_maria', NOW(), NOW(), 'active', 0.97)
ON CONFLICT (id) DO NOTHING;

-- 2. BUSINESS
INSERT INTO business.companies (
    id, user_id, cnpj, root_cnpj, legal_name, legal_representative_user_id, status
) VALUES 
('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '11222333000100', '11222333', 'Valley Tecnologia LTDA', '10000000-0000-0000-0000-000000000001', 'active'),
('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', '22333444000199', '22333444', 'João Silva Reformas ME', '10000000-0000-0000-0000-000000000002', 'active'),
('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', '99888777000188', '99888777', 'Oliveira Transportes S.A.', '10000000-0000-0000-0000-000000000003', 'active')
ON CONFLICT (id) DO NOTHING;

-- Para os outros módulos, se a tabela tiver muitas restrições, usaremos metadados JSONB para simplificar se disponível,
-- mas aqui tentaremos manter o padrão das primeiras migrações.

COMMIT;

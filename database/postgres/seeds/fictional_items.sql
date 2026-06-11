BEGIN;

-- Criar um usuário vendedor se não existir (ou usar o primeiro disponível)
INSERT INTO identity.users (
    id, full_name, cpf_document, birth_date, email, phone_e164, 
    password_hash, face_hash, terms_accepted_at, lgpd_consent_at, status, liveness_score
) VALUES (
    '00000000-0000-0000-0000-000000000001', 'Vendedor Valley', '12345678901', '1980-01-01', 
    'vendedor@valley.com', '+5511999999999', 'hash', 'face_vendedor', NOW(), NOW(), 'active', 0.95
) ON CONFLICT (id) DO NOTHING;

-- Criar uma empresa se não existir
INSERT INTO business.companies (
    id, user_id, cnpj, root_cnpj, legal_name, legal_representative_user_id, status
) VALUES (
    '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 
    '12345678000199', '12345678', 'Valley Store', '00000000-0000-0000-0000-000000000001', 'active'
) ON CONFLICT (id) DO NOTHING;

-- 1. Hambúrguer Gourmet Valley (Alimentos)
INSERT INTO business.catalog_offers (
    id, user_id, company_id, source_module, offer_type, title, short_description, 
    business_category, price_amount, status, metadata, published_at
) VALUES (
    '00000000-0000-0000-0000-000000000101', 
    '00000000-0000-0000-0000-000000000001', 
    '00000000-0000-0000-0000-000000000002', 
    'marketplace', 'food', 'Hambúrguer Gourmet Valley', 
    'Blend de 180g de carne premium, queijo canastra derretido, cebola caramelizada e pão artesanal.',
    'Alimentação', 45.90, 'published', 
    jsonb_build_object(
        'image_url', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80',
        'video_url', 'https://www.w3schools.com/html/mov_bbb.mp4',
        'ingredients', ARRAY['Carne 180g', 'Queijo Canastra', 'Cebola Caramelizada'],
        'calories', 850
    ),
    NOW()
) ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, metadata = EXCLUDED.metadata;

-- 2. Monitor Gamer UltraSharp 4K (Produtos)
INSERT INTO business.catalog_offers (
    id, user_id, company_id, source_module, offer_type, title, short_description, 
    business_category, price_amount, status, metadata, published_at
) VALUES (
    '00000000-0000-0000-0000-000000000102', 
    '00000000-0000-0000-0000-000000000001', 
    '00000000-0000-0000-0000-000000000002', 
    'marketplace', 'product', 'Monitor Gamer UltraSharp 4K', 
    'Monitor de 32 polegadas, 144Hz, HDR1000 e tempo de resposta de 1ms. O auge da imersão.',
    'Eletrônicos', 3499.00, 'published', 
    jsonb_build_object(
        'image_url', 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80',
        'video_url', 'https://www.w3schools.com/html/movie.mp4',
        'specs', jsonb_build_object('refresh_rate', '144Hz', 'resolution', '4K', 'panel', 'IPS')
    ),
    NOW()
) ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, metadata = EXCLUDED.metadata;

-- 3. Consultoria de IA Estratégica (Serviços)
INSERT INTO business.catalog_offers (
    id, user_id, company_id, source_module, offer_type, title, short_description, 
    business_category, price_amount, status, metadata, published_at
) VALUES (
    '00000000-0000-0000-0000-000000000103', 
    '00000000-0000-0000-0000-000000000001', 
    '00000000-0000-0000-0000-000000000002', 
    'marketplace', 'service', 'Consultoria de IA Estratégica', 
    'Implementação de agentes inteligentes e automação de processos via LLMs de última geração.',
    'Tecnologia', NULL, 'published', 
    jsonb_build_object(
        'image_url', 'https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80',
        'video_url', 'https://www.w3schools.com/html/mov_bbb.mp4',
        'duration_weeks', 4,
        'specialties', ARRAY['NLP', 'Computer Vision', 'Generative AI']
    ),
    NOW()
) ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, metadata = EXCLUDED.metadata;

COMMIT;

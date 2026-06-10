import { useState } from 'react';

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL || 'http://localhost:8000';

export default function OfferWizard({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    offer_type: 'product',
    category_id: '',
    title: '',
    short_description: '',
    price_amount: 0,
    availability_type: 'immediate',
    location_type: 'online',
    source_module: 'marketplace'
  });

  type OfferForm = typeof formData

  const updateForm = <Key extends keyof OfferForm>(key: Key, value: OfferForm[Key]) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const publishOffer = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_HUB_URL}/gateway/business/valley/catalog/offers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });
      if (!response.ok) throw new Error('Falha ao publicar');
      
      const data = await response.json();
      
      
      await fetch(`${API_HUB_URL}/gateway/business/valley/catalog/offers/${data.id}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'published' })
      });
      
      alert('Oferta publicada com sucesso no Valley!');
      onClose();
    } catch (err) {
      alert('Erro ao publicar: ' + String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
      <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', width: '90%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <h2>Publicar Nova Oferta - Passo {step} de 11</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer' }}>&times;</button>
        </div>

        {step === 1 && (
          <div>
            <h3>1. O que você vende?</h3>
            <select 
              value={formData.offer_type} 
              onChange={e => updateForm('offer_type', e.target.value)}
              style={{ width: '100%', padding: '0.5rem', margin: '1rem 0' }}
            >
              <option value="product">Produto Físico/Digital</option>
              <option value="service">Serviço Profissional</option>
              <option value="food">Alimentação/Delivery</option>
              <option value="appointment">Consulta/Agendamento</option>
            </select>
          </div>
        )}

        {step === 2 && (
          <div>
            <h3>2. Categoria</h3>
            <input type="text" placeholder="Ex: Eletrônicos, Serviços Domésticos" style={{ width: '100%', padding: '0.5rem', margin: '1rem 0' }} onChange={e => updateForm('category_id', e.target.value)} />
          </div>
        )}

        {step === 3 && (
          <div>
            <h3>3. Título e Descrição</h3>
            <input type="text" placeholder="Título da Oferta" value={formData.title} onChange={e => updateForm('title', e.target.value)} style={{ width: '100%', padding: '0.5rem', margin: '0.5rem 0' }} />
            <textarea placeholder="Descrição curta" value={formData.short_description} onChange={e => updateForm('short_description', e.target.value)} style={{ width: '100%', padding: '0.5rem', margin: '0.5rem 0', minHeight: '100px' }} />
          </div>
        )}

        {/* Simplificando steps intermediários visualmente para o MVP, mas mantendo a jornada em 11 */}
        {step > 3 && step < 10 && (
          <div>
            <h3>Passo {step} (Configurações Adicionais)</h3>
            <p>Configurando imagens, preços, estoque, etc.</p>
            {step === 5 && (
              <input type="number" placeholder="Preço (R$)" value={formData.price_amount} onChange={e => updateForm('price_amount', parseFloat(e.target.value))} style={{ width: '100%', padding: '0.5rem', margin: '1rem 0' }} />
            )}
          </div>
        )}

        {step === 10 && (
          <div>
            <h3>10. Revisão</h3>
            <pre style={{ background: '#f1f5f9', padding: '1rem', borderRadius: '4px' }}>
              {JSON.stringify(formData, null, 2)}
            </pre>
          </div>
        )}

        {step === 11 && (
          <div>
            <h3>11. Publicar no Valley</h3>
            <p>Sua oferta estará disponível imediatamente para todos os clientes.</p>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2rem' }}>
          <button 
            disabled={step === 1 || loading} 
            onClick={() => setStep(s => s - 1)}
            style={{ padding: '0.5rem 1rem', background: '#cbd5e1', border: 'none', borderRadius: '4px' }}
          >
            Voltar
          </button>
          
          {step < 11 ? (
            <button 
              onClick={() => setStep(s => s + 1)}
              style={{ padding: '0.5rem 1rem', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px' }}
            >
              Avançar
            </button>
          ) : (
            <button 
              onClick={publishOffer}
              disabled={loading}
              style={{ padding: '0.5rem 1rem', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', fontWeight: 'bold' }}
            >
              {loading ? 'Publicando...' : 'Publicar Agora'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

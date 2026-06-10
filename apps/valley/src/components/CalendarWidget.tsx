import { useEffect, useState } from 'react';

const API_HUB_URL = import.meta.env.VITE_API_HUB_URL ?? '';

export default function CalendarWidget() {
  const [slots, setSlots] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    
    fetch(`${API_HUB_URL}/services/providers/mock-provider/time-slots?date=2026-06-10`)
      .then(res => res.json())
      .then(data => {
        setSlots(data.available_slots || ["09:00", "10:00", "11:30", "14:00", "15:30"]);
        setLoading(false);
      })
      .catch(() => {
        
        setSlots(["09:00", "10:00", "11:30", "14:00", "15:30"]);
        setLoading(false);
      });
  }, []);

  const handleReserve = async () => {
    if (!selectedSlot) return;
    try {
      const res = await fetch(`${API_HUB_URL}/services/providers/mock-provider/reserve-slot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot: selectedSlot, customer_id: 'cust-123' })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erro ao reservar');
      setMessage(`Sucesso! Horário ${selectedSlot} reservado.`);
      setSlots(slots.filter(s => s !== selectedSlot));
      setSelectedSlot(null);
    } catch (err: unknown) {
      setMessage(`Erro: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  return (
    <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <h2 style={{ marginBottom: '1rem', color: '#0f172a' }}>Gerenciamento de Agenda (Motor de Conflitos)</h2>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>Data: 10 de Junho de 2026</p>
      
      {message && <div style={{ padding: '1rem', marginBottom: '1rem', background: message.startsWith('Erro') ? '#fee2e2' : '#d1fae5', color: message.startsWith('Erro') ? '#991b1b' : '#065f46', borderRadius: '4px' }}>{message}</div>}

      {loading ? (
        <p>Carregando slots...</p>
      ) : (
        <div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
            {slots.map(slot => (
              <button
                key={slot}
                onClick={() => setSelectedSlot(slot)}
                style={{
                  padding: '0.5rem 1rem',
                  border: `2px solid ${selectedSlot === slot ? '#3b82f6' : '#e2e8f0'}`,
                  background: selectedSlot === slot ? '#eff6ff' : 'white',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                {slot}
              </button>
            ))}
          </div>
          <button 
            onClick={handleReserve}
            disabled={!selectedSlot}
            style={{ padding: '0.75rem 1.5rem', background: selectedSlot ? '#3b82f6' : '#94a3b8', color: 'white', border: 'none', borderRadius: '4px', cursor: selectedSlot ? 'pointer' : 'not-allowed' }}
          >
            Bloquear Horário
          </button>
        </div>
      )}
    </div>
  );
}

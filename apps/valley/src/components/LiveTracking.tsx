import React, { useState, useEffect } from 'react';

const WEBSOCKET_URL = import.meta.env.VITE_API_HUB_URL?.replace('http', 'ws') || 'ws://localhost:8000';

export default function LiveTracking({ deliveryId = 'del-123' }) {
  const [logs, setLogs] = useState<string[]>([]);
  const [position, setPosition] = useState({ lat: -23.5505, lng: -46.6333 });
  const [connected, setConnected] = useState(false);
  const positionRef = React.useRef(position);

  useEffect(() => {
    positionRef.current = position;
  }, [position]);

  useEffect(() => {
    const ws = new WebSocket(`${WEBSOCKET_URL}/ws/tracking/${deliveryId}`);
    let intervalId: ReturnType<typeof setInterval>;

    ws.onopen = () => {
      setConnected(true);
      setLogs(prev => [...prev, `[SISTEMA] Conectado ao rastreamento: ${deliveryId}`]);
      
      intervalId = setInterval(() => {
        if(ws.readyState === WebSocket.OPEN) {
           ws.send(JSON.stringify({ 
             lat: positionRef.current.lat + (Math.random() * 0.001), 
             lng: positionRef.current.lng + (Math.random() * 0.001) 
           }));
        }
      }, 5000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status === 'connected') {
          setPosition({ lat: data.lat, lng: data.lng });
        } else if (data.update) {
           const parsedUpdate = JSON.parse(data.update);
           setPosition({ lat: parsedUpdate.lat, lng: parsedUpdate.lng });
           setLogs(prev => [...prev, `[SISTEMA] GPS Atualizado: Lat ${parsedUpdate.lat.toFixed(4)}, Lng ${parsedUpdate.lng.toFixed(4)}`].slice(-5));
        }
      } catch (e) {
        console.error(e);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      setLogs(prev => [...prev, `[SISTEMA] Desconectado do servidor.`]);
    };

    return () => {
      clearInterval(intervalId);
      ws.close();
    };
  }, [deliveryId]);

  return (
    <div style={{ background: '#0f172a', padding: '2rem', minHeight: '100vh', color: 'white' }}>
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem' }}>Live Tracking (WebSockets)</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: connected ? '#10b981' : '#ef4444' }} />
          <span>{connected ? 'Sinal Ativo' : 'Buscando sinal GPS...'}</span>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>
        <div style={{ background: '#1e293b', borderRadius: '8px', padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
          {/* Mock Map view */}
          <div style={{ width: '60px', height: '60px', background: '#3b82f6', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)', transition: 'all 0.3s ease' }}>
            📍
          </div>
          <p style={{ marginTop: '1rem', color: '#94a3b8' }}>
            {position.lat.toFixed(5)}, {position.lng.toFixed(5)}
          </p>
          <h3 style={{ marginTop: '2rem' }}>Motorista a caminho!</h3>
        </div>

        <div style={{ background: '#1e293b', borderRadius: '8px', padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid #334155', paddingBottom: '0.5rem' }}>Logs da Telemetria</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontFamily: 'monospace', fontSize: '0.875rem', color: '#a7f3d0' }}>
            {logs.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

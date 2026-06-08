import React, { useState } from 'react';

const RidersPermissions: React.FC = () => {
  const [query, setQuery] = useState('');

  return (
    <div className="container">
      <section className="hero">
        <h1>RidersPermissions</h1>
        <p>Gerencie seus itens com facilidade.</p>
      </section>

      <div className="filters-section">
        <div className="search-row">
          <input 
            type="text" 
            placeholder="Buscar..." 
            value={query} 
            onChange={(e) => setQuery(e.target.value)} 
          />
          <button className="btn-primary">Filtrar</button>
        </div>
      </div>

      <div className="data-grid">
        <div className="empty-state">
          <p>Nenhum item encontrado.</p>
        </div>
      </div>
    </div>
  );
};

export default RidersPermissions;

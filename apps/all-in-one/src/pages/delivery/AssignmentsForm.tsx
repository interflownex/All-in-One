import React, { useState } from 'react';

const AssignmentsForm: React.FC = () => {
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    setTimeout(() => setLoading(false), 1000);
  };

  return (
    <div className="container">
      <form className="neo-form" onSubmit={handleSubmit}>
        <h2>Novo Registro - AssignmentsForm</h2>
        <div className="field-group">
          <label>Nome</label>
          <input type="text" placeholder="Digite o nome..." required />
        </div>
        <div className="field-group">
          <label>Descrição</label>
          <textarea placeholder="Detalhes opcionais..."></textarea>
        </div>
        <div className="actions-row">
          <button type="button" className="btn-secondary">Cancelar</button>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Salvando...' : 'Confirmar'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AssignmentsForm;

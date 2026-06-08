import React from 'react';

const BpmOverview: React.FC = () => {
  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <nav>
          <ul>
            <li className="active">Visão Geral</li>
            <li>Relatórios</li>
            <li>Configurações</li>
          </ul>
        </nav>
      </aside>
      <main className="dashboard-content">
        <header className="content-header">
          <h1>BpmOverview</h1>
          <button className="btn-primary">Ação Rápida</button>
        </header>
        <section className="metrics-grid">
          <div className="metric-card">
            <h3>Total</h3>
            <p className="value">0</p>
          </div>
          <div className="metric-card">
            <h3>Ativos</h3>
            <p className="value">0</p>
          </div>
        </section>
      </main>
    </div>
  );
};

export default BpmOverview;

import argparse
import os
from pathlib import Path

# Templates boilerplate TSX

DASHBOARD_TEMPLATE = """import React from 'react';

const {name}: React.FC = () => {{
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
          <h1>{name}</h1>
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
}};

export default {name};
"""

LIST_TEMPLATE = """import React, {{ useState }} from 'react';

const {name}: React.FC = () => {{
  const [query, setQuery] = useState('');

  return (
    <div className="container">
      <section className="hero">
        <h1>{name}</h1>
        <p>Gerencie seus itens com facilidade.</p>
      </section>

      <div className="filters-section">
        <div className="search-row">
          <input 
            type="text" 
            placeholder="Buscar..." 
            value={{query}} 
            onChange={{(e) => setQuery(e.target.value)}} 
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
}};

export default {name};
"""

FORM_TEMPLATE = """import React, {{ useState }} from 'react';

const {name}: React.FC = () => {{
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {{
    e.preventDefault();
    setLoading(true);
    // Simular submissão
    setTimeout(() => setLoading(false), 1000);
  }};

  return (
    <div className="container">
      <form className="neo-form" onSubmit={{handleSubmit}}>
        <h2>Novo Registro - {name}</h2>
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
          <button type="submit" className="btn-primary" disabled={{loading}}>
            {{loading ? 'Salvando...' : 'Confirmar'}}
          </button>
        </div>
      </form>
    </div>
  );
}};

export default {name};
"""

MODAL_TEMPLATE = """import React from 'react';

interface {name}Props {{
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}}

const {name}: React.FC<{name}Props> = ({{ isOpen, onClose, onConfirm }}) => {{
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content neo-brutalism">
        <header>
          <h2>{name}</h2>
          <button onClick={{onClose}} className="close-btn">&times;</button>
        </header>
        <div className="modal-body">
          <p>Você tem certeza que deseja realizar esta ação?</p>
        </div>
        <footer>
          <button className="btn-secondary" onClick={{onClose}}>Cancelar</button>
          <button className="btn-primary" onClick={{onConfirm}}>Confirmar</button>
        </footer>
      </div>
    </div>
  );
}};

export default {name};
"""

def generate_template(app_name, template_type, component_name, sub_dest):
    root = Path(__file__).resolve().parents[1]
    dest_path = root / "apps" / app_name / "src" / sub_dest
    
    if not dest_path.exists():
        dest_path.mkdir(parents=True)
        print(f"Diretório criado: {dest_path}")

    file_name = f"{component_name}.tsx"
    full_path = dest_path / file_name

    templates = {
        "dashboard": DASHBOARD_TEMPLATE,
        "list": LIST_TEMPLATE,
        "form": FORM_TEMPLATE,
        "modal": MODAL_TEMPLATE
    }

    if template_type not in templates:
        print(f"Erro: Tipo de template '{template_type}' não suportado.")
        return

    content = templates[template_type].format(name=component_name)
    
    full_path.write_text(content, encoding="utf-8")
    print(f"✅ Componente '{component_name}' criado com sucesso em: {full_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold de UI Templates para o Valley")
    parser.add_argument("--app", required=True, help="Nome da app (valley ou valley_business)")
    parser.add_argument("--type", required=True, choices=["dashboard", "list", "form", "modal"], help="Tipo de template")
    parser.add_argument("--name", required=True, help="Nome do componente")
    parser.add_argument("--dest", default="components", help="Subdiretório de destino dentro de src/")

    args = parser.parse_args()
    generate_template(args.app, args.type, args.name, args.dest)

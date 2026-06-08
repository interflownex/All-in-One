import json
from pathlib import Path

def generate_app_tsx():
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "config" / "stitch" / "screen_manifest.json"
    
    if not manifest_path.exists():
        print("Erro: Manifesto não encontrado.")
        return

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    
    imports = [
        "import React, { Suspense, lazy } from 'react';",
        "import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';",
        "import Navigation from './components/Navigation';",
        "import './index.css';"
    ]
    
    routes = []
    
    for project in manifest["projects"]:
        module = project["module"]
        # Overview
        name = f"{module.capitalize()}Overview"
        path = f"./pages/{module}/{name}"
        imports.append(f"const {name} = lazy(() => import('{path}'));")
        routes.append(f'<Route path="/{module}" element={{{name} ? <{name} /> : <div>Carregando...</div>}} />')
        
        # Mapping other special screens
        for special in project.get("special_screens", []):
            comp_name = "".join(word.capitalize() for word in special.split("_"))
            path = f"./pages/{module}/{comp_name}"
            imports.append(f"const {comp_name} = lazy(() => import('{path}'));")
            routes.append(f'<Route path="/{module}/{special.replace("_", "-")}" element={{{comp_name} ? <{comp_name} /> : <div>Carregando...</div>}} />')

    app_content = f"""
{chr(10).join(imports)}

function App() {{
  return (
    <Router>
      <div className="app-layout">
        <Navigation />
        <main className="content-area">
          <Suspense fallback={{<div className="loader">Carregando...</div>}}>
            <Routes>
              <Route path="/" element={{<div className="container hero"><h1>Bem-vindo ao All-in-One</h1><p>Selecione um módulo no menu lateral para começar.</p></div>}} />
              {chr(10).join('              ' + r for r in routes)}
            </Routes>
          </Suspense>
        </main>
      </div>
    </Router>
  );
}}

export default App;
"""
    
    app_path = root / "apps" / "all-in-one" / "src" / "App.tsx"
    app_path.write_text(app_content, encoding="utf-8")
    print(f"✅ App.tsx gerado com sucesso em: {app_path}")

if __name__ == "__main__":
    generate_app_tsx()

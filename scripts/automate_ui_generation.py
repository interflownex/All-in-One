import json
import subprocess
from pathlib import Path

# Configuração de mapeamento: Tipo de tela Stitch -> Tipo de template Scaffold
TYPE_MAPPING = {
    "overview": "dashboard",
    "audit_permissions": "list",
    "one_screen_per_entity": "list", # Listagem é o padrão para entidades
}

def run_scaffold(app, template_type, name, dest):
    cmd = [
        "python3", "scripts/scaffold_ui_templates.py",
        "--app", app,
        "--type", template_type,
        "--name", name,
        "--dest", dest
    ]
    print(f"Executando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def automate_ui_generation():
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "config" / "stitch" / "screen_manifest.json"
    catalog_path = root / "config" / "module_catalog.json"
    
    if not manifest_path.exists() or not catalog_path.exists():
        print("Erro: Manifestos não encontrados.")
        return

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    
    # Criar um mapa de entidades por módulo para 'one_screen_per_entity'
    module_entities = {m["slug"]: m["entities"] for m in catalog["modules"]}
    
    # Mapeamento de módulo para App principal (heurística simples)
    # A maioria das telas de gerenciamento vai para 'valley-business' (B2B)
    # Telas de consumidor vão para 'valley'
    
    for project in manifest["projects"]:
        module = project["module"]
        # Determinar app de destino
        # O usuário especificou que o nome deve ser apenas 'all-in-one'
        target_app = "all-in-one" 
        
        print(f"\n🏗️ Gerando telas para o módulo: {module}")
        
        # 1. Telas Padrão (overview, audit, entities)
        for std_type in manifest["screen_generation"]["standard"]:
            if std_type == "overview":
                name = f"{module.capitalize()}Overview"
                run_scaffold(target_app, "dashboard", name, f"pages/{module}")
            
            elif std_type == "audit_permissions":
                name = f"{module.capitalize()}Permissions"
                run_scaffold(target_app, "list", name, f"pages/{module}")
                
            elif std_type == "one_screen_per_entity":
                entities = module_entities.get(module, [])
                for entity in entities:
                    # Converter snake_case para PascalCase
                    name = "".join(word.capitalize() for word in entity.split("_"))
                    name = f"{name}List"
                    run_scaffold(target_app, "list", name, f"pages/{module}")
                    
                    # Gerar também um formulário para cada entidade (opcional, mas útil)
                    form_name = name.replace("List", "Form")
                    run_scaffold(target_app, "form", form_name, f"pages/{module}")

        # 2. Telas Especiais
        for special in project.get("special_screens", []):
            name = "".join(word.capitalize() for word in special.split("_"))
            # Heurística: se tem 'search' é list, se tem 'manager/control' é dashboard, resto form/modal
            template = "form"
            if "search" in special or "list" in special:
                template = "list"
            elif "manager" in special or "control" in special or "overview" in special:
                template = "dashboard"
            elif "modal" in special or "dialog" in special:
                template = "modal"
            
            run_scaffold(target_app, template, name, f"pages/{module}")

if __name__ == "__main__":
    automate_ui_generation()

import React, { memo, useDeferredValue, useEffect, useMemo, useState } from 'react';
import { loadCatalog, requestHomologation, saveDocument } from '../features/dynamicForms/api';
import { createField, demoBindings, demoCatalog, loadLocalDocument, saveLocalDocument } from '../features/dynamicForms/model';
import type { BuilderDocument, BuilderFeedback, BuilderField, CatalogField, FieldBinding } from '../features/dynamicForms/types';

type IconName = 'search' | 'filter' | 'save' | 'eye' | 'send' | 'plus' | 'up' | 'down' | 'trash' | 'settings' | 'close' | 'field';

const Icon = ({ name, size = 18 }: { name: IconName; size?: number }) => {
  const paths: Record<IconName, React.ReactNode> = {
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    filter: <path d="M4 5h16l-6 7v5l-4 2v-7Z"/>,
    save: <><path d="M5 4h12l2 2v14H5Z"/><path d="M8 4v6h8V4M8 20v-6h8v6"/></>,
    eye: <><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></>,
    send: <><path d="m3 11 18-8-8 18-2-8Z"/><path d="m11 13 5-5"/></>,
    plus: <path d="M12 5v14M5 12h14"/>,
    up: <path d="m6 15 6-6 6 6"/>,
    down: <path d="m6 9 6 6 6-6"/>,
    trash: <><path d="M4 7h16M9 7V4h6v3M7 7l1 13h8l1-13"/><path d="M10 11v5M14 11v5"/></>,
    settings: <><circle cx="12" cy="12" r="3"/><path d="M19 13.5v-3l-2-.7-.5-1.2.9-1.9-2.1-2.1-1.9.9-1.2-.5L11.5 3h-3l-.7 2-1.2.5-1.9-.9-2.1 2.1.9 1.9L3 9.8l-2 .7v3l2 .7.5 1.2-.9 1.9 2.1 2.1 1.9-.9 1.2.5.7 2h3l.7-2 1.2-.5 1.9.9 2.1-2.1-.9-1.9.5-1.2Z"/></>,
    close: <path d="m6 6 12 12M18 6 6 18"/>,
    field: <><path d="M5 5h14v14H5Z"/><path d="M8 9h8M8 13h5"/></>,
  };
  return <svg className="df-icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
};

const componentLabel: Record<string, string> = {
  text: 'Texto curto', textarea: 'Texto longo', number: 'Número', decimal: 'Decimal', currency: 'Moeda',
  email: 'E-mail', phone: 'Telefone', date: 'Data', datetime: 'Data e hora', select: 'Lista suspensa',
  multiselect: 'Seleção múltipla', checkbox: 'Sim/Não', file: 'Arquivo', unit: 'Unidade', radio: 'Seleção única',
};

const CatalogRail = memo(function CatalogRail({ catalog, bindings, search, onSearch, onAdd }: {
  catalog: CatalogField[]; bindings: FieldBinding[]; search: string; onSearch: (value: string) => void; onAdd: (field: CatalogField, binding: FieldBinding) => void;
}) {
  const deferredSearch = useDeferredValue(search.toLocaleLowerCase('pt-BR'));
  const bindingMap = useMemo(() => new Map(bindings.map(item => [item.field_catalog_id, item])), [bindings]);
  const filtered = useMemo(() => catalog.filter(item => `${item.description} ${item.logical_field} ${item.data_type}`.toLocaleLowerCase('pt-BR').includes(deferredSearch)), [catalog, deferredSearch]);
  return (
    <aside className="df-catalog" aria-label="Catálogo de campos permitidos">
      <h2>Campos disponíveis</h2>
      <div className="df-search"><Icon name="search"/><input value={search} onChange={event => onSearch(event.target.value)} placeholder="Buscar campo" aria-label="Buscar campo"/><button type="button" aria-label="Filtrar catálogo"><Icon name="filter"/></button></div>
      <div className="df-catalog-tabs" role="tablist"><button className="active" role="tab">Todos</button><button role="tab">Básicos</button><button role="tab">Avançados</button></div>
      <div className="df-catalog-list">
        {filtered.map(item => {
          const binding = bindingMap.get(item.id);
          return <button key={item.id} type="button" disabled={!binding} onClick={() => binding && onAdd(item, binding)} className="df-catalog-row">
            <span className="df-field-symbol"><Icon name="field" size={16}/></span><span><strong>{item.description}</strong><small>{item.logical_entity}.{item.logical_field}</small></span><em>{item.data_type}</em><Icon name="plus" size={16}/>
          </button>;
        })}
        {!filtered.length ? <p className="df-empty">Nenhum campo permitido corresponde à busca.</p> : null}
      </div>
      <p className="df-catalog-note">Somente campos e bindings lógicos autorizados pelo backend.</p>
    </aside>
  );
});

const PreviewControl = ({ field }: { field: BuilderField }) => {
  if (field.component === 'textarea') return <textarea placeholder={field.placeholder || field.help_text} disabled={field.read_only}/>;
  if (field.component === 'checkbox') return <label className="df-preview-check"><input type="checkbox" disabled={field.read_only}/> Sim</label>;
  if (field.component === 'select' || field.component === 'multiselect' || field.component === 'radio') return <select disabled={field.read_only}><option>Selecione uma opção</option></select>;
  const type = field.component === 'email' ? 'email' : field.component === 'date' ? 'date' : field.component === 'datetime' ? 'datetime-local' : field.component === 'number' ? 'number' : 'text';
  return <div className={field.component === 'currency' ? 'df-money-input' : ''}>{field.component === 'currency' ? <span>R$</span> : null}<input type={type} placeholder={field.placeholder || (field.component === 'email' ? 'email@exemplo.com' : '')} disabled={field.read_only}/></div>;
};

const FormCanvas = ({ document, selectedId, preview, onSelect, onMove, onRemove, onAddSection }: {
  document: BuilderDocument; selectedId: string | null; preview: boolean; onSelect: (id: string) => void; onMove: (id: string, direction: -1 | 1) => void; onRemove: (id: string) => void; onAddSection: () => void;
}) => (
  <main className={`df-canvas ${preview ? 'preview' : ''}`} aria-label={preview ? 'Pré-visualização do formulário' : 'Canvas do formulário'}>
    {document.blocks.map(block => {
      const fields = document.fields.filter(field => field.block_id === block.id).toSorted((a, b) => a.display_order - b.display_order);
      return <section className="df-form-section" key={block.id}>
        <header><span className="df-grip" aria-hidden="true">⠿</span><div><h2>{block.title}</h2>{block.description ? <p>{block.description}</p> : null}</div></header>
        <div className="df-fields-grid">
          {fields.map(field => <article key={field.id} style={{ gridColumn: `span ${field.width}` }} className={`df-field-row ${selectedId === field.id ? 'selected' : ''}`} onClick={() => !preview && onSelect(field.id)}>
            <label>{field.label}{field.required ? <span aria-label="obrigatório"> *</span> : null}</label>
            {field.help_text ? <p>{field.help_text}</p> : null}
            <PreviewControl field={field}/>
            {!preview ? <div className="df-field-actions" aria-label={`Ações de ${field.label}`}>
              <button type="button" onClick={event => { event.stopPropagation(); onMove(field.id, -1); }} aria-label="Mover campo para cima"><Icon name="up" size={15}/></button>
              <button type="button" onClick={event => { event.stopPropagation(); onMove(field.id, 1); }} aria-label="Mover campo para baixo"><Icon name="down" size={15}/></button>
              <button type="button" onClick={event => { event.stopPropagation(); onRemove(field.id); }} aria-label="Remover campo"><Icon name="trash" size={15}/></button>
            </div> : null}
          </article>)}
        </div>
        {!fields.length ? <div className="df-drop-empty"><span><Icon name="plus"/></span><strong>Adicione um campo permitido</strong><p>Escolha um item no catálogo à esquerda.</p></div> : null}
      </section>;
    })}
    {!preview ? <button className="df-add-section" type="button" onClick={onAddSection}><Icon name="plus"/> Adicionar seção</button> : null}
  </main>
);

const FieldInspector = ({ field, validationCount, onChange, onClose }: { field: BuilderField | null; validationCount: number; onChange: (patch: Partial<BuilderField>) => void; onClose: () => void }) => (
  <aside className="df-inspector" aria-label="Propriedades do campo">
    <header><h2>Propriedades do campo</h2><button type="button" onClick={onClose} aria-label="Fechar inspetor"><Icon name="close"/></button></header>
    {field ? <div className="df-inspector-body">
      <div className="df-selected-summary"><span><Icon name="field" size={15}/>{componentLabel[field.component] ?? field.component}</span><strong>{field.label}</strong></div>
      <fieldset><legend>Propriedades</legend>
        <label>Rótulo<input value={field.label} maxLength={160} onChange={event => onChange({ label: event.target.value })}/></label>
        <label>Texto de ajuda<textarea value={field.help_text} maxLength={300} onChange={event => onChange({ help_text: event.target.value })}/><small>{field.help_text.length}/300</small></label>
        <label>Placeholder<input value={field.placeholder} maxLength={240} onChange={event => onChange({ placeholder: event.target.value })}/></label>
        <label className="df-toggle-row"><span><strong>Obrigatório</strong><small>O preenchimento é obrigatório</small></span><input type="checkbox" checked={field.required} onChange={event => onChange({ required: event.target.checked })}/></label>
        <label className="df-toggle-row"><span><strong>Somente leitura</strong><small>Impede edição pelo usuário</small></span><input type="checkbox" checked={field.read_only} onChange={event => onChange({ read_only: event.target.checked })}/></label>
        <label>Largura<select value={field.width} onChange={event => onChange({ width: Number(event.target.value) })}><option value={12}>100% (linha inteira)</option><option value={8}>66%</option><option value={6}>50%</option><option value={4}>33%</option></select></label>
      </fieldset>
      <details open><summary>Validações <span>{validationCount}</span></summary><p>Validações estruturais vêm do catálogo e sempre executam no backend.</p></details>
      <details><summary>Permissões</summary><p>O backend aplica tenant, papel, escopo e sensibilidade antes da submissão.</p></details>
    </div> : <div className="df-inspector-empty"><Icon name="settings" size={28}/><h3>Selecione um campo</h3><p>As propriedades autorizadas aparecerão aqui.</p></div>}
  </aside>
);

const DynamicFormBuilder: React.FC = () => {
  const [document, setDocument] = useState<BuilderDocument>(loadLocalDocument);
  const [catalog, setCatalog] = useState<CatalogField[]>(demoCatalog);
  const [bindings, setBindings] = useState<FieldBinding[]>(demoBindings);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [tab, setTab] = useState<'structure' | 'validations' | 'permissions'>('structure');
  const [preview, setPreview] = useState(false);
  const [feedback, setFeedback] = useState<BuilderFeedback>({ kind: 'idle', message: 'Alterações salvas localmente' });

  useEffect(() => {
    let active = true;
    Promise.all([loadCatalog()]).then(([result]) => {
      if (active && result.catalog.length) { setCatalog(result.catalog); setBindings(result.bindings); setFeedback({ kind: 'idle', message: 'Catálogo sincronizado com o backend' }); }
    }).catch(() => active && setFeedback({ kind: 'idle', message: 'Modo local seguro · conecte o backend para publicar' }));
    return () => { active = false; };
  }, []);

  useEffect(() => { saveLocalDocument(document); }, [document]);

  const selected = useMemo(() => document.fields.find(field => field.id === selectedId) ?? null, [document.fields, selectedId]);
  const selectedValidationCount = useMemo(() => document.validations.filter(item => item.field_id === selectedId).length, [document.validations, selectedId]);

  const addField = (catalogField: CatalogField, binding: FieldBinding) => {
    const block = document.blocks[0];
    if (!block || document.fields.some(item => item.field_catalog_id === catalogField.id)) { setFeedback({ kind: 'error', message: 'Este campo já está no formulário.' }); return; }
    const created = createField(catalogField, binding, block.id, document.fields.length);
    setDocument(current => ({ ...current, status: 'editing', fields: [...current.fields, created.field], validations: [...current.validations, ...created.validations] }));
    setSelectedId(created.field.id);
    setFeedback({ kind: 'success', message: `${created.field.label} adicionado ao formulário.` });
  };

  const updateSelected = (patch: Partial<BuilderField>) => setDocument(current => ({ ...current, fields: current.fields.map(field => field.id === selectedId ? { ...field, ...patch } : field) }));
  const removeField = (id: string) => setDocument(current => ({ ...current, fields: current.fields.filter(field => field.id !== id).map((field, index) => ({ ...field, display_order: index })), validations: current.validations.filter(item => item.field_id !== id) }));
  const moveField = (id: string, direction: -1 | 1) => setDocument(current => {
    const fields = [...current.fields].toSorted((a, b) => a.display_order - b.display_order);
    const index = fields.findIndex(field => field.id === id); const target = index + direction;
    if (index < 0 || target < 0 || target >= fields.length) return current;
    [fields[index], fields[target]] = [fields[target], fields[index]];
    return { ...current, fields: fields.map((field, order) => ({ ...field, display_order: order })) };
  });

  const addSection = () => setDocument(current => ({ ...current, blocks: [...current.blocks, { id: crypto.randomUUID(), block_type: 'section', parent_block_id: null, display_order: current.blocks.length, title: `Nova seção ${current.blocks.length + 1}`, description: '', width: 12, collapsible: false, visibility_rule_id: null, repeatable: false, allowed_style: 'default' }] }));

  const save = async () => {
    if (!document.fields.length) { setFeedback({ kind: 'error', message: 'Adicione ao menos um campo antes de salvar no backend.' }); return; }
    setFeedback({ kind: 'loading', message: 'Validando e salvando no backend…' });
    try { const ids = await saveDocument(document); setDocument(current => ({ ...current, definitionId: ids.definitionId, versionId: ids.versionId, status: 'editing' })); setFeedback({ kind: 'success', message: 'Rascunho validado e salvo no backend.' }); }
    catch (error) { setFeedback({ kind: 'error', message: error instanceof Error ? error.message : 'Falha ao salvar.' }); }
  };

  const homologate = async () => {
    if (!document.versionId) { setFeedback({ kind: 'error', message: 'Salve o rascunho antes de enviar para homologação.' }); return; }
    setFeedback({ kind: 'loading', message: 'Enviando para homologação…' });
    try { await requestHomologation(document.versionId); setDocument(current => ({ ...current, status: 'submitted' })); setFeedback({ kind: 'success', message: 'Versão enviada para homologação.' }); }
    catch (error) { setFeedback({ kind: 'error', message: error instanceof Error ? error.message : 'Falha ao homologar.' }); }
  };

  return <section className="dynamic-form-builder">
    <header className="df-command-bar"><div><h1>Construtor de formulários</h1></div><div className="df-command-actions">
      <button type="button" onClick={save} disabled={feedback.kind === 'loading'}><Icon name="save"/> Salvar rascunho</button>
      <button type="button" onClick={() => setPreview(value => !value)} className={preview ? 'active' : ''}><Icon name="eye"/> {preview ? 'Voltar ao editor' : 'Pré-visualizar'}</button>
      <button type="button" className="primary" onClick={homologate} disabled={feedback.kind === 'loading' || document.status === 'submitted'}><Icon name="send"/> Enviar para homologação</button>
    </div></header>
    <div className={`df-workspace ${preview ? 'preview' : ''}`}>
      {!preview ? <CatalogRail catalog={catalog} bindings={bindings} search={search} onSearch={setSearch} onAdd={addField}/> : null}
      <div className="df-editor"><header className="df-document-header"><div><span className="df-document-icon"><Icon name="field" size={22}/></span><div><input value={document.name} onChange={event => setDocument(current => ({ ...current, name: event.target.value }))} aria-label="Nome do formulário"/><p><span className={`df-status ${document.status}`}>{document.status === 'submitted' ? 'Em homologação' : document.status === 'editing' ? 'Editando' : 'Rascunho'}</span><span>v{document.versionNumber}</span></p></div></div><button type="button"><Icon name="settings"/> Configurações do formulário</button></header>
        {!preview ? <nav className="df-editor-tabs" aria-label="Áreas do editor"><button className={tab === 'structure' ? 'active' : ''} onClick={() => setTab('structure')}>Estrutura</button><button className={tab === 'validations' ? 'active' : ''} onClick={() => setTab('validations')}>Validações</button><button className={tab === 'permissions' ? 'active' : ''} onClick={() => setTab('permissions')}>Permissões</button></nav> : <div className="df-preview-heading"><strong>Pré-visualização</strong><span>Os cálculos e validações oficiais executam no backend.</span></div>}
        {tab === 'structure' || preview ? <FormCanvas document={document} selectedId={selectedId} preview={preview} onSelect={setSelectedId} onMove={moveField} onRemove={removeField} onAddSection={addSection}/> : tab === 'validations' ? <div className="df-policy-view"><h2>Validações do formulário</h2><p>{document.validations.length} regras estruturais vinculadas ao catálogo.</p>{document.validations.map(item => <article key={item.id}><strong>{item.validation_type}</strong><span>{document.fields.find(field => field.id === item.field_id)?.label}</span><em>Backend obrigatório</em></article>)}</div> : <div className="df-policy-view"><h2>Permissões e proteção</h2><p>Tenant, papel, escopo, MFA e sensibilidade são verificados pelo serviço.</p><article><strong>Designer</strong><span>Editar rascunho e solicitar homologação</span><em>forms:write</em></article><article><strong>Homologador</strong><span>Revisar com segregação de funções</span><em>forms:review + MFA</em></article><article><strong>Publicador</strong><span>Publicar somente versão aprovada</span><em>forms:publish + MFA</em></article></div>}
        <footer className={`df-save-status ${feedback.kind}`} aria-live="polite"><span aria-hidden="true">{feedback.kind === 'error' ? '!' : feedback.kind === 'loading' ? '…' : '✓'}</span>{feedback.message}</footer>
      </div>
      {!preview ? <FieldInspector field={selected} validationCount={selectedValidationCount} onChange={updateSelected} onClose={() => setSelectedId(null)}/> : null}
    </div>
  </section>;
};

export default DynamicFormBuilder;

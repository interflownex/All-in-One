import { useState } from 'react';
import { type JourneyHint, type ViewKey } from '../lib/api';
import { Modal } from '../ui';

type Navigate = (view: ViewKey, hint?: JourneyHint) => void;
type IntentOption = { label: string; description: string; view: ViewKey; hint?: JourneyHint };
type ConsumerIntent = { key: string; label: string; description: string; symbol: string; options: IntentOption[] };

const intents: ConsumerIntent[] = [
  {
    key: 'comprar', label: 'Comprar', description: 'Produtos, ofertas e itens perto de você.', symbol: '↓',
    options: [
      { label: 'Marketplace', description: 'Abrir o feed de produtos e novidades locais.', view: 'marketplace', hint: { intent: 'comprar', mode: 'feed' } },
      { label: 'Estoque', description: 'Abrir o feed de produtos de fornecedores.', view: 'stock', hint: { intent: 'comprar', mode: 'feed' } },
    ],
  },
  {
    key: 'vender', label: 'Vender', description: 'Anuncie um item com fotos, preço e condições.', symbol: '↑',
    options: [{ label: 'Vender um item', description: 'Abrir o cadastro de anúncio no Marketplace.', view: 'marketplace', hint: { intent: 'vender', mode: 'sell' } }],
  },
  {
    key: 'contratar', label: 'Contratar', description: 'Encontre a ajuda profissional necessária.', symbol: '+',
    options: [
      { label: 'Contratar para uma vaga', description: 'Publicar uma oportunidade e encontrar candidatos.', view: 'jobs', hint: { intent: 'contratar', mode: 'recruit' } },
      { label: 'Apoio jurídico', description: 'Buscar orientação, contratos e acompanhamento.', view: 'legal', hint: { intent: 'contratar', mode: 'hire' } },
      { label: 'Atendimento de saúde', description: 'Buscar especialidade, profissional ou consulta.', view: 'health', hint: { intent: 'contratar', mode: 'hire' } },
    ],
  },
  {
    key: 'alugar', label: 'Alugar', description: 'Imóveis, propriedades e unidades para locação.', symbol: '◇',
    options: [{ label: 'Buscar imóvel ou propriedade', description: 'Abrir o feed de locações.', view: 'property', hint: { intent: 'alugar', mode: 'rent' } }],
  },
  {
    key: 'consertar', label: 'Consertar', description: 'Publique um item que precisa de especialista.', symbol: '⌁',
    options: [{ label: 'Publicar pedido de conserto', description: 'Descrever item, defeito e região.', view: 'marketplace', hint: { intent: 'consertar', mode: 'repair-request' } }],
  },
  {
    key: 'pagar', label: 'Pagar', description: 'Cobranças, pedidos e pagamentos.', symbol: '−',
    options: [{ label: 'Abrir financeiro', description: 'Consultar e realizar pagamentos.', view: 'finance', hint: { intent: 'pagar', mode: 'pay' } }],
  },
  {
    key: 'receber', label: 'Receber', description: 'Carteira, repasses e valores a receber.', symbol: '=',
    options: [{ label: 'Abrir financeiro', description: 'Consultar recebimentos e gerar cobranças.', view: 'finance', hint: { intent: 'receber', mode: 'receive' } }],
  },
  {
    key: 'trabalhar', label: 'Trabalhar', description: 'Busque emprego ou ofereça seu trabalho.', symbol: '✦',
    options: [
      { label: 'Buscar emprego', description: 'Cadastrar currículo e abrir o feed de vagas.', view: 'jobs', hint: { intent: 'trabalhar', mode: 'seek' } },
      { label: 'Oferecer trabalho', description: 'Cadastrar-se como prestador especializado.', view: 'jobs', hint: { intent: 'trabalhar', mode: 'offer' } },
    ],
  },
];

const modules: Array<{ label: string; symbol: string; view: ViewKey; hint?: JourneyHint }> = [
  { label: 'Marketplace', symbol: '▦', view: 'marketplace', hint: { mode: 'feed' } },
  { label: 'Estoque', symbol: '▤', view: 'stock', hint: { mode: 'feed' } },
  { label: 'Financeiro', symbol: '◈', view: 'finance', hint: { mode: 'pay' } },
  { label: 'Trabalho', symbol: '✦', view: 'jobs', hint: { mode: 'seek' } },
  { label: 'Serviços', symbol: '⌁', view: 'services' },
  { label: 'Entregas', symbol: '➜', view: 'delivery' },
  { label: 'Mobilidade', symbol: '◇', view: 'mobility' },
  { label: 'Saúde', symbol: '✚', view: 'health' },
  { label: 'Jurídico', symbol: '§', view: 'legal' },
  { label: 'Imóveis', symbol: '⌂', view: 'property' },
  { label: 'Documentos', symbol: '▣', view: 'life' },
  { label: 'Conta', symbol: '●', view: 'account' },
  { label: 'Ajustes', symbol: '⚙', view: 'settings' },
];

export function ConsumerHome({ onNavigate }: { onNavigate: Navigate }) {
  const [selectedIntent, setSelectedIntent] = useState<ConsumerIntent | null>(null);
  const [showModules, setShowModules] = useState(false);

  const chooseIntent = (intent: ConsumerIntent) => {
    if (intent.options.length === 1) {
      const option = intent.options[0];
      onNavigate(option.view, option.hint);
      return;
    }
    setSelectedIntent(intent);
  };

  return <section className='intent-home'>
    <div className='intent-hero'><h1>O que você quer fazer?</h1><p>Escolha uma intenção simples. O Valley abre diretamente a jornada certa.</p></div>
    <div className='intent-grid'>{intents.map(intent => <button key={intent.key} type='button' className='intent-card' onClick={() => chooseIntent(intent)}><span className='intent-symbol' aria-hidden='true'>{intent.symbol}</span><span className='intent-copy'><strong>{intent.label}</strong><small>{intent.description}</small></span><span className='intent-arrow' aria-hidden='true'>›</span></button>)}</div>
    <button className='all-modules-button' type='button' onClick={() => setShowModules(true)}><span aria-hidden='true'>▦</span><strong>Ver todos os módulos</strong><small>Explore tudo que está disponível no Valley.</small></button>

    {selectedIntent && <Modal title={selectedIntent.label} onClose={() => setSelectedIntent(null)}><p className='intent-modal-copy'>{selectedIntent.description}</p><div className='intent-option-list'>{selectedIntent.options.map(option => <button key={option.label} type='button' className='intent-option' onClick={() => { setSelectedIntent(null); onNavigate(option.view, option.hint); }}><strong>{option.label}</strong><span>{option.description}</span><b aria-hidden='true'>›</b></button>)}</div></Modal>}

    {showModules && <Modal title='Todos os módulos' onClose={() => setShowModules(false)}><div className='module-icon-grid'>{modules.map(module => <button key={module.label} type='button' onClick={() => { setShowModules(false); onNavigate(module.view, module.hint); }}><span className='module-icon' aria-hidden='true'>{module.symbol}</span><small>{module.label}</small></button>)}</div></Modal>}
  </section>;
}

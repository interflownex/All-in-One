import { useState } from 'react';
import type { JourneyHint, ViewKey } from '../lib/api';
import { Modal } from '../ui';

type Navigate = (view: ViewKey, hint?: JourneyHint) => void;
type Option = { label: string; description: string; view: ViewKey; hint?: JourneyHint };
type Intent = { key: string; label: string; description: string; symbol: string; options: Option[] };

const intents: Intent[] = [
  { key:'comprar', label:'Comprar', description:'Encontre produtos no Marketplace ou no Estoque.', symbol:'↓', options:[
    { label:'Marketplace', description:'Abrir diretamente o feed de novidades, categorias e produtos.', view:'marketplace', hint:{ intent:'comprar', mode:'feed' } },
    { label:'Estoque', description:'Abrir o feed de produtos de fornecedores e empresas.', view:'stock', hint:{ intent:'comprar', mode:'feed' } },
  ]},
  { key:'vender', label:'Vender', description:'Crie um anúncio para vender um item.', symbol:'↑', options:[
    { label:'Vender um item', description:'Abrir o Marketplace no modo de criação de anúncio.', view:'marketplace', hint:{ intent:'vender', mode:'sell' } },
  ]},
  { key:'contratar', label:'Contratar', description:'Contrate uma pessoa, atendimento jurídico ou cuidado de saúde.', symbol:'+', options:[
    { label:'Contratar uma pessoa', description:'Cadastrar ou acompanhar uma oportunidade de trabalho.', view:'jobs', hint:{ intent:'contratar', mode:'recruit' } },
    { label:'Atendimento jurídico', description:'Buscar profissional ou serviço jurídico.', view:'legal', hint:{ intent:'contratar', mode:'hire' } },
    { label:'Saúde', description:'Buscar profissional, consulta ou atendimento de saúde.', view:'health', hint:{ intent:'contratar', mode:'hire' } },
  ]},
  { key:'alugar', label:'Alugar', description:'Busque propriedades e imóveis disponíveis.', symbol:'◇', options:[
    { label:'Imóveis e propriedades', description:'Abrir ofertas de locação por região e tipo.', view:'property', hint:{ intent:'alugar', mode:'feed' } },
  ]},
  { key:'consertar', label:'Consertar', description:'Anuncie um item que precisa de reparo especializado.', symbol:'⌁', options:[
    { label:'Solicitar conserto', description:'Criar no Marketplace um pedido de assistência ou orçamento.', view:'marketplace', hint:{ intent:'consertar', mode:'repair-request' } },
  ]},
  { key:'pagar', label:'Pagar', description:'Abra seus pagamentos e cobranças.', symbol:'−', options:[
    { label:'Pagar', description:'Ir para o menu financeiro e consultar valores a pagar.', view:'finance', hint:{ intent:'pagar', mode:'pay' } },
  ]},
  { key:'receber', label:'Receber', description:'Acompanhe carteira, repasses e recebimentos.', symbol:'=', options:[
    { label:'Receber', description:'Ir para o menu financeiro e consultar valores a receber.', view:'finance', hint:{ intent:'receber', mode:'receive' } },
  ]},
  { key:'trabalhar', label:'Trabalhar', description:'Busque emprego ou ofereça seu trabalho.', symbol:'✦', options:[
    { label:'Buscar emprego', description:'Abrir currículo, filtros e feed de vagas.', view:'jobs', hint:{ intent:'trabalhar', mode:'seek' } },
    { label:'Oferecer trabalho', description:'Cadastrar-se como profissional ou prestador especializado.', view:'jobs', hint:{ intent:'trabalhar', mode:'offer' } },
  ]},
];

export function IntentHome({ onNavigate }: { onNavigate: Navigate }) {
  const [selected, setSelected] = useState<Intent | null>(null);
  const choose = (intent: Intent) => {
    if (intent.options.length === 1) {
      const option = intent.options[0];
      onNavigate(option.view, option.hint);
      return;
    }
    setSelected(intent);
  };
  return <section className='intent-home'>
    <div className='intent-hero'><h1>O que você quer fazer?</h1><p>Escolha uma ação e o VALLEY leva você diretamente ao contexto necessário.</p></div>
    <div className='intent-grid'>{intents.map(intent => <button key={intent.key} className='intent-card' type='button' onClick={() => choose(intent)}><span className='intent-symbol'>{intent.symbol}</span><span className='intent-copy'><strong>{intent.label}</strong><small>{intent.description}</small></span><span className='intent-arrow'>›</span></button>)}</div>
    {selected && <Modal title={selected.label} onClose={() => setSelected(null)}><div className='intent-option-list'>{selected.options.map(option => <button key={option.label} className='intent-option' type='button' onClick={() => { setSelected(null); onNavigate(option.view, option.hint); }}><strong>{option.label}</strong><span>{option.description}</span><b>›</b></button>)}</div></Modal>}
  </section>;
}

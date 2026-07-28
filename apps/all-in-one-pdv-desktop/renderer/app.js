const api = window.pdv;
let state = null;
let currentView = 'checkout';
let cart = [];
let editingProductId = null;
let editingPromotionId = null;
let toastTimer;

const ui = {
  search: '',
  barcode: '',
  coupon: '',
  manualDiscountPercent: 0,
  manualDiscountAmount: 0,
  managerPin: '',
  paymentMethod: 'cash',
  mixedCash: 0,
  customerName: '',
  customerUserId: '',
  orderMode: 'counter',
  operatorName: 'Operador',
  openingCash: 0,
  countedCash: 0,
  cashType: 'supply',
  cashAmount: 0,
  cashReason: ''
};

const pageTitles = {
  checkout: 'Caixa',
  orders: 'Pedidos',
  catalog: 'Produtos',
  promotions: 'Promoções',
  cash: 'Turno e caixa',
  reports: 'Relatórios',
  settings: 'Configurações'
};

const money = (cents) => Number(cents || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
const dateTime = (value) => value ? new Date(value).toLocaleString('pt-BR') : 'Sem registro';
const esc = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);
const uid = () => globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
const byId = (id) => document.getElementById(id);
const formValue = (form, name) => form.elements.namedItem(name)?.value ?? '';
const checked = (form, name) => Boolean(form.elements.namedItem(name)?.checked);

function showToast(message, error = false) {
  const element = byId('toast');
  element.textContent = message;
  element.className = `toast visible${error ? ' error' : ''}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { element.className = 'toast'; }, 3800);
}

function updateChrome() {
  byId('page-title').textContent = pageTitles[currentView];
  const network = byId('network-status');
  network.textContent = navigator.onLine ? 'Internet disponível' : 'Sem internet';
  network.className = `status-chip ${navigator.onLine ? 'online' : 'offline'}`;
  const shift = byId('shift-status');
  shift.textContent = state?.openShift ? 'Caixa aberto' : 'Caixa fechado';
  shift.className = `status-chip ${state?.openShift ? 'open' : 'closed'}`;
  document.querySelectorAll('.nav-item').forEach((button) => button.classList.toggle('active', button.dataset.view === currentView));
}

function hero(title, text, badges = []) {
  return `<section class="hero"><div><p class="eyebrow">PDV DESKTOP OFFLINE</p><h2>${esc(title)}</h2><p>${esc(text)}</p></div><div class="hero-badges">${badges.map((badge) => `<span class="badge ${badge.good ? 'good' : badge.warn ? 'warn' : ''}">${esc(badge.label)}</span>`).join('')}</div></section>`;
}

function checkoutTotals() {
  const subtotalCents = cart.reduce((sum, item) => sum + item.priceCents * item.quantity, 0);
  const promotion = state.promotions.find((item) => item.active && item.code === ui.coupon.trim().toUpperCase());
  const couponDiscountCents = promotion
    ? promotion.discountType === 'fixed'
      ? Math.min(subtotalCents, Math.round(Number(promotion.discountValue || 0) * 100))
      : Math.round(subtotalCents * Number(promotion.discountValue || 0) / 100)
    : 0;
  const manualPercentCents = Math.round(subtotalCents * Math.max(0, Number(ui.manualDiscountPercent || 0)) / 100);
  const manualAmountCents = Math.round(Math.max(0, Number(ui.manualDiscountAmount || 0)) * 100);
  const discountCents = Math.min(subtotalCents, couponDiscountCents + manualPercentCents + manualAmountCents);
  return { subtotalCents, couponDiscountCents, discountCents, totalCents: Math.max(0, subtotalCents - discountCents) };
}

function renderCheckout() {
  const totals = checkoutTotals();
  const products = state.products.filter((product) => product.active && `${product.name} ${product.sku} ${product.barcode} ${product.category}`.toLowerCase().includes(ui.search.toLowerCase()));
  return `${hero('Venda sem depender da internet', 'Produtos, caixa, estoque, pedidos e comprovantes ficam armazenados neste computador. A sincronização acontece depois, quando houver conexão.', [
    { label: state.openShift ? 'Caixa aberto' : 'Abra o caixa para vender', good: Boolean(state.openShift), warn: !state.openShift },
    { label: `${state.syncQueue.filter((item) => item.status === 'pending').length} evento(s) aguardando envio` },
    { label: 'Base local protegida', good: true }
  ])}
  <div class="grid two">
    <section class="card">
      <div class="toolbar">
        <input id="product-search" class="control grow" value="${esc(ui.search)}" placeholder="Buscar produto, SKU ou categoria">
        <input id="barcode-input" class="control grow" value="${esc(ui.barcode)}" placeholder="Ler código de barras e pressionar Enter">
        <button class="btn" data-action="scan-barcode">Adicionar</button>
      </div>
      <div class="product-grid">
        ${products.length ? products.map((product) => `<button class="product" data-action="add-product" data-id="${product.id}">
          <div class="product-head"><span>${esc(product.name)}</span><span class="price">${money(product.priceCents)}</span></div>
          <div class="product-meta"><span>${esc(product.sku || 'Sem SKU')}</span><span>${product.trackStock ? `Estoque ${product.stock}` : 'Sem controle'}</span></div>
        </button>`).join('') : '<div class="empty">Nenhum produto encontrado.</div>'}
      </div>
    </section>
    <section class="card">
      <div class="card-title"><h2>Carrinho</h2><button class="btn danger" data-action="clear-cart">Limpar</button></div>
      <div class="cart-list">
        ${cart.length ? cart.map((item) => `<div class="cart-row">
          <div><strong>${esc(item.name)}</strong><span class="muted small">${money(item.priceCents)} cada</span></div>
          <div class="quantity"><button data-action="qty" data-id="${item.productId}" data-delta="-1">−</button><span>${item.quantity}</span><button data-action="qty" data-id="${item.productId}" data-delta="1">+</button></div>
          <strong>${money(item.priceCents * item.quantity)}</strong>
        </div>`).join('') : '<div class="empty">Leia um código ou selecione um produto.</div>'}
      </div>
      <div class="form-grid" style="margin-top:16px">
        <label class="field">Cupom<input id="coupon" value="${esc(ui.coupon)}" placeholder="LOJA10"></label>
        <label class="field">Desconto manual (%)<input id="manual-percent" type="number" min="0" max="100" value="${ui.manualDiscountPercent}"></label>
        <label class="field">Desconto manual (R$)<input id="manual-amount" type="number" min="0" step="0.01" value="${ui.manualDiscountAmount}"></label>
        <label class="field">PIN gerencial<input id="manager-pin" type="password" value="${esc(ui.managerPin)}" placeholder="Quando exigido"></label>
        <label class="field">Cliente<input id="customer-name" value="${esc(ui.customerName)}" placeholder="Nome opcional"></label>
        <label class="field">ID Valley do cliente<input id="customer-user-id" value="${esc(ui.customerUserId)}" placeholder="Para aviso de pedido pronto"></label>
        <label class="field">Tipo do pedido<select id="order-mode"><option value="counter" ${ui.orderMode === 'counter' ? 'selected' : ''}>Balcão</option><option value="pickup" ${ui.orderMode === 'pickup' ? 'selected' : ''}>Retirada</option><option value="delivery" ${ui.orderMode === 'delivery' ? 'selected' : ''}>Entrega</option></select></label>
        <label class="field">Pagamento<select id="payment-method"><option value="cash" ${ui.paymentMethod === 'cash' ? 'selected' : ''}>Dinheiro</option><option value="pix" ${ui.paymentMethod === 'pix' ? 'selected' : ''}>Pix</option><option value="card" ${ui.paymentMethod === 'card' ? 'selected' : ''}>Cartão</option><option value="wallet" ${ui.paymentMethod === 'wallet' ? 'selected' : ''}>Carteira Valley</option><option value="mixed" ${ui.paymentMethod === 'mixed' ? 'selected' : ''}>Misto: dinheiro + Pix</option></select></label>
        ${ui.paymentMethod === 'mixed' ? `<label class="field">Parte em dinheiro<input id="mixed-cash" type="number" min="0" step="0.01" value="${ui.mixedCash}"></label>` : ''}
      </div>
      <div class="totals">
        <div class="total-row"><span>Subtotal</span><span>${money(totals.subtotalCents)}</span></div>
        <div class="total-row"><span>Descontos</span><span>− ${money(totals.discountCents)}</span></div>
        <div class="total-row final"><span>Total</span><span>${money(totals.totalCents)}</span></div>
      </div>
      <button class="btn primary block" data-action="finish-sale" ${!cart.length ? 'disabled' : ''}>Finalizar venda</button>
    </section>
  </div>`;
}

function renderOrders() {
  const columns = [
    ['paid', 'Recebidos', 'preparing', 'Iniciar preparo'],
    ['preparing', 'Em preparo', 'ready', 'Marcar pronto'],
    ['ready', 'Prontos', 'delivered', 'Entregar']
  ];
  return `${hero('Fila digital de pedidos', 'A fila funciona na rede local do aplicativo mesmo sem internet. Quando o pedido fica pronto, o evento entra na fila de sincronização para avisar o cliente assim que houver conexão.', [{ label: `${state.orders.filter((item) => item.status === 'ready').length} pronto(s)`, good: true }])}
  <div class="order-board">${columns.map(([status, label, next, actionLabel]) => `<section class="order-column"><h2>${label}</h2>${state.orders.filter((order) => order.status === status).map((order) => `<article class="order-card"><div class="order-number">#${order.queueNumber}</div><p>${esc(order.customerName || 'Cliente não identificado')}</p><p class="muted small">${order.items.map((item) => `${item.quantity}x ${esc(item.name)}`).join(', ')}</p><strong>${money(order.totalCents)}</strong><div class="order-actions"><button class="btn primary" data-action="order-status" data-id="${order.id}" data-status="${next}">${actionLabel}</button></div></article>`).join('') || '<div class="empty">Fila vazia.</div>'}</section>`).join('')}</div>`;
}

function renderCatalog() {
  const product = editingProductId ? state.products.find((item) => item.id === editingProductId) : null;
  return `${hero('Catálogo e estoque local', 'Cadastre produtos, preços, códigos de barras e saldo. Toda venda baixa o estoque imediatamente, mesmo sem conexão.', [{ label: `${state.products.length} produto(s)` }, { label: `${state.products.filter((item) => item.trackStock && item.stock <= Number(state.settings.lowStockThreshold || 5)).length} em estoque baixo`, warn: true }])}
  <div class="grid two">
    <form id="product-form" class="card">
      <div class="card-title"><h2>${product ? 'Editar produto' : 'Novo produto'}</h2>${product ? '<button type="button" class="btn" data-action="cancel-product-edit">Cancelar</button>' : ''}</div>
      <input type="hidden" name="id" value="${product?.id || ''}">
      <div class="form-grid">
        <label class="field">Nome<input name="name" required value="${esc(product?.name || '')}"></label>
        <label class="field">Categoria<input name="category" value="${esc(product?.category || 'Geral')}"></label>
        <label class="field">SKU<input name="sku" value="${esc(product?.sku || '')}"></label>
        <label class="field">Código de barras<input name="barcode" value="${esc(product?.barcode || '')}"></label>
        <label class="field">Preço<input name="price" type="number" min="0" step="0.01" value="${product ? product.priceCents / 100 : 0}"></label>
        <label class="field">Custo<input name="cost" type="number" min="0" step="0.01" value="${product ? product.costCents / 100 : 0}"></label>
        <label class="field">Estoque<input name="stock" type="number" min="0" step="1" value="${product?.stock || 0}"></label>
        <label class="field">Unidade<input name="unit" value="${esc(product?.unit || 'un')}"></label>
      </div>
      <label class="checkbox" style="margin-top:14px"><input name="trackStock" type="checkbox" ${product?.trackStock !== false ? 'checked' : ''}>Controlar estoque</label>
      <label class="checkbox"><input name="active" type="checkbox" ${product?.active !== false ? 'checked' : ''}>Produto ativo</label>
      <button class="btn primary block" type="submit">Salvar produto</button>
    </form>
    <section class="card"><div class="card-title"><h2>Produtos cadastrados</h2></div><div class="list">${state.products.map((item) => `<article class="list-row"><div><strong>${esc(item.name)}</strong><div class="muted small">${esc(item.sku)} · ${esc(item.barcode)} · ${esc(item.category)}</div></div><span class="badge ${item.trackStock && item.stock <= Number(state.settings.lowStockThreshold || 5) ? 'warn' : 'good'}">${item.trackStock ? `Estoque ${item.stock}` : 'Sem controle'}</span><strong>${money(item.priceCents)}</strong><div><button class="btn" data-action="edit-product" data-id="${item.id}">Editar</button> <button class="btn danger" data-action="delete-product" data-id="${item.id}">Excluir</button></div></article>`).join('')}</div></section>
  </div>`;
}

function renderPromotions() {
  const promotion = editingPromotionId ? state.promotions.find((item) => item.id === editingPromotionId) : null;
  return `${hero('Promoções presenciais e geolocalizadas', 'Crie cupons e regras “somente na loja”. A disponibilidade ao consumidor será sincronizada quando houver internet.', [{ label: `${state.promotions.filter((item) => item.active).length} ativa(s)`, good: true }])}
  <div class="grid two">
    <form id="promotion-form" class="card">
      <div class="card-title"><h2>${promotion ? 'Editar promoção' : 'Nova promoção'}</h2>${promotion ? '<button type="button" class="btn" data-action="cancel-promotion-edit">Cancelar</button>' : ''}</div>
      <input type="hidden" name="id" value="${promotion?.id || ''}">
      <div class="form-grid">
        <label class="field">Nome<input name="name" required value="${esc(promotion?.name || '')}"></label>
        <label class="field">Código<input name="code" required value="${esc(promotion?.code || '')}"></label>
        <label class="field">Tipo<select name="discountType"><option value="percent" ${promotion?.discountType !== 'fixed' ? 'selected' : ''}>Percentual</option><option value="fixed" ${promotion?.discountType === 'fixed' ? 'selected' : ''}>Valor fixo</option></select></label>
        <label class="field">Desconto<input name="discountValue" type="number" min="0" step="0.01" value="${promotion?.discountValue || 10}"></label>
        <label class="field">Raio da loja em metros<input name="radiusM" type="number" min="0" value="${promotion?.radiusM || 300}"></label>
        <label class="field">Descrição<input name="description" value="${esc(promotion?.description || '')}"></label>
      </div>
      <label class="checkbox" style="margin-top:14px"><input name="inStoreOnly" type="checkbox" ${promotion?.inStoreOnly !== false ? 'checked' : ''}>Somente para clientes próximos da loja</label>
      <label class="checkbox"><input name="active" type="checkbox" ${promotion?.active !== false ? 'checked' : ''}>Promoção ativa</label>
      <button class="btn primary block" type="submit">Salvar promoção</button>
    </form>
    <section class="card"><div class="list">${state.promotions.map((item) => `<article class="list-row"><div><strong>${esc(item.name)}</strong><div class="muted small">${esc(item.description)} · ${item.inStoreOnly ? `raio ${item.radiusM}m` : 'todos os canais'}</div></div><span class="badge ${item.active ? 'good' : ''}">${esc(item.code)}</span><strong>${item.discountValue}${item.discountType === 'percent' ? '%' : ' reais'}</strong><div><button class="btn" data-action="edit-promotion" data-id="${item.id}">Editar</button> <button class="btn danger" data-action="delete-promotion" data-id="${item.id}">Excluir</button></div></article>`).join('')}</div></section>
  </div>`;
}

function renderCash() {
  return `${hero('Controle completo do turno', 'Abertura, suprimento, sangria, vendas em dinheiro, estornos, conferência e diferença ficam registrados localmente.', [{ label: state.openShift ? `Aberto por ${state.openShift.operatorName}` : 'Nenhum turno aberto', good: Boolean(state.openShift), warn: !state.openShift }])}
  <div class="grid three">
    <form id="open-shift-form" class="card"><h2>Abertura</h2><label class="field">Operador<input name="operatorName" value="${esc(ui.operatorName)}"></label><label class="field">Fundo de caixa<input name="openingCash" type="number" min="0" step="0.01" value="${ui.openingCash}"></label><button class="btn primary block" ${state.openShift ? 'disabled' : ''}>Abrir caixa</button>${state.openShift ? `<p class="muted small">Aberto em ${dateTime(state.openShift.openedAt)}</p>` : ''}</form>
    <form id="cash-movement-form" class="card"><h2>Movimentação</h2><label class="field">Tipo<select name="type"><option value="supply">Suprimento</option><option value="withdrawal">Sangria</option></select></label><label class="field">Valor<input name="amount" type="number" min="0" step="0.01"></label><label class="field">Motivo<input name="reason"></label><label class="field">PIN gerencial<input name="managerPin" type="password" placeholder="Obrigatório na sangria"></label><button class="btn warning block" ${!state.openShift ? 'disabled' : ''}>Registrar</button></form>
    <form id="close-shift-form" class="card"><h2>Fechamento</h2><label class="field">Dinheiro contado<input name="countedCash" type="number" min="0" step="0.01"></label><label class="field">PIN gerencial<input name="managerPin" type="password" required></label><button class="btn danger block" ${!state.openShift ? 'disabled' : ''}>Fechar e conferir</button><p class="muted small">O aplicativo calcula o valor esperado e a diferença.</p></form>
  </div>
  <section class="card" style="margin-top:18px"><div class="card-title"><h2>Movimentos recentes</h2></div><div class="table-wrap"><table><thead><tr><th>Data</th><th>Tipo</th><th>Motivo</th><th>Valor</th></tr></thead><tbody>${state.cashMovements.slice(0,50).map((item) => `<tr><td>${dateTime(item.createdAt)}</td><td>${esc(item.type)}</td><td>${esc(item.reason)}</td><td>${money(item.amountCents)}</td></tr>`).join('')}</tbody></table></div></section>`;
}

function renderReports() {
  const reports = state.reports;
  return `${hero('Resultados e auditoria', 'Os relatórios usam a base local e continuam disponíveis mesmo quando a nuvem estiver inacessível.', [{ label: `${reports.salesCount} venda(s)` }, { label: money(reports.revenueCents), good: true }])}
  <div class="grid four">
    <article class="card metric"><span class="muted">Vendas válidas</span><strong>${reports.salesCount}</strong></article>
    <article class="card metric"><span class="muted">Faturamento</span><strong>${money(reports.revenueCents)}</strong></article>
    <article class="card metric"><span class="muted">Ticket médio</span><strong>${money(reports.averageTicketCents)}</strong></article>
    <article class="card metric"><span class="muted">Fila de sincronização</span><strong>${state.syncQueue.filter((item) => item.status === 'pending').length}</strong></article>
  </div>
  <section class="card" style="margin-top:18px"><div class="card-title"><h2>Vendas recentes</h2><button class="btn" data-action="export-sales">Exportar CSV</button></div><div class="table-wrap"><table><thead><tr><th>Comprovante</th><th>Data</th><th>Operador</th><th>Cliente</th><th>Total</th><th>Status</th><th>Ações</th></tr></thead><tbody>${state.sales.slice(0,100).map((sale) => `<tr><td>${esc(sale.receiptNumber)}</td><td>${dateTime(sale.createdAt)}</td><td>${esc(sale.operatorName)}</td><td>${esc(sale.customerName || '')}</td><td>${money(sale.totalCents)}</td><td>${esc(sale.status)}</td><td><button class="btn" data-action="print-sale" data-id="${sale.id}">Imprimir</button>${sale.status !== 'refunded' ? ` <button class="btn danger" data-action="refund-sale" data-id="${sale.id}">Estornar</button>` : ''}</td></tr>`).join('')}</tbody></table></div></section>
  <div class="grid two" style="margin-top:18px"><section class="card"><h2>Formas de pagamento</h2><div class="list">${Object.entries(reports.paymentTotals || {}).map(([method, cents]) => `<div class="list-row"><strong>${esc(method)}</strong><span></span><strong>${money(cents)}</strong><span></span></div>`).join('') || '<div class="empty">Sem vendas.</div>'}</div></section><section class="card"><h2>Produtos mais vendidos</h2><div class="list">${(reports.topProducts || []).map((item) => `<div class="list-row"><strong>${esc(item.name)}</strong><span>${item.quantity} un</span><strong>${money(item.revenueCents)}</strong><span></span></div>`).join('') || '<div class="empty">Sem vendas.</div>'}</div></section></div>`;
}

async function renderSettings() {
  const info = await api.getAppInfo();
  const secret = await api.getSyncSecretStatus();
  byId('view').innerHTML = `${hero('Configuração local e sincronização', 'Nenhuma chave de API fica no código. O token é criptografado pelo Windows e a operação local não depende dele.', [{ label: `Versão ${info.version}` }, { label: info.arch }, { label: secret.apiTokenConfigured ? 'Token configurado' : 'Token pendente', good: secret.apiTokenConfigured, warn: !secret.apiTokenConfigured }])}
  <div class="grid two">
    <form id="settings-form" class="card"><h2>Loja e equipamentos</h2><div class="form-grid">
      <label class="field">Nome da loja<input name="storeName" value="${esc(state.settings.storeName)}"></label>
      <label class="field">Unidade<input name="branchName" value="${esc(state.settings.branchName)}"></label>
      <label class="field">CNPJ<input name="cnpj" value="${esc(state.settings.cnpj)}"></label>
      <label class="field">Terminal<input name="terminalId" value="${esc(state.settings.terminalId)}"></label>
      <label class="field">Endereço<input name="address" value="${esc(state.settings.address)}"></label>
      <label class="field">Estoque baixo a partir de<input name="lowStockThreshold" type="number" value="${state.settings.lowStockThreshold}"></label>
      <label class="field">Limite de desconto sem gerente (%)<input name="managerDiscountLimit" type="number" value="${state.settings.managerDiscountLimit}"></label>
      <label class="field">Novo PIN gerencial<input name="managerPin" type="password" placeholder="Deixe vazio para manter"></label>
      <label class="field">Impressora<select name="printerMode"><option value="navegador" ${state.settings.printerMode === 'navegador' ? 'selected' : ''}>Impressão do Windows</option><option value="bridge" ${state.settings.printerMode === 'bridge' ? 'selected' : ''}>Bridge ESC/POS</option></select></label>
      <label class="field">Leitor<select name="barcodeMode"><option value="teclado">Modo teclado</option><option value="serial">Serial/USB bridge</option></select></label>
      <label class="field">Gaveta<select name="cashDrawerMode"><option value="manual">Manual</option><option value="printer">Via impressora</option><option value="bridge">Bridge local</option></select></label>
      <label class="field">Balança<select name="scaleMode"><option value="manual">Digitação manual</option><option value="bridge">Bridge serial/USB</option></select></label>
    </div><button class="btn primary block">Salvar configurações</button></form>
    <div class="grid">
      <form id="sync-form" class="card"><h2>Sincronização opcional</h2><div class="notice">O PDV continua funcionando mesmo que estes campos estejam vazios.</div><label class="checkbox" style="margin-top:14px"><input name="syncEnabled" type="checkbox" ${state.settings.syncEnabled ? 'checked' : ''}>Enviar eventos ao servidor quando houver internet</label><label class="field">Endpoint completo<input name="syncEndpoint" value="${esc(state.settings.syncEndpoint)}" placeholder="https://api.exemplo.com/pdv/sync"></label><label class="field">Intervalo em minutos<input name="autoSyncMinutes" type="number" min="1" value="${state.settings.autoSyncMinutes}"></label><label class="field">Token da API<input name="apiToken" type="password" placeholder="Não é exibido após salvar"></label><div class="toolbar"><button class="btn primary grow">Salvar sincronização</button><button type="button" class="btn" data-action="sync-now">Sincronizar agora</button></div></form>
      <section class="card"><h2>Segurança e cópias</h2><p class="muted small">Base local: <span class="code">${esc(state.dataFile)}</span></p><p class="muted small">Pasta do aplicativo: <span class="code">${esc(info.userDataPath)}</span></p><div class="toolbar"><button class="btn" data-action="backup">Salvar backup</button><button class="btn warning" data-action="restore">Restaurar backup</button></div></section>
    </div>
  </div>`;
}

async function render() {
  if (!state) return;
  updateChrome();
  const view = byId('view');
  if (currentView === 'checkout') view.innerHTML = renderCheckout();
  if (currentView === 'orders') view.innerHTML = renderOrders();
  if (currentView === 'catalog') view.innerHTML = renderCatalog();
  if (currentView === 'promotions') view.innerHTML = renderPromotions();
  if (currentView === 'cash') view.innerHTML = renderCash();
  if (currentView === 'reports') view.innerHTML = renderReports();
  if (currentView === 'settings') await renderSettings();
}

function addProduct(productId) {
  const product = state.products.find((item) => item.id === productId);
  if (!product) return;
  const existing = cart.find((item) => item.productId === productId);
  if (existing) existing.quantity += 1;
  else cart.push({ productId, name: product.name, priceCents: product.priceCents, quantity: 1 });
  render();
}

function captureCheckoutInputs() {
  ui.search = byId('product-search')?.value || ui.search;
  ui.barcode = byId('barcode-input')?.value || '';
  ui.coupon = byId('coupon')?.value || '';
  ui.manualDiscountPercent = Number(byId('manual-percent')?.value || 0);
  ui.manualDiscountAmount = Number(byId('manual-amount')?.value || 0);
  ui.managerPin = byId('manager-pin')?.value || '';
  ui.customerName = byId('customer-name')?.value || '';
  ui.customerUserId = byId('customer-user-id')?.value || '';
  ui.orderMode = byId('order-mode')?.value || 'counter';
  ui.paymentMethod = byId('payment-method')?.value || 'cash';
  ui.mixedCash = Number(byId('mixed-cash')?.value || 0);
}

async function finishSale() {
  captureCheckoutInputs();
  if (!state.openShift) {
    showToast('Abra o caixa antes de vender.', true);
    currentView = 'cash';
    return render();
  }
  const totals = checkoutTotals();
  let payments;
  if (ui.paymentMethod === 'mixed') {
    const cash = Math.max(0, Math.min(totals.totalCents, Math.round(ui.mixedCash * 100)));
    payments = [{ method: 'cash', amount: cash / 100 }, { method: 'pix', amount: (totals.totalCents - cash) / 100 }];
  } else payments = [{ method: ui.paymentMethod, amount: totals.totalCents / 100 }];
  try {
    const result = await api.createSale({
      idempotencyKey: uid(),
      offlineId: uid(),
      terminalId: state.settings.terminalId,
      operatorName: state.openShift.operatorName,
      items: cart.map((item) => ({ productId: item.productId, quantity: item.quantity })),
      couponCode: ui.coupon || undefined,
      manualDiscountPercent: ui.manualDiscountPercent,
      manualDiscountAmount: ui.manualDiscountAmount,
      managerPin: ui.managerPin || undefined,
      payments,
      customerName: ui.customerName || undefined,
      customerUserId: ui.customerUserId || undefined,
      orderMode: ui.orderMode
    });
    cart = [];
    Object.assign(ui, { coupon: '', manualDiscountPercent: 0, manualDiscountAmount: 0, managerPin: '', customerName: '', customerUserId: '', mixedCash: 0 });
    showToast(`Venda concluída. Pedido #${result.order.queueNumber}.`);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function handleAction(button) {
  const action = button.dataset.action;
  const id = button.dataset.id;
  if (action === 'add-product') addProduct(id);
  if (action === 'qty') {
    const item = cart.find((candidate) => candidate.productId === id);
    if (item) item.quantity += Number(button.dataset.delta);
    cart = cart.filter((candidate) => candidate.quantity > 0);
    render();
  }
  if (action === 'clear-cart') { cart = []; render(); }
  if (action === 'scan-barcode') {
    captureCheckoutInputs();
    const product = state.products.find((item) => item.barcode === ui.barcode.trim() || item.sku.toLowerCase() === ui.barcode.trim().toLowerCase());
    if (!product) return showToast('Código não encontrado.', true);
    ui.barcode = '';
    addProduct(product.id);
  }
  if (action === 'finish-sale') await finishSale();
  if (action === 'order-status') {
    try { await api.updateOrderStatus({ orderId: id, status: button.dataset.status }); showToast('Pedido atualizado.'); } catch (error) { showToast(error.message, true); }
  }
  if (action === 'edit-product') { editingProductId = id; render(); }
  if (action === 'cancel-product-edit') { editingProductId = null; render(); }
  if (action === 'delete-product' && confirm('Excluir este produto?')) {
    try { await api.deleteProduct(id); showToast('Produto excluído.'); } catch (error) { showToast(error.message, true); }
  }
  if (action === 'edit-promotion') { editingPromotionId = id; render(); }
  if (action === 'cancel-promotion-edit') { editingPromotionId = null; render(); }
  if (action === 'delete-promotion' && confirm('Excluir esta promoção?')) {
    try { await api.deletePromotion(id); showToast('Promoção excluída.'); } catch (error) { showToast(error.message, true); }
  }
  if (action === 'export-sales') {
    const result = await api.exportSalesCsv();
    if (!result.canceled) showToast(`Arquivo salvo em ${result.filePath}`);
  }
  if (action === 'print-sale') {
    const result = await api.printReceipt(id);
    showToast(result.success ? 'Comprovante enviado para impressão.' : `Impressão não concluída: ${result.failureReason}`, !result.success);
  }
  if (action === 'refund-sale') {
    const pin = prompt('Informe o PIN gerencial para o estorno:');
    if (!pin) return;
    const reason = prompt('Motivo do estorno:') || 'Estorno gerencial';
    try { await api.refundSale({ saleId: id, managerPin: pin, reason }); showToast('Venda estornada e estoque recomposto.'); } catch (error) { showToast(error.message, true); }
  }
  if (action === 'sync-now') {
    const result = await api.syncNow();
    showToast(result.ok ? `${result.synced || 0} evento(s) sincronizado(s).` : (result.error || result.reason), !result.ok && !result.skipped);
  }
  if (action === 'backup') {
    const result = await api.backup();
    if (!result.canceled) showToast(`Backup salvo em ${result.filePath}`);
  }
  if (action === 'restore' && confirm('A restauração substituirá os dados atuais. Continuar?')) {
    try { const result = await api.restore(); if (!result.canceled) showToast('Backup restaurado.'); } catch (error) { showToast(error.message, true); }
  }
}

document.addEventListener('click', async (event) => {
  const nav = event.target.closest('[data-view]');
  if (nav) {
    if (currentView === 'checkout') captureCheckoutInputs();
    currentView = nav.dataset.view;
    return render();
  }
  const action = event.target.closest('[data-action]');
  if (action) await handleAction(action);
});

document.addEventListener('input', (event) => {
  if (event.target.id === 'product-search') {
    ui.search = event.target.value;
    render();
    requestAnimationFrame(() => { const input = byId('product-search'); input?.focus(); input?.setSelectionRange(ui.search.length, ui.search.length); });
  }
});

document.addEventListener('keydown', async (event) => {
  if (event.target.id === 'barcode-input' && event.key === 'Enter') {
    event.preventDefault();
    const button = document.querySelector('[data-action="scan-barcode"]');
    if (button) await handleAction(button);
  }
});

document.addEventListener('change', (event) => {
  if (currentView === 'checkout' && ['coupon', 'manual-percent', 'manual-amount', 'manager-pin', 'customer-name', 'customer-user-id', 'order-mode', 'payment-method', 'mixed-cash'].includes(event.target.id)) {
    captureCheckoutInputs();
    render();
  }
});

document.addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.target;
  try {
    if (form.id === 'product-form') {
      await api.saveProduct({
        id: formValue(form, 'id') || undefined,
        name: formValue(form, 'name'),
        category: formValue(form, 'category'),
        sku: formValue(form, 'sku'),
        barcode: formValue(form, 'barcode'),
        price: Number(formValue(form, 'price')),
        cost: Number(formValue(form, 'cost')),
        stock: Number(formValue(form, 'stock')),
        unit: formValue(form, 'unit'),
        trackStock: checked(form, 'trackStock'),
        active: checked(form, 'active')
      });
      editingProductId = null;
      showToast('Produto salvo.');
    }
    if (form.id === 'promotion-form') {
      await api.savePromotion({
        id: formValue(form, 'id') || undefined,
        name: formValue(form, 'name'),
        code: formValue(form, 'code'),
        description: formValue(form, 'description'),
        discountType: formValue(form, 'discountType'),
        discountValue: Number(formValue(form, 'discountValue')),
        radiusM: Number(formValue(form, 'radiusM')),
        inStoreOnly: checked(form, 'inStoreOnly'),
        active: checked(form, 'active')
      });
      editingPromotionId = null;
      showToast('Promoção salva.');
    }
    if (form.id === 'open-shift-form') {
      ui.operatorName = formValue(form, 'operatorName');
      ui.openingCash = Number(formValue(form, 'openingCash'));
      await api.openShift({ operatorName: ui.operatorName, openingCash: ui.openingCash, terminalId: state.settings.terminalId });
      showToast('Caixa aberto.');
    }
    if (form.id === 'cash-movement-form') {
      await api.addCashMovement({ type: formValue(form, 'type'), amount: Number(formValue(form, 'amount')), reason: formValue(form, 'reason'), managerPin: formValue(form, 'managerPin') });
      showToast('Movimento registrado.');
    }
    if (form.id === 'close-shift-form') {
      const result = await api.closeShift({ countedCash: Number(formValue(form, 'countedCash')), managerPin: formValue(form, 'managerPin') });
      showToast(`Caixa fechado. Diferença: ${money(result.differenceCents)}.`);
    }
    if (form.id === 'settings-form') {
      await api.updateSettings({
        storeName: formValue(form, 'storeName'),
        branchName: formValue(form, 'branchName'),
        cnpj: formValue(form, 'cnpj'),
        terminalId: formValue(form, 'terminalId'),
        address: formValue(form, 'address'),
        lowStockThreshold: Number(formValue(form, 'lowStockThreshold')),
        managerDiscountLimit: Number(formValue(form, 'managerDiscountLimit')),
        managerPin: formValue(form, 'managerPin') || undefined,
        printerMode: formValue(form, 'printerMode'),
        barcodeMode: formValue(form, 'barcodeMode'),
        cashDrawerMode: formValue(form, 'cashDrawerMode'),
        scaleMode: formValue(form, 'scaleMode')
      });
      showToast('Configurações salvas.');
    }
    if (form.id === 'sync-form') {
      await api.updateSettings({ syncEnabled: checked(form, 'syncEnabled'), syncEndpoint: formValue(form, 'syncEndpoint'), autoSyncMinutes: Number(formValue(form, 'autoSyncMinutes')) });
      if (formValue(form, 'apiToken')) await api.saveSyncSecret({ apiToken: formValue(form, 'apiToken') });
      showToast('Sincronização configurada.');
    }
  } catch (error) {
    showToast(error.message, true);
  }
});

window.addEventListener('online', () => { updateChrome(); void api.syncNow(); });
window.addEventListener('offline', updateChrome);
setInterval(() => { byId('clock').textContent = new Date().toLocaleString('pt-BR'); }, 1000);

(async function init() {
  try {
    state = await api.getState();
    api.onStateChanged((next) => { state = next; render(); });
    await render();
    byId('clock').textContent = new Date().toLocaleString('pt-BR');
  } catch (error) {
    byId('view').innerHTML = `<div class="empty">Não foi possível abrir a base local: ${esc(error.message)}</div>`;
  }
})();

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const now = () => new Date().toISOString();
const id = (prefix) => `${prefix}_${crypto.randomUUID()}`;
const toCents = (value) => Math.round((Number(value) || 0) * 100);
const fromCents = (value) => Math.round(Number(value || 0)) / 100;
const clone = (value) => JSON.parse(JSON.stringify(value));
const pinHash = (pin) => crypto.createHash('sha256').update(`all-in-one-pdv:${pin}`).digest('hex');

function initialData() {
  return {
    schemaVersion: 1,
    updatedAt: now(),
    settings: {
      storeName: 'Loja All in One',
      branchName: 'Unidade principal',
      cnpj: '',
      address: '',
      terminalId: 'PDV-01',
      currency: 'BRL',
      lowStockThreshold: 5,
      managerDiscountLimit: 10,
      managerPinHash: '',
      syncEnabled: false,
      syncEndpoint: '',
      autoSyncMinutes: 2,
      printerMode: 'navegador',
      barcodeMode: 'teclado',
      cashDrawerMode: 'manual',
      scaleMode: 'manual',
      customerDisplayMode: 'segunda tela'
    },
    products: [
      { id: id('product'), sku: 'CAF-001', barcode: '7891000000011', name: 'Café especial', category: 'Bebidas', priceCents: 850, costCents: 310, stock: 80, unit: 'un', active: true, trackStock: true },
      { id: id('product'), sku: 'PDC-001', barcode: '7891000000028', name: 'Pão de queijo', category: 'Alimentos', priceCents: 600, costCents: 220, stock: 120, unit: 'un', active: true, trackStock: true },
      { id: id('product'), sku: 'SUC-001', barcode: '7891000000035', name: 'Suco natural', category: 'Bebidas', priceCents: 1000, costCents: 420, stock: 45, unit: 'un', active: true, trackStock: true },
      { id: id('product'), sku: 'SAN-001', barcode: '7891000000042', name: 'Sanduíche artesanal', category: 'Alimentos', priceCents: 2200, costCents: 950, stock: 35, unit: 'un', active: true, trackStock: true },
      { id: id('product'), sku: 'AGU-001', barcode: '7891000000059', name: 'Água mineral', category: 'Bebidas', priceCents: 400, costCents: 140, stock: 100, unit: 'un', active: true, trackStock: true },
      { id: id('product'), sku: 'BOL-001', barcode: '7891000000066', name: 'Bolo do dia', category: 'Alimentos', priceCents: 900, costCents: 360, stock: 28, unit: 'fatia', active: true, trackStock: true }
    ],
    promotions: [
      { id: id('promotion'), code: 'LOJA10', name: 'Desconto na loja', description: '10% para compras presenciais', discountType: 'percent', discountValue: 10, active: true, inStoreOnly: true, radiusM: 300, startsAt: now(), endsAt: null }
    ],
    combos: [],
    shifts: [],
    cashMovements: [],
    sales: [],
    orders: [],
    audit: [],
    syncQueue: [],
    idempotency: {}
  };
}

class PdvStore {
  constructor(baseDir) {
    this.baseDir = baseDir;
    this.dataFile = path.join(baseDir, 'pdv-data.json');
    this.backupFile = path.join(baseDir, 'pdv-data.backup.json');
    fs.mkdirSync(baseDir, { recursive: true });
    this.data = this.#load();
    this.#normalize();
    this.#save();
  }

  #load() {
    if (!fs.existsSync(this.dataFile)) return initialData();
    try {
      return JSON.parse(fs.readFileSync(this.dataFile, 'utf8'));
    } catch (error) {
      if (fs.existsSync(this.backupFile)) {
        try {
          return JSON.parse(fs.readFileSync(this.backupFile, 'utf8'));
        } catch {}
      }
      throw new Error(`Base local corrompida: ${error.message}`);
    }
  }

  #normalize() {
    const defaults = initialData();
    this.data = { ...defaults, ...this.data };
    this.data.settings = { ...defaults.settings, ...(this.data.settings || {}) };
    for (const key of ['products', 'promotions', 'combos', 'shifts', 'cashMovements', 'sales', 'orders', 'audit', 'syncQueue']) {
      if (!Array.isArray(this.data[key])) this.data[key] = [];
    }
    if (!this.data.idempotency || typeof this.data.idempotency !== 'object') this.data.idempotency = {};
  }

  #save() {
    this.data.updatedAt = now();
    const json = JSON.stringify(this.data, null, 2);
    const temp = `${this.dataFile}.tmp`;
    fs.writeFileSync(temp, json, 'utf8');
    const fd = fs.openSync(temp, 'r');
    fs.fsyncSync(fd);
    fs.closeSync(fd);
    if (fs.existsSync(this.dataFile)) fs.copyFileSync(this.dataFile, this.backupFile);
    fs.copyFileSync(temp, this.dataFile);
    fs.rmSync(temp, { force: true });
  }

  #audit(action, detail, payload = {}) {
    this.data.audit.unshift({ id: id('audit'), action, detail, payload, createdAt: now() });
    this.data.audit = this.data.audit.slice(0, 1000);
  }

  #queue(type, payload) {
    this.data.syncQueue.push({ id: id('sync'), type, payload, status: 'pending', attempts: 0, createdAt: now(), lastError: null });
  }

  #openShift() {
    return this.data.shifts.find((shift) => shift.status === 'open') || null;
  }

  verifyManagerPin(pin) {
    if (!this.data.settings.managerPinHash) throw new Error('Cadastre um PIN gerencial nas configurações.');
    if (!pin || pinHash(String(pin)) !== this.data.settings.managerPinHash) throw new Error('PIN gerencial inválido.');
    return true;
  }

  getState() {
    const settings = { ...this.data.settings, managerPinHash: undefined, managerPinConfigured: Boolean(this.data.settings.managerPinHash) };
    delete settings.managerPinHash;
    return clone({
      settings,
      products: this.data.products,
      promotions: this.data.promotions,
      combos: this.data.combos,
      openShift: this.#openShift(),
      shifts: this.data.shifts,
      cashMovements: this.data.cashMovements,
      sales: this.data.sales,
      orders: this.data.orders,
      audit: this.data.audit,
      syncQueue: this.data.syncQueue,
      reports: this.getReports(),
      dataFile: this.dataFile
    });
  }

  updateSettings(input) {
    const next = { ...this.data.settings, ...input };
    if (input.managerPin) next.managerPinHash = pinHash(String(input.managerPin));
    delete next.managerPin;
    this.data.settings = next;
    this.#audit('Configurações atualizadas', 'Loja, terminal, equipamentos e sincronização foram atualizados.');
    this.#save();
    return this.getState();
  }

  openShift({ operatorName, openingCash, terminalId }) {
    if (this.#openShift()) throw new Error('Já existe um caixa aberto.');
    const shift = {
      id: id('shift'),
      operatorName: String(operatorName || 'Operador'),
      terminalId: String(terminalId || this.data.settings.terminalId),
      openingCashCents: toCents(openingCash),
      status: 'open',
      openedAt: now()
    };
    this.data.shifts.unshift(shift);
    this.#audit('Caixa aberto', `Turno iniciado por ${shift.operatorName}.`, { shiftId: shift.id });
    this.#queue('shift.opened', shift);
    this.#save();
    return clone(shift);
  }

  addCashMovement({ type, amount, reason, managerPin }) {
    const shift = this.#openShift();
    if (!shift) throw new Error('Abra o caixa antes de movimentar valores.');
    if (!['supply', 'withdrawal'].includes(type)) throw new Error('Tipo de movimento inválido.');
    if (type === 'withdrawal') this.verifyManagerPin(managerPin);
    const amountCents = toCents(amount);
    if (amountCents <= 0) throw new Error('Informe um valor positivo.');
    const movement = { id: id('cash'), shiftId: shift.id, type, amountCents, reason: String(reason || ''), createdAt: now() };
    this.data.cashMovements.unshift(movement);
    this.#audit(type === 'supply' ? 'Suprimento realizado' : 'Sangria realizada', `${type === 'supply' ? 'Entrada' : 'Retirada'} de ${fromCents(amountCents).toFixed(2)}.`, { movementId: movement.id });
    this.#queue('cash.movement.created', movement);
    this.#save();
    return clone(movement);
  }

  closeShift({ countedCash, managerPin }) {
    const shift = this.#openShift();
    if (!shift) throw new Error('Não existe caixa aberto.');
    this.verifyManagerPin(managerPin);
    const movements = this.data.cashMovements.filter((movement) => movement.shiftId === shift.id);
    const expectedCashCents = movements.reduce((total, movement) => {
      if (['sale', 'supply'].includes(movement.type)) return total + movement.amountCents;
      return total - movement.amountCents;
    }, shift.openingCashCents);
    const countedCashCents = toCents(countedCash);
    Object.assign(shift, {
      status: 'closed',
      expectedCashCents,
      countedCashCents,
      differenceCents: countedCashCents - expectedCashCents,
      closedAt: now()
    });
    this.#audit('Caixa fechado', `Diferença de caixa: ${fromCents(shift.differenceCents).toFixed(2)}.`, { shiftId: shift.id });
    this.#queue('shift.closed', shift);
    this.#save();
    return clone(shift);
  }

  saveProduct(input) {
    const existing = input.id ? this.data.products.find((item) => item.id === input.id) : null;
    const product = {
      id: existing?.id || id('product'),
      sku: String(input.sku || '').trim(),
      barcode: String(input.barcode || '').trim(),
      name: String(input.name || '').trim(),
      category: String(input.category || 'Geral').trim(),
      priceCents: toCents(input.price),
      costCents: toCents(input.cost),
      stock: Math.max(0, Number(input.stock || 0)),
      unit: String(input.unit || 'un'),
      active: input.active !== false,
      trackStock: input.trackStock !== false,
      updatedAt: now()
    };
    if (!product.name) throw new Error('Nome do produto é obrigatório.');
    if (product.priceCents < 0) throw new Error('Preço inválido.');
    if (existing) Object.assign(existing, product);
    else this.data.products.unshift(product);
    this.#audit(existing ? 'Produto atualizado' : 'Produto criado', `${product.name} salvo no catálogo.`, { productId: product.id });
    this.#queue(existing ? 'product.updated' : 'product.created', product);
    this.#save();
    return clone(product);
  }

  deleteProduct(productId) {
    const index = this.data.products.findIndex((item) => item.id === productId);
    if (index < 0) throw new Error('Produto não encontrado.');
    const [product] = this.data.products.splice(index, 1);
    this.#audit('Produto excluído', `${product.name} removido do catálogo.`, { productId });
    this.#queue('product.deleted', { productId });
    this.#save();
    return true;
  }

  savePromotion(input) {
    const existing = input.id ? this.data.promotions.find((item) => item.id === input.id) : null;
    const promotion = {
      id: existing?.id || id('promotion'),
      code: String(input.code || '').trim().toUpperCase(),
      name: String(input.name || '').trim(),
      description: String(input.description || '').trim(),
      discountType: input.discountType === 'fixed' ? 'fixed' : 'percent',
      discountValue: Math.max(0, Number(input.discountValue || 0)),
      active: input.active !== false,
      inStoreOnly: input.inStoreOnly !== false,
      radiusM: Math.max(0, Number(input.radiusM || 0)),
      startsAt: input.startsAt || now(),
      endsAt: input.endsAt || null,
      updatedAt: now()
    };
    if (!promotion.code || !promotion.name) throw new Error('Código e nome da promoção são obrigatórios.');
    if (existing) Object.assign(existing, promotion);
    else this.data.promotions.unshift(promotion);
    this.#audit(existing ? 'Promoção atualizada' : 'Promoção criada', `${promotion.name} salva.`, { promotionId: promotion.id });
    this.#queue(existing ? 'promotion.updated' : 'promotion.created', promotion);
    this.#save();
    return clone(promotion);
  }

  deletePromotion(promotionId) {
    const index = this.data.promotions.findIndex((item) => item.id === promotionId);
    if (index < 0) throw new Error('Promoção não encontrada.');
    this.data.promotions.splice(index, 1);
    this.#audit('Promoção excluída', 'Regra promocional removida.', { promotionId });
    this.#queue('promotion.deleted', { promotionId });
    this.#save();
    return true;
  }

  createSale(input) {
    const key = String(input.idempotencyKey || '').trim();
    if (!key) throw new Error('Chave de idempotência obrigatória.');
    if (this.data.idempotency[key]) {
      const sale = this.data.sales.find((item) => item.id === this.data.idempotency[key]);
      return clone({ sale, duplicate: true });
    }
    const shift = this.#openShift();
    if (!shift) throw new Error('Abra o caixa antes de vender.');
    if (!Array.isArray(input.items) || input.items.length === 0) throw new Error('Adicione itens ao carrinho.');

    const items = input.items.map((line) => {
      const product = this.data.products.find((item) => item.id === line.productId && item.active);
      if (!product) throw new Error('Produto indisponível.');
      const quantity = Math.max(1, Math.floor(Number(line.quantity || 1)));
      if (product.trackStock && product.stock < quantity) throw new Error(`Estoque insuficiente para ${product.name}.`);
      return {
        productId: product.id,
        sku: product.sku,
        barcode: product.barcode,
        name: product.name,
        quantity,
        unitPriceCents: product.priceCents,
        lineTotalCents: product.priceCents * quantity,
        note: String(line.note || '')
      };
    });

    const subtotalCents = items.reduce((sum, item) => sum + item.lineTotalCents, 0);
    const promotion = input.couponCode
      ? this.data.promotions.find((item) => item.active && item.code === String(input.couponCode).trim().toUpperCase())
      : null;
    let couponDiscountCents = 0;
    if (promotion && (!promotion.endsAt || new Date(promotion.endsAt).getTime() >= Date.now())) {
      couponDiscountCents = promotion.discountType === 'fixed'
        ? Math.min(subtotalCents, toCents(promotion.discountValue))
        : Math.round(subtotalCents * promotion.discountValue / 100);
    }
    const manualPercent = Math.max(0, Number(input.manualDiscountPercent || 0));
    const manualDiscountCents = Math.round(subtotalCents * manualPercent / 100) + toCents(input.manualDiscountAmount || 0) + toCents(input.comboDiscount || 0);
    const totalDiscountCents = Math.min(subtotalCents, couponDiscountCents + manualDiscountCents);
    const effectivePercent = subtotalCents ? totalDiscountCents / subtotalCents * 100 : 0;
    if (effectivePercent > Number(this.data.settings.managerDiscountLimit || 0)) this.verifyManagerPin(input.managerPin);
    const totalCents = Math.max(0, subtotalCents - totalDiscountCents);
    const payments = Array.isArray(input.payments) ? input.payments.map((payment) => ({ method: payment.method, amountCents: toCents(payment.amount), reference: String(payment.reference || '') })) : [];
    const paidCents = payments.reduce((sum, payment) => sum + payment.amountCents, 0);
    if (Math.abs(paidCents - totalCents) > 1) throw new Error('A soma dos pagamentos deve ser igual ao total da venda.');

    for (const item of items) {
      const product = this.data.products.find((candidate) => candidate.id === item.productId);
      if (product.trackStock) product.stock -= item.quantity;
    }

    const sequence = this.data.orders.length + 1;
    const receiptNumber = `PDV-${new Date().toISOString().slice(0, 10).replaceAll('-', '')}-${String(sequence).padStart(5, '0')}`;
    const sale = {
      id: id('sale'),
      shiftId: shift.id,
      idempotencyKey: key,
      offlineId: input.offlineId || null,
      terminalId: input.terminalId || this.data.settings.terminalId,
      operatorName: String(input.operatorName || shift.operatorName),
      items,
      subtotalCents,
      couponCode: promotion?.code || null,
      couponDiscountCents,
      manualDiscountCents,
      totalDiscountCents,
      totalCents,
      payments,
      customerName: String(input.customerName || ''),
      customerUserId: input.customerUserId || null,
      pairingCode: input.pairingCode || null,
      orderMode: input.orderMode || 'counter',
      tableNumber: input.tableNumber || null,
      receiptNumber,
      fiscalStatus: 'pending_sync',
      status: 'paid',
      createdAt: now()
    };
    const order = {
      id: id('order'),
      saleId: sale.id,
      queueNumber: sequence,
      status: 'paid',
      items,
      totalCents,
      customerName: sale.customerName,
      customerUserId: sale.customerUserId,
      orderMode: sale.orderMode,
      tableNumber: sale.tableNumber,
      createdAt: now(),
      updatedAt: now()
    };
    this.data.sales.unshift(sale);
    this.data.orders.unshift(order);
    this.data.idempotency[key] = sale.id;
    for (const payment of payments.filter((item) => item.method === 'cash')) {
      this.data.cashMovements.unshift({ id: id('cash'), shiftId: shift.id, type: 'sale', amountCents: payment.amountCents, reason: receiptNumber, createdAt: now() });
    }
    this.#audit('Venda concluída', `${receiptNumber} registrada.`, { saleId: sale.id, orderId: order.id, offlineId: sale.offlineId });
    this.#queue('sale.created', { sale, order });
    this.#save();
    return clone({ sale, order, duplicate: false });
  }

  updateOrderStatus(orderId, status) {
    if (!['paid', 'preparing', 'ready', 'delivered', 'cancelled'].includes(status)) throw new Error('Status inválido.');
    const order = this.data.orders.find((item) => item.id === orderId);
    if (!order) throw new Error('Pedido não encontrado.');
    order.status = status;
    order.updatedAt = now();
    if (status === 'ready') order.readyAt = now();
    if (status === 'delivered') order.deliveredAt = now();
    this.#audit('Pedido atualizado', `Pedido ${order.queueNumber} definido como ${status}.`, { orderId });
    this.#queue('order.status.changed', clone(order));
    this.#save();
    return clone(order);
  }

  refundSale(saleId, managerPin, reason) {
    this.verifyManagerPin(managerPin);
    const sale = this.data.sales.find((item) => item.id === saleId);
    if (!sale) throw new Error('Venda não encontrada.');
    if (sale.status === 'refunded') throw new Error('Venda já estornada.');
    for (const item of sale.items) {
      const product = this.data.products.find((candidate) => candidate.id === item.productId);
      if (product?.trackStock) product.stock += item.quantity;
    }
    sale.status = 'refunded';
    sale.refundReason = String(reason || 'Estorno gerencial');
    sale.refundedAt = now();
    const order = this.data.orders.find((item) => item.saleId === sale.id);
    if (order) {
      order.status = 'cancelled';
      order.updatedAt = now();
    }
    const shift = this.#openShift();
    const cashCents = sale.payments.filter((item) => item.method === 'cash').reduce((sum, item) => sum + item.amountCents, 0);
    if (shift && cashCents > 0) this.data.cashMovements.unshift({ id: id('cash'), shiftId: shift.id, type: 'refund', amountCents: cashCents, reason: sale.receiptNumber, createdAt: now() });
    this.#audit('Venda estornada', `${sale.receiptNumber} estornada.`, { saleId });
    this.#queue('sale.refunded', clone(sale));
    this.#save();
    return clone(sale);
  }

  getReports() {
    const validSales = this.data.sales.filter((sale) => sale.status !== 'refunded');
    const revenueCents = validSales.reduce((sum, sale) => sum + sale.totalCents, 0);
    const paymentTotals = {};
    const productTotals = {};
    for (const sale of validSales) {
      for (const payment of sale.payments) paymentTotals[payment.method] = (paymentTotals[payment.method] || 0) + payment.amountCents;
      for (const item of sale.items) {
        const current = productTotals[item.productId] || { name: item.name, quantity: 0, revenueCents: 0 };
        current.quantity += item.quantity;
        current.revenueCents += item.lineTotalCents;
        productTotals[item.productId] = current;
      }
    }
    return {
      salesCount: validSales.length,
      revenueCents,
      averageTicketCents: validSales.length ? Math.round(revenueCents / validSales.length) : 0,
      paymentTotals,
      topProducts: Object.values(productTotals).sort((a, b) => b.quantity - a.quantity).slice(0, 10)
    };
  }

  pendingSync(limit = 100) {
    return clone(this.data.syncQueue.filter((item) => item.status === 'pending').slice(0, limit));
  }

  markSyncSuccess(ids) {
    const idSet = new Set(ids);
    this.data.syncQueue = this.data.syncQueue.filter((item) => !idSet.has(item.id));
    this.#save();
  }

  markSyncFailure(ids, message) {
    const idSet = new Set(ids);
    for (const item of this.data.syncQueue) {
      if (idSet.has(item.id)) {
        item.attempts += 1;
        item.lastError = String(message || 'Falha de sincronização');
        item.lastAttemptAt = now();
      }
    }
    this.#save();
  }

  exportSnapshot(destination) {
    this.#save();
    fs.copyFileSync(this.dataFile, destination);
    return destination;
  }

  restoreSnapshot(source) {
    const parsed = JSON.parse(fs.readFileSync(source, 'utf8'));
    if (!parsed || typeof parsed !== 'object' || !Array.isArray(parsed.products) || !Array.isArray(parsed.sales)) throw new Error('Arquivo de backup inválido.');
    if (fs.existsSync(this.dataFile)) fs.copyFileSync(this.dataFile, this.backupFile);
    this.data = parsed;
    this.#normalize();
    this.#audit('Backup restaurado', 'A base local foi restaurada a partir de um arquivo externo.');
    this.#save();
    return this.getState();
  }
}

module.exports = { PdvStore, toCents, fromCents, pinHash };

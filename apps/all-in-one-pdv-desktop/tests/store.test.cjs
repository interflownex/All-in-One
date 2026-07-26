const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { PdvStore } = require('../electron/store.cjs');

function tempDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'all-in-one-pdv-'));
}

function makeSale(store, key = 'sale-key-1') {
  const state = store.getState();
  const product = state.products[0];
  return store.createSale({
    idempotencyKey: key,
    offlineId: `offline-${key}`,
    items: [{ productId: product.id, quantity: 2 }],
    payments: [{ method: 'cash', amount: (product.priceCents * 2) / 100 }],
    operatorName: 'Operador Teste',
    orderMode: 'counter'
  });
}

test('venda local reduz estoque e cria pedido', () => {
  const store = new PdvStore(tempDir());
  const before = store.getState();
  const product = before.products[0];
  store.openShift({ operatorName: 'Operador Teste', openingCash: 100 });
  const result = makeSale(store);
  const after = store.getState();
  const changed = after.products.find((item) => item.id === product.id);
  assert.equal(result.duplicate, false);
  assert.equal(changed.stock, product.stock - 2);
  assert.equal(after.orders[0].status, 'paid');
  assert.equal(after.syncQueue.some((event) => event.type === 'sale.created'), true);
});

test('idempotência impede venda duplicada', () => {
  const store = new PdvStore(tempDir());
  store.openShift({ operatorName: 'Operador Teste', openingCash: 0 });
  const first = makeSale(store, 'same-key');
  const second = makeSale(store, 'same-key');
  assert.equal(first.duplicate, false);
  assert.equal(second.duplicate, true);
  assert.equal(store.getState().sales.length, 1);
});

test('estorno gerencial recompõe estoque', () => {
  const store = new PdvStore(tempDir());
  store.updateSettings({ managerPin: '1234' });
  store.openShift({ operatorName: 'Operador Teste', openingCash: 0 });
  const before = store.getState().products[0];
  const result = makeSale(store, 'refund-key');
  store.refundSale(result.sale.id, '1234', 'Teste automatizado');
  const after = store.getState();
  const product = after.products.find((item) => item.id === before.id);
  assert.equal(product.stock, before.stock);
  assert.equal(after.sales[0].status, 'refunded');
  assert.equal(after.orders[0].status, 'cancelled');
});

test('backup externo pode ser restaurado', () => {
  const directory = tempDir();
  const store = new PdvStore(directory);
  const backup = path.join(directory, 'snapshot.json');
  const originalCount = store.getState().products.length;
  store.exportSnapshot(backup);
  store.saveProduct({ name: 'Produto temporário', price: 10, stock: 1 });
  assert.equal(store.getState().products.length, originalCount + 1);
  store.restoreSnapshot(backup);
  assert.equal(store.getState().products.length, originalCount);
});

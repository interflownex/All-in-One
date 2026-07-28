const { app, BrowserWindow, dialog, ipcMain, safeStorage, shell } = require('electron');
const path = require('node:path');
const fs = require('node:fs');
const { PdvStore } = require('./store.cjs');

let mainWindow;
let store;
let syncTimer;

const secretFile = () => path.join(app.getPath('userData'), 'pdv-secrets.json');
const readSecrets = () => {
  try {
    if (!fs.existsSync(secretFile())) return {};
    const parsed = JSON.parse(fs.readFileSync(secretFile(), 'utf8'));
    if (parsed.apiToken && safeStorage.isEncryptionAvailable()) parsed.apiToken = safeStorage.decryptString(Buffer.from(parsed.apiToken, 'base64'));
    else delete parsed.apiToken;
    return parsed;
  } catch {
    return {};
  }
};
const writeSecrets = (input) => {
  const payload = {};
  if (input.apiToken) {
    if (!safeStorage.isEncryptionAvailable()) throw new Error('Criptografia do Windows indisponível neste dispositivo.');
    payload.apiToken = safeStorage.encryptString(String(input.apiToken)).toString('base64');
  }
  fs.writeFileSync(secretFile(), JSON.stringify(payload, null, 2), 'utf8');
  return { apiTokenConfigured: Boolean(payload.apiToken) };
};

function broadcastState() {
  if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send('pdv:state-changed', store.getState());
}

async function syncNow() {
  const state = store.getState();
  if (!state.settings.syncEnabled || !state.settings.syncEndpoint) return { ok: false, skipped: true, reason: 'Sincronização desativada ou endpoint ausente.' };
  const events = store.pendingSync(100);
  if (!events.length) return { ok: true, synced: 0, pending: 0 };
  const secrets = readSecrets();
  const headers = { 'Content-Type': 'application/json', 'X-PDV-Terminal': state.settings.terminalId };
  if (secrets.apiToken) headers.Authorization = `Bearer ${secrets.apiToken}`;
  try {
    const response = await fetch(state.settings.syncEndpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify({ terminalId: state.settings.terminalId, storeName: state.settings.storeName, events })
    });
    if (!response.ok) throw new Error(`Servidor respondeu HTTP ${response.status}.`);
    store.markSyncSuccess(events.map((event) => event.id));
    broadcastState();
    return { ok: true, synced: events.length, pending: store.pendingSync().length };
  } catch (error) {
    store.markSyncFailure(events.map((event) => event.id), error.message);
    broadcastState();
    return { ok: false, synced: 0, pending: store.pendingSync().length, error: error.message };
  }
}

function scheduleSync() {
  clearInterval(syncTimer);
  const minutes = Math.max(1, Number(store.getState().settings.autoSyncMinutes || 2));
  syncTimer = setInterval(() => void syncNow(), minutes * 60 * 1000);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 1080,
    minHeight: 680,
    backgroundColor: '#070a17',
    autoHideMenuBar: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });
  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  mainWindow.once('ready-to-show', () => mainWindow.show());
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:/i.test(url)) shell.openExternal(url);
    return { action: 'deny' };
  });
}

function registerIpc() {
  ipcMain.handle('pdv:get-state', () => store.getState());
  ipcMain.handle('pdv:update-settings', (_event, input) => {
    const result = store.updateSettings(input || {});
    scheduleSync();
    broadcastState();
    return result;
  });
  ipcMain.handle('pdv:save-sync-secret', (_event, input) => writeSecrets(input || {}));
  ipcMain.handle('pdv:get-sync-secret-status', () => ({ apiTokenConfigured: Boolean(readSecrets().apiToken) }));
  ipcMain.handle('pdv:sync-now', () => syncNow());
  ipcMain.handle('pdv:open-shift', (_event, input) => { const result = store.openShift(input || {}); broadcastState(); return result; });
  ipcMain.handle('pdv:close-shift', (_event, input) => { const result = store.closeShift(input || {}); broadcastState(); return result; });
  ipcMain.handle('pdv:add-cash-movement', (_event, input) => { const result = store.addCashMovement(input || {}); broadcastState(); return result; });
  ipcMain.handle('pdv:save-product', (_event, input) => { const result = store.saveProduct(input || {}); broadcastState(); return result; });
  ipcMain.handle('pdv:delete-product', (_event, productId) => { const result = store.deleteProduct(productId); broadcastState(); return result; });
  ipcMain.handle('pdv:save-promotion', (_event, input) => { const result = store.savePromotion(input || {}); broadcastState(); return result; });
  ipcMain.handle('pdv:delete-promotion', (_event, promotionId) => { const result = store.deletePromotion(promotionId); broadcastState(); return result; });
  ipcMain.handle('pdv:create-sale', (_event, input) => { const result = store.createSale(input || {}); broadcastState(); return result; });
  ipcMain.handle('pdv:update-order-status', (_event, input) => { const result = store.updateOrderStatus(input.orderId, input.status); broadcastState(); return result; });
  ipcMain.handle('pdv:refund-sale', (_event, input) => { const result = store.refundSale(input.saleId, input.managerPin, input.reason); broadcastState(); return result; });
  ipcMain.handle('pdv:backup', async () => {
    const result = await dialog.showSaveDialog(mainWindow, { title: 'Salvar backup do PDV', defaultPath: `All-in-One-PDV-Backup-${new Date().toISOString().slice(0, 10)}.json`, filters: [{ name: 'Backup JSON', extensions: ['json'] }] });
    if (result.canceled || !result.filePath) return { canceled: true };
    store.exportSnapshot(result.filePath);
    return { canceled: false, filePath: result.filePath };
  });
  ipcMain.handle('pdv:restore', async () => {
    const result = await dialog.showOpenDialog(mainWindow, { title: 'Restaurar backup do PDV', properties: ['openFile'], filters: [{ name: 'Backup JSON', extensions: ['json'] }] });
    if (result.canceled || !result.filePaths[0]) return { canceled: true };
    store.restoreSnapshot(result.filePaths[0]);
    broadcastState();
    return { canceled: false, filePath: result.filePaths[0] };
  });
  ipcMain.handle('pdv:export-sales-csv', async () => {
    const result = await dialog.showSaveDialog(mainWindow, { title: 'Exportar vendas', defaultPath: `Vendas-PDV-${new Date().toISOString().slice(0, 10)}.csv`, filters: [{ name: 'CSV', extensions: ['csv'] }] });
    if (result.canceled || !result.filePath) return { canceled: true };
    const state = store.getState();
    const rows = [['Comprovante', 'Data', 'Operador', 'Cliente', 'Total', 'Status'], ...state.sales.map((sale) => [sale.receiptNumber, sale.createdAt, sale.operatorName, sale.customerName || '', (sale.totalCents / 100).toFixed(2), sale.status])];
    const csv = rows.map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(';')).join('\r\n');
    fs.writeFileSync(result.filePath, `\uFEFF${csv}`, 'utf8');
    return { canceled: false, filePath: result.filePath };
  });
  ipcMain.handle('pdv:print-receipt', async (_event, saleId) => {
    const sale = store.getState().sales.find((item) => item.id === saleId);
    if (!sale) throw new Error('Venda não encontrada.');
    const printWindow = new BrowserWindow({ show: false, webPreferences: { sandbox: true } });
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>body{font-family:monospace;width:72mm;margin:0;padding:6mm}h1{font-size:18px;text-align:center}.row{display:flex;justify-content:space-between}.line{border-top:1px dashed #000;margin:8px 0}</style></head><body><h1>All in One PDV</h1><div>${sale.receiptNumber}</div><div>${new Date(sale.createdAt).toLocaleString('pt-BR')}</div><div class="line"></div>${sale.items.map((item) => `<div>${item.quantity}x ${item.name}</div><div class="row"><span></span><span>R$ ${(item.lineTotalCents / 100).toFixed(2)}</span></div>`).join('')}<div class="line"></div><div class="row"><strong>TOTAL</strong><strong>R$ ${(sale.totalCents / 100).toFixed(2)}</strong></div><p style="text-align:center">Obrigado pela preferência.</p></body></html>`;
    await printWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    return new Promise((resolve) => printWindow.webContents.print({ silent: false, printBackground: true }, (success, failureReason) => { printWindow.close(); resolve({ success, failureReason }); }));
  });
  ipcMain.handle('pdv:get-app-info', () => ({ version: app.getVersion(), userDataPath: app.getPath('userData'), platform: process.platform, arch: process.arch }));
}

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) app.quit();
else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
  app.whenReady().then(() => {
    store = new PdvStore(path.join(app.getPath('userData'), 'data'));
    registerIpc();
    createWindow();
    scheduleSync();
    void syncNow();
    app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
  });
}

app.on('window-all-closed', () => {
  clearInterval(syncTimer);
  if (process.platform !== 'darwin') app.quit();
});

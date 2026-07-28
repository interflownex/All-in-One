const { contextBridge, ipcRenderer } = require('electron');

const invoke = (channel, payload) => ipcRenderer.invoke(channel, payload);

contextBridge.exposeInMainWorld('pdv', {
  getState: () => invoke('pdv:get-state'),
  updateSettings: (input) => invoke('pdv:update-settings', input),
  saveSyncSecret: (input) => invoke('pdv:save-sync-secret', input),
  getSyncSecretStatus: () => invoke('pdv:get-sync-secret-status'),
  syncNow: () => invoke('pdv:sync-now'),
  openShift: (input) => invoke('pdv:open-shift', input),
  closeShift: (input) => invoke('pdv:close-shift', input),
  addCashMovement: (input) => invoke('pdv:add-cash-movement', input),
  saveProduct: (input) => invoke('pdv:save-product', input),
  deleteProduct: (productId) => invoke('pdv:delete-product', productId),
  savePromotion: (input) => invoke('pdv:save-promotion', input),
  deletePromotion: (promotionId) => invoke('pdv:delete-promotion', promotionId),
  createSale: (input) => invoke('pdv:create-sale', input),
  updateOrderStatus: (input) => invoke('pdv:update-order-status', input),
  refundSale: (input) => invoke('pdv:refund-sale', input),
  backup: () => invoke('pdv:backup'),
  restore: () => invoke('pdv:restore'),
  exportSalesCsv: () => invoke('pdv:export-sales-csv'),
  printReceipt: (saleId) => invoke('pdv:print-receipt', saleId),
  getAppInfo: () => invoke('pdv:get-app-info'),
  onStateChanged: (callback) => {
    const listener = (_event, state) => callback(state);
    ipcRenderer.on('pdv:state-changed', listener);
    return () => ipcRenderer.removeListener('pdv:state-changed', listener);
  }
});

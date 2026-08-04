import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import './assets/valley_design_system.css';
import './experience.css';
import './product_feed.css';
import App from './App.tsx';
import { installNativeFetchBridge } from './lib/nativeBridge';

installNativeFetchBridge();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

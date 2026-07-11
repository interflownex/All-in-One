import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/mobility': { target: 'http://localhost:8100', changeOrigin: true },
      '/riders': { target: 'http://localhost:8100', changeOrigin: true },
      '/finance': { target: 'http://localhost:8100', changeOrigin: true },
    },
  },
})

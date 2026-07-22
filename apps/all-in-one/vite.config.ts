import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'


export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks(id) {
          const vendorPkgs = ['react', 'react-dom', 'react-router-dom'];
          if (vendorPkgs.some((pkg) => id.includes(`node_modules/${pkg}`))) {
            return 'vendor';
          }
        },
      },
    },
  },
  server: {
    proxy: {
      '/gateway': {
        target: 'http://localhost:8100',
        changeOrigin: true,
      },
    },
  },
})

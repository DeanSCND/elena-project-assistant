import { defineConfig } from 'vite'
import { resolve } from 'path'
import { copyFileSync } from 'fs'

export default defineConfig({
  server: {
    port: 5173,
    host: true,
    cors: true,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8100',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index_v2.html')
      }
    }
  },
  plugins: [
    {
      name: 'copy-pdf-viewer',
      closeBundle() {
        // Copy pdf-viewer.js to dist after build
        copyFileSync(
          resolve(__dirname, 'pdf-viewer.js'),
          resolve(__dirname, 'dist/pdf-viewer.js')
        )
      }
    }
  ]
})
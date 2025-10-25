import { defineConfig } from 'vite'
import legacy from '@vitejs/plugin-legacy'

export default defineConfig({
  build: {
    outDir: 'agentpm/web/static/js/dist',
    minify: 'terser',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: 'agentpm/web/src/js/main.js'
      },
      output: {
        entryFileNames: '[name].[hash].js',
        chunkFileNames: '[name].[hash].js',
        assetFileNames: '[name].[hash].[ext]',
        manualChunks: {
          vendor: ['alpinejs', 'htmx.org']
        }
      }
    },
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  plugins: [
    legacy({
      targets: ['defaults', 'not IE 11']
    })
  ],
  server: {
    port: 3000,
    hmr: {
      port: 3001
    },
    proxy: {
      '^/(?!src/).*': {
        target: 'http://localhost:5003',
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': '/agentpm/web/src'
    }
  }
})

import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Load env file but prefer command environment for BACKEND_PORT
  const env = loadEnv(mode, process.cwd(), '')
  const backendPort = process.env.BACKEND_PORT || env.BACKEND_PORT || '9000'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: `http://127.0.0.1:${backendPort}`,
          changeOrigin: false,
        },
      },
    },
    preview: {
      port: 5173,
      proxy: {
        '/api': {
          target: `http://127.0.0.1:${backendPort}`,
          changeOrigin: false,
        },
      },
    },
  }
})

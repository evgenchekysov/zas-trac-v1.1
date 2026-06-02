import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://ominous-rotary-phone-jjjx7rvj76jfg4x-8080.app.github.dev',
        changeOrigin: true,
      },
    },
  },
})

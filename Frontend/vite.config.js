import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/Advisor': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/Student': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/Admin': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})
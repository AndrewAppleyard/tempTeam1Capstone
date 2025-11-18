import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/',
  build: {
    outDir: 'dist',
  },
  plugins: [vue()],
  server: {
    proxy: {
      '/Advisor': {
        target: 'http://127.0.0.1:5000', // locally testing
        // target: 'http://uafs_backend:5000', // docker container
        changeOrigin: true,
      },
      '/Student': {
        target: 'http://127.0.0.1:5000', // locally testing
        //  target: 'http://uafs_backend:5000', // docker container
        changeOrigin: true,
      },
      '/Admin': {
        target: 'http://127.0.0.1:5000', // locally testing
        //  target: 'http://uafs_backend:5000', // docker container
        changeOrigin: true,
      },
      '/Schedule': {
        target: 'http://127.0.0.1:5000', // locally testing
        //  target: 'http://uafs_backend:5000', // docker container
        changeOrigin: true,
      },
      '/DegreePlan': {
        target: 'http://127.0.0.1:5000', // locally testing
        //  target: 'http://uafs_backend:5000', // docker container
        changeOrigin: true,
      },
      '/Transcript': {
      '/CurrentCourses': {
        target: 'http://127.0.0.1:5000', // locally testing
        //  target: 'http://uafs_backend:5000', // docker container
        changeOrigin: true,
      },
    },
  },
})

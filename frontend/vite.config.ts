import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { 
    host: '0.0.0.0',  // 🔥 监听所有网络接口，允许局域网访问
    port: 5173,
    strictPort: true,  // 🔥 强制使用5173端口，如果被占用则报错而不是自动切换
    // 🔥 添加代理配置，彻底解决CORS问题
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})

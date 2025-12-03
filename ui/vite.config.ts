import { fileURLToPath, URL } from 'node:url'
import type { ProxyOptions } from 'vite'
import { defineConfig, loadEnv } from 'vite'
import fs from 'fs'
import path from 'path'

import vue from '@vitejs/plugin-vue'
import DefineOptions from 'unplugin-vue-define-options/vite'

// 读取config.js配置文件
function loadAppConfig() {
  try {
    const configPath = path.resolve(__dirname, 'public/config.js')
    if (fs.existsSync(configPath)) {
      const configContent = fs.readFileSync(configPath, 'utf-8')
      // 提取配置对象
      const match = configContent.match(/window\.APP_CONFIG\s*=\s*({[\s\S]*?});/)
      if (match) {
        // 使用eval来解析配置对象（在构建时是安全的）
        const configStr = match[1]
        return eval(`(${configStr})`)
      }
    }
  } catch (error) {
    console.warn('Failed to load config.js, using default config:', error)
  }
  
  // 默认配置
  return {
    VITE_STATIC_PATH: '/ui/',
    VITE_API_PATH: ''
  }
}

const config = loadAppConfig()
declare const config: Record<string, any>

const envDir = './env'
// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const ENV = loadEnv(mode, envDir)
  const prefix = process.env.VITE_DYNAMIC_PREFIX || config.VITE_STATIC_PATH || '/'
  console.log('prefix', prefix)
  const proxyConf: Record<string, string | ProxyOptions> = {}
  
  // API proxy configuration
  proxyConf['/api'] = {
    target: 'http://10.4.1.132:8080',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, config.VITE_API_PATH + '/api')
  }
  
  // Backend API proxy configuration - 直接代理完整的后端API路径
  proxyConf[config.VITE_API_PATH + '/api'] = {
    target: 'http://10.4.1.132:8080',
    changeOrigin: true,
    rewrite: (path) => path.replace(new RegExp(`^${config.VITE_API_PATH.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`), '')
  }
  
  // Document proxy configuration
  proxyConf['/doc'] = {
    target: 'http://10.4.1.132:8080',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/doc/, config.VITE_STATIC_PATH + '/doc')
  }
  
  // Static files proxy configuration
  proxyConf['/static'] = {
    target: 'http://10.4.1.132:8080',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/static/, config.VITE_STATIC_PATH + '/static')
  }
  return {
    preflight: false,
    lintOnSave: false,
    base: prefix,
    envDir: envDir,
    plugins: [vue(), DefineOptions()],
    server: {
      cors: true,
      host: '0.0.0.0',
      port: Number(ENV.VITE_APP_PORT),
      strictPort: true,
      proxy: proxyConf
    },
    build: {
      target: "es2015",
      cssTarget: "chrome80",
      outDir: 'dist/ui',
      reportCompressedSize: false,
      // chunkSizeWarningLimit: 1200,
      // 生产环境移除console
      minify: "terser",
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true
        }
      },
      sourcemap: false,
      rollupOptions: {
        // external:[], // 外部依赖，不想打包进库的依赖
        output: {
          chunkFileNames: "js/[name]-[hash].js",
          entryFileNames: "js/[name]-[hash].js",
          assetFileNames: "[ext]/[name]-[hash].[ext]",
          manualChunks: {
            "lodash": ["lodash"],
            "logicflow": ["@logicflow/core", "@logicflow/extension"],
            "codemirror": ["codemirror", "@codemirror/theme-one-dark", "vue-codemirror"],
            "echarts": ["echarts"],
            "element-plus": ["element-plus", "use-element-plus-theme"],
            // "moment": ["moment"],
            "md-editor-v3": ["md-editor-v3"],
            "pinyin-pro": ["pinyin-pro"]
          }
        }
      }
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    }
  }
})

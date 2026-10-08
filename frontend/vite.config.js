import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],

    server: {
      port: Number(env.VITE_PORT) || 4449, // 4444 대신 4449로 변경
      strictPort: true, // 4449가 이미 점유 중이면 다른 포트로 자동 전환되지 않고 에러 출력
    },
  }
})
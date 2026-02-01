/**
 * Vite Configuration for Electron + React
 *
 * This configuration handles:
 * - React app (renderer process)
 * - Electron main process (ES modules)
 * - Preload script (CommonJS - required by Electron)
 * - Native module externalization
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import electron from 'vite-plugin-electron/simple';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    electron({
      // Main process configuration
      main: {
        entry: 'electron/main.ts',
        vite: {
          build: {
            outDir: 'dist-electron',
            rollupOptions: {
              // IMPORTANT: Externalize Electron and native modules
              // These cannot be bundled and must be loaded at runtime
              external: ['electron', 'better-sqlite3', 'electron-store'],
              output: {
                format: 'es',
                entryFileNames: '[name].mjs',
              },
            },
          },
        },
      },

      // Preload script configuration
      // IMPORTANT: Must be CommonJS format (.cjs) for Electron compatibility
      preload: {
        input: 'electron/preload.ts',
        vite: {
          build: {
            outDir: 'dist-electron',
            rollupOptions: {
              output: {
                format: 'cjs',
                entryFileNames: '[name].cjs',
              },
            },
          },
        },
      },

      // Renderer process - uses default Vite build
      renderer: {},
    }),
  ],

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  build: {
    outDir: 'dist',
  },

  // Ensure React is properly bundled (prevents duplicate React instances)
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
});

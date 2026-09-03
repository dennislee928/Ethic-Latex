/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the erh-guardian-mcp worker (no trailing /mcp). */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

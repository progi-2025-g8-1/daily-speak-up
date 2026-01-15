/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_BASE_URL: string
    readonly VITE_ANALYTICS_ID: string
    readonly VITE_AUTH0_DOMAIN: string
    readonly VITE_AUTH0_CLIENT_ID: string
    readonly VITE_AUTH0_REDIRECT_URI: string
    readonly VITE_ENVIRONMENT: string
    readonly VITE_API_DOMAIN: string
    readonly VITE_ROOT_ADMIN_EMAIL: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}
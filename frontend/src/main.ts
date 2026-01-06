import App from './App.vue';
import { createApp } from 'vue';
import './style.css'
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';
import Tooltip from 'primevue/tooltip';
import Lara from '@primeuix/themes/lara';
import { createPinia } from 'pinia';
import router from './router';
import { initSuperTokens } from './supertokens';
import { useThemeStore } from './stores/themeStore';
import 'primeicons/primeicons.css'

// DailySpeakUp Color System (from email templates)
// Primary: #3b82f6 (blue-500)
// Primary Dark: #1e3a8a (blue-900) 
// Primary Light: #eff6ff (blue-50)
// Background: #f0f4f8
// Text Primary: #1e40af (blue-800)
// Text Secondary: #4b5563 (gray-600)
// Text Dark: #1f2937 (gray-800)

// Initialize SuperTokens
initSuperTokens();

const app = createApp(App);

// Create and use Pinia store
const pinia = createPinia();
app.use(pinia);

// Initialize theme from store
const themeStore = useThemeStore();
themeStore.initializeTheme();

// middleware
app.use(PrimeVue, {
    theme: {
        preset: Lara,
        options: {
            prefix: 'p',
            darkModeSelector: '.dark',
            cssLayer: false
        }
    }
});

app.use(ToastService);

app.use(ConfirmationService);

app.use(router);

app.directive('tooltip', Tooltip);

app.mount('#app');
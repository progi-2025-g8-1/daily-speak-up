import App from './App.vue';
import { createApp } from 'vue';
import './style.css'
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';
import Tooltip from 'primevue/tooltip';
import Lara from '@primeuix/themes/lara';
import { definePreset } from '@primeuix/themes';
import router from './router';
import { initSuperTokens } from './supertokens';
import 'primeicons/primeicons.css'
import i18n from './i18n';

// DailySpeakUp Color System (from email templates)
// Primary: #3b82f6 (blue-500)
// Primary Dark: #1e3a8a (blue-900) 
// Primary Light: #eff6ff (blue-50)
// Background: #f0f4f8
// Text Primary: #1e40af (blue-800)
// Text Secondary: #4b5563 (gray-600)
// Text Dark: #1f2937 (gray-800)

const DailySpeakUpPreset = definePreset(Lara, {
    semantic: {
        primary: {
            50: '#eff6ff',   // Very light blue
            100: '#dbeafe',  // Light blue
            200: '#bfdbfe',  // Lighter blue
            300: '#93c5fd',  // Light-medium blue
            400: '#60a5fa',  // Medium blue
            500: '#3b82f6',  // Primary blue (main brand color)
            600: '#2563eb',  // Darker blue
            700: '#1d4ed8',  // Dark blue
            800: '#1e40af',  // Very dark blue (text primary)
            900: '#1e3a8a',  // Darkest blue (brand dark)
            950: '#172554'   // Nearly black blue
        },
        colorScheme: {
            light: {
                surface: {
                    0: '#ffffff',
                    50: '#f0f4f8',    // Background color from email
                    100: '#f9fafb',
                    200: '#f3f4f6',
                    300: '#e5e7eb',
                    400: '#d1d5db',
                    500: '#9ca3af',
                    600: '#6b7280',
                    700: '#4b5563',   // Secondary text
                    800: '#1f2937',   // Dark text
                    900: '#111827',
                    950: '#030712'
                }
            }
        }
    }
});

// Initialize SuperTokens
initSuperTokens();

const app = createApp(App);

// Load language preference from localStorage
const savedLanguage = localStorage.getItem('app-language');
if (savedLanguage && (savedLanguage === 'hr' || savedLanguage === 'en')) {
    i18n.global.locale.value = savedLanguage;
}

// middleware
app.use(PrimeVue, {
    theme: {
        preset: DailySpeakUpPreset,
        options: {
            darkModeSelector: false
        }
    }
});

app.use(ToastService);

app.use(ConfirmationService);

app.use(router);

app.use(i18n);

app.directive('tooltip', Tooltip);

app.mount('#app');
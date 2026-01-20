import { createI18n } from 'vue-i18n';
import hr from './locales/hr.json';
import en from './locales/en.json';

const i18n = createI18n({
    legacy: false, // Use Composition API
    locale: 'hr', // Default locale
    fallbackLocale: 'en',
    messages: {
        hr,
        en
    }
});

export default i18n;

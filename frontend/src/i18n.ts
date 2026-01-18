import { createI18n } from 'vue-i18n';

// Minimal messages to enable i18n; extend as needed.
const messages = {
  en: {},
  hr: {},
};

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages,
});

export default i18n;
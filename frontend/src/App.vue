<script setup>
  import { RouterView, RouterLink } from 'vue-router';
  import { ref, onMounted, watch } from 'vue';
  import { useRoute } from 'vue-router';
  import { useI18n } from 'vue-i18n';
  import LoginModal from './components/LoginModal.vue';
  import Logout from './components/Logout.vue';
  import User from './components/User.vue';
  import EnvironmentIndicator from './components/EnvironmentIndicator.vue';
  import { isAuthenticated } from './auth';
  import { usePrimeVue } from 'primevue/config';
  import { useI18n } from 'vue-i18n';
  import { primevue_hr, primevue_en } from './locales/primevue';

  const route = useRoute();
  const authenticated = ref(false);
  const primevue = usePrimeVue();
  const { locale } = useI18n();

  const checkAuth = async () => {
    authenticated.value = await isAuthenticated();
  };

  const updatePrimeVueLocale = (lang) => {
    if (lang === 'hr') {
      primevue.config.locale = primevue_hr;
    } else {
      primevue.config.locale = primevue_en;
    }
  };

  onMounted(async () => {
    await checkAuth();
    updatePrimeVueLocale(locale.value);
  });

  // Re-check authentication when route changes (e.g., after OAuth callback)
  watch(() => route.path, async () => {
    await checkAuth();
  });

  watch(locale, (newLocale) => {
    updatePrimeVueLocale(newLocale);
  });
</script>

<template>
  <EnvironmentIndicator />
  <RouterView />
</template>
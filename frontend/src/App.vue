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

  const route = useRoute();
  const authenticated = ref(false);
  const { locale } = useI18n();

  const checkAuth = async () => {
    authenticated.value = await isAuthenticated();
  };

  const loadUserLanguage = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/me`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.preferred_lang && (data.preferred_lang === 'hr' || data.preferred_lang === 'en')) {
          locale.value = data.preferred_lang;
        }
      }
    } catch (e) {
      console.error('Failed to load user language:', e);
    }
  };

  onMounted(async () => {
    await checkAuth();
    if (authenticated.value) {
      await loadUserLanguage();
    }
  });

  // Re-check authentication when route changes (e.g., after OAuth callback)
  watch(() => route.path, async () => {
    await checkAuth();
    if (authenticated.value) {
      await loadUserLanguage();
    }
  });
</script>

<template>
  <EnvironmentIndicator />
  <RouterView />
</template>
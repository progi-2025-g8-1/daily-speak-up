<template>
    <Button :label="$t('common.logout')" icon="pi pi-sign-out" severity="warn" @click="handleLogout" :loading="loading" />
</template>

<script>
import { ref } from 'vue';
import { logout } from '../auth';
import { useRouter } from 'vue-router';
import Button from 'primevue/button';

export default {
  components: {
    Button
  },
  setup() {
    const router = useRouter();
    const loading = ref(false);

    const handleLogout = async () => {
      loading.value = true;
      try {
        await logout();
        router.push('/');
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        loading.value = false;
      }
    };

    return {
      loading,
      handleLogout
    };
  }
};
</script>

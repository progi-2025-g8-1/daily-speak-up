<template>
  <div>
    <Button 
      :label="$t('login.continue_google')" 
      icon="pi pi-google" 
      @click="handleGoogleLogin"
      :loading="loading"
      severity="contrast"
    />
  </div>
</template>

<script>
import { ref } from 'vue';
import { signInWithGoogle } from '../auth';
import Button from 'primevue/button';

export default {
  components: {
    Button
  },
  setup() {
    const loading = ref(false);

    const handleGoogleLogin = async () => {
      loading.value = true;
      try {
        await signInWithGoogle();
        // User will be redirected to Google, then back to our callback
      } catch (error) {
        console.error('Google login error:', error);
        loading.value = false;
      }
    };

    return {
      loading,
      handleGoogleLogin
    };
  }
};
</script>

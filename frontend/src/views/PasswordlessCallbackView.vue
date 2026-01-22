<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
      <div v-if="loading" class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <h2 class="text-xl font-semibold text-gray-800">Verifying your login...</h2>
        <p class="text-gray-600 mt-2">Please wait while we sign you in</p>
      </div>

      <div v-else-if="error" class="text-center">
        <div class="text-red-500 text-5xl mb-4">⚠️</div>
        <h2 class="text-xl font-semibold text-gray-800 mb-2">Verification Failed</h2>
        <p class="text-gray-600 mb-4">{{ error }}</p>
        <button 
          @click="goHome"
          class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Return to Home
        </button>
      </div>

      <div v-else class="text-center">
        <div class="text-green-500 text-5xl mb-4">✓</div>
        <h2 class="text-xl font-semibold text-gray-800 mb-2">Success!</h2>
        <p class="text-gray-600 mb-4">Redirecting you now...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Passwordless from 'supertokens-web-js/recipe/passwordless';;

const router = useRouter();
const loading = ref(true);
const error = ref('');

onMounted(async () => {
  try {
    const response = await Passwordless.consumeCode();
    
    if (response.status === 'OK') {
      if (response.createdNewRecipeUser) {
        try {
          const apiDomain = import.meta.env.VITE_API_DOMAIN || (window as any).ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
          
          // Get stored preferences from localStorage
          const storedLanguage = localStorage.getItem('app-language') || 'en';
          const storedTheme = localStorage.getItem('app-theme') || 'light';
          
          const registerResponse = await fetch(`${apiDomain}/api/v1/user/register`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: response.user.emails[0],
              preferred_lang: storedLanguage,
              preferred_theme: storedTheme
            })
          });
          
          if (registerResponse.ok) {
            console.log('✓ New user registered in database');
            // New user - redirect to onboarding
            setTimeout(() => {
              router.push('/onboarding');
            }, 1000);
            return;
          } else {
            console.error('Failed to register user');
          }
        } catch (regError) {
          console.error('Failed to register user:', regError);
        }
      }
      
      // Existing user - router guard will handle redirect based on onboarding status
      setTimeout(() => {
        router.push('/');
      }, 1000);
    } else if (response.status === 'RESTART_FLOW_ERROR') {
      error.value = 'The magic link has expired. Please request a new one.';
      loading.value = false;
    } else if (response.status === 'INCORRECT_USER_INPUT_CODE_ERROR') {
      error.value = 'Invalid magic link. Please try signing in again.';
      loading.value = false;
    } else {
      error.value = 'Sign in failed. Please try again.';
      loading.value = false;
    }
  } catch (err: any) {
    console.error('Magic link verification error:', err);
    // Handle stale session errors specifically
    if (err.message && (err.message.includes('session') || err.message.includes('unauthorized'))) {
      error.value = 'Your previous session was invalid. Please try logging in again.';
      // Redirect to home after a delay
      setTimeout(() => {
        router.push('/');
      }, 3000);
    } else {
      error.value = err.message || 'An error occurred during verification. Please try again.';
    }
    loading.value = false;
  }
});

const goHome = () => {
  router.push('/');
};
</script>

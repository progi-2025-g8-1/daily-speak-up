<template>
  <div class="flex flex-col items-center justify-center min-h-screen">
    <ProgressSpinner v-if="loading" style="width: 50px; height: 50px" strokeWidth="4" />
    <div v-if="loading" class="mt-4 text-lg">Completing sign in...</div>
    <Message v-if="error" severity="error" class="mt-4">{{ error }}</Message>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import ThirdParty from 'supertokens-web-js/recipe/thirdparty';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';

export default {
  components: {
    ProgressSpinner,
    Message
  },
  setup() {
    const router = useRouter();
    const loading = ref(true);
    const error = ref('');

    onMounted(async () => {
      try {
        const response = await ThirdParty.signInAndUp();
        
        if (response.status === 'OK') {
          // Successfully signed in with Google
          const user = response.user;
          const createdNewUser = response.createdNewRecipeUser;
          
          // Only register in our database if this is a newly created user
          if (createdNewUser) {
            try {
              const apiDomain = import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
              
              // Get stored preferences from localStorage
              const storedLanguage = localStorage.getItem('app-language') || 'en';
              const storedTheme = localStorage.getItem('app-theme') || 'light';
              
              const registerResponse = await fetch(`${apiDomain}/api/v1/user/register`, {
                method: 'PUT',
                credentials: 'include', // Include session cookies
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  email: user.emails[0], // Google provides email in the user object
                  preferred_lang: storedLanguage,
                  preferred_theme: storedTheme
                })
              });

              if (registerResponse.ok) {
                // User successfully registered in database, go to onboarding
                router.push('/onboarding');
              } else {
                const errorData = await registerResponse.json();
                error.value = errorData.detail || 'Failed to register user in database';
              }
            } catch (registerErr) {
              console.error('Registration error:', registerErr);
              error.value = 'Failed to complete registration. Please try again.';
            }
          } else {
            // Existing user, router guard will handle redirect based on onboarding status
            router.push('/');
          }
        } else if (response.status === 'NO_EMAIL_GIVEN_BY_PROVIDER') {
          error.value = 'Google did not provide an email. Please try again.';
        } else {
          error.value = 'Sign in failed. Please try again.';
        }
      } catch (err) {
        console.error('OAuth callback error:', err);
        // Handle stale session errors specifically
        if (err instanceof Error && (err.message.includes('session') || err.message.includes('unauthorized'))) {
          error.value = 'Your previous session was invalid. Please try logging in again.';
          // Redirect to home after a delay
          setTimeout(() => {
            router.push('/');
          }, 3000);
        } else {
          error.value = 'An error occurred during sign in. Please try again.';
        }
      } finally {
        loading.value = false;
      }
    });

    return {
      loading,
      error
    };
  }
};
</script>

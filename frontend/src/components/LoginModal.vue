<template>
  <div>
    <button 
      @click="showModal = true"
      class="px-6 py-2.5 text-white font-semibold rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
      style="background-color: var(--color-primary);">
      Log In
    </button>

    <Transition name="modal">
      <div 
        v-if="showModal" 
        class="fixed inset-0 flex items-center justify-center z-50 p-4"
        @click.self="closeModal"
      >
        <div class="rounded-2xl shadow-2xl w-full max-w-md relative" style="background-color: var(--color-bg-card);">
          <button 
            @click="closeModal"
            class="absolute top-4 right-4 transition-colors"
            style="color: var(--color-text-light);"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div class="text-center pt-8 pb-6 px-8" style="border-bottom: 1px solid var(--color-border-light);">
            <div class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style="background-color: var(--color-primary);">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold" style="color: var(--color-text-dark);">Welcome Back</h2>
            <p class="mt-2" style="color: var(--color-text-secondary);">Sign in to continue to DailySpeakUp</p>
          </div>

          <div class="p-8">
            <button
              @click="handleGoogleLogin"
              class="w-full flex items-center justify-center gap-3 px-4 py-3 border-2 rounded-lg transition-colors font-medium mb-4"
              style="background-color: var(--color-bg-card); border-color: var(--color-border-medium); color: var(--color-text-dark);"
            >
              <svg class="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </button>

            <div class="relative my-6">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full" style="border-top: 1px solid var(--color-border-light);"></div>
              </div>
              <div class="relative font-medium" style="background-color: var(--color-bg-card); color: var(--color-text-secondary);">
                <span class="px-4 font-medium" style="background-color: var(--color-bg-card); color: var(--color-text-secondary);">OR</span>
              </div>
            </div>

            <div v-if="!emailSent">
              <label class="block text-sm mb-2" style="color: var(--color-text-dark);">Email address</label>
              <input
                v-model="email"
                type="email"
                placeholder="you@example.com"
                class="w-full px-4 py-3 border rounded-lg transition-all outline-none"
                style="border-color: var(--color-border-light); background-color: var(--color-bg-main); color: var(--color-text-dark);"
                @keyup.enter="handleEmailLogin"
              />
              <button
                @click="handleEmailLogin"
                :disabled="!email || emailLoading"
                class="w-full mt-4 px-4 py-3 text-white font-semibold rounded-lg transition-colors flex items-center justify-center"
                style="background-color: var(--color-primary);"
              >
                <span v-if="emailLoading" class="flex items-center gap-2">
                  <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Sending...</span>
                </span>
                <span v-else>Send Magic Link</span>
              </button>
            </div>
rounded-lg" style="background-color: var(--color-bg-main); border: 1px solid var(--color-border-light);">
                <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-success);">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-sm font-medium" style="color: var(--color-success);">
                  Magic link sent!
                </p>
                <p class="text-sm mt-1" style="color: var(--color-text-secondary);">
                  Check your email at <strong>{{ email }}</strong>
                </p>
              </div>
              
              <p class="text-sm mb-4" style="color: var(--color-text-secondary);">
                Click the link in your email to sign in. You can close this window.
              </p>
              
              <button
                @click="closeModal"
                class="w-full px-4 py-2 font-medium rounded-lg transition-colors"
                style="background-color: var(--color-bg-main); color: var(--color-text-primary);
                @click="closeModal"
                class="w-full px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
              >
                Close
              </button>rounded-lg" style="background-color: var(--color-bg-main); border: 1px solid var(--color-error);">
              <p class="text-sm" style="color: var(--color-error);

            <div v-if="errorMessage" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-800">{{ errorMessage }}</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { signInWithGoogle, createPasswordlessCode } from '../auth';

const showModal = ref(false);
const email = ref('');
const emailSent = ref(false);
const emailLoading = ref(false);
const errorMessage = ref('');

const handleEscapeKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && showModal.value) {
    closeModal();
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey);
});

const closeModal = () => {
  showModal.value = false;
  resetForm();
};

const resetForm = () => {
  email.value = '';
  emailSent.value = false;
  errorMessage.value = '';
  emailLoading.value = false;
};

const handleGoogleLogin = async () => {
  try {
    await signInWithGoogle();
  } catch (error: any) {
    errorMessage.value = error.message || 'Failed to sign in with Google';
  }
};

const handleEmailLogin = async () => {
  if (!email.value) return;
  
  emailLoading.value = true;
  errorMessage.value = '';
  
  try {
    const response = await createPasswordlessCode(email.value);
    if (response.status === 'OK') {
      emailSent.value = true;
    } else {
      errorMessage.value = 'Failed to send magic link. Please try again.';
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Failed to send magic link';
  } finally {
    emailLoading.value = false;
  }
};
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

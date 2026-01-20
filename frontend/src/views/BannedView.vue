<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Logout from '../components/Logout.vue'

const reason = ref('');
const expiresAt = ref<string | null>(null);
const router = useRouter();

onMounted(async () => {
  const apiDomain = import.meta.env.VITE_API_DOMAIN || 'http://localhost:8123';
  const response = await fetch(`${apiDomain}/api/v1/user/amibanned`, {
    credentials: 'include'
  });
  
  if (response.ok) {
    const data = await response.json();
    if (!data.banned) {
      router.push('/home');
    } else {
      reason.value = data.reason;
      expiresAt.value = data.expires_at;
    }
  }
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-amber-50 flex items-center justify-center p-4">
    <!-- Main Card -->
    <div class="w-full max-w-lg">
      <div class="bg-white rounded-3xl shadow-2xl overflow-hidden">
        
        <!-- Icon Header -->
        <div class="bg-gradient-to-br from-red-500 to-rose-600 px-6 py-12 sm:py-16 flex flex-col items-center">
          <div class="w-20 h-20 sm:w-24 sm:h-24 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mb-4 sm:mb-6 animate-pulse">
            <svg class="w-10 h-10 sm:w-12 sm:h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold text-white text-center mb-2">
            {{ $t('banned.title') }}
          </h1>
          <p class="text-red-100 text-sm sm:text-base text-center">
            {{ $t('banned.subtitle') }}
          </p>
        </div>

        <!-- Content Section -->
        <div class="p-6 sm:p-8 space-y-6">
          
          <!-- Reason Card -->
          <div class="bg-gray-50 rounded-2xl p-5 border border-gray-100">
            <div class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg class="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <h2 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                  {{ $t('banned.reason_title') }}
                </h2>
                <p class="text-gray-800 text-sm sm:text-base leading-relaxed break-words">
                  {{ reason || $t('banned.reason_missing') }}
                </p>
              </div>
            </div>
          </div>


          <!-- Info Message -->
          <div class="bg-blue-50 border border-blue-100 rounded-2xl p-4 sm:p-5">
            <div class="flex gap-3">
              <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-blue-900 text-xs sm:text-sm leading-relaxed">
                {{ $t('banned.appeal_info') }}
              </p>
            </div>
          </div>

          <div>
            <Logout />
          </div>

          <!-- Footer Note -->
          <div class="text-center pt-2">
            <p class="text-xs text-gray-400">
              {{ $t('banned.privacy_info') }}
            </p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
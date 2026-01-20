<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api';
import Phase1 from '../components/Phase1.vue';
import Phase2 from '../components/Phase2.vue';
import ProgressSpinner from 'primevue/progressspinner';
import Card from 'primevue/card';

const router = useRouter();
const phase = ref<number | null>(null);
const loading = ref(true);

onMounted(async () => {
  try {
    const st = await api('/onboarding/state', { method: 'GET' });
    if (st.completed) return router.replace('/home');
    phase.value = st.phase;
  } catch (e) {
    console.warn('Onboarding state fetch failed; defaulting to phase 1:', e);
    // Backend might be offline; default to phase 1 so user can proceed
    phase.value = 1;
  } finally {
    loading.value = false;
  }
});

function onPhase1Done() { phase.value = 2; }
function onPhase2Done() { router.replace('/home'); }
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4 bg-main">
    <div v-if="!loading" class="w-full max-w-2xl">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold mb-2" style="color: var(--color-primary-dark);">{{ $t('onboarding.welcome') }}</h1>
        <p class="text-secondary">{{ $t('onboarding.subtitle') }}</p>
      </div>

      <!-- Progress Steps -->
      <div class="mb-8 flex items-center justify-center gap-4">
        <div class="flex items-center">
          <div 
            class="flex items-center justify-center w-10 h-10 rounded-full font-semibold transition-all duration-300"
            :class="phase! >= 1 ? 'bg-primary text-white shadow-lg' : 'bg-gray-200 text-gray-500'"
          >
            1
          </div>
          <span class="ml-2 font-medium" :class="phase! >= 1 ? 'text-primary' : 'text-gray-500'">{{ $t('onboarding.profile') }}</span>
        </div>
        
        <div class="w-16 h-1 rounded" :class="phase! >= 2 ? 'bg-primary' : 'bg-gray-300'"></div>
        
        <div class="flex items-center">
          <div 
            class="flex items-center justify-center w-10 h-10 rounded-full font-semibold transition-all duration-300"
            :class="phase! >= 2 ? 'bg-primary text-white shadow-lg' : 'bg-gray-200 text-gray-500'"
          >
            2
          </div>
          <span class="ml-2 font-medium" :class="phase! >= 2 ? 'text-primary' : 'text-gray-500'">{{ $t('onboarding.interests') }}</span>
        </div>
      </div>

      <!-- Content Card -->
      <Card class="shadow-xl">
        <template #content>
          <Phase1 v-if="phase === 1" @done="onPhase1Done" />
          <Phase2 v-else-if="phase === 2" @done="onPhase2Done" />
        </template>
      </Card>
    </div>
    
    <!-- Loading State -->
    <div v-else class="flex flex-col items-center justify-center gap-4">
      <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="4" />
      <p class="text-secondary text-lg">{{ $t('onboarding.loading') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const environment = computed(() => {
  const env = import.meta.env.VITE_ENVIRONMENT || 
               (window as any).ENV?.VITE_ENVIRONMENT || 
               import.meta.env.MODE || 
               'development';
  
  return env.toLowerCase();
});

const showIndicator = computed(() => {
  const env = environment.value;
  return env !== 'prod' && env !== 'production';
});

const indicatorConfig = computed(() => {
  const env = environment.value;
  
  if (env === 'development' || env === 'dev') {
    return {
      color: '#f59e0b', // warning yellow
      label: 'DEV',
      fullLabel: 'Development'
    };
  } else if (env === 'staging' || env === 'stage') {
    return {
      color: '#3b82f6', // primary blue
      label: 'STAGING',
      fullLabel: 'Staging'
    };
  } else if (env === 'test' || env === 'testing') {
    return {
      color: '#8b5cf6', // purple
      label: 'TEST',
      fullLabel: 'Testing'
    };
  } else {
    return {
      color: '#f97316', // orange
      label: env.toUpperCase(),
      fullLabel: env.charAt(0).toUpperCase() + env.slice(1)
    };
  }
});
</script>

<template>
  <div 
    v-if="showIndicator"
    class="fixed top-0 left-0 pointer-events-none"
    style="z-index: 9999;"
  >
    <div 
      :style="{
        'background-color': indicatorConfig.color,
        'border-bottom-right-radius': '0.5rem'
      }"
      class="px-3 py-1.5 text-white font-bold text-xs shadow-lg flex items-center gap-2"
      :title="`Environment: ${indicatorConfig.fullLabel}`"
    >
      <span class="inline-block w-2 h-2 bg-white rounded-full animate-pulse"></span>
      <span>{{ indicatorConfig.label }}</span>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>

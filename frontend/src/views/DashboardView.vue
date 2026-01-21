<script setup lang="ts">
   import { useRouter } from 'vue-router';
   import Button from 'primevue/button';
   import DashboardTabs from '../components/DashboardTabs.vue';

   const router = useRouter();
   const goBack = () => router.push('/home');
</script>

<template>
   <div class="flex flex-col items-center w-full h-[92vh] my-[2vh] mx-[2vw]">
      <div class="w-full flex items-center gap-4 mb-6">
         <Button icon="pi pi-arrow-left"
                 severity="secondary"
                 text
                 rounded
                 :aria-label="$t('profile.back')"
                 @click="goBack"
                 class="back-button" />
         <h2 class="text-3xl font-bold dashboard-title">{{ $t('dashboard.title') }}</h2>
      </div>
      <DashboardTabs />

   </div>
</template>

<style scoped>
.dashboard-title {
   color: var(--color-text-dark);
}

.back-button {
   transition: all 0.2s;
}

.back-button:hover {
   background-color: var(--color-bg-accent) !important;
}
</style>

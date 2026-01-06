<script setup lang="ts">
   import { useRouter } from 'vue-router';
   import Button from 'primevue/button';
   import DashboardTabs from '../components/DashboardTabs.vue';

   const router = useRouter();
   const goBack = () => router.push('/home');
</script>

<template>
   <div class="flex flex-col items-center w-[96] h-[92vh] my-[2vh] mx-[2vw]">
      <div class="w-full flex items-center justify-center relative gap-5 mb-4
                  border-2 border-gray-800 rounded-full">
         <Button icon="pi pi-arrow-left" 
                 severity="contrast" 
                 text 
                 rounded 
                 aria-label="Natrag"
                 variant="outlined"
                 @click="goBack" />
         <h2 class="text-2xl font-bold text-gray-800">Kontrolna ploča</h2>
      </div>
      <DashboardTabs />

   </div>
</template>

<style scoped>

</style>

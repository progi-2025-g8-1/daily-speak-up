<script setup lang="ts">
  import { ref } from 'vue';
  import ProfileHeader from './ProfileHeader.vue';  
  import Card from 'primevue/card';
</script>

<template>
  <div class="lg:w-[35vw]">
    <Card>
      <template #header>
        <div class="flex items-center gap-3 px-6 pt-6 pb-2">
          <h2 class="text-xl font-semibold text-dark">Profile view</h2>
        </div>
        <ProfileHeader />
      </template>
      
    </Card>
  </div>
</template>

<style scoped>

</style>
<script setup lang="ts">
  import CurrentUsersProfile from './CurrentUsersProfile.vue';
  
  const emits = defineEmits(['date-selected']);

  const handleDateSelected = (date: Date, hasSpeeches: boolean, videoInfo: any) => {
    if (hasSpeeches) {
      emits('date-selected', date, hasSpeeches, videoInfo);
    }
  };
</script>

<template>
  <div class="flex flex-col items-center lg:w-[40vw] lg:h-full">
    <CurrentUsersProfile @date-selected="handleDateSelected" />
  </div>
</template>

<style scoped>

</style>
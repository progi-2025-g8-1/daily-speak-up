<script setup>
    import SettingsDrawer from './SettingsDrawer.vue';
</script>

<template>

    <div class="flex flex-row justify-between items-center w-[95%] border border-gray-100
                mx-2 mt-[2vh] rounded-full p-[0.5vh] shadow-lg bg-blue-50">

        <div class="flex flex-row items-center justify-center ml-1">
            <img src="../assets/DSU_logo_circle.svg" alt="Daily Speak Up Logo" class="h-[4vh] mr-3"/>
            <div class="text-sky-500 font-semibold text-[2.5vh]">DailySpeakUp</div>
        </div>

        <div class="flex flex-row items-center gap-2 mr-1">
      <button
        @click="$router.push('/search')"
        class="icon-button"
        title="Search"
      >
        <i class="pi pi-search text-black text-lg"></i>
      </button>

      <SettingsDrawer />
    </div>
    </div>
    
</template>

<style scoped>
</style>
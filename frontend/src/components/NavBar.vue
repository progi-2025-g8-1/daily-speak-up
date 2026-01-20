<script setup>
    import SettingsDrawer from './SettingsDrawer.vue';
    import SearchIcon from './SearchIcon.vue'
</script>

<template>

    <div class="flex flex-row justify-between items-center w-[95%] mx-2 mt-[2vh] rounded-full p-[0.5vh] shadow-lg" style="border: 1px solid var(--color-border-light); background-color: var(--color-bg-accent);">

        <div class="flex flex-row items-center justify-center ml-1">
            <img src="../assets/DSU_logo_circle.svg" alt="Daily Speak Up Logo" class="h-[4vh] mr-3"/>
            <div class="font-semibold text-[2.5vh]" style="color: var(--color-primary);">DailySpeakUp</div>
        </div>

        <div class="flex flex-row items-center gap-2 mr-1">
            <SearchIcon />
            <SettingsDrawer />
        </div>
    </div>
    
</template>

<style scoped>
</style>
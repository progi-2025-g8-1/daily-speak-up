<script setup>
    import SettingsDrawer from './SettingsDrawer.vue';
    import SearchIcon from './SearchIcon.vue'
    import { RouterLink } from 'vue-router'
</script>

<template>

    <div class="flex flex-row justify-between items-center w-full mt-4 py-2 px-4 lg:px-4" style="border: 1px solid var(--color-border-light); background-color: var(--color-bg-card); box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08); border-radius: 1.25rem;">

        <RouterLink to="/" class="flex flex-row items-center justify-center">
            <img src="../assets/DSU_logo_circle.svg" alt="Daily Speak Up Logo" class="h-[4vh] mr-3"/>
            <div class="font-semibold text-[2.5vh]" style="color: var(--color-text-dark);">DailySpeakUp</div>
        </RouterLink>

        <div class="flex flex-row items-center gap-2">
            <SearchIcon />
            <SettingsDrawer />
        </div>
    </div>
    
</template>

<style scoped>
</style>
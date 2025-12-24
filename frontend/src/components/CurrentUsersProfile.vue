<script setup>
    import ProfileHeader from './ProfileHeader.vue';  
    import Card from 'primevue/card';
    import Calendar from './Calendar.vue';
</script>


<template>
    <div class="flex flex-col items-center w-[95%] h-full">
        <Card class="w-full mt-[2vh]">
            <template #content>
                <ProfileHeader />
            </template>
        </Card>

        <Calendar class="w-full mt-[2vh]"/>
    </div>
</template>


<style scoped>
</style>
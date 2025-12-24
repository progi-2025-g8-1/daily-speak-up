<script setup>
    import Drawer from 'primevue/drawer';
    import Button from 'primevue/button';
    import Login from './LoginModal.vue';
    import Logout from './Logout.vue';
    import User from './User.vue';
    import { RouterLink } from 'vue-router';

    import { ref } from 'vue';
    const visible = ref(false);

</script>

<template>
    <div class="flex justify-center">
        <Drawer v-model:visible="visible" header="Postavke računa" position="left" 
                :dismissable="false" class="!w-full lg:!w-[40vw]">
            <User />

            <div class="flex flex-col justify-start items-stretch">
                <Logout class="mt-10" />
            </div>
        </Drawer>
        <div class="flex flex-col justify-center items-center border-2 border-solid aspect-square
                    rounded-full border-blue w-10 mr-1 h-10 hover:scale-105 cursor-pointer transition duration-200"
            @click="visible = true">
            <span class="pi pi-cog" style="color:black; font-size: 1.2rem;"></span>
        </div>
    </div>
</template>

<style scoped>
    .yMargin {
        margin: 1.3rem 0;
    }

</style>

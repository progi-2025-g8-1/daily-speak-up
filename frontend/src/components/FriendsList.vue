<script setup>
    import { ref } from 'vue';
    import ScrollPanel from 'primevue/scrollpanel';

    const emits = defineEmits(['hide-friends']);

    const friendsList = ref([]);

    const handleBack = () => {
      emits('hide-friends');
    };

    const showFriends = (userId) => {
      visible.value = true;
      /*const response = fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/${userId}/friends`)
        .then(res => res.json())
        .then(data => {
          friendsList.value = data.friends;
        })
        .catch(err => {
          console.error('Failed to fetch friends list', err);
        });*/
    };

    defineExpose({
      showFriends
    });
</script>


<template>

    <div class="flex flex-col items-center w-[93%]">
        <div class="flex flex-row w-full justify-center items-center gap-4 mb-6 mt-[2vh]">
            <div class="flex flex-row items-center gap-10" >
                <span class="pi pi-chevron-circle-left cursor-pointer" style="font-size: 2.5vw;" v-on:click="handleBack"></span>
                <h2 class="font-semibold text-3xl">Popis prijatelja</h2>
            </div>
        </div>
        <div v-if="friendsList.length === 0" class="text-gray-500">Nemate prijatelje za prikaz.</div>
        <div v-else class="w-full">
            <ScrollPanel style="height: 70vh;" class="w-full">
                <div class="flex flex-col gap-4 p-4">
                    <div v-for="friend in friendsList" :key="friend.handle" class="flex flex-row items-center gap-4 p-2 border-b border-gray-200">
                        <img :src="friend.avatar_url" alt="Avatar" class="w-12 h-12 rounded-full object-cover" />
                        <div class="flex flex-col">
                            <span class="font-medium text-lg">{{ friend.name }}</span>
                            <span class="text-gray-500 text-sm">@{{ friend.handle }}</span>
                        </div>
                    </div>
                </div>
            </ScrollPanel>
        </div>
    </div>

</template>


<style scoped>

</style>
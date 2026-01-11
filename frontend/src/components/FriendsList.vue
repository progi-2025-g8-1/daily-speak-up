<script setup>
    import { ref } from 'vue';
    import Card from 'primevue/card';
    import ScrollPanel from 'primevue/scrollpanel';
    import ProgressSpinner from 'primevue/progressspinner';
    import Avatar from 'primevue/avatar';

    const emits = defineEmits(['hide-friends']);

    const friendsList = ref([]);
    const loading = ref(false);
    const error = ref('');

    const handleBack = () => {
        emits('hide-friends');
    };

    const showFriends = async (userId) => {
        loading.value = true;
        error.value = '';
        try {
            const apiDomain = import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
            const res = await fetch(`${apiDomain}/api/v1/user/${userId}/friends`, {
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            if (Array.isArray(data)) {
                friendsList.value = data;
            } else if (data && Array.isArray(data.friends)) {
                friendsList.value = data.friends;
            } else {
                friendsList.value = [];
            }
        } catch (err) {
            console.error('Failed to fetch friends list', err);
            error.value = 'Neuspjelo učitavanje popisa prijatelja.';
            friendsList.value = [];
        } finally {
            loading.value = false;
        }
    };

    defineExpose({
        showFriends
    });
</script>


<template>

    <div class="flex flex-col items-center w-[93%]">
        <Card class="w-full h-[8vh] mt-[2vh]">
            <template #content>
                <div class="flex justify-center items-center gap-4">
                    <span class="pi pi-chevron-circle-left cursor-pointer" style="font-size: 2.5vw;" v-on:click="handleBack"></span>
                    <h2 class="font-semibold text-3xl">Popis prijatelja</h2>
                </div>
            </template>
        </Card>
        <Card v-if="loading" class="w-full mt-[2vh]">
            <template #content>
                <ProgressSpinner style="width: 4rem; height: 4rem;" />
                <div class="mt-4 text-gray-500">Učitavanje prijatelja...</div>
            </template>
        </Card>
        <Card v-else-if="error" class="w-full mt-[2vh]">
            <template #content>
                <div class="text-red-600">{{ error }}</div>
            </template>
        </Card>
        <Card v-else-if="friendsList.length === 0" class="mt-[2vh]">
            <template #content>
                Nema prijatelja za prikazati.
            </template>
        </Card>
        <Card v-else class="w-full h-[86vh] mt-[2vh]">
            <template #content class="flex justify-center items-center">
                <ScrollPanel  class="w-full h-[82vh]">
                    <div class="flex flex-col gap-4 p-4">
                        <div v-for="friend in friendsList" :key="friend.handle" class="flex flex-row items-center gap-4 p-2 border-b border-gray-200">
                            <Avatar :image="friend.profile_picture_url" class="mr-2" size="xlarge" shape="circle" />
                            <div class="flex flex-col">
                                <span class="font-medium text-lg">{{ friend.name }}</span>
                                <span class="text-gray-500 text-sm">@{{ friend.handle }}</span>
                            </div>
                        </div>
                    </div>
                </ScrollPanel>
            </template>
        </Card>
    </div>

</template>


<style scoped>

</style>
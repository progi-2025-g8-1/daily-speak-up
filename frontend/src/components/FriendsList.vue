<script setup>
    import { ref } from 'vue';
    import Card from 'primevue/card';
    import ScrollPanel from 'primevue/scrollpanel';
    import ProgressSpinner from 'primevue/progressspinner';
    import Avatar from 'primevue/avatar';
    import Button from 'primevue/button';

    const emits = defineEmits(['hide-friends']);

    const friendsList = ref([]);
    const requestsList = ref([]);
    const loading = ref(false);
    const error = ref('');
    const viewMode = ref('friends'); // 'friends' or 'requests'
    const respondingId = ref(null);

    const handleBack = () => {
        emits('hide-friends');
    };

    const showFriends = async (userId) => {
        loading.value = true;
        error.value = '';
        viewMode.value = 'friends';
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

    const fetchRequests = async () => {
        loading.value = true;
        error.value = '';
        try {
            const apiDomain = import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
            const res = await fetch(`${apiDomain}/api/v1/friend/requests/incoming`, {
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            requestsList.value = Array.isArray(data) ? data : [];
        } catch (err) {
            console.error('Failed to fetch requests', err);
            error.value = 'Neuspjelo učitavanje zahtjeva.';
            requestsList.value = [];
        } finally {
            loading.value = false;
        }
    };

    const switchToRequests = async () => {
        viewMode.value = 'requests';
        await fetchRequests();
    };

    const respondToRequest = async (friendshipId, accept) => {
        respondingId.value = friendshipId;
        try {
            const apiDomain = import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
            const res = await fetch(`${apiDomain}/api/v1/friend/request/${friendshipId}/respond`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accept })
            });

            if (res.ok) {
                // Remove from list
                requestsList.value = requestsList.value.filter(r => r.friendship_id !== friendshipId);
            } else {
                error.value = accept ? 'Neuspjelo prihvaćanje zahtjeva.' : 'Neuspjelo odbijanje zahtjeva.';
            }
        } catch (err) {
            console.error('Failed to respond to request', err);
            error.value = accept ? 'Neuspjelo prihvaćanja zahtjeva.' : 'Neuspjelo odbijanja zahtjeva.';
        } finally {
            respondingId.value = null;
        }
    };

    defineExpose({
        showFriends,
        fetchRequests
    });
</script>


<template>

    <div class="flex flex-col items-center w-[93%]">
        <Card class="w-full mt-[2vh]">
            <template #content>
                <div class="relative py-4">
                    <span class="pi pi-chevron-circle-left cursor-pointer absolute left-2 top-1/2 -translate-y-1/2 z-10" style="font-size: 2.2rem;" @click="handleBack"></span>
                    <h2 class="font-semibold text-3xl text-center w-full">
                        {{ viewMode === 'friends' ? 'Popis prijatelja' : 'Zahtjevi za prijateljstvo' }}
                    </h2>
                </div>
            </template>
        </Card>

        <!-- Tabs/Toggle -->
        <Card class="w-full mt-[2vh]">
            <template #content>
                <div class="flex gap-2 justify-center">
                    <Button 
                        :label="`Prijatelji (${friendsList.length})`"
                        outlined
                        @click="viewMode = 'friends'"
                        :class="{ 'border-2': viewMode === 'friends' }"
                        style="color: #3b82f6; border-color: #3b82f6;"
                    />
                    <Button 
                        :label="`Zahtjevi (${requestsList.length})`"
                        outlined
                        @click="switchToRequests"
                        :class="{ 'border-2': viewMode === 'requests' }"
                        style="color: #3b82f6; border-color: #3b82f6;"
                    />
                </div>
            </template>
        </Card>

        <Card v-if="loading" class="w-full mt-[2vh]">
            <template #content>
                <ProgressSpinner style="width: 4rem; height: 4rem;" />
                <div class="mt-4 text-gray-500">Učitavanje...</div>
            </template>
        </Card>

        <Card v-else-if="error" class="w-full mt-[2vh]">
            <template #content>
                <div class="text-red-600">{{ error }}</div>
            </template>
        </Card>

        <!-- Friends View -->
        <template v-else-if="viewMode === 'friends'">
            <Card v-if="friendsList.length === 0" class="mt-[2vh]">
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
        </template>

        <!-- Requests View -->
        <template v-else-if="viewMode === 'requests'">
            <Card v-if="requestsList.length === 0" class="mt-[2vh]">
                <template #content>
                    Nema zahtjeva za prijateljstvo.
                </template>
            </Card>
            <Card v-else class="w-full h-[86vh] mt-[2vh]">
                <template #content class="flex justify-center items-center">
                    <ScrollPanel  class="w-full h-[82vh]">
                        <div class="flex flex-col gap-4 p-4">
                            <div v-for="request in requestsList" :key="request.friendship_id" class="flex flex-row items-center gap-4 p-2 border-b border-gray-200">
                                <Avatar :image="request.profile_picture_url" class="mr-2" size="xlarge" shape="circle" />
                                <div class="flex flex-col flex-1">
                                    <span class="font-medium text-lg">{{ request.handle }}</span>
                                    <span class="text-gray-500 text-sm">{{ new Date(request.created_at).toLocaleDateString() }}</span>
                                </div>
                                <div class="flex gap-2">
                                    <Button 
                                        label="Prihvati" 
                                        icon="pi pi-check"
                                        @click="respondToRequest(request.friendship_id, true)"
                                        :loading="respondingId === request.friendship_id"
                                        style="background-color: #3b82f6; border-color: #3b82f6;"
                                        class="p-button-sm"
                                    />
                                    <Button 
                                        label="Odbij" 
                                        icon="pi pi-times"
                                        @click="respondToRequest(request.friendship_id, false)"
                                        :loading="respondingId === request.friendship_id"
                                        outlined
                                        style="color: #3b82f6; border-color: #3b82f6;"
                                        class="p-button-sm"
                                    />
                                </div>
                            </div>
                        </div>
                    </ScrollPanel>
                </template>
            </Card>
        </template>
    </div>

</template>


<style scoped>

</style>
<script setup>
    import { ref } from 'vue';
    import { useRouter } from 'vue-router';
    import Card from 'primevue/card';
    import ScrollPanel from 'primevue/scrollpanel';
    import ProgressSpinner from 'primevue/progressspinner';
    import Avatar from 'primevue/avatar';
    import Button from 'primevue/button';

    const emits = defineEmits(['hide-friends']);
    const router = useRouter();

    const friendsList = ref([]);
    const requestsList = ref([]);
    const loading = ref(false);
    const error = ref('');
    const viewMode = ref('friends'); // 'friends' or 'requests'
    const respondingId = ref(null);
    const currentUserId = ref(null);

    const handleBack = () => {
        emits('hide-friends');
    };

    const goToProfile = (handle) => {
        if (handle) {
            emits('hide-friends');
            router.push(`/${handle}`);
        }
    };

    const showFriends = async (userId) => {
        loading.value = true;
        error.value = '';
        viewMode.value = 'friends';
        currentUserId.value = userId;
        try {
            const apiDomain = import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
            
            // Fetch friends and requests in parallel
            const [friendsRes, requestsRes] = await Promise.all([
                fetch(`${apiDomain}/api/v1/user/${userId}/friends`, {
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' }
                }),
                fetch(`${apiDomain}/api/v1/friend/requests/incoming`, {
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' }
                })
            ]);

            if (!friendsRes.ok) throw new Error(`Friends HTTP ${friendsRes.status}`);

            const friendsData = await friendsRes.json();

            if (Array.isArray(friendsData)) {
                friendsList.value = friendsData;
            } else if (friendsData && Array.isArray(friendsData.friends)) {
                friendsList.value = friendsData.friends;
            } else {
                friendsList.value = [];
            }

            // Fetch requests data
            if (requestsRes.ok) {
                const requestsData = await requestsRes.json();
                requestsList.value = Array.isArray(requestsData) ? requestsData : [];
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
                
                // If accepted, refetch friends list to include the new friend
                if (accept && currentUserId.value) {
                    try {
                        const friendsRes = await fetch(`${apiDomain}/api/v1/user/${currentUserId.value}/friends`, {
                            credentials: 'include',
                            headers: { 'Content-Type': 'application/json' }
                        });
                        if (friendsRes.ok) {
                            const friendsData = await friendsRes.json();
                            if (Array.isArray(friendsData)) {
                                friendsList.value = friendsData;
                            } else if (friendsData && Array.isArray(friendsData.friends)) {
                                friendsList.value = friendsData.friends;
                            }
                        }
                    } catch (err) {
                        console.error('Failed to refetch friends list', err);
                    }
                }
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

    <div class="flex flex-col items-center w-full px-0">
        <Card class="w-full mt-0">
            <template #content>
                <div class="relative py-4">
                    <span class="pi pi-chevron-circle-left cursor-pointer absolute left-0 top-1/2 -translate-y-1/2 z-10" style="font-size: 2.2rem;" @click="handleBack"></span>
                    <h2 class="font-semibold text-xl w-full text-center">
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
            <Card v-else class="w-full min-h-[500px] mt-[2vh]">
                <template #content>
                    <div class="flex flex-col gap-4 p-4">
                            <div 
                                v-for="friend in friendsList" 
                                :key="friend.handle" 
                                class="flex flex-row items-center gap-4 p-2 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors"
                                @click="goToProfile(friend.handle)"
                            >
                                <Avatar 
                                    :image="friend.profile_picture_url" 
                                    :label="!friend.profile_picture_url ? (friend.handle?.[0]?.toUpperCase() || 'U') : undefined"
                                    class="mr-2 bg-sky-400 text-white" 
                                    size="xlarge" 
                                    shape="circle" 
                                />
                                <div class="flex flex-col">
                                    <span class="font-medium text-lg">{{ friend.handle }}</span>
                                </div>
                            </div>
                        </div>
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
            <Card v-else class="w-full min-h-[500px] mt-[2vh]">
                <template #content>
                    <div class="flex flex-col gap-4 p-4">
                            <div 
                                v-for="request in requestsList" 
                                :key="request.friendship_id" 
                                class="flex flex-row items-center gap-4 p-2 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors"
                                @click="goToProfile(request.handle)"
                            >
                                <Avatar 
                                    :image="request.profile_picture_url" 
                                    :label="!request.profile_picture_url ? (request.handle?.[0]?.toUpperCase() || 'U') : undefined"
                                    class="mr-2 bg-sky-400 text-white" 
                                    size="xlarge" 
                                    shape="circle" 
                                />
                                <div class="flex flex-col flex-1">
                                    <span class="font-medium text-lg">{{ request.handle }}</span>
                                    <span class="text-gray-500 text-sm">{{ new Date(request.created_at).toLocaleDateString() }}</span>
                                </div>
                                <div class="flex gap-2" @click.stop>
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
                </template>
            </Card>
        </template>
    </div>

</template>


<style scoped>

</style>
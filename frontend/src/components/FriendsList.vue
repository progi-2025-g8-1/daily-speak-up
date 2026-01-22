<script setup>
    import { ref } from 'vue';
    import { useRouter } from 'vue-router';
    import ProgressSpinner from 'primevue/progressspinner';
    import Avatar from 'primevue/avatar';
    import Button from 'primevue/button';
    import { useI18n } from 'vue-i18n';

    const { t } = useI18n();

    const props = defineProps({
        isOwnProfile: {
            type: Boolean,
            default: false
        }
    });

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
            
            // Fetch friends and requests in parallel if own profile
            const promises = [
                fetch(`${apiDomain}/api/v1/user/${userId}/friends`, {
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' }
                })
            ];

            if (props.isOwnProfile) {
                promises.push(
                    fetch(`${apiDomain}/api/v1/friend/requests/incoming`, {
                        credentials: 'include',
                        headers: { 'Content-Type': 'application/json' }
                    })
                );
            }

            const results = await Promise.all(promises);
            const friendsRes = results[0];
            const requestsRes = props.isOwnProfile ? results[1] : null;

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
            if (requestsRes && requestsRes.ok) {
                const requestsData = await requestsRes.json();
                requestsList.value = Array.isArray(requestsData) ? requestsData : [];
            }
        } catch (err) {
            console.error('Failed to fetch friends list', err);
            error.value = t('friends.error_loading');
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
            error.value = t('friends.error_loading');
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
                error.value = t('friends.error_loading');
            }
        } catch (err) {
            console.error('Failed to respond to request', err);
            error.value = t('friends.error_loading');
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
    <div class="friends-container">
        <!-- Header -->
        <div class="friends-header">
            <Button
                icon="pi pi-arrow-left"
                text
                rounded
                class="back-button"
                @click="handleBack"
                :aria-label="$t('profile.back')"
            />
            <h2 class="friends-title">{{ $t('friends.title') }}</h2>
        </div>

        <!-- Tabs for own profile -->
        <div v-if="props.isOwnProfile" class="tabs-container">
            <button
                class="tab-button"
                :class="{ active: viewMode === 'friends' }"
                @click="viewMode = 'friends'"
            >
                <span class="pi pi-users tab-icon"></span>
                {{ $t('friends.tabs.friends') }} ({{ friendsList.length }})
            </button>
            <button
                class="tab-button"
                :class="{ active: viewMode === 'requests' }"
                @click="switchToRequests"
            >
                <span class="pi pi-bell tab-icon"></span>
                {{ $t('friends.tabs.requests') }} ({{ requestsList.length }})
            </button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="state-container">
            <ProgressSpinner style="width: 3rem; height: 3rem;" />
            <div class="state-text">{{ $t('friends.loading') }}</div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="state-container">
            <i class="pi pi-exclamation-circle error-icon"></i>
            <div class="state-text">{{ error }}</div>
        </div>

        <!-- Friends List -->
        <div v-else-if="viewMode === 'friends'" class="content-area">
            <div v-if="friendsList.length === 0" class="empty-state">
                <i class="pi pi-users empty-icon"></i>
                <p class="empty-text">{{ $t('friends.no_friends') }}</p>
            </div>
            <div v-else class="friends-list">
                <div
                    v-for="friend in friendsList"
                    :key="friend.handle"
                    class="friend-item"
                    @click="goToProfile(friend.handle)"
                >
                    <Avatar
                        :image="friend.profile_picture_url"
                        :label="!friend.profile_picture_url ? (friend.handle?.[0]?.toUpperCase() || 'U') : undefined"
                        class="friend-avatar"
                        size="large"
                        shape="circle"
                    />
                    <div class="friend-info">
                        <span class="friend-handle">@{{ friend.handle }}</span>
                    </div>
                    <i class="pi pi-chevron-right chevron-icon"></i>
                </div>
            </div>
        </div>

        <!-- Requests List -->
        <div v-else-if="viewMode === 'requests'" class="content-area">
            <div v-if="requestsList.length === 0" class="empty-state">
                <i class="pi pi-bell empty-icon"></i>
                <p class="empty-text">{{ $t('friends.no_requests') }}</p>
            </div>
            <div v-else class="friends-list">
                <div
                    v-for="request in requestsList"
                    :key="request.friendship_id"
                    class="request-item"
                >
                    <div class="request-user" @click="goToProfile(request.handle)">
                        <Avatar
                            :image="request.profile_picture_url"
                            :label="!request.profile_picture_url ? (request.handle?.[0]?.toUpperCase() || 'U') : undefined"
                            class="friend-avatar"
                            size="large"
                            shape="circle"
                        />
                        <div class="friend-info">
                            <span class="friend-handle">@{{ request.handle }}</span>
                            <span class="request-date">{{ new Date(request.created_at).toLocaleDateString() }}</span>
                        </div>
                    </div>
                    <div class="request-actions">
                        <Button
                            icon="pi pi-check"
                            rounded
                            @click="respondToRequest(request.friendship_id, true)"
                            :loading="respondingId === request.friendship_id"
                            class="accept-button"
                            :aria-label="$t('friends.accept')"
                        />
                        <Button
                            icon="pi pi-times"
                            rounded
                            outlined
                            @click="respondToRequest(request.friendship_id, false)"
                            :loading="respondingId === request.friendship_id"
                            class="reject-button"
                            :aria-label="$t('friends.reject')"
                        />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.friends-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.friends-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.5rem 0;
}

.back-button {
    color: var(--color-text-secondary);
    transition: all 0.2s;
}

.back-button:hover {
    background-color: var(--color-bg-accent) !important;
    transform: translateX(-2px);
}

.friends-title {
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--color-text-dark);
    margin: 0;
}

.tabs-container {
    display: flex;
    gap: 0.5rem;
    padding: 0.25rem;
    background-color: var(--color-bg-accent);
    border-radius: 0.75rem;
}

.tab-button {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border: none;
    background: transparent;
    color: var(--color-text-secondary);
    font-size: 0.95rem;
    font-weight: 500;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
}

.tab-button:hover {
    background-color: var(--color-bg-card);
}

.tab-button.active {
    background-color: var(--color-bg-card);
    color: var(--color-primary);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tab-icon {
    font-size: 1rem;
}

.state-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 1rem;
    gap: 1rem;
}

.state-text {
    color: var(--color-text-secondary);
    font-size: 1rem;
}

.error-icon {
    font-size: 3rem;
    color: var(--color-error);
}

.content-area {
    min-height: 400px;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    gap: 1rem;
}

.empty-icon {
    font-size: 4rem;
    color: var(--color-text-muted);
    opacity: 0.5;
}

.empty-text {
    color: var(--color-text-secondary);
    font-size: 1.1rem;
    margin: 0;
}

.friends-list {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.friend-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid var(--color-border-light);
    cursor: pointer;
    transition: all 0.2s;
}

.friend-item:hover {
    background-color: var(--color-bg-accent);
}

.friend-item:last-child {
    border-bottom: none;
}

.friend-avatar {
    background-color: var(--color-primary);
    color: white;
    flex-shrink: 0;
}

.friend-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.friend-handle {
    font-weight: 600;
    font-size: 1rem;
    color: var(--color-text-dark);
}

.request-date {
    font-size: 0.875rem;
    color: var(--color-text-muted);
}

.chevron-icon {
    color: var(--color-text-muted);
    font-size: 1rem;
}

.request-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid var(--color-border-light);
}

.request-item:last-child {
    border-bottom: none;
}

.request-user {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex: 1;
    cursor: pointer;
    transition: all 0.2s;
    padding: 0.5rem;
    margin: -0.5rem;
    border-radius: 0.5rem;
}

.request-user:hover {
    background-color: var(--color-bg-accent);
}

.request-actions {
    display: flex;
    gap: 0.5rem;
    flex-shrink: 0;
}

.accept-button {
    background-color: var(--color-success) !important;
    border-color: var(--color-success) !important;
}

.accept-button:hover {
    background-color: #059669 !important;
}

.reject-button {
    color: var(--color-error) !important;
    border-color: var(--color-error) !important;
}

.reject-button:hover {
    background-color: rgba(239, 68, 68, 0.1) !important;
}
</style>
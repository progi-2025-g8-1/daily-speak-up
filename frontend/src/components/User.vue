<template>
  <div class="flex items-center gap-3">
    <ProgressSpinner v-if="loading" style="width: 30px; height: 30px" strokeWidth="4" />
    
    <div 
      v-else-if="user" 
      class="flex items-center gap-3 cursor-pointer hover:bg-gray-100 p-2 rounded-lg transition-colors"
      @click="goToProfile"
    >
      <Avatar :label="user.handle?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase()" 
              shape="circle" 
              size="large" 
              class="bg-sky-500 text-white" />
      <div class="flex flex-col">
        <span class="font-semibold">{{ user.handle || user.email }}</span>
        <span class="text-sm text-gray-500">{{ user.email }}</span>
      </div>
    </div>
    
    <Message v-else-if="error" severity="error" :closable="false" class="m-0">{{ error }}</Message>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getUserId, isAuthenticated } from '../auth';
import Avatar from 'primevue/avatar';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';

export default {
  components: {
    Avatar,
    ProgressSpinner,
    Message
  },
  setup() {
    const router = useRouter();
    const user = ref(null);
    const userId = ref('');
    const loading = ref(true);
    const error = ref('');

    const goToProfile = () => {
      if (user.value) {
        const handle = user.value.handle || user.value.email;
        router.push(`/${handle}`);
      }
    };

    onMounted(async () => {
      try {
        const authenticated = await isAuthenticated();
        if (!authenticated) {
          error.value = 'Not authenticated';
          loading.value = false;
          return;
        }

        userId.value = await getUserId();

        // Fetch user data from backend API
        const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/me`, {
          method: 'GET',
          credentials: 'include', // Important: Include cookies for SuperTokens session
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          user.value = await response.json();
        } else {
          error.value = 'Failed to fetch user data';
        }
      } catch (e) {
        error.value = 'An error occurred while fetching user data';
        console.error('User fetch error:', e);
      } finally {
        loading.value = false;
      }
    });

    return {
      user,
      userId,
      loading,
      error,
      goToProfile
    };
  },
};
</script>
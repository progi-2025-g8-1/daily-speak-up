<template>
    <div class="flex items-center gap-6">
      <ProgressSpinner v-if="loading" style="width: 50px; height: 50px" strokeWidth="4" />
      
      <div v-else-if="user" class="flex items-start gap-6 w-full">
        <Avatar 
          :label="user.handle?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase()" 
          shape="circle" 
          class="bg-sky-400 text-white"
          style="width: 100px; height: 100px; font-size: 3rem;"
        />
  
        <div class="flex flex-col">
          <h2 class="text-2xl font-semibold text-dark m-0 mb-1">
            {{ user.handle || user.email }}
          </h2>
          
          <h3 class="text-sm text-gray-500 m-0 mb-3">
            {{ user.email }}
          </h3>
  
          <div class="flex gap-6">
            <div class="flex flex-col items-center">
              <span class="text-2xl font-bold text-dark">{{ user.streak || 0 }}</span>
              <span class="text-xs text-gray-600">streak</span>
            </div>
            <div class="flex flex-col items-center">
              <span class="text-2xl font-bold text-dark">{{ user.friends_count || 0 }}</span>
              <span class="text-xs text-gray-600">followers</span>
            </div>
          </div>
        </div>
      </div>
      
      <Message v-else-if="error" severity="error" :closable="false" class="m-0">
        {{ error }}
      </Message>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
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
      const user = ref(null);
      const userId = ref('');
      const loading = ref(true);
      const error = ref('');
  
      onMounted(async () => {
        try {
          const authenticated = await isAuthenticated();
          if (!authenticated) {
            error.value = 'Not authenticated';
            loading.value = false;
            return;
          }
  
          userId.value = await getUserId();
  
          const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/me`, {
            method: 'GET',
            credentials: 'include',
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
        error
      };
    },
  };
  </script>
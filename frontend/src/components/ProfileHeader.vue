<template>
    <div class="flex items-center gap-6">
      <ProgressSpinner v-if="loading" style="width: 50px; height: 50px" strokeWidth="4" />
      
      <div v-else-if="user" class="flex flex-row justify-around w-full">
        <Avatar 
          :label="user.handle?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase()" 
          shape="circle" 
          style="width: 100px; height: 100px; font-size: 3rem; background-color: var(--color-primary); color: white;"
        />
  
        <div class="flex flex-col items-start">
          <h2 class="text-2xl font-semibold m-0 mb-1" style="color: var(--color-text-dark);">
            {{ user.handle || user.email }}
          </h2>
          
          <h3 class="text-sm m-0 mb-3" style="color: var(--color-text-secondary);">
            {{ user.email }}
          </h3>
  
          <div class="flex gap-10">
            <div class="flex flex-col items-start">
              <div class="flex flex-row items-center gap-2">
                <span class="text-2xl font-bold" style="color: var(--color-text-dark);">{{ user.streak || 0 }}</span>
                <span class="pi pi-sparkles font-xl"></span>
              </div>
              <span class="text-xs" style="color: var(--color-text-light);">streak</span>
            </div>
            <div class="flex flex-col items-start">
              <div class="flex flex-row items-center gap-2" v-on:click="handleShowFriends">
                <span class="text-2xl font-bold" style="color: var(--color-text-dark);">{{ user.friends_count || 0 }}</span>
                <span class="pi pi-users font-xl"></span>
              </div>
              <span class="text-xs" style="color: var(--color-text-light);">prijatelji</span>
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
    setup(props, { emit }) {
      const user = ref(null);
      const userId = ref('');
      const loading = ref(true);
      const error = ref('');

      const handleShowFriends = () => {
        emit('show-friends', userId.value);
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
        error,
        handleShowFriends
      };
    },
  };
  </script>
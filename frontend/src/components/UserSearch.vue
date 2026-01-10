<template>
    <div class="w-full space-y-4">
      <div class="relative">
        <IconField iconPosition="left">
          <InputIcon>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
          </InputIcon>
          <InputText 
            v-model="searchQuery" 
            placeholder="Pretražite korisnike pomoću handlea ili emaila..."
            class="w-full"
            @input="handleSearch"
          />
        </IconField>
      </div>
  
      <div v-if="searching" class="flex justify-center py-8">
        <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="4" />
      </div>
  
      <div v-else-if="searchResults.length > 0" class="space-y-2">
        <div 
          v-for="user in searchResults" 
          :key="user.user_id"
          class="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-all cursor-pointer hover:bg-gray-50"
          @click="navigateToProfile(user.handle)"
        >
          <Avatar 
            :label="user.handle?.[0]?.toUpperCase()" 
            shape="circle" 
            class="bg-sky-400 text-white"
            :image="user.profile_picture_url"
            size="large"
          />
          <div>
            <p class="font-semibold text-dark">{{ user.handle }}</p>
          </div>
        </div>
      </div>
  
      <!-- No Results -->
      <div v-else-if="searchQuery && !searching" class="text-center py-8">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <p class="text-gray-500">Nijedan korisnik nije pronađen</p>
      </div>
  
      <div v-else class="text-center py-8">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="text-gray-500">Pretražite korisnike s kojima se možete povezati</p>
      </div>
  
      <!-- Error Message -->
      <Message v-if="error" severity="error" :closable="true" @close="error = ''">
        {{ error }}
      </Message>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import Avatar from 'primevue/avatar';
  import InputText from 'primevue/inputtext';
  import IconField from 'primevue/iconfield';
  import InputIcon from 'primevue/inputicon';
  import ProgressSpinner from 'primevue/progressspinner';
  import Message from 'primevue/message';
  
  const router = useRouter();
  const searchQuery = ref('');
  const searchResults = ref([]);
  const searching = ref(false);
  const error = ref('');
  let searchTimeout = null;
  
  const handleSearch = () => {
    // Debounce search
    clearTimeout(searchTimeout);
    
    if (!searchQuery.value || searchQuery.value.length < 2) {
      searchResults.value = [];
      return;
    }
    
    searchTimeout = setTimeout(async () => {
      await performSearch();
    }, 500);
  };
  
  const performSearch = async () => {
    searching.value = true;
    error.value = '';
    
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/search/users?query=${encodeURIComponent(searchQuery.value)}&limit=20`,
        {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
  
      if (response.ok) {
        searchResults.value = await response.json();
      } else {
        error.value = 'Failed to search users';
      }
    } catch (e) {
      error.value = 'Došlo je do pogreške tijekom pretraživanja';
      console.error('Search error:', e);
    } finally {
      searching.value = false;
    }
  };
  
  const navigateToProfile = (handle) => {
    router.push(`/${handle}`);
  };
  </script>
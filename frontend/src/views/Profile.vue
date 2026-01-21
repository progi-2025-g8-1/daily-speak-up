<template>
  <div class="min-h-screen bg-main overflow-x-hidden">

    <NavBar />
    
    <div class="max-w-2xl mx-auto w-full" id="i1">
      
      <Card class="shadow-lg mt-4 w-full">
        <template #header>
          <div class="px-6 pt-4 pb-0">
            <div class="flex items-center justify-between mb-0">
              <router-link 
                to="/home" 
                class="inline-flex items-center gap-2 px-3 py-1.5 font-medium transition-colors duration-200"
                style="background-color: white; color: #3b82f6;"
                @mouseenter="$event.target.style.backgroundColor = '#f3f4f6'"
                @mouseleave="$event.target.style.backgroundColor = 'white'"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
                </svg>
                {{ $t('profile.back') }}
              </router-link>
              <h2 class="text-xl font-semibold text-dark">{{ $t('onboarding.profile') }}</h2>
            </div>
          </div>
        </template>
        
        <template #content>
          <div class="w-full">
            <div v-if="showFriendsPanel">
              <FriendsList ref="friendsListRef" :is-own-profile="isOwnProfile" @hide-friends="hideFriends" />
            </div>
            <div v-else>
              <CurrentUsersProfile v-if="isOwnProfile" @show-friends="handleShowFriends" @date-selected="handleDateSelected" />
              <OtherUsersProfile v-else @show-friends="handleShowFriends" @date-selected="handleDateSelected" />
            </div>
          </div>
        </template>
      </Card>
    </div>
    
    <PlaySpeechFrame ref="playSpeechFrame" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import NavBar from '../components/NavBar.vue';
import CurrentUsersProfile from '../components/CurrentUsersProfile.vue';
import OtherUsersProfile from '../components/OtherUsersProfile.vue';
import FriendsList from '../components/FriendsList.vue';
import PlaySpeechFrame from '../components/PlaySpeechFrame.vue';
import Card from 'primevue/card';
import { isAuthenticated } from '../auth';

const route = useRoute();
const isOwnProfile = ref(false);
const showFriendsPanel = ref(false);
const friendsListRef = ref(null);
const playSpeechFrame = ref(null);

const handleShowFriends = async (userId) => {
  showFriendsPanel.value = true;
  await nextTick();
  if (friendsListRef.value && typeof friendsListRef.value.showFriends === 'function') {
    friendsListRef.value.showFriends(userId);
  }
};

const hideFriends = () => {
  showFriendsPanel.value = false;
};

const handleDateSelected = (date, hasSpeeches, videoInfo) => {
  if (playSpeechFrame.value && hasSpeeches) {
    playSpeechFrame.value.displaySpeechDialog(date, hasSpeeches, videoInfo);
  }
};

const checkIfOwnProfile = async () => {
  try {
    const authenticated = await isAuthenticated();
    if (!authenticated) {
      isOwnProfile.value = false;
      return;
    }

    const handle = route.params.handle;

    // Fetch current user's data
    const response = await fetch(
      `${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/me`,
      {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.ok) {
      const userData = await response.json();
      // Check if route handle matches current user's handle
      isOwnProfile.value = userData.handle === handle;
    } else {
      isOwnProfile.value = false;
    }
  } catch (e) {
    console.error('Error checking profile ownership:', e);
    isOwnProfile.value = false;
  }
};

// Check on mount
onMounted(async () => {
  await checkIfOwnProfile();
});

// Watch for route changes (if user navigates to different profile)
watch(() => route.params.handle, async () => {
  showFriendsPanel.value = false;
  await checkIfOwnProfile();
});
</script>

<style>
  #i1{
      display:flex;
      align-items:baseline;
      justify-content: center;
      padding: 0 1rem;
  }
  @media (max-width: 600px) {
      #i1{
          flex-wrap: wrap;
          gap: 1rem;
          padding: 0 0.5rem;
      }
  }

  /* Make calendar responsive */
  #i1 :deep(.p-datepicker) {
    width: 100% !important;
    max-width: 100% !important;
  }

  #i1 :deep(.p-datepicker-calendar-container) {
    width: 100% !important;
  }

  #i1 :deep(.p-datepicker table) {
    width: 100% !important;
    font-size: 0.875rem;
  }

  /* Mobile adjustments */
  @media (max-width: 640px) {
    #i1 :deep(.p-datepicker) {
      font-size: 0.75rem;
    }

    #i1 :deep(.p-datepicker table td) {
      padding: 0.25rem;
    }

    #i1 :deep(.p-datepicker table th) {
      padding: 0.25rem;
      font-size: 0.75rem;
    }

    #i1 :deep(.p-datepicker-header) {
      padding: 0.5rem;
    }

    #i1 :deep(.p-datepicker-title) {
      font-size: 0.875rem;
    }
  }

  /* Extra small screens */
  @media (max-width: 400px) {
    #i1 :deep(.p-datepicker table) {
      font-size: 0.7rem;
    }

    #i1 :deep(.p-datepicker table td),
    #i1 :deep(.p-datepicker table th) {
      padding: 0.15rem;
    }
  }

  /* Reduce padding in Profile card content */
  #i1 :deep(.p-card-content) {
    padding-top: 0 !important;
  }
</style>
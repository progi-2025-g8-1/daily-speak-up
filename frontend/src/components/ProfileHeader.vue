<template>
  <div class="flex flex-col gap-4">
    <ProgressSpinner v-if="loading" style="width: 50px; height: 50px" strokeWidth="4" />
    
    <div v-else-if="displayUser" class="flex flex-col gap-4">
      <!-- User Info Section -->
      <div class="flex flex-row justify-around w-full">
        <Avatar 
          :image="displayUser.profile_picture_url"
          :label="!displayUser.profile_picture_url ? (displayUser.handle?.[0]?.toUpperCase() || displayUser.email?.[0]?.toUpperCase()) : undefined"
          shape="circle" 
          class="bg-sky-400 text-white"
          style="width: 100px; height: 100px; font-size: 3rem;"
        />

        <div class="flex flex-col items-start">
          <h2 class="text-2xl font-semibold text-dark m-0 mb-1">
            {{ displayUser.handle || displayUser.email }}
          </h2>
          
          <h3 v-if="!isOtherUser" class="text-sm text-gray-500 m-0 mb-3">
            {{ displayUser.email }}
          </h3>

          <div class="flex gap-10">
            <div class="flex flex-col items-start">
              <div class="flex flex-row items-center gap-2">
                <span class="text-2xl font-bold text-dark">{{ displayUser.streak || displayUser.current_streak || 0 }}</span>
                <span class="pi pi-sparkles font-xl"></span>
              </div>
              <span class="text-xs text-gray-600">streak</span>
            </div>
            <div class="flex flex-col items-start">
              <div 
                class="flex flex-row items-center gap-2"
                :class="{ 'cursor-pointer hover:opacity-70': canViewFriends }"
                @click="canViewFriends ? handleShowFriends() : null"
              >
                <span class="text-2xl font-bold text-dark">{{ displayUser.friends_count || displayUser.friend_count || 0 }}</span>
                <span class="pi pi-users font-xl"></span>
              </div>
              <span class="text-xs text-gray-600">prijatelji</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Interests Section -->
      <div v-if="shouldShowInterests" class="w-full">
        <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <i class="pi pi-heart"></i>
          Interesi
        </h3>
        <div v-if="interests.length > 0" class="flex flex-wrap gap-2">
          <Chip 
            v-for="interest in interests" 
            :key="interest"
            :label="interest"
            class="interest-chip"
          />
        </div>
        <p v-else class="text-sm text-gray-500 italic">
          Nema dodanih interesa
        </p>
      </div>
    </div>
    
    <Message v-else-if="error" severity="error" :closable="false" class="m-0">
      {{ error }}
    </Message>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { getUserId, isAuthenticated } from '../auth';
import Avatar from 'primevue/avatar';
import Chip from 'primevue/chip';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';

export default {
  components: {
    Avatar,
    Chip,
    ProgressSpinner,
    Message
  },
  props: {
    otherUserData: {
      type: Object,
      default: null
    },
    isOtherUser: {
      type: Boolean,
      default: false
    },
    friendshipStatus: {
      type: String,
      default: null
    }
  },
  setup(props, { emit }) {
    const user = ref(null);
    const userId = ref('');
    const loading = ref(true);
    const error = ref('');
    const interests = ref([]);

    const displayUser = computed(() => {
      return props.otherUserData || user.value;
    });

    const canViewFriends = computed(() => {
      return !props.isOtherUser || props.friendshipStatus === 'accepted';
    });

    // Show interests if:
    // 1. Own profile (always)
    // 2. Other user profile AND friends
    const shouldShowInterests = computed(() => {
      if (!props.isOtherUser) {
        return true; // Own profile
      }
      return props.friendshipStatus === 'accepted'; // Friends only
    });

    const handleShowFriends = () => {
      if (!canViewFriends.value) return;
      
      const idToEmit = props.isOtherUser 
        ? props.otherUserData?.id 
        : userId.value;
      emit('show-friends', idToEmit);
    };

    onMounted(async () => {
      if (props.isOtherUser) {
        // For other users, interests come from otherUserData
        interests.value = props.otherUserData?.interests || [];
        loading.value = false;
        return;
      }

      try {
        const authenticated = await isAuthenticated();
        if (!authenticated) {
          error.value = 'Not authenticated';
          loading.value = false;
          return;
        }

        userId.value = await getUserId();

        const apiDomain = import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123';

        // Fetch user data and interests in parallel
        const [userResponse, interestsResponse] = await Promise.all([
          fetch(`${apiDomain}/api/v1/user/me`, {
            method: 'GET',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            },
          }),
          fetch(`${apiDomain}/api/v1/user/interests`, {
            method: 'GET',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            },
          })
        ]);

        if (userResponse.ok) {
          user.value = await userResponse.json();
          localStorage.setItem('userRole', user.value.role);
          emit('user-role', user.value.role);
        } else {
          error.value = 'Failed to fetch user data';
        }

        if (interestsResponse.ok) {
          const interestsData = await interestsResponse.json();
          interests.value = interestsData.interests || [];
        }

      } catch (e) {
          error.value = 'An error occurred while fetching user data';
          console.error('User fetch error:', e);
        } finally {
          loading.value = false;
        }
    });

    return {
      displayUser,
      userId,
      loading,
      error,
      interests,
      canViewFriends,
      shouldShowInterests,
      handleShowFriends
    };
  },
};
</script>
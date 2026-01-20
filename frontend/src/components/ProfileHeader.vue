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
          
          <h3 v-if="!isOtherUser" class="text-lg text-gray-500 m-0 mb-3">
            {{ displayUser.email }}
          </h3>

          <div class="flex gap-10">
            <div class="flex flex-col items-start">
              <div class="flex flex-row items-center gap-2">
                <span class="text-2xl font-bold text-dark">{{ displayUser.streak || displayUser.current_streak || 0 }}</span>
                <span class="pi pi-sparkles font-xl"></span>
              </div>
              <span class="text-xs text-gray-600">{{ $t('profile.header.streak') }}</span>
            </div>
            <div class="flex flex-col items-start">
              <div 
                class="flex flex-row items-center gap-2 relative"
                :class="{ 'cursor-pointer hover:opacity-70': canViewFriends }"
                @click="canViewFriends ? handleShowFriends() : null"
              >
                <span class="text-2xl font-bold text-dark">{{ displayUser.friends_count || displayUser.friend_count || 0 }}</span>
                <span class="pi pi-users font-xl"></span>
                <!-- Red badge for incoming requests (own profile only) -->
                <span v-if="!isOtherUser && incomingRequestsCount > 0" class="absolute -top-2 -right-3 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                  {{ incomingRequestsCount }}
                </span>
              </div>
              <span class="text-xs text-gray-600">{{ $t('profile.header.friends') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Interests Section -->
      <div v-if="shouldShowInterests" class="w-full">
        <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <i class="pi pi-heart"></i>
          {{ $t('profile.header.interests') }}
        </h3>
        <div v-if="interests.length > 0" class="flex flex-wrap gap-2">
          <Chip
            v-for="interest in interests"
            :key="interest"
            :label="getTranslatedInterestLabel(interest)"
            class="interest-chip"
          />
        </div>
        <p v-else class="text-sm text-gray-500 italic">
          {{ $t('profile.header.no_interests') }}
        </p>
      </div>
    </div>
    
    <Message v-else-if="error" severity="error" :closable="false" class="m-0">
      {{ error }}
    </Message>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue';
import { getUserId, isAuthenticated } from '../auth';
import Avatar from 'primevue/avatar';
import Chip from 'primevue/chip';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import { useI18n } from 'vue-i18n';

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
    const { t, locale } = useI18n();
    const user = ref(null);
    const userId = ref('');
    const loading = ref(true);
    const error = ref('');
    const interests = ref([]);
    const interestSlugs = ref([]);

    const getTranslatedInterestLabel = (slug) => {
      const translations = t('interests');
      if (translations && typeof translations === 'object' && slug in translations) {
        return translations[slug];
      }
      return slug.replace('_', ' ').charAt(0).toUpperCase() + slug.slice(1);
    };

    watch(locale, () => {
      // Force re-render of interests when language changes
      // This will cause getTranslatedInterestLabel to be called again
    });
    const incomingRequestsCount = ref(0);

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

    const fetchIncomingRequestsCount = async () => {
      try {
        const apiDomain = import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
        const res = await fetch(`${apiDomain}/api/v1/friend/requests/incoming`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (res.ok) {
          const data = await res.json();
          incomingRequestsCount.value = Array.isArray(data) ? data.length : 0;
        }
      } catch (e) {
        console.error('Failed to fetch incoming requests count:', e);
      }
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

        // Fetch user data, interests, and incoming requests in parallel
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
          error.value = t('profile.error_fetch');
        }

        if (interestsResponse.ok) {
          const interestsData = await interestsResponse.json();
          interests.value = interestsData.interests || [];
        }

        // Fetch incoming requests count
        await fetchIncomingRequestsCount();
      } catch (e) {
          error.value = t('profile.error_generic');
          console.error('User fetch error:', e);
        } finally {
          loading.value = false;
        }
    });

    console.log(displayUser)

    return {
      displayUser,
      userId,
      loading,
      error,
      interests,
      incomingRequestsCount,
      canViewFriends,
      shouldShowInterests,
      handleShowFriends,
      getTranslatedInterestLabel
    };
  },
};
</script>
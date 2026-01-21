<script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import Card from 'primevue/card';
  import DatePicker from 'primevue/datepicker';
  import Message from 'primevue/message';
  import Button from 'primevue/button';
  import Skeleton from 'primevue/skeleton';
  import ProfileHeader from './ProfileHeader.vue';
  import { useI18n } from 'vue-i18n';
  
  const { t } = useI18n();
  const route = useRoute();
  const router = useRouter();
  const apiDomain = import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
  
  const emits = defineEmits(['date-selected', 'show-friends']);
  
  const profile = ref(null);
  const friendshipStatus = ref(null);
  const showErrorMessage = ref(false);
  const eventDates = ref([]);
  const calendarKey = ref(0);
  const videoInfoList = ref([]);
  const loading = ref(true);
  const error = ref(null);
  const sendingRequest = ref(false);
  
  const userId = computed(() => profile.value?.id);
  const areFriends = computed(() => friendshipStatus.value === 'accepted');
  const hasPendingRequest = computed(() => 
    friendshipStatus.value === 'pending_outgoing' || 
    friendshipStatus.value === 'pending_incoming'
  );
  
  const hasEvent = (day) => {
    return eventDates.value.includes(day);
  };
  
  const handleShowFriends = (userId) => {
    emits('show-friends', userId);
  };
  
  const handleSelectedDate = (date) => {
    let day = date.getDate();
    let videoInfo = null;
  
    if(hasEvent(day)) {
      for (const vi of videoInfoList.value) {
        if(vi.day === day) {
          videoInfo = vi;
          break;
        }
      }
      emits('date-selected', date, true, videoInfo);
      showErrorMessage.value = false;
    } else {
      emits('date-selected', date, false, null);
      showErrorMessage.value = true;
    }
  };
  
  const handleMonthChange = async (event) => {
    if (!userId.value || !areFriends.value) return;
    
    const current_year = event.year;
    const current_month = event.month;
  
    try {
      const response = await fetch(
        `${apiDomain}/api/v1/friend/${userId.value}/videos?year=${current_year}&month=${current_month}`,
        {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        eventDates.value = data.map(video => new Date(video.created_at).getDate());
        videoInfoList.value = data.map(video => ({
          video_id: video.id,
          day: new Date(video.created_at).getDate(),
          caption: video.caption,
          url: video.url
        }));
        calendarKey.value += 1;
      }
    } catch (err) {
      console.error('Failed to fetch videos for month:', err);
    }
  };
  
  const checkFriendshipStatus = async () => {
    if (!userId.value) return;
    
    try {
      const response = await fetch(
        `${apiDomain}/api/v1/friend/check/${userId.value}`,
        {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        friendshipStatus.value = data.status;
      }
    } catch (err) {
      console.error('Failed to check friendship status:', err);
    }
  };
  
  const loadProfile = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    const handle = route.params.handle;
    
    // 1. Get user profile by handle (sada vraća i interese)
    const profileRes = await fetch(`${apiDomain}/api/v1/user/profile/${handle}`, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!profileRes.ok) {
      error.value = profileRes.status === 404 ? t('profile.user_not_found') : t('profile.error_loading');
      return;
    }
    
    profile.value = await profileRes.json();
    // profile.value sada sadrži i interests polje
    
    // 2. Check friendship status
    await checkFriendshipStatus();
    
    // 3. Load current month's videos only if friends
    if (areFriends.value) {
      const current_year = new Date().getFullYear();
      const current_month = new Date().getMonth() + 1;
      
      const videosRes = await fetch(
        `${apiDomain}/api/v1/friend/${profile.value.id}/videos?year=${current_year}&month=${current_month}`,
        {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (videosRes.ok) {
        const data = await videosRes.json();
        eventDates.value = data.map(video => new Date(video.created_at).getDate());
        videoInfoList.value = data.map(video => ({
          video_id: video.id,
          day: new Date(video.created_at).getDate(),
          caption: video.caption,
          url: video.url
        }));
      }
    }
    
  } catch (err) {
    console.error('Error loading profile:', err);
    error.value = t('profile.error_loading');
  } finally {
    loading.value = false;
  }
};

const sendFriendRequest = async () => {
  if (!profile.value || !profile.value.id) return;
  sendingRequest.value = true;
  try {
    const res = await fetch(`${apiDomain}/api/v1/friend/request`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_user_id: profile.value.id })
    });

    if (res.ok) {
      // Mark as outgoing pending from the frontend perspective
      friendshipStatus.value = 'pending_outgoing';
    } else {
      const err = await res.json().catch(() => null);
      console.error('Failed to send friend request', err);
      showErrorMessage.value = true;
    }
  } catch (err) {
    console.error('Error sending friend request:', err);
    showErrorMessage.value = true;
  } finally {
    sendingRequest.value = false;
  }
};

  
  onMounted(() => {
    loadProfile();
  });
  </script>
  
  <template>
    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center w-full">
      <Card class="w-full mt-[2vh]">
        <template #content>
          <div class="flex items-center gap-4">
            <Skeleton shape="circle" size="5rem" />
            <div class="flex-1">
              <Skeleton width="10rem" class="mb-2" />
              <Skeleton width="15rem" />
            </div>
          </div>
        </template>
      </Card>
      <Skeleton class="mt-[2vh] w-full" height="20rem" />
    </div>
  
    <!-- Error State -->
    <div v-else-if="error" class="flex flex-col items-center w-full">
      <Card class="w-full mt-[2vh]">
        <template #content>
          <div class="text-center py-8">
            <i class="pi pi-exclamation-circle text-4xl text-red-500 mb-4"></i>
            <p class="text-lg" style="color: var(--color-text-dark);">{{ error }}</p>
            <Button :label="$t('profile.back')" @click="router.push('/home')" class="mt-4" />
          </div>
        </template>
      </Card>
    </div>
  
    <!-- Profile Content -->
    <div v-else class="flex flex-col items-center w-full">
      <!-- Profile Header Card -->
      <Card class="w-full">
        <template #content>
          <ProfileHeader 
            :other-user-data="profile" 
            :is-other-user="true"
            :friendship-status="friendshipStatus"
            @show-friends="handleShowFriends"
          />
        </template>
      </Card>
  
      <!-- Follow Button for Non-Friends -->
      <Card v-if="!areFriends" class="w-full mt-[2vh]">
        <template #content>
          <div class="text-center py-4">
            <template v-if="hasPendingRequest">
              <p class="mb-3" style="color: var(--color-text-secondary);">
                {{ friendshipStatus === 'pending_outgoing' ? $t('profile.friendship.req_sent') : $t('profile.friendship.req_incoming') }}
              </p>
              <Button 
                :label="$t('profile.friendship.requests')" 
                icon="pi pi-users" 
                @click="router.push('/friends')" 
                outlined
              />
            </template>
            <template v-else>
              <p class="mb-3" style="color: var(--color-text-secondary);">{{ $t('profile.friendship.connect_hint') }}</p>
              <Button 
                :label="$t('profile.friendship.send_request')" 
                icon="pi pi-user-plus" 
                :disabled="sendingRequest"
                :loading="sendingRequest"
                @click="sendFriendRequest"
              />
            </template>
          </div>
        </template>
      </Card>
  
      <!-- Calendar (only for friends) -->
      <template v-if="areFriends">
        <DatePicker 
          inline 
          class="mt-[2vh] w-full" 
          @date-select="handleSelectedDate" 
          @month-change="handleMonthChange" 
          :key="calendarKey"
        >
          <template #date="{ date }">
            <div class="relative flex items-center justify-center w-10 h-10">
              {{ date.day }}
              <span 
                v-if="hasEvent(date.day)" 
                class="absolute inset-0 border-2 rounded-full pointer-events-none"
                style="border-color: var(--color-primary);"
              ></span>
            </div>
          </template>
  
          <template #footer>
            <div class="p-3 text-sm" style="color: var(--color-text-light);">
              {{ $t('profile.select_date_other') }}
            </div>
          </template>
        </DatePicker>
  
        <Message severity="error" class="mt-[4vh]" v-if="showErrorMessage">
          {{ $t('profile.no_speeches') }}
        </Message>
      </template>
    </div>
  </template>
  
  <style scoped>
:deep(.p-datepicker) {
  border-radius: 1.25rem !important;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08) !important;
  overflow: hidden;
}
</style>
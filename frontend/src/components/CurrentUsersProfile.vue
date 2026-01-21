<script setup>
    import { ref, onMounted } from 'vue';
    import ProfileHeader from './ProfileHeader.vue';  
    import Card from 'primevue/card';
  
    import Button from 'primevue/button';
    import DatePicker from 'primevue/datepicker';
    import Message from 'primevue/message';
    import { getUserId } from'../auth';
    import { useRouter } from 'vue-router';

    const emits = defineEmits(['date-selected', 'show-friends']);

    const router = useRouter();

    const showErrorMessage = ref(false)
    const eventDates = ref([]); 
    const calendarKey = ref(0);
    let videoInfoList = ref([]);
    const showDashboardButton = ref(false);
    const userRole = ref(null);

    const hasEvent = (day) => {
      return eventDates.value.includes(day);
    };

    const deleteVideo = (videoId) => {
      videoInfoList.value = videoInfoList.value.filter(vi => vi.video_id !== videoId);
      eventDates.value = videoInfoList.value.map(vi => vi.day);
      calendarKey.value += 1;
    };

    const handleShowFriends = (userId) => {
      emits('show-friends', userId);
    };

    const setUserRole = (role) => {
      userRole.value = role;
      console.log('User role set to:', role);
      const adminRole = import.meta.env.VITE_ADMIN_ROLE || window.ENV?.VITE_ADMIN_ROLE || 'admin';
      const modRole = import.meta.env.VITE_MODERATOR_ROLE || window.ENV?.VITE_MODERATOR_ROLE || 'mod';
      const rootRole = import.meta.env.VITE_ROOT_ROLE || window.ENV?.VITE_ROOT_ROLE || 'root';
      console.log('Comparing role:', role, 'with admin:', adminRole, 'mod:', modRole, 'root:', rootRole);
      showDashboardButton.value = (role === adminRole || role === modRole || role === rootRole);
      console.log('Dashboard button visibility:', showDashboardButton.value);
    };

    const goToDashboard = () => {
      router.push('/dashboard');
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

    const fetchVideos = async () => {
      const userId = await getUserId();
      const current_year = new Date().getFullYear();
      const current_month = new Date().getMonth() + 1; 
      const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/${userId}/${current_year}/${current_month}/videos`);
      
      if (response.ok) {
        const data = await response.json();
        eventDates.value = [];
        data.videos.forEach(video_info => {
          eventDates.value.push(video_info.day);
        });
        videoInfoList.value = data.videos;
        calendarKey.value += 1;
      } else {
        console.error('Failed to fetch user videos');
      }
    };

    const handleMonthChange = async (event) => {
      const userId = await getUserId();
      const current_year = event.year;
      const current_month = event.month; 

      const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/${userId}/${current_year}/${current_month}/videos`);
      
      if (response.ok) {
        const data = await response.json();
        eventDates.value = [];
        data.videos.forEach(video_info => {
          eventDates.value.push(video_info.day);
        });
        videoInfoList.value = data.videos;
      } else {
        console.error('Failed to fetch user videos for month change');
      }
    };

    onMounted(async () => {
      await fetchVideos();
    });

    defineExpose({
      deleteVideo,
      fetchVideos
    });
</script>


<template>
    <div class="flex flex-col items-center w-full">
        <Card class="w-full uniform-surface">
            <template #content>
                <ProfileHeader @show-friends="handleShowFriends" @user-role="setUserRole"/>
            </template>
        </Card>

        <Button v-if="showDashboardButton" icon="pi pi-sliders-h" :label="$t('profile.dashboard_button')" class="w-full mt-[2vh]" :onClick="goToDashboard"  />

        <DatePicker inline class="mt-[2vh] w-full uniform-surface" @date-select="handleSelectedDate" @month-change="handleMonthChange" :key="calendarKey">
          <template #date="{ date }">
            <div class="relative flex items-center justify-center w-10 h-10">
              {{ date.day }}
              <span 
                v-if="hasEvent(date.day)" 
                class="absolute inset-0 rounded-full pointer-events-none"
                style="border: 2px solid var(--color-primary);"
              ></span>
            </div>
          </template>

           <template #footer>
                <div class="p-3 text-sm" style="color: var(--color-text-secondary);">
                    {{ $t('profile.select_date_me') }}
                </div>
            </template>
        </DatePicker>

        <Message severity="error" class="mt-[2vh]" v-if="showErrorMessage">{{ $t('profile.no_speeches') }}</Message>
    </div>
</template>


<style scoped>
.uniform-surface {
  border: 1px solid var(--color-border-light);
  border-radius: 1.25rem !important;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08) !important;
  background-color: var(--color-bg-card);
}

:deep(.p-card) {
  border-radius: 1.25rem !important;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08) !important;
  border: 1px solid var(--color-border-light) !important;
  background-color: var(--color-bg-card) !important;
  overflow: hidden;
}

:deep(.p-card .p-card-body) {
  padding: 1.25rem;
}

:deep(.p-datepicker) {
  border-radius: 1.25rem !important;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08) !important;
  border: 1px solid var(--color-border-light) !important;
  background-color: var(--color-bg-card) !important;
  overflow: hidden;
}

:deep(.p-datepicker-inline) {
  border-radius: 1.25rem !important;
  overflow: hidden;
}

:deep(.p-datepicker .p-datepicker-header) {
  border-top-left-radius: 1.25rem !important;
  border-top-right-radius: 1.25rem !important;
}

:deep(.p-datepicker .p-datepicker-calendar-container) {
  border-bottom-left-radius: 1.25rem !important;
  border-bottom-right-radius: 1.25rem !important;
}
</style>
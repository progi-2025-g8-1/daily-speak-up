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
      showDashboardButton.value = (role === import.meta.env.VITE_ADMIN_ROLE || role === import.meta.env.VITE_MODERATOR_ROLE || role === import.meta.env.VITE_ROOT_ROLE);
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
        <Card class="w-full">
            <template #content>
                <ProfileHeader @show-friends="handleShowFriends" @user-role="setUserRole"/>
            </template>
        </Card>

        <Button v-if="showDashboardButton" icon="pi pi-sliders-h" :label="$t('profile.dashboard_button')" class="w-full mt-[2vh]" :onClick="goToDashboard"  />

        <DatePicker inline class="mt-[2vh] w-full" @date-select="handleSelectedDate" @month-change="handleMonthChange" :key="calendarKey">
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
</style>
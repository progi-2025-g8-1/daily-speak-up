<script setup>
    import { ref, onMounted } from 'vue';
    import ProfileHeader from './ProfileHeader.vue';  
    import Card from 'primevue/card';
  
    import DatePicker from 'primevue/datepicker';
    import Message from 'primevue/message';
    import { getUserId } from'../auth';

    const emits = defineEmits(['date-selected', 'show-friends']);

    const showErrorMessage = ref(false)
    const eventDates = ref([]); 
    const calendarKey = ref(0);
    let videoInfoList = ref([]);

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
      const userId = await getUserId();
      const current_year = new Date().getFullYear();
      const current_month = new Date().getMonth() + 1; 
      const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/${userId}/${current_year}/${current_month}/videos`);
      
      if (response.ok) {
        const data = await response.json();
        data.videos.forEach(video_info => {
          eventDates.value.push(video_info.day);
        });
        videoInfoList.value = data.videos;
      } else {
        console.error('Failed to fetch user videos');
      }
    });

    defineExpose({
      deleteVideo
    });
</script>


<template>
    <div class="flex flex-col items-center w-[93%]">
        <Card class="w-full mt-[2vh]">
            <template #content>
                <ProfileHeader @show-friends="handleShowFriends" />
            </template>
        </Card>

        <DatePicker inline class="mt-[2vh] w-full" @date-select="handleSelectedDate" @month-change="handleMonthChange" :key="calendarKey">
          <template #date="{ date }">
            <div class="relative flex items-center justify-center w-10 h-10">
              {{ date.day }}
              <span 
                v-if="hasEvent(date.day)" 
                class="absolute inset-0 border-2 border-blue-500 rounded-full pointer-events-none"
              ></span>
            </div>
          </template>

           <template #footer>
                <div class="p-3 text-sm text-gray-500">
                    Odaberite datum za pregled Vaših snimljenih govora.
                </div>
            </template>
        </DatePicker>

        <Message severity="error" class="mt-[4vh]" v-if="showErrorMessage">Ne postoje snimljeni govori za odabrani datum.</Message>
    </div>
</template>


<style scoped>
</style>
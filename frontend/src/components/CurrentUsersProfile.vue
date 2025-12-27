<script setup>
    import { ref, onMounted } from 'vue';
    import ProfileHeader from './ProfileHeader.vue';  
    import Card from 'primevue/card';
    import Calendar from './Calendar.vue';
    import DatePicker from 'primevue/datepicker';
    import Message from 'primevue/message';
    import {getUserId} from'../auth';

    const showErrorMessage = ref(false)

    const emits = defineEmits(['date-selected']);

    // mock data for days of given month that have recorded speeches
    const eventDates = ref([]); 

    const hasEvent = (date) => {
      return eventDates.value.includes(date.day);
    };

    const handleSelectedDate = (date) => {
      if(hasEvent({ day: date.getDate() })) {
        emits('date-selected', date, true);
        showErrorMessage.value = false;
      } else {
        emits('date-selected', date, false);
        showErrorMessage.value = true;
      }
    };

    onMounted(async () => {
      const userId = await getUserId();
      const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/${userId}/2025/12/videos`);
      if (response.ok) {
        const data = await response.json();
        let j = Object.keys(data.videos);
        eventDates.value = j.map(key => parseInt(key));
        console.log(eventDates.value);
      } else {
        console.error('Failed to fetch user videos');
      }
    });
</script>


<template>
    <div class="flex flex-col items-center w-[93%]">
        <Card class="w-full mt-[2vh]">
            <template #content>
                <ProfileHeader />
            </template>
        </Card>

        <DatePicker inline class="mt-[2vh] w-full" @date-select="handleSelectedDate">
          <template #date="{ date }">
            <div class="relative flex items-center justify-center w-10 h-10">
              {{ date.day }}
              <span 
                v-if="hasEvent(date)" 
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
<script setup>
    import { ref } from 'vue';
    import ProfileHeader from './ProfileHeader.vue';  
    import Card from 'primevue/card';
    import Calendar from './Calendar.vue';
    import DatePicker from 'primevue/datepicker';
    import Message from 'primevue/message';

    const showErrorMessage = ref(false)

    const emits = defineEmits(['date-selected']);

    // mock data for days of given month that have recorded speeches
    const eventDates = [12, 15, 16, 17, 18, 20]; 

    const hasEvent = (date) => {
      return eventDates.includes(date.day);
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
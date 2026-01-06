<template>
    <div class="calendar-container">
      <div class="calendar-header">
        <Button 
          icon="pi pi-chevron-left" 
          text 
          rounded 
          @click="previousMonth"
        />
        <h3 class="calendar-title">{{ currentMonthYear }}</h3>
        <Button 
          icon="pi pi-chevron-right" 
          text 
          rounded 
          @click="nextMonth"
        />
      </div>
  
      <div class="weekdays">
        <div v-for="day in weekdays" :key="day" class="weekday">
          {{ day }}
        </div>
      </div>
  
      <div class="calendar-days">
        <div
          v-for="(day, index) in calendarDays"
          :key="index"
          class="calendar-day"
          :class="{
            'has-video': day.hasVideo,
            'empty': day.isEmpty
          }"
          @click="handleDayClick(day)"
        >
          {{ day.isEmpty ? '' : day.day }}
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed } from 'vue';
  import Button from 'primevue/button';
  
  export default {
    name: 'Calendar',
    components: {
      Button
    },
    props: {
      videoDates: {
        type: Array,
        default: () => []
      }
    },
    emits: ['day-click', 'month-change'],
    setup(props, { emit }) {
      const currentDate = ref(new Date());
      const weekdays = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
      
      const currentMonthYear = computed(() => {
        const months = [
          'January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December'
        ];
        return `${months[currentDate.value.getMonth()]} ${currentDate.value.getFullYear()}`;
      });
      
      const calendarDays = computed(() => {
        const year = currentDate.value.getFullYear();
        const month = currentDate.value.getMonth();
        
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();
        
        const days = [];
        
        // Add empty cells for days before the month starts
        for (let i = 0; i < startingDayOfWeek; i++) {
          days.push({
            day: 0,
            date: '',
            hasVideo: false,
            isEmpty: true
          });
        }
        
        // Add all days of the month
        for (let day = 1; day <= daysInMonth; day++) {
          const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          const hasVideo = props.videoDates.includes(dateStr);
          
          days.push({
            day,
            date: dateStr,
            hasVideo,
            isEmpty: false
          });
        }
        
        return days;
      });
      
      const previousMonth = () => {
        currentDate.value = new Date(
          currentDate.value.getFullYear(),
          currentDate.value.getMonth() - 1,
          1
        );
        emit('month-change', currentDate.value);
      };
      
      const nextMonth = () => {
        currentDate.value = new Date(
          currentDate.value.getFullYear(),
          currentDate.value.getMonth() + 1,
          1
        );
        emit('month-change', currentDate.value);
      };
      
      const handleDayClick = (day) => {
        if (!day.isEmpty && day.hasVideo) {
          emit('day-click', day);
        }
      };
      
      return {
        weekdays,
        currentMonthYear,
        calendarDays,
        previousMonth,
        nextMonth,
        handleDayClick
      };
    }
  };
  </script>
  
  <style scoped>
  .calendar-container {
    width: 100%;
    max-width: 500px;
    background: var(--color-bg-card);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .calendar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  
  .calendar-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text-dark);
    margin: 0;
  }
  
  .weekdays {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-bottom: 8px;
  }
  
  .weekday {
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: var(--color-text-light);
    padding: 8px 4px;
  }
  
  .calendar-days {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
  }
  
  .calendar-day {
    width: 100%;
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 500;
    color: var(--color-text-dark);
    border-radius: 8px;
    transition: all 0.2s ease;
    cursor: default;
    min-height: 40px;
  }
  
  .calendar-day:not(.empty):hover {
    background: var(--color-bg-main);
  }
  
  .calendar-day.has-video {
    color: var(--color-primary) !important;
    font-weight: 700;
    cursor: pointer;
  }
  
  .calendar-day.has-video:hover {
    background: var(--color-bg-accent);
    transform: scale(1.05);
  }
  
  .calendar-day.empty {
    cursor: default;
    visibility: hidden;
  }
  </style>
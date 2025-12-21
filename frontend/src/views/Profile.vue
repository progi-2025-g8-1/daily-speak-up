<template>
    <div class="min-h-screen bg-main">

      <NavBar />
      
      <div class="max-w-md mx-auto" id="i1">
        
        <Card class="shadow-lg mt-6 mx-4">
          <template #header>
            <div class="flex items-center gap-3 px-6 pt-6 pb-2">
              <h2 class="text-xl font-semibold text-dark">Profile view</h2>
            </div>
          </template>
          
          <template #content>
            
            <User />
          </template>
        </Card>
        
            <Calendar />
        
      </div>
    </div>
  </template>
  
  <script setup>
  import NavBar from '../components/NavBar.vue';
  import User from '../components/User.vue';
  import Card from 'primevue/card';
  import Calendar from '../components/Calendar.vue'
  </script>

  <style>
    #i1{
        display:flex;
        align-items:baseline;
        justify-content: center;
    }
  </style>
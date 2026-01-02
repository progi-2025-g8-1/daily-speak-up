<template>
    <div class="min-h-screen bg-main">

      <NavBar />
      
      <div class="max-w-md mx-auto" id="i1">
        
        <Card class="shadow-lg mt-6 mx-4">
          <template #header>
            <div class="px-6 pt-6 pb-2">
              <div class="flex items-center justify-between mb-2">
                <router-link 
                  to="/home" 
                  class="inline-flex items-center gap-2 px-3 py-1.5 font-medium transition-colors duration-200"
                  style="background-color: white; color: #3b82f6;"
                  @mouseenter="$event.target.style.backgroundColor = '#f3f4f6'"
                  @mouseleave="$event.target.style.backgroundColor = 'white'"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
                  </svg>
                  Back
                </router-link>
                <h2 class="text-xl font-semibold text-dark">Profile</h2>
              </div>
            </div>
          </template>
          
          <template #content>
            
            <ProfileHeader />
          </template>
        </Card>
        
            <Calendar />
        
      </div>
    </div>
  </template>
  
  <script setup>
  import NavBar from '../components/NavBar.vue';
  import ProfileHeader from '../components/ProfileHeader.vue';
  import Card from 'primevue/card';
  import Calendar from '../components/Calendar.vue'
  </script>

  <style>
    #i1{
        display:flex;
        align-items:baseline;
        justify-content: center;
    }
    @media (max-width: 600px) {
        #i1{
            flex-wrap: wrap;
            gap: 1rem;
        }
    }

  </style>
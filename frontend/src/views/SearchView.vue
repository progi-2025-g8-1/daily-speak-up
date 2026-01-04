<template>
    <div class="min-h-screen bg-main">
      <NavBar />
      
      <div class="max-w-2xl mx-auto px-4 py-6">
        <Card class="shadow-lg">
          <template #header>
            <div class="px-6 pt-6 pb-2">
              <h2 class="text-2xl font-semibold text-dark">Search Users</h2>
            </div>
          </template>
          
          <template #content>
            <UserSearch />
          </template>
        </Card>
      </div>
    </div>
  </template>
  
  <script setup>
  import NavBar from '../components/NavBar.vue';
  import UserSearch from '../components/UserSearch.vue';
  import Card from 'primevue/card';
  </script>
<script setup lang="ts">
  import { ref } from 'vue';
  import CurrentUsersProfile from './CurrentUsersProfile.vue';
  import FriendsList from './FriendsList.vue';
  
  const emits = defineEmits(['date-selected', 'show-friends']);

  const showCurrentUsersProfile = ref(true);
  const showFriendsList = ref(false);
  const userId = ref('');

  const handleShowFriends = (id: string) => {
    userId.value = id;
    showCurrentUsersProfile.value = false;
    showFriendsList.value = true;

  };

  const hideFriends = () => {
    showFriendsList.value = false;
    showCurrentUsersProfile.value = true;
  };

  const handleDateSelected = (date: Date, hasSpeeches: boolean, videoInfo: any) => {
    if (hasSpeeches) {
      emits('date-selected', date, hasSpeeches, videoInfo);
    }
  };
</script>

<template>
  <div class="flex flex-col items-center lg:w-[40vw] lg:h-full">
    <CurrentUsersProfile v-if="showCurrentUsersProfile"
                         @date-selected="handleDateSelected"
                         @show-friends="handleShowFriends" />

    <FriendsList v-else-if="showFriendsList" @hide-friends="hideFriends"/>
  </div>
</template>

<style scoped>

</style>
<script setup lang="ts">
  import { ref, nextTick } from 'vue';
  import CurrentUsersProfile from './CurrentUsersProfile.vue';
  import FriendsList from './FriendsList.vue';
  import type { FriendsListInstance } from '../types/friends-list';
  import type { DeleteVideoInstance } from '../types/delete-video';
  
  const emits = defineEmits(['date-selected', 'show-friends']);

  const showCurrentUsersProfile = ref(true);
  const showFriendsList = ref(false);
  const friendsListRef = ref<FriendsListInstance | null>(null);
  const currentUsersProfileRef = ref<DeleteVideoInstance | null>(null);
  const userId = ref('');

  const deleteVideo = (videoId: string) => {
    if (currentUsersProfileRef.value) {
      currentUsersProfileRef.value.deleteVideo(videoId);
    }
  };

  const handleShowFriends = async (id: string) => {
    showCurrentUsersProfile.value = false;
    showFriendsList.value = true;
    await nextTick();
    if (friendsListRef.value) {
      friendsListRef.value.showFriends(id);
      userId.value = id;
    }
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

  defineExpose({
    deleteVideo
  });
</script>

<template>
  <div class="flex flex-col items-center lg:w-[40vw] lg:h-full p-4">
    <CurrentUsersProfile v-if="showCurrentUsersProfile"
                         ref="currentUsersProfileRef"
                         @date-selected="handleDateSelected"
                         @show-friends="handleShowFriends" />

    <FriendsList v-else-if="showFriendsList" ref="friendsListRef"
                                             @hide-friends="hideFriends"/>
  </div>
</template>

<style scoped>

</style>
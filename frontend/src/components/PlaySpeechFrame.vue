<script setup>
    import { ref } from 'vue';
    import Dialog from 'primevue/dialog';
    import Button from 'primevue/button';
    import ToggleButton from 'primevue/togglebutton';
    import { getUserId } from '../auth';

    const emits = defineEmits(['video-deleted']);

    const visible = ref(false);
    let dateString = ref('');
    const videoCaption = ref(''); 
    const videoVisibility = ref(false);
    const isOwner = ref(false);

    let videoInfo = null;

    const checkIsOwner = async() => {
        try {
            const userId = await getUserId();
            isOwner.value = videoInfo && videoInfo.owner_id === userId;
        } catch (error) {
            console.error('Error fetching user ID:', error);
            isOwner.value = false;
        }
    }; 

    const handleVisibilitySwitch = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/video/${videoInfo.video_id}/visibility`, {
                method: 'PUT'
            });
            if (response.ok) {
                if (videoInfo.visibility === 'private') {
                    videoInfo.visibility = 'friends';
                } else {
                    videoInfo.visibility = 'private';
                }
            } else {
                console.error('Failed to toggle visibility');
                videoVisibility.value = !videoVisibility.value;
            }
        } catch (error) {
            console.error('Error toggling visibility:', error);
            videoVisibility.value = !videoVisibility.value;
        }
    };

    const deleteVideo = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/video/${videoInfo.video_id}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                visible.value = false;
                emits('video-deleted', videoInfo.video_id);
            } else {
                console.error('Failed to delete video');
            }
        } catch (error) {
            console.error('Error deleting video:', error);
        }
    };

    const displaySpeechDialog = (date, hasSpeeches, video) => {
      if (hasSpeeches) {
        visible.value = true;
        dateString.value = `${date.getDate()}. ${date.getMonth() + 1}. ${date.getFullYear()}`;
        videoInfo = video;
        videoCaption.value = video.caption;
        videoVisibility.value = video.visibility === 'private';
        checkIsOwner();
      }
    };

    defineExpose({
      displaySpeechDialog
    });
</script>


<template>
  <Dialog v-model:visible="visible" :draggable="false" modal class="w-[90vw] lg:w-[60vw] h-auto">
    <template #header>
        <p class="text-xl lg:text-2xl font-semibold"><i>DailySpeakUp</i>, {{ dateString }}</p>
    </template>
    <div class="w-full aspect-video flex flex-col items-center justify-center">
        <iframe 
            width="100%" 
            height="100%" 
            :src="videoInfo.url"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        ></iframe>
      </div>
      <div>{{ videoCaption }}</div>
      <div class="flex flex-row items-center justify-between w-full mt-6">
          <div class="flex flex-row items-center gap-3">
              <div class="flex gap-1">
                <span v-for="i in 5" :key="i" class="text-yellow-400">★</span>
              </div>
              <p>{{ $t('speech.rating') }} 5.0</p>
          </div>
          <div class="flex flex-row items-center gap-4">
            <div v-if="isOwner" class="flex flex-row items-center gap-4">
              <ToggleButton :onLabel="$t('speech.private')" :offLabel="$t('speech.friends')" onIcon="pi pi-lock" 
                          offIcon="pi pi-lock-open" class="w-36" aria-label="Do you confirm" 
                          @change="handleVisibilitySwitch" v-model="videoVisibility"/>
              <Button icon="pi pi-eraser" :label="$t('speech.delete')" severity="danger" v-on:click="deleteVideo" />
            </div>
          </div>
      </div>
</Dialog>
</template>

<style scoped>
</style>
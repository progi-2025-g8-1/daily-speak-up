<script setup>
    import { ref } from 'vue';
    import Dialog from 'primevue/dialog';
    import Rating from 'primevue/rating'; 
    import Button from 'primevue/button';
    import ToggleButton from 'primevue/togglebutton';
    import { getUserId } from '../auth';


    const visible = ref(false);
    let dateString = ref('');
    const videoCaption = ref(''); 
    let videoInfo = null;

    const isOwner = async() => {
        try {
            const userId = await getUserId();
            return videoInfo && videoInfo.owner_id === userId;
        } catch (error) {
            console.error('Error fetching user ID:', error);
            return false;
        }
    }; 

    const displaySpeechDialog = (date, hasSpeeches, video) => {
      if (hasSpeeches) {
        visible.value = true;
        dateString.value = `${date.getDate()}. ${date.getMonth() + 1}. ${date.getFullYear()}`;
        videoInfo = video;
        videoCaption.value = video.caption;
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
    <div>{{ videoCaption }}</div>
    <div class="w-full aspect-video flex flex-col items-center justify-center">
        <iframe 
            width="100%" 
            height="100%" 
            :src="videoInfo.url"
            allow="autoplay" 
        ></iframe>
        <div class="flex flex-row items-center justify-between w-full mt-6">
            <div class="flex flex-row items-center gap-3">
                <Rating :modelValue="5" readonly />
                <p>Ocjena: 5.0</p>
            </div>
            <div class="flex flex-row items-center gap-4">
              <div class="pi pi-share-alt" style="color:black; font-size: 1.2rem;"></div>
              <div v-if="isOwner()" class="flex flex-row items-center gap-4">
                <ToggleButton v-model="checked" onLabel="Privatno" offLabel="Za prijatelje" onIcon="pi pi-lock" 
                            offIcon="pi pi-lock-open" class="w-36" aria-label="Do you confirm" />
                <Button icon="pi pi-eraser" label="Obriši" severity="danger" />
              </div>
            </div>
        </div>
    </div>
</Dialog>
</template>

<style scoped>
</style>
<script setup>
    import { ref } from 'vue';
    import Dialog from 'primevue/dialog';
    import Rating from 'primevue/rating';


    const visible = ref(false);
    let dateString = ref('');
    const videoCaption = ref(''); 
    let videoInfo = null;
  

    const displaySpeechDialog = (date, hasSpeeches, video) => {
      if (hasSpeeches) {
        visible.value = true;
        dateString.value = `${date.getDate()}. ${date.getMonth() + 1}. ${date.getFullYear()}`;
        videoInfo = video;
        videoCaption.value = video.caption;
        console.log(videoInfo);
      }
    };

    defineExpose({
      displaySpeechDialog
    });
</script>


<template>
  <Dialog v-model:visible="visible" modal class="w-[60vw]">
    <template #header>
        <p class="text-4xl font-semibold">Vaš <i>DailySpeakUp ({{ dateString }})</i></p>
    </template>
    <div class="w-full aspect-video flex flex-col items-center justify-center">
        <iframe 
            width="100%" 
            height="100%" 
            :src="videoInfo.url"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" 
        ></iframe>
        <div>{{ videoCaption }}</div>
        <div class="flex flex-row items-center justify-between w-full mt-6">
            <div class="flex flex-row items-center gap-3">
                <Rating :modelValue="5" readonly />
                <p>Ocjena: 5.0</p>
            </div>
            <div class="pi pi-share-alt" style="color:black; font-size: 1.2rem;"></div>
        </div>
    </div>
</Dialog>
</template>

<style scoped>
</style>
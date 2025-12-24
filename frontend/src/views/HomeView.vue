<script setup lang="ts">
  import { ref } from "vue";
  import MainFrame from '../components/MainFrame.vue';
  import FriendsFrame from '../components/FriendsFrame.vue';
  import Divider from 'primevue/divider';
  import VideoRecorderFrame from '../components/VideoRecorderFrame.vue';
  import type { VideoRecorderFrameInstance } from "../types/video-recorder-frame";
  import Toast from 'primevue/toast';

  const videoFrame = ref<VideoRecorderFrameInstance | null>(null);

  const handleStartRecording = (start: boolean) => {
    if (start && videoFrame.value) {
      videoFrame.value.startRecording();
    }
  };

  const handleUploadData = (uploadMethod: string, uploadUrl: string, userId: string, videoPath: string) => {
    if (videoFrame.value) {
      videoFrame.value.uploadData(uploadMethod, uploadUrl, userId, videoPath);
    }
  };

  const handleTopicGenerated = (interes: string, tema: string) => {
    if (videoFrame.value) {
      videoFrame.value.setSpeechTopic(interes, tema);
    }
  };
</script>

<template>
  <div class="flex flex-col lg:flex-row w-full h-full">
    <Toast />
    <VideoRecorderFrame ref="videoFrame" />
    <MainFrame 
      @start-recording="handleStartRecording" 
      @upload-data="handleUploadData"
      @topic-generated="handleTopicGenerated"></MainFrame>
    <div class="hidden lg:block">
      <Divider layout="vertical" :pt="{root:{class:'divider'}}"/>
    </div>
    <div class="block lg:hidden">
      <Divider layout="horizontal"  :pt="{root:{class:'divider'}}" />
    </div>
    <FriendsFrame />
  </div>
</template>

<style scoped>
.divider{
  --p-divider-vertical-margin:0 0 0 0;
  --p-divider-horizontal-margin:0 0 0 0;
}
.btnmy {
  --p-button-border-radius: 9rem;
}
</style>

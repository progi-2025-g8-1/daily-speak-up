<script setup lang="ts">
  import { ref } from "vue";
  import MainFrame from '../components/MainFrame.vue';
  import SecondaryFrame from '../components/SecondaryFrame.vue';
  import VideoRecorderFrame from '../components/VideoRecorderFrame.vue';
  import PlaySpeechFrame from "../components/PlaySpeechFrame.vue";
  import type { VideoRecorderFrameInstance } from "../types/video-recorder-frame";
  import type { PlaySpeechFrameInstance } from "../types/play-speech-frame";
  import Toast from 'primevue/toast';

  const videoFrame = ref<VideoRecorderFrameInstance | null>(null);
  const playSpeechFrame = ref<PlaySpeechFrameInstance | null>(null);

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

  const handleDateSelected = (date: Date, hasSpeeches: boolean) => {
    playSpeechFrame.value.displaySpeechDialog(date, hasSpeeches);
  };
</script>

<template>
  <div class="flex flex-col lg:flex-row w-full h-full">
    <Toast />
    <VideoRecorderFrame ref="videoFrame" />
    <PlaySpeechFrame ref="playSpeechFrame" />
    <SecondaryFrame 
      @date-selected="handleDateSelected" />
    <MainFrame 
      @start-recording="handleStartRecording" 
      @upload-data="handleUploadData"
      @topic-generated="handleTopicGenerated"></MainFrame>
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

<script setup lang="ts">
  import { ref, provide } from "vue";
  import MainFrame from '../components/MainFrame.vue';
  import SecondaryFrame from '../components/SecondaryFrame.vue';
  import VideoRecorderFrame from '../components/VideoRecorderFrame.vue';
  import PlaySpeechFrame from "../components/PlaySpeechFrame.vue";
  import type { VideoRecorderFrameInstance } from "../types/video-recorder-frame";
  import type { PlaySpeechFrameInstance } from "../types/play-speech-frame";
  import type { DeleteVideoInstance } from "../types/delete-video";
  import Toast from 'primevue/toast';

  const emits = defineEmits(['video-deleted']);

  provide('deleteVideo', (videoId: string) => {

  });

  const videoFrame = ref<VideoRecorderFrameInstance | null>(null);
  const playSpeechFrame = ref<PlaySpeechFrameInstance | null>(null);
  const secondaryFrame = ref<DeleteVideoInstance | null>(null);

  const handleDeletedVideo = (videoId: string) => {
    if(secondaryFrame.value) {
      secondaryFrame.value.deleteVideo(videoId);
    }
  };

  const handleRecordingFinished = () => {
    if(secondaryFrame.value) {
      secondaryFrame.value.refreshData();
    }
  };

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

  const handleDateSelected = (date: Date, hasSpeeches: boolean, videoInfo: any) => {
    if(playSpeechFrame.value && hasSpeeches) {
      playSpeechFrame.value.displaySpeechDialog(date, hasSpeeches, videoInfo);
    }
  };
</script>

<template>
  <div class="flex flex-col lg:flex-row w-full h-full">
    <Toast />
    <VideoRecorderFrame ref="videoFrame" @recording-finished="handleRecordingFinished" />
    <PlaySpeechFrame ref="playSpeechFrame" @video-deleted="handleDeletedVideo" />
    <SecondaryFrame 
      @date-selected="handleDateSelected"
      class="hidden lg:flex"
      ref="secondaryFrame"/>
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

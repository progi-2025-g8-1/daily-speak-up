<script setup>
import { ref, nextTick } from "vue";
import Dialog from 'primevue/dialog';
import { VideoConstraints } from "../AV_settings/video_constraints";
import { AudioContraints } from "../AV_settings/audio_constraints";

let stream = null;
let audioTrack = null;
let videoTrack = null;
let recordingTimeout = null;
let videoFrame = null;
let visibleDialog = ref(false);
const RECORDING_DURATION = 10000; 

function startRecording() {
  navigator.mediaDevices.getUserMedia({
        video: VideoConstraints,
        audio: AudioContraints
    })
    .then(async (stream) => {
        const audioTracks = stream.getAudioTracks();
        const videoTracks = stream.getVideoTracks();

        if (audioTracks.length > 0) {
        audioTrack = audioTracks[0];
        }
        if (videoTracks.length > 0) {
        videoTrack = videoTracks[0];
        }

        visibleDialog.value = true;

        await nextTick();

        videoFrame = document.getElementById("video-frame");

        videoFrame.srcObject = stream;

        recordingTimeout = setTimeout(() => {
          stopRecording();
        }, RECORDING_DURATION);
    })
    .catch((error) => {
        console.error("Error accessing media devices.", error);
    });
}

function stopRecording() {
  if (recordingTimeout) {
    clearTimeout(recordingTimeout);
    recordingTimeout = null;
  }

  if (audioTrack) {
    audioTrack.stop();
    audioTrack = null;
  }

  if (videoTrack) {
    videoTrack.stop();
    videoTrack = null;
  }

  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }

  const videoFrame = document.getElementById("video-frame");
  if (videoFrame) {
    videoFrame.srcObject = null;
  }

  visibleDialog.value = false;
}

defineExpose({
  startRecording,
  stopRecording
});
</script>

<template>
  <Dialog v-model:visible="visibleDialog" modal header="🎥 Speak Up!" :style="{ width: '25rem' }" :closable="false" :closeOnEscape="false">
    <video id="video-frame" autoplay muted playsinline></video>
  </Dialog>
</template>

<style scoped>
</style>
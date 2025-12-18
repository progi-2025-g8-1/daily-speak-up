<script setup>
import { ref } from "vue";
import { VideoConstraints } from "../AV_settings/video_constraints";
import { AudioContraints } from "../AV_settings/audio_constraints";

let stream = null;
let audioTrack = null;
let videoTrack = null;
let recordingTimeout = null;
const RECORDING_DURATION = 60000; // 60 seconds

function startRecording() {
  let videoFrame = document.getElementById("video-frame");

  navigator.mediaDevices.getUserMedia({
        video: VideoConstraints,
        audio: AudioContraints
    })
    .then((mediaStream) => {
        stream = mediaStream;
        const audioTracks = stream.getAudioTracks();
        const videoTracks = stream.getVideoTracks();

        if (audioTracks.length > 0) {
        audioTrack = audioTracks[0];
        }
        if (videoTracks.length > 0) {
        videoTrack = videoTracks[0];
        }

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
}

defineExpose({
  startRecording,
  stopRecording
});
</script>

<template>
    <video id="video-frame" autoplay muted playsinline></video>
</template>

<style scoped>
</style>
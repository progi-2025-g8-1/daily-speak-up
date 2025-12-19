<script setup>
import { ref, nextTick } from "vue";
import Dialog from 'primevue/dialog';
import { VideoConstraints } from "../AV_settings/video_constraints";
import { AudioContraints } from "../AV_settings/audio_constraints";


const videoRef = ref(null);
const recordingContainerRef = ref(null);


const visibleDialog = ref(false);
const countdown = ref(null);
const showRecording = ref(false);
const showDoneMessage = ref(false);

let stream = null;
let audioTrack = null;
let videoTrack = null;

let recordingTimeout = null;
let countdownInterval = null;

const RECORDING_DURATION = 60000;
const AFTER_RECORDING_CLOSE_DELAY = 3500;

function initializeMedia(mediaStream) {
  stream = mediaStream;
  const audioTracks = mediaStream.getAudioTracks();
  const videoTracks = mediaStream.getVideoTracks();

  if (audioTracks.length > 0) {
    audioTrack = audioTracks[0];
  }
  if (videoTracks.length > 0) {
    videoTrack = videoTracks[0];
  }
}

function startCountdown() {
  countdown.value = RECORDING_DURATION / 1000;
  countdownInterval = setInterval(() => {
    countdown.value--;
  }, 1000);
}

function stopCountdown() {
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
  countdown.value = null;
}

function stopMediaTracks() {
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
}

function clearTimers() {
  if (recordingTimeout) {
    clearTimeout(recordingTimeout);
    recordingTimeout = null;
  }
  stopCountdown();
}


async function startRecording() {
  try {
    const mediaStream = await navigator.mediaDevices.getUserMedia({
      video: VideoConstraints,
      audio: AudioContraints
    });

    initializeMedia(mediaStream);
    visibleDialog.value = true;
    showRecording.value = true;
    showDoneMessage.value = false;

    await nextTick();

    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream;
    }

    startCountdown();

    recordingTimeout = setTimeout(() => {
      stopRecording();
    }, RECORDING_DURATION);
  } catch (error) {
    console.error("Error accessing media devices.", error);
    visibleDialog.value = false;
  }
}

function stopRecording() {
  clearTimers();

  if (recordingContainerRef.value) {
    recordingContainerRef.value.classList.add("fade-out");

    setTimeout(() => {
      // Stop stream and hide recording
      if (videoRef.value) {
        videoRef.value.srcObject = null;
      }
      showRecording.value = false;
      recordingContainerRef.value.classList.remove("fade-out");

      stopMediaTracks();

      showDoneMessage.value = true;

      setTimeout(() => {
        visibleDialog.value = false;
        showDoneMessage.value = false;
      }, AFTER_RECORDING_CLOSE_DELAY);
    }, 500);
  }
}

defineExpose({
  startRecording,
  stopRecording
});
</script>

<template>
  <Dialog
    v-model:visible="visibleDialog"
    modal
    :closable="false"
    :closeOnEscape="false"
    class="!flex mx-2"
  >
    <div v-if="showRecording" 
         ref="recordingContainerRef" 
         class="w-full"
         >
      <h1 class="pb-2 mb-1">🎥 Snimanje...</h1>
      <p class="mb-4 text-lg font-bold">Vaša je tema: ...</p>
      <div class="!flex flex-col justify-center items-center relative inline-block w-full">
        <video
          ref="videoRef"
          class="rounded-2xl w-[70vw] lg:w-[70vh] block"
          autoplay
          muted
          playsinline
        ></video>
        <div
          class="absolute bottom-2 left-1/2 -translate-x-1/2 
                font-bold text-white bg-black/60 rounded-full 
                w-20 h-10 flex items-center justify-center pointer-events-none"
        >
          00:{{ String(countdown).padStart(2, '0') }}
        </div>
      </div>
    </div>

    <div v-if="showDoneMessage" class="text-center">
      <h2 class="text-xl font-bold mb-2">Recording complete! 🎉</h2>
      <p class="text-gray-600">The window will close automatically shortly.</p>
    </div>
  </Dialog>
</template>

<style scoped>
.recording-container.fade-out {
  animation: fadeOut 0.5s ease-out forwards;
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}
</style>
<script setup>
import { ref, nextTick } from "vue";
import Dialog from 'primevue/dialog';
import { VideoConstraints } from "../AV_settings/video_constraints";
import { AudioConstraints } from "../AV_settings/audio_constraints";


const videoRef = ref(null);
const recordingContainerRef = ref(null);


const visibleDialog = ref(false);
const countdown = ref(0);
const showRecording = ref(false);
const showDoneMessage = ref(false);

let stream = null;
let audioTrack = null;
let videoTrack = null;
let mediaRecorder = null;
let recordedChunks = [];
let recordedBlob = null;

let uploadMethod = "";
let uploadUrl = "";
let userId = "";
let videoPath = "";

let recordingTimeout = null;
let countdownInterval = null;

const RECORDING_DURATION = 5000;
const AFTER_RECORDING_CLOSE_DELAY = 4000;

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
  countdown.value = 0;
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

function uploadData(method, url, uId, vPath) {
  uploadMethod = method;
  uploadUrl = url;
  userId = uId;
  videoPath = vPath;
}

async function uploadToS3() {
  if (!recordedBlob || !uploadUrl) {
    console.error("Missing recorded blob or upload URL");
    return;
  }

  try {
    const response = await window.fetch(uploadUrl, {
      method: "PUT",
      body: recordedBlob,
      headers: {
        "Content-Type": "video/mp4"
      }
    });

    if (!response.ok) {   
      throw new Error(`S3 upload failed with status ${response.status}`);
    }

    console.log("Video successfully uploaded to S3");
  } catch (error) {
    console.error("Error uploading video to S3:", error);
  }
}

async function startRecording() {
  try {
    const mediaStream = await navigator.mediaDevices.getUserMedia({
      video: VideoConstraints,
      audio: AudioConstraints
    });

    initializeMedia(mediaStream);
    visibleDialog.value = true;
    showRecording.value = true;
    showDoneMessage.value = false;

    await nextTick();

    if (videoRef.value) {
      mediaRecorder = new MediaRecorder(mediaStream);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        recordedBlob = new Blob(recordedChunks, { type: 'video/mp4' });
        recordedChunks = [];
      };

      mediaRecorder.onerror = (event) => {
        console.error("MediaRecorder error:", event.error);
      };

      mediaRecorder.start();
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
    if (mediaRecorder) {
      mediaRecorder.stop();
      mediaRecorder = null;
    }

    setTimeout(() => {
      if (videoRef.value) {
        videoRef.value.srcObject = null;
      }
      showRecording.value = false;
      recordingContainerRef.value.classList.remove("fade-out");

      stopMediaTracks();

      if (uploadUrl) {
        uploadToS3();
      }

      showDoneMessage.value = true;

      setTimeout(() => {
        visibleDialog.value = false;
        showDoneMessage.value = false;
      }, AFTER_RECORDING_CLOSE_DELAY);
    }, 450);
  }
}

defineExpose({
  startRecording,
  stopRecording,
  uploadData
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
         class="recording-container w-full"
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
      <h2 class="text-xl font-bold mb-2">Vaš <i>DailySpeakUp</i> je pohranjen! 🎉</h2>
      <p class="text-gray-600">Prozor će se uskoro automatski zatvoriti.</p>
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
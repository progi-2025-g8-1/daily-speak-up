<script setup>
import { ref, nextTick } from "vue";
import Dialog from 'primevue/dialog';
import { useToast } from 'primevue/usetoast';
import ProgressSpinner from 'primevue/progressspinner';
import { VideoConstraints } from "../AV_settings/video_constraints";
import { AudioConstraints } from "../AV_settings/audio_constraints";
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();
const emit = defineEmits(['recording-finished']);
const RECORDING_DURATION = 60000;
const TOAST_DISPLAY_DURATION = 4000;

const videoRef = ref(null);
const visibleDialog = ref(false);
const countdown = ref(0);
const preCountdown = ref(0);
const showRecording = ref(false);
const isFadingOut = ref(false);
const isLoadingCamera = ref(false);
const isPreCountdown = ref(false);
const speechTopic = ref("");
const speechInterest = ref("");

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


function initializeMedia(mediaStream) {
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
      method: uploadMethod || "PUT",
      body: recordedBlob,
    });

    if (!response.ok) {   
      throw new Error(`S3 upload failed with status ${response.status}`);
    }

  } catch (error) {
    console.error("Error uploading video to S3:", error);
  }
}

async function startRecording() {
  try {
    visibleDialog.value = true;
    isLoadingCamera.value = true;
    showRecording.value = false;

    const mediaStream = await navigator.mediaDevices.getUserMedia({
      video: VideoConstraints,
      audio: AudioConstraints
    });

    initializeMedia(mediaStream);

    isLoadingCamera.value = false;
    
    isPreCountdown.value = true;
    
    await nextTick();
    
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream;
    }

    for (let i = 3; i >= 1; i--) {
      preCountdown.value = i;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    isPreCountdown.value = false;
    showRecording.value = true;

    await nextTick();

    if (videoRef.value) {
      const mimeTypes = [
        "video/mp4",
        "video/webm;codecs=h264",
        "video/webm"
      ];
      let selectedMimeType = "video/webm";
      for (const type of mimeTypes) {
        if (MediaRecorder.isTypeSupported(type)) {
          selectedMimeType = type;
          break;
        }
      }

      mediaRecorder = new MediaRecorder(mediaStream, { mimeType: selectedMimeType });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        recordedBlob = new Blob(recordedChunks, { type: selectedMimeType });
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

async function stopRecording() {
  clearTimers();

  if (mediaRecorder) {
    mediaRecorder.stop();
    mediaRecorder = null;
  }

  isFadingOut.value = true;

  await new Promise(resolve => setTimeout(resolve, 500));

  if (videoRef.value) {
    videoRef.value.srcObject = null;
  }
  showRecording.value = false;
  isFadingOut.value = false;

  stopMediaTracks();

  if (uploadUrl) {
    await uploadToS3();
    emit('recording-finished');
  }

  visibleDialog.value = false;
  
  toast.add({
    severity: 'success',
    summary: t('recorder.success_title'),
    detail: t('recorder.success_msg'),
    life: TOAST_DISPLAY_DURATION
  });
}

function setSpeechTopic(interest, topic) {
  speechInterest.value = interest;
  speechTopic.value = topic;
}

defineExpose({
  startRecording,
  stopRecording,
  uploadData,
  setSpeechTopic
});
</script>

<template>
  <Dialog
    v-model:visible="visibleDialog"
    modal
    :closable="false"
    :closeOnEscape="false"
    :class="['!flex mx-2', { 'fade-out': isFadingOut }]"
    :pt="{ mask: { class: isFadingOut ? 'fade-out' : '' } }"
  >
    <div v-if="isLoadingCamera" class="w-full text-center py-8 px-8">
      <h2 class="pb-2 mb-8 text-2xl font-bold">{{ $t('recorder.topic') }}</h2>
      <h2 class="mb-4 text-lg font-bold">{{ speechTopic }} ({{ speechInterest }})</h2>
      <br />
      <ProgressSpinner />
      <br />
      <p class="text-lg font-bold">{{ $t('recorder.camera_loading') }} </p>
    </div>

    <div v-if="isPreCountdown || showRecording" class="w-full">
      <h1 class="pb-2 mb-1">🎥 {{ isPreCountdown ? $t('recorder.recording_in') : $t('recorder.speakup') }}</h1>
      <p class="mb-4 text-lg font-bold">{{ $t('recorder.topic') }} {{ speechTopic }} ({{ speechInterest }})</p>
      <div class="!flex flex-col justify-center items-center relative inline-block w-full">
        <div class="rounded-2xl overflow-hidden w-[70vw] lg:w-[65vh]">
          <video
            ref="videoRef"
            :class="['w-full block transition-all duration-300', isPreCountdown ? 'blur-sm scale-105' : 'scale-100']"
            autoplay
            muted
            playsinline
          ></video>
        </div>
        <!-- Pre-countdown overlay -->
        <div
          v-if="isPreCountdown"
          class="absolute inset-0 flex items-center justify-center pointer-events-none"
        >
          <span class="text-9xl font-bold text-white drop-shadow-[0_4px_8px_rgba(0,0,0,0.5)]">
            {{ preCountdown }}
          </span>
        </div>
        <!-- Recording timer -->
        <div
          v-else
          class="absolute bottom-2 left-1/2 -translate-x-1/2 
                font-bold text-white bg-black/60 rounded-full 
                w-20 h-10 flex items-center justify-center pointer-events-none"
        >
          00:{{ String(countdown).padStart(2, '0') }}
        </div>
      </div>
    </div>
  </Dialog>
</template>

<style>
.fade-out {
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
<script setup>
import { ref, onBeforeUnmount } from "vue";
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';

const { t } = useI18n();
const toast = useToast(); 

const props = defineProps({
  interes: {
    type: String,
    default: "",
  },
  lang: {
    type: String,
    default: "hr",
  },
});

const emit = defineEmits(["topic-generated", "start-recording", "upload-data"]);

const progress = ref(0);
const isCounting = ref(false);

let intervalId = null;
const DURATION = 5_000; // 5 sekundi

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.ENV?.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'

// Store video session data
let videoSessionData = null;

const getRandomTopic = (interest) => {
  const topics = LOCAL_TOPICS[interest] || LOCAL_TOPICS.general;
  return topics[Math.floor(Math.random() * topics.length)];
};

const startTimer = async () => {
  if (isCounting.value) return;

  console.log("[RecordButton] startTimer - starting countdown and calling /start");
  
  // Start the timer immediately
  isCounting.value = true;
  progress.value = 0;
  const start = Date.now();

  intervalId = setInterval(() => {
    const elapsed = Date.now() - start;
    progress.value = Math.min(1, elapsed / DURATION);

    if (elapsed >= DURATION) {
      console.log("[RecordButton] timer finished, starting recording");
      clearInterval(intervalId);
      intervalId = null;
      progress.value = 1;
      isCounting.value = false;

      startRecording();
    }
  }, 1000 / 60);
  
  // Call /start API in parallel (don't wait for it to start the timer)
  try {
    const response = await fetch(`${API_BASE_URL}/video/start`, {
      signal: AbortSignal.timeout(4000)
    });

    if (response.ok) {
      const data = await response.json();
      console.log("[RecordButton] Video session created:", data);
      videoSessionData = data;
    } else if (response.status === 400) {
      const errorData = await response.json();
      if (errorData.detail && errorData.detail.includes("already recorded a video today")) {
        toast.add({
          severity: 'warn',
          summary: t('recorder.error_already_recorded'),
          life: 5000
        });
      } else {
        toast.add({
          severity: 'error',
          summary: t('recorder.error_start'),
          life: 4000
        });
      }
      // Cancel the timer on error
      if (intervalId !== null) {
        clearInterval(intervalId);
        intervalId = null;
      }
      isCounting.value = false;
      progress.value = 0;
      return;
    } else {
      throw new Error(`Server returned ${response.status}`);
    }
  } catch (error) {
    console.error("[RecordButton] Error starting video session:", error);
    toast.add({
      severity: 'error',
      summary: t('recorder.error_start'),
      life: 4000
    });
    // Cancel the timer on error
    if (intervalId !== null) {
      clearInterval(intervalId);
      intervalId = null;
    }
    isCounting.value = false;
    progress.value = 0;
    return;
  }
};

const cancelTimer = async () => {
  console.log("[RecordButton] cancelTimer");
  if (intervalId !== null) {
    clearInterval(intervalId);
    intervalId = null;
  }
  isCounting.value = false;
  progress.value = 0;
  
  // Mark the video as cancelled in the backend
  if (videoSessionData && videoSessionData.video_path) {
    try {
      const videoId = videoSessionData.video_path.split('/').pop().replace('.webm', '');
      await fetch(`${API_BASE_URL}/video/${videoId}/cancel`, {
        method: 'PUT'
      });
      console.log("[RecordButton] Video marked as cancelled");
    } catch (error) {
      console.error("[RecordButton] Error cancelling video:", error);
    }
    videoSessionData = null;
  }
};

onBeforeUnmount(() => {
  if (intervalId !== null) clearInterval(intervalId);
});

const startRecording = () => {
  console.log("[RecordButton] startRecording - emitting data");
  
  if (!videoSessionData) {
    console.error("[RecordButton] No video session data available");
    toast.add({
      severity: 'error',
      summary: t('recorder.error_start'),
      life: 4000
    });
    return;
  }

  emit("upload-data", videoSessionData.upload_method, videoSessionData.upload_url, videoSessionData.user_id, videoSessionData.video_path);
  emit("topic-generated", videoSessionData.interest, videoSessionData.topic, props.lang);
  emit("start-recording", true);
  
  // Clear session data after emitting
  videoSessionData = null;
  progress.value = 0;
};

</script>

<template>
  <div class="relative flex justify-center items-center mx-auto" style="width: fit-content;">
    <!-- Krug sa hover efektom koji ga samo potamni -->
    <div
      class="relative w-48 h-48 md:w-64 md:h-64 rounded-full shadow-lg flex items-center justify-center hover:cursor-pointer transition-all duration-200 hover:brightness-90"
             style="background: radial-gradient(circle, rgba(196, 234, 254, 0.8), var(--color-primary));"
      @click="!isCounting ? startTimer() : null"
    >
      <!-- Progress ring - INSIDE the button -->
      <svg
        v-if="isCounting"
        class="absolute -rotate-90 pointer-events-none"
        :style="{
          width: '100%',
          height: '100%',
          top: '0',
          left: '0'
        }"
        viewBox="0 0 100 100"
      >
        <circle
          cx="50"
          cy="50"
          r="46"
          stroke="rgba(255, 255, 255, 0.8)"
          stroke-width="4"
          fill="none"
          stroke-dasharray="289.03"
          :stroke-dashoffset="289.03 - 289.03 * progress"
          class="transition-all duration-100"
        />
      </svg>

      <!-- Mikrofon ikona - u sredini kada se ne broji -->
      <span
        v-if="!isCounting"
        class="pi pi-microphone text-white record-icon"
      ></span>

      <!-- X za prekid tijekom brojanja - zamjena ikone -->
      <span
        v-else
        class="text-white record-icon hover:text-red-300 transition-colors cursor-pointer"
        @click.stop="cancelTimer"
      >
        ✖
      </span>
    </div>
  </div>
</template>

<style scoped>
.record-icon {
  font-size: 6rem; /* Fits inside w-48 (12rem) */
  line-height: 1;
}

@media (min-width: 768px) {
  .record-icon {
    font-size: 8rem; /* Fits inside w-64 (16rem) */
  }
}

.pi-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

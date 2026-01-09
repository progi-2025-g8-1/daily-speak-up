<script setup>
import { ref, onBeforeUnmount } from "vue";

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
const isGeneratingTopic = ref(false);

let intervalId = null;
let progressIntervalId = null;
const DURATION = 5_000; // 5 sekundi
const TOPIC_GENERATION_DURATION = 5_000; // 5 sekundi za generiranje

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.ENV?.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'

const getRandomTopic = (interest) => {
  const topics = LOCAL_TOPICS[interest] || LOCAL_TOPICS.general;
  return topics[Math.floor(Math.random() * topics.length)];
};

const startTimer = () => {
  if (isCounting.value) return;

  console.log("[RecordButton] startTimer");
  isCounting.value = true;
  progress.value = 0;
  const start = Date.now();

  intervalId = setInterval(() => {
    const elapsed = Date.now() - start;
    progress.value = Math.min(1, elapsed / DURATION);

    if (elapsed >= DURATION) {
      console.log("[RecordButton] timer finished, calling generateTopic");
      clearInterval(intervalId);
      intervalId = null;
      progress.value = 1;
      isCounting.value = false;

      generateTopic();
    }
  }, 1000 / 60);
};

const cancelTimer = () => {
  console.log("[RecordButton] cancelTimer");
  if (intervalId !== null) {
    clearInterval(intervalId);
    intervalId = null;
  }
  isCounting.value = false;
  // Ne resetuj progress - ostaje ring na mjestu gdje je stao
};

onBeforeUnmount(() => {
  if (intervalId !== null) clearInterval(intervalId);
  if (progressIntervalId !== null) clearInterval(progressIntervalId);
});

const generateTopic = async () => {
  console.log("[RecordButton] generateTopic START");

  isGeneratingTopic.value = true;
  // Ne resetuj progress - nastavi od gdje je ring stao
  const start = Date.now();

  // Pokreni progress ring za 5 sekundi tijekom generiranja
  progressIntervalId = setInterval(() => {
    const elapsed = Date.now() - start;
    // Ring ide od 1 do 1 (već je na kraju od brojanja, ostaje na kraju)
    progress.value = 1;

    if (elapsed >= TOPIC_GENERATION_DURATION) {
      clearInterval(progressIntervalId);
      progress.value = 1;
    }
  }, 1000 / 60);

  try {
    // Pokušaj preuzeti temu sa backend servisa
    const response = await fetch(`${API_BASE_URL}/video/start`, {
      signal: AbortSignal.timeout(4000) // Timeout nakon 4 sekunde
    });

    if (response.ok) {
      const data = await response.json();
      console.log("[RecordButton] tema od backend-a:", data);
      
      // Čekaj da se progress ring završi
      await new Promise(resolve => setTimeout(resolve, Math.max(0, TOPIC_GENERATION_DURATION - (Date.now() - start))));
      clearInterval(progressIntervalId);
      progress.value = 1; // Ostavi na kraju
      isGeneratingTopic.value = false;

      emit("upload-data", data.upload_method, data.upload_url, data.user_id, data.video_path);
      emit("topic-generated", data.interest, data.topic, props.lang);
      emit("start-recording", true);
      return;
    } else {
      throw new Error(`Server returned ${response.status}`);
    }
  } catch (error) {
    console.error("[RecordButton] Error starting video session:", error);
    alert("Greška pri pokretanju sesije snimanja. Provjerite vezu ili pokušajte ponovno.");
  } finally {
    clearInterval(progressIntervalId);
    isGeneratingTopic.value = false;
    progress.value = 0;
  }
};
</script>

<template>
  <div class="relative flex justify-center items-center mx-auto" style="width: fit-content;">
    <!-- Progress ring - IZVAN kruga, veći od kruga -->
    <svg
      v-if="isCounting || isGeneratingTopic"
      class="absolute -rotate-90 pointer-events-none"
      :style="{
        width: 'calc(100% + 40px)',
        height: 'calc(100% + 40px)',
        top: '-20px',
        left: '-20px'
      }"
      viewBox="0 0 100 100"
    >
      <circle
        cx="50"
        cy="50"
        r="48"
        stroke="rgba(255, 255, 255, 0.6)"
        stroke-width="3"
        fill="none"
        stroke-dasharray="301.59"
        :stroke-dashoffset="301.59 - 301.59 * progress"
        class="transition-all duration-100"
      />
    </svg>

    <!-- Krug sa hover efektom koji ga samo potamni -->
    <div
      class="relative w-[22vw] h-[22vw] 2xl:w-[16vw] 2xl:h-[16vw] rounded-full
             bg-[radial-gradient(circle,_#c4eafe,_#38bdf8)]
             shadow-lg flex items-center justify-center
             hover:cursor-pointer transition-all duration-200
             hover:brightness-90"
      @click="!isCounting ? startTimer() : null"
    >
      <!-- Mikrofon ikona - u sredini kada se ne broji -->
      <span
        v-if="!isCounting && !isGeneratingTopic"
        class="pi pi-microphone text-white"
        style="font-size: 9vw;"
      ></span>

      <!-- X za prekid tijekom brojanja - zamjena ikone -->
      <span
        v-else-if="isCounting"
        class="text-white text-6xl hover:text-red-300 transition-colors cursor-pointer"
        @click.stop="cancelTimer"
      >
        ✖
      </span>

      <!-- Animirani spinner tijekom generiranja tema -->
      <span
        v-else
        class="text-white"
        style="font-size: 9vw;"
      >
        <i class="pi pi-spin pi-spinner text-white"></i>
      </span>
    </div>
  </div>
</template>

<style scoped>
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

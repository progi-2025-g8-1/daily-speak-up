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

const emit = defineEmits(["topic-generated", "start-recording"]);

const progress = ref(0);
const isCounting = ref(false);

let intervalId = null;
const DURATION = 10_000;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.ENV?.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'

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
  progress.value = 0;
};

onBeforeUnmount(() => {
  if (intervalId !== null) clearInterval(intervalId);
});

const generateTopic = async () => {
  console.log("[RecordButton] generateTopic START", {
    interes: props.interes,
    lang: props.lang,
  });

  try {
    const response = await fetch(`${API_BASE_URL}/userdata/topic`);

    console.log("[RecordButton] response status:", response);

    if (!response.ok) {
      // i u slučaju greške emitiramo nešto
      const msg = "🫣 Oops! Trenutni AI servis je preopterećen. Pokušaj ponovno za 1 minutu.";
      console.error("[RecordButton]", msg);
      emit("topic-generated", msg, props.lang);
      emit("start-recording", true);
      return;
    }

    const data = await response.json();
    console.log("[RecordButton] data from backend:", data);

    emit("topic-generated", data.interest ?? "Nije odabran interes", data.topic ?? "Nema teme u odgovoru", data.lang ?? props.lang);
    emit("start-recording", true);
  } catch (error) {
    console.error("[RecordButton] fetch error:", error);
    // čak i ako fetch pukne, prikaži poruku u Fieldsetu
    emit("topic-generated", props.interes, "🫣 Oops! Trenutni AI servis je preopterećen. Pokušaj ponovno za 1 minutu.", props.lang);
  }
};
</script>

<template>
  <div class="relative flex justify-center items-center mx-auto">
    <!-- Krug sa hover efektom koji ga samo potamni -->
    <div
      class="w-[22vw] h-[22vw] 2xl:w-[16vw] 2xl:h-[16vw] rounded-full
             bg-[radial-gradient(circle,_#c4eafe,_#38bdf8)]
             shadow-lg flex items-center justify-center
             hover:cursor-pointer transition-all duration-200
             hover:brightness-90"
      @click="isCounting ? cancelTimer() : startTimer()"
    >
      <!-- Mikrofon -->
      <span
        v-if="!isCounting"
        class="pi pi-microphone text-white"
        style="font-size: 9vw;"
      ></span>

      <!-- X za prekid -->
      <span
        v-else
        class="text-white"
        style="font-size: 9vw;"
        @click.stop="cancelTimer"
      >
        ✖
      </span>
    </div>

    <!-- Progress ring -->
    <svg
      v-if="isCounting"
      class="absolute w-full h-full -rotate-90 pointer-events-none"
      viewBox="0 0 100 100"
    >
      <circle
        cx="50"
        cy="50"
        r="48"
        stroke="#38bdf8"
        stroke-width="4"
        fill="none"
        stroke-dasharray="301.59"
        :stroke-dashoffset="301.59 - 301.59 * progress"
        class="transition-all duration-100"
      />
    </svg>
  </div>
</template>

<style scoped>
</style>

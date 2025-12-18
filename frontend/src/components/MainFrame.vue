<script setup lang="ts">
import { ref } from "vue";
import NavBar from "./NavBar.vue";
import RecordButton from "./RecordButton.vue";
import Fieldset from "primevue/fieldset";
import VideoFrame from "./VideoFrame.vue";
import type { VideoFrameInstance } from "../types/video-frame";
 
const topic = ref<string | null>(null);
const interest = ref<string>("");
const lang = ref<string>("hr");
const videoFrame = ref<VideoFrameInstance | null>(null)


const handleTopicGenerated = (interes: string, tema: string, generatedLang: string) => {
  console.log("[Page] topic-generated event:", tema, generatedLang);
  topic.value = tema;
  interest.value = interes
  // lang.value = generatedLang; // ako želiš
};

const handleStartRecording = (start: boolean) => {
  if (start && videoFrame.value) {
    videoFrame.value.startRecording();
  }
};

</script>

<template>
  <div
    class="flex flex-col justify-start items-center bg-sky-100 w-[100vw] h-[60vh] lg:w-[65%] lg:h-full"
  >
    <NavBar />

    <div
      class="w-full h-[53vh] lg:h-full flex flex-col justify-around items-center "
    >
      <div
        class="border-black justify-center
                font-sans text-[1.5vw] font-semibold text-center"
      >
        <h1>Start practicing!</h1>
      </div>

      <div class="my-[5vh]">
        <RecordButton
          :interes="interest"
          :lang="lang"
          @topic-generated="handleTopicGenerated"
          @start-recording="handleStartRecording"
        />
      </div>

      <VideoFrame ref="videoFrame"/>

      <div>
        <Fieldset legend="Tema za govor" :toggleable="true">
          <p class="m-0 font-bold" v-if="interest">
            Interes: {{ interest }}
          </p>
          <p class="m-0" v-if="topic">
            {{ topic }}
          </p>
          <p class="m-0" v-else>
            Vaša će se tema za govor pojaviti ovdje nakon što pritisnete gumb
            za snimanje.
          </p>
        </Fieldset>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>

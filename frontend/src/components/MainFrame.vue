<script setup lang="ts">
import { ref } from "vue";
import NavBar from "./NavBar.vue";
import RecordButton from "./RecordButton.vue";
import Fieldset from "primevue/fieldset";

const emit = defineEmits(["start-recording", "upload-data", "topic-generated"]);
 
const topic = ref<string | null>(null);
const interest = ref<string>("");
const lang = ref<string>("hr");

const handleTopicGenerated = (interes: string, tema: string, generatedLang: string) => {
  console.log("[Page] topic-generated event:", tema, generatedLang);
  topic.value = tema;
  interest.value = interes;
  emit("topic-generated", interes, tema);
  // lang.value = generatedLang; // ako želiš
};

const handleStartRecording = (start: boolean) => {
  if(start){
    emit("start-recording", start);
  }
};

const handleUploadData = (uploadMethod: string, uploadUrl: string, userId: string, videoPath: string) => {
  emit("upload-data", uploadMethod, uploadUrl, userId, videoPath);
};

</script>

<template>
  <div
    class="flex flex-col justify-start items-center bg-sky-100 w-[100vw] lg:w-[60vw] h-full"
  >
    <NavBar />

    <div
      class="w-full h-full flex flex-col justify-around items-center "
    >
      <h1 class="font-sans text-4xl font-semibold text-center">Započnite vježbu!</h1>

      <div class="my-[5vh]">
        <RecordButton
          :interes="interest"
          :lang="lang"
          @topic-generated="handleTopicGenerated"
          @start-recording="handleStartRecording"
          @upload-data="handleUploadData"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>

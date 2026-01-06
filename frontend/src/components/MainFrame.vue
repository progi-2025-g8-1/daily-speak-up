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
    class="flex flex-col justify-start items-center w-[100vw] lg:w-[60vw] h-full"
    style="background-color: var(--color-bg-main);"
  >
    <NavBar />

    <div
      class="w-full h-[53vh] lg:h-full flex flex-col justify-around items-center "
    >
      <div
        class="justify-center font-sans text-[1.1vw] font-semibold text-center"
        style="border: 1px solid var(--color-border-primary); color: var(--color-text-primary);"
      >
        <h1>Započnite vježbu!</h1>
      </div>

      <div class="my-[5vh]">
        <RecordButton
          :interes="interest"
          :lang="lang"
          @topic-generated="handleTopicGenerated"
          @start-recording="handleStartRecording"
          @upload-data="handleUploadData"
        />
      </div>

      <div>
        <Fieldset legend="Tema za govor" :toggleable="true" style="--p-fieldset-legend-color: var(--color-primary); --p-fieldset-background: var(--color-bg-card); --p-fieldset-border-color: var(--color-primary);">
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
/* Osnovna boja gumba */
:deep(.p-button) {
  background-color: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
  color: #fff !important;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Hover stanje */
:deep(.p-button:hover) {
  background-color: var(--color-primary-dark) !important;
  border-color: var(--color-primary-dark) !important;
}

/* Fokus (da ne posvijetli) */
:deep(.p-button:focus) {
  box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.3) !important;
}


:deep(.p-button:disabled) {
  background-color: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
  opacity: 0.6;
}

</style>

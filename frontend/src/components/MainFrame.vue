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
      class="w-full h-[53vh] lg:h-full flex flex-col justify-around items-center "
    >
      <div
        class="border-black justify-center
                font-sans text-[1.5vw] font-semibold text-center"
      >
        <h1>{{ $t('main.start_exercise') }}</h1>
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
        <Fieldset :legend="$t('main.speech_topic_title')" 
        :toggleable="true"
        :pt="{
          legendLabel: { style: 'color: #000000 !important' }
          }" 
        >
          <p class="m-0 font-bold" v-if="interest">
            {{ $t('main.interest_label') }} {{ interest }}
          </p>
          <p class="m-0" v-if="topic">
            {{ topic }}
          </p>
          <p class="m-0" v-else>
            {{ $t('main.topic_placeholder') }}
          </p>
        </Fieldset>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>

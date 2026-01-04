<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import ReportFrame from './ReportFrame.vue';
import Paginator from 'primevue/paginator';
import Skeleton from 'primevue/skeleton';
import Dialog from 'primevue/dialog';
import type { ReportInfo } from '../types/report-info';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'
const videos = ref<ReportInfo[]>([]);
const first = ref(0);
const showReasonDialog = ref(false);
const reportReasons = ref<string[]>([]);
const numOfRowsPerPage = ref(2);
const numOfPageLinks = ref(3);

const firstVideo = computed(() => videos.value[first.value]);
const secondVideo = computed(() => videos.value[first.value + 1]);

const handleShowReasons = (reportInfo: ReportInfo) => {
    reportReasons.value = reportInfo.report_reasons;
    showReasonDialog.value = true;
};

onMounted(async () => {
    const response = await fetch(`${API_BASE_URL}/dashboard/reported-videos`);
    if(response.ok) {
        const data = await response.json();
        videos.value = data;
        console.log(videos.value);
    } else {
        console.error('Failed to fetch reported videos:', response.statusText);
    }
    numOfRowsPerPage.value = window.innerWidth < 768 ? 1 : 2;
    numOfPageLinks.value = window.innerWidth < 640 ? 3 : 5;

    window.addEventListener('resize', () => {
        numOfRowsPerPage.value = window.innerWidth < 768 ? 1 : 2;
        numOfPageLinks.value = window.innerWidth < 640 ? 3 : 5;
    });
});
</script>

<template>
    <Dialog header="Razlozi prijave" 
            v-model:visible="showReasonDialog" 
            :modal="true" 
            :closable="true" 
            class="lg:w-1/3 md:w-2/3 w-4/5">
        <ul class="list-disc pl-5">
            <li v-for="(reason, index) in reportReasons" :key="index" class="mb-2">
                {{ reason }}
            </li>
        </ul>
    </Dialog>
    <div class="flex flex-col justify-center items-center gap-6 w-full h-full">
        <div v-if="!firstVideo" class="w-[90%] h-[30em] flex flex-col justify-center gap-10">
            <div class="flex h-full w-full flex-row justify-center items-center gap-10">
                <div class="w-full md:w-1/2 h-full">
                    <Skeleton class="h-full w-full" height="100%"></Skeleton>
                </div>
                <div class="hidden md:block w-1/2 h-full">
                    <Skeleton class="w-full h-full" height="100%"></Skeleton>
                </div>
            </div>
            <Skeleton class="w-full" height="20%"></Skeleton>
        </div>
        <div class="w-full flex flex-col lg:flex-row justify-evenly items-center gap-10">
            <ReportFrame
                class="lg:w-1/2 w-full"
                v-if="firstVideo"
                :reportInfo="firstVideo"
                @showReasons="handleShowReasons"
            />

            <ReportFrame
                class="lg:w-1/2 hidden lg:block"
                v-if="secondVideo"
                :reportInfo="secondVideo"
                @showReasons="handleShowReasons"
            />
        </div>
        <Paginator 
            v-if="firstVideo"
            v-model:first="first" 
            :rows="numOfRowsPerPage" 
            :pageLinkSize="numOfPageLinks"
            :totalRecords="videos.length"
            template="FirstPageLink PageLinks LastPageLink CurrentPageReport JumpToPageInput"
        ></Paginator>
    </div>
</template>

<style scoped>
    .p-paginator-jtp-input {
       --p-paginator-jump-to-page-input-max-width: 4rem;
    }
</style>
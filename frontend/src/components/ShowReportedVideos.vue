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
});
</script>

<template>
    <Dialog header="Razlozi prijave" v-model:visible="showReasonDialog" :modal="true" :closable="true" :style="{ width: '35vw' }">
        <ul class="list-disc pl-5">
            <li v-for="(reason, index) in reportReasons" :key="index" class="mb-2">
                {{ reason }}
            </li>
        </ul>
    </Dialog>
    <div class="flex flex-col justify-center items-center gap-9 w-full h-full">
        <div v-if="!firstVideo" class="w-[90%] h-[30em] flex flex-col justify-center gap-10">
            <div class="flex h-full w-full flex-row justify-center items-center gap-10">
                <Skeleton class="w-1/2 h-full" height="100%"></Skeleton>
                <Skeleton class="w-1/2 h-full" height="100%"></Skeleton>
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
                class="lg:w-1/2 w-full"
                v-if="secondVideo"
                :reportInfo="secondVideo"
                @showReasons="handleShowReasons"
            />
        </div>
        <Paginator 
            v-if="firstVideo"
            v-model:first="first" 
            :rows="2" 
            :totalRecords="videos.length"
            template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink JumpToPageDropdown"
        ></Paginator>
    </div>
</template>
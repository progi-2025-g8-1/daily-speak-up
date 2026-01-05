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
const numOfRowsPerPage = ref(2);
const numOfPageLinks = ref(3);

const firstVideo = computed(() => videos.value[first.value]);
const secondVideo = computed(() => videos.value[first.value + 1]);

const handleShowReasons = (reportInfo: ReportInfo) => {
    showReasonDialog.value = true;
};

onMounted(async () => {
    const response = await fetch(`${API_BASE_URL}/dashboard/reported-videos`);
    if(response.ok) {
        const data = await response.json();
        videos.value = data;
    } else {
        console.error('Failed to fetch reported videos:', response.statusText);
    }
    numOfRowsPerPage.value = window.innerWidth < 1024 ? 1 : 2;
    numOfPageLinks.value = window.innerWidth < 640 ? 3 : 5;

    window.addEventListener('resize', () => {
        numOfRowsPerPage.value = window.innerWidth < 1024 ? 1 : 2;
        numOfPageLinks.value = window.innerWidth < 640 ? 3 : 5;
    });
});
</script>

<template>
    <Dialog header="Upute za prijavljene videozapise" 
            v-model:visible="showReasonDialog" 
            :modal="true" 
            :closable="true" 
            :draggable="false"
            class="lg:w-2/3 md:w-3/4 w-[95%]">
        <ul class="list-disc pl-5 space-y-2">
            <li>
                Opis videozapisa i razlozi zbog kojih je video prijavljen nalaze se u kliznom okviru svakog prijavljenog videozapisa.
            </li>
            <li>
                Možete poduzeti radnje kao što su brisanje prijave, brisanje videozapisa ili uručenje zabrane koristeći odgovarajuće gumbe na okviru prijave.
                
                <ul class="list-disc pl-5 mt-2 space-y-1">
                    <li>
                        Brisanje prijave, pritiskom na dugme s ikonom <span class="pi pi-angle-double-left text-purple-600"></span>, uklanja samo prijavu, odbacuje ju u sustavu.
                    </li>
                    <li>
                        Brisanje videozapisa, pritiskom na dugme s ikonom <span class="pi pi-delete-left text-orange-600"></span>, trajno uklanja videozapis s platforme.
                    </li>
                    <li>
                        Uručivanje zabrane korisniku pritiskom na dugme s ikonom <span class="pi pi-times text-red-600"></span> sprječava korisnika da prenosi nove videozapise na platformu.
                    </li>
                </ul>
            </li>
        </ul>
    </Dialog>
    
    <div class="flex flex-col 
                items-center 
                w-full min-h-full 
                py-6 px-4 space-y-6">

        <div v-if="!firstVideo" class="w-full max-w-7xl 
                                  h-full space-y-6">

            <div class="flex flex-col 
                        md:flex-row 
                        gap-6 h-full">

                <div class="w-full md:w-1/2 
                            h-full">

                    <Skeleton class="w-full !h-60" ></Skeleton>

                </div> 

                <div class="hidden 
                            md:block w-1/2
                            h-full">
                            
                    <Skeleton class="w-full !h-60"></Skeleton>
                    
                </div>

            </div>

            <Skeleton class="w-full !h-10"></Skeleton>

        </div>

        <div v-else class="w-full max-w-7xl space-y-6">
            <div class="flex flex-col lg:flex-row gap-6 lg:gap-10">
                <ReportFrame
                    class="w-full lg:w-1/2"
                    :reportInfo="firstVideo"
                    @showReasons="handleShowReasons"
                />

                <ReportFrame
                    class="w-full lg:w-1/2 hidden lg:block"
                    v-if="secondVideo"
                    :reportInfo="secondVideo"
                    @showReasons="handleShowReasons"
                />
            </div>
            
            <Paginator 
                v-model:first="first" 
                :rows="numOfRowsPerPage" 
                :pageLinkSize="numOfPageLinks"
                :totalRecords="videos.length"
                template="FirstPageLink PageLinks LastPageLink CurrentPageReport JumpToPageInput"
            ></Paginator>
        </div>
    </div>
</template>

<style scoped>
    .p-paginator-jtp-input {
       --p-paginator-jump-to-page-input-max-width: 4rem;
    }
</style>
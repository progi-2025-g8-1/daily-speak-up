<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from 'vue';
import ReportFrame from './ReportFrame.vue';
import ConfirmBanDialog from './ConfirmBanDialog.vue';
import { useConfirm } from "primevue/useconfirm";
import Paginator from 'primevue/paginator';
import Skeleton from 'primevue/skeleton';
import Dialog from 'primevue/dialog';
import type { ReportInfo } from '../types/report-info';
import { outlined } from '@primeuix/themes/aura/message';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'
const videos = ref<ReportInfo[]>([]);
const first = ref(0);
const showReasonDialog = ref(false);
const numOfRowsPerPage = ref(2);
const numOfPageLinks = ref(3);
const banReasons = ref<any[] | undefined>(undefined);
const showBanConfirmDialog = ref(false);
const banHandle = ref<string | null | undefined>(null);
const banUserId = ref<string | null | undefined>(null);

const firstVideo = computed(() => videos.value[first.value]);
const secondVideo = computed(() => videos.value[first.value + 1]);
const confirm = useConfirm();

const handleShowInstructions = () => {
      console.log('show instructions');
    showReasonDialog.value = true;
};

const showConfirmBanDialog = (user_id: string, handle: string, reasons: string[] | undefined) => {
    const updatedReasons = reasons ? [...reasons, 'Prilagođeni razlog'] : ['Prilagođeni razlog'];
    let reasonObjectList = [];
    for (let reason of updatedReasons) {
        reasonObjectList.push({name: reason});
    }
    banReasons.value = reasonObjectList;
    banHandle.value = handle;
    banUserId.value = user_id;
    showBanConfirmDialog.value = true;
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

onBeforeUnmount(() => {
    window.removeEventListener('resize', () => {
        numOfRowsPerPage.value = window.innerWidth < 1024 ? 1 : 2;
        numOfPageLinks.value = window.innerWidth < 640 ? 3 : 5;
    });
});

const handleDismissReport = (video_id: string) => {
    confirm.require({
        message: 'Jeste li sigurni da želite obrisati ovu prijavu?',
        header: 'Potvrda brisanja prijave',
        icon: 'pi pi-exclamation-triangle',
        acceptProps: { label: 'Obriši prijavu', icon: 'pi pi-times', severity: 'danger' },
        rejectProps: { label: 'Odustani', outlined: true, severity: 'secondary' },
        accept: async () => {
            const response = await fetch(`${API_BASE_URL}/dashboard/dismiss-reports/${video_id}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                videos.value = videos.value.filter(video => video.video_id !== video_id);
            } else {
                console.error('Failed to dismiss report:', response.statusText);
            }
        },
        reject: () => {
        }
    });

};

const handleDeleteVideo = (video_id: string) => {
    confirm.require({
        message: 'Jeste li sigurni da želite obrisati ovaj videozapis?',
        header: 'Potvrda brisanja videozapisa',
        icon: 'pi pi-exclamation-triangle',
        acceptProps: { label: 'Obriši video', icon: 'pi pi-times', severity: 'danger' },
        rejectProps: { label: 'Odustani', outlined: true, severity: 'secondary' },
        accept: async () => {
            const response = await fetch(`${API_BASE_URL}/video/${video_id}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                videos.value = videos.value.filter(video => video.video_id !== video_id);
            } else {
                console.error('Failed to delete video:', response.statusText);
            }
        },
        reject: () => {
        }
    });

};
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

    <ConfirmBanDialog :reasons="banReasons"
                      :handle="banHandle"
                      :userId="banUserId"
                      v-model:showDialog="showBanConfirmDialog" />
    
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
                    @showInstructions="handleShowInstructions"
                    @banUser="showConfirmBanDialog"
                    @dismissReport="handleDismissReport"
                    @deleteVideo="handleDeleteVideo"
                />

                <ReportFrame
                    class="w-full lg:w-1/2 hidden lg:block"
                    v-if="secondVideo"
                    :reportInfo="secondVideo"
                    @showInstructions="handleShowInstructions"
                    @banUser="showConfirmBanDialog"
                    @dismissReport="handleDismissReport"
                    @deleteVideo="handleDeleteVideo"
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
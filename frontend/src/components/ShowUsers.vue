<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import ConfirmBanDialog from './ConfirmBanDialog.vue';
import DataView from 'primevue/dataview';
import Avatar from 'primevue/avatar';
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import ToggleButton from 'primevue/togglebutton';



const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'
const users = ref([]);
const showUsers = ref([]);
const rowHeight = ref(0);
const containerHeight = ref(0);
const handles = ref<string[]>([]);
const searchValue = ref(null)
const banReasons = ref<any[] | undefined>(undefined);
const showBanConfirmDialog = ref(false);
const banHandle = ref<string | null | undefined>(null);
const banUserId = ref<string | null | undefined>(null);


const rowsPerPage = computed(() => {
    if (rowHeight.value === 0 || containerHeight.value === 0) return 5;
    const paginatorHeight = 60; 
    const availableHeight = containerHeight.value - paginatorHeight;
    
    return Math.floor(availableHeight / rowHeight.value);
});

onMounted(async () => {
    const response = await fetch(`${API_BASE_URL}/dashboard/users`);
    if(response.ok) {
        const data = await response.json();
        users.value = data;
        showUsers.value = data;
        handles.value = data.map((user: any) => user.handle);
        setTimeout(() => {
            measureDimensions();
        }, 100);
    } else {
        console.error('Failed to fetch users:', response.statusText);
    }
    
    window.addEventListener('resize', measureDimensions);
});

const search = (event: { query: string }) => {
    const query = event.query.toLowerCase();

    let query_result = users.value
        .map((user: any) => user.handle)
        .filter((handle: string) => handle.toLowerCase().includes(query));
    handles.value = query_result;
    showUsers.value = users.value.filter((user: any) => 
        user.handle.toLowerCase().includes(query)
    );
};

const resetUsers = () => {
    handles.value = users.value.map((user: any) => user.handle);
    showUsers.value = users.value;
};

const measureDimensions = () => {
    const firstRow = document.querySelector('.user-row');
    if (firstRow) {
        rowHeight.value = firstRow.getBoundingClientRect().height;
    }
    
    const container = document.querySelector('.dataview-container');
    if (container) {
        containerHeight.value = container.getBoundingClientRect().height;
    }
};

const showConfirmBanDialog = async (user: any) => {

    const response = await fetch(`${API_BASE_URL}/dashboard/report-reasons/${user.user_id}`);
    if(response.ok) {
        let data = await response.json();
        data.push('Prilagođeni razlog');
        let reasonObjectList = [];
        for (let reason of data) {
            reasonObjectList.push({name: reason});
        }
        banReasons.value = reasonObjectList;
    } else {
        console.error('Failed to fetch ban reasons:', response.statusText);
        banReasons.value = [{name: 'Prilagođeni razlog'}];
    }

    banHandle.value = user.handle;
    banUserId.value = user.user_id;
    showBanConfirmDialog.value = true;
};

</script>

<template>
    <ConfirmBanDialog :reasons="banReasons"
                      :handle="banHandle"
                      :userId="banUserId"
                     v-model:showDialog="showBanConfirmDialog" />

   <div class="flex flex-col justify-center items-center gap-2">
        <div class="w-full flex justify-center items-center">
            <AutoComplete v-model="searchValue" placeholder="Pretraži korisnike po korisničkom imenu..." :suggestions="handles" :dropdown="false" @complete="search" @clear="resetUsers"/> 
        </div>

        <div class="dataview-container w-[90%]" style="height: calc(100vh - 215px)">
            <DataView :value="showUsers" paginator :rows="rowsPerPage">
                <template #list="slotProps">
                    <div class="flex flex-col">
                        <div v-for="(item, index) in slotProps.items" :key="index" class="user-row">
                            <div class="flex flex-row items-center justify-between py-3 border-b border-gray-400">
                                <div class="flex flex-row justify-start items-center">
                                    <div class="md:w-40 flex flex-col justify-center items-center">
                                        <Avatar :image="item.profile_picture_url" shape="circle" />
                                    </div>
                                    <div class="flex flex-col justify-start items-start">
                                        <div class="text-lg font-medium">{{ item.handle }}</div>
                                        <div class="font-medium text-surface-500 dark:text-surface-400 text-sm">{{ item.email }}</div>
                                    </div>
                                </div>
                                <div class="flex flex-row gap-4 mr-8">
                                    <Button icon="pi pi-video" rounded variant="outlined" aria-label="Videos" v-tooltip.top="{ value: 'Prikaži videozapise', showDelay: 500, hideDelay: 100 }" />
                                    <Button icon="pi pi-times" severity="danger" rounded variant="outlined" aria-label="Ban" v-tooltip.top="{ value: 'Uruči zabranu', showDelay: 500, hideDelay: 100 }" :onClick="() => showConfirmBanDialog(item)" />
                                    <ToggleButton onLabel="Moderator" offLabel="Korisnik" onIcon="pi pi-user-edit" offIcon="pi pi-user" class="w-36" aria-label="Do you confirm" v-tooltip.top="{ value: 'Promijeni ulogu', showDelay: 500, hideDelay: 100 }" />
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </DataView>
        </div>
    </div>
</template>

<style scoped>
:deep(.p-autocomplete) {
    display: flex;
    justify-content: center;
    width: 100%;
}

:deep(.p-autocomplete .p-autocomplete-input) {
    width: 60%;
    --p-inputtext-border-color: gray;
}

.p-avatar {
    --p-avatar-width: 5vw;
    --p-avatar-height: 5vw;
}

.dataview-container {
    overflow: hidden;
}

.p-togglebutton {
    --p-togglebutton-checked-color: rgb(123, 56, 128);
    --p-togglebutton-checked-border-color: rgb(123, 56, 128);
    --p-togglebutton-icon-checked-color: rgb(123, 56, 128);
    --p-togglebutton-checked-background: rgb(255, 248, 254);
}

</style>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DataView from 'primevue/dataview';
import Avatar from 'primevue/avatar';
import AutoComplete from 'primevue/autocomplete';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'
const users = ref([]);
const rowHeight = ref(0);
const containerHeight = ref(0);
const handles = ref([]);
const searchValue = ref(null)

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
        handles.value = data.map((user: any) => user.handle);
        setTimeout(() => {
            measureDimensions();
        }, 100);
    } else {
        console.error('Failed to fetch users:', response.statusText);
    }
    
    // Recalculate on window resize
    window.addEventListener('resize', measureDimensions);
});

const search = (event: { query: string }) => {
    const query = event.query.toLowerCase();
    handles.value = users.value
        .map((user: any) => user.handle)
        .filter((handle: string) => handle.toLowerCase().includes(query));
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
</script>

<template>
   <div class="flex flex-col justify-end gap-2">
        <div class="w-full flex justify-center items-center">
            <AutoComplete v-model="searchValue" placeholder="Pretraži korisnike po korisničkom imenu..." :suggestions="handles" @complete="search"/> 
        </div>

        <div class="dataview-container w-full" style="height: calc(100vh - 215px)">
            <DataView :value="users" paginator :rows="rowsPerPage">
                <template #list="slotProps">
                    <div class="flex flex-col">
                        <div v-for="(item, index) in slotProps.items" :key="index" class="user-row">
                            <div class="flex flex-row items-center justify-start py-3 border-b border-surface-200">
                                <div class="md:w-40 flex flex-col justify-center items-center">
                                    <Avatar :image="item.profile_picture_url" shape="circle" />
                                </div>
                                <div class="flex flex-col justify-start items-start">
                                    <div class="text-lg font-medium">{{ item.handle }}</div>
                                    <div class="font-medium text-surface-500 dark:text-surface-400 text-sm">{{ item.email }}</div>
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
</style>
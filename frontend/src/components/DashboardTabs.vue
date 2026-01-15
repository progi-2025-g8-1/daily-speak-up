<script setup lang="ts">
    import { ref, onMounted } from 'vue';
    import Tabs from 'primevue/tabs';
    import TabList from 'primevue/tablist';
    import Tab from 'primevue/tab';
    import TabPanels from 'primevue/tabpanels';
    import TabPanel from 'primevue/tabpanel';
    import ShowUsers from './ShowUsers.vue';
    import ShowReportedVideos from './ShowReportedVideos.vue';
    import ShowBans from './ShowBans.vue';
    import ConfirmDialog from 'primevue/confirmdialog';
    import ShowStats from './ShowStats.vue';
    import type { ShowBansInterface } from '../types/show-bans';
    import type { RefreshStatsInterface } from '../types/stats-types';

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1/';

    const activeTab = ref('1');
    const showBansRef = ref<ShowBansInterface | null>(null);
    const showAdminTabs = ref(false);
    const showStatsRef = ref<RefreshStatsInterface | null>(null);

    onMounted(async () => {
        const userRole = localStorage.getItem('userRole');
        if(userRole === undefined || userRole === null) {
            const response = await fetch(`${API_BASE_URL}/user/me`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const userData = await response.json();
                localStorage.setItem('userRole', userData.role);
                showAdminTabs.value = userData.role === import.meta.env.VITE_ADMIN_ROLE || userData.role === import.meta.env.VITE_ROOT_ROLE;
                activeTab.value = showAdminTabs.value ? '0' : '1';
            }
        } else {
            showAdminTabs.value = userRole === import.meta.env.VITE_ADMIN_ROLE || userRole === import.meta.env.VITE_ROOT_ROLE;
            activeTab.value = showAdminTabs.value ? '0' : '1';
        }
    });

    const handleTabChange = (newValue: string | number) => {
        if (newValue === '2' && showBansRef.value) {
            showBansRef.value.refreshBans();
        }
        if (newValue === '3' && showStatsRef.value) {
            showStatsRef.value.refreshStats();
        }
    };
</script>

<template>
    <ConfirmDialog></ConfirmDialog>
    <Tabs v-model:value="activeTab" class="w-full h-full flex flex-col" @update:value="handleTabChange">
        <TabList>
            <Tab v-if="showAdminTabs" value="0">
                <div :class="['hover:text-blue-600 transition-colors', activeTab === '0' ? 'text-blue-600 font-semibold' : '']">
                    <span class="pi pi-users mr-3"></span>
                    <span>{{ $t('dashboard.tabs.users') }}</span>
                </div>
            </Tab>
            
            <Tab value="1">
                <div :class="['hover:text-amber-600 transition-colors', activeTab === '1' ? 'text-amber-600 font-semibold' : '']">
                    <span class="pi pi-flag mr-3"></span>
                    <span>{{ $t('dashboard.tabs.reported_videos') }}</span>
                </div>
            </Tab>
            
            <Tab value="2">
                <div :class="['hover:text-red-600 transition-colors', activeTab === '2' ? 'text-red-600 font-semibold' : '']">
                    <span class="pi pi-ban mr-3"></span>
                    <span>{{ $t('dashboard.tabs.bans') }}</span>
                </div>
            </Tab>
            
            <Tab v-if="showAdminTabs" value="3">
                <div :class="['hover:text-purple-600 transition-colors', activeTab === '3' ? 'text-purple-600 font-semibold' : '']">
                    <span class="pi pi-chart-pie mr-3"></span>
                    <span>{{ $t('dashboard.tabs.stats') }}</span>
                </div>
            </Tab>
        </TabList>
        
        <TabPanels>
            <TabPanel v-if="showAdminTabs" value="0" class="w-full h-full">
                <ShowUsers />
            </TabPanel>
            <TabPanel value="1" 
                      class="w-full h-full overflow-hidden">
                 <div class="w-full h-full overflow-y-auto">
                    <ShowReportedVideos />
                </div>
            </TabPanel>
            <TabPanel value="2" class="w-full h-full overflow-hidden">
               <div class="w-full h-full overflow-y-auto">
                    <ShowBans ref="showBansRef" />
               </div>
            </TabPanel>
            <TabPanel v-if="showAdminTabs" value="3" class="w-full h-full overflow-hidden">
                <div class="w-full h-full overflow-y-auto">
                    <ShowStats ref="showStatsRef" />
                </div>
            </TabPanel>
        </TabPanels>
    </Tabs>
</template>

<style scoped>

:deep(.p-tabpanels) {
    background-color: rgb(255, 255, 255);
    flex: 1;
    min-height: 0; 
    overflow: hidden;
}

:deep(.p-tabpanel) {
    height: 100%;
}


:deep(.p-tab[data-p-active="true"]) {
    border-bottom: 2px solid transparent !important;
}

:deep(.p-tab[data-pc-name="tab"][data-p-active="true"]:nth-child(1)) {
    border-top-color: rgb(37, 99, 235) !important;
}

:deep(.p-tab[data-pc-name="tab"][data-p-active="true"]:nth-child(2)) {
    border-top-color: rgb(217, 119, 6) !important;
}

:deep(.p-tab[data-pc-name="tab"][data-p-active="true"]:nth-child(3)) {
    border-top-color: rgb(220, 38, 38) !important;
}

:deep(.p-tab[data-pc-name="tab"][data-p-active="true"]:nth-child(4)) {
    border-top-color: rgb(147, 51, 234) !important;
}

:deep(.p-tablist) {
    display: flex;
    justify-content: center;
    flex-shrink: 0; 
}
</style>
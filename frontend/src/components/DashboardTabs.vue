<script setup lang="ts">
    import { ref, onMounted } from 'vue';
    import Tabs from 'primevue/tabs';
    import TabList from 'primevue/tablist';
    import Tab from 'primevue/tab';
    import TabPanels from 'primevue/tabpanels';
    import TabPanel from 'primevue/tabpanel';
    import ShowUsers from './ShowUsers.vue';

    const activeTab = ref('0');
</script>

<template>
    <Tabs v-model:value="activeTab" class="w-full h-full">
        <TabList>
            <Tab value="0">
                <div :class="['hover:text-blue-600 transition-colors', activeTab === '0' ? 'text-blue-600 font-semibold' : '']">
                    <span class="pi pi-users mr-3"></span>
                    <span>Korisnici</span>
                </div>
            </Tab>
            
            <Tab value="1">
                <div :class="['hover:text-amber-600 transition-colors', activeTab === '1' ? 'text-amber-600 font-semibold' : '']">
                    <span class="pi pi-flag mr-3"></span>
                    <span>Prijavljeni videozapisi</span>
                </div>
            </Tab>
            
            <Tab value="2">
                <div :class="['hover:text-red-600 transition-colors', activeTab === '2' ? 'text-red-600 font-semibold' : '']">
                    <span class="pi pi-ban mr-3"></span>
                    <span>Uručene zabrane</span>
                </div>
            </Tab>
            
            <Tab value="3">
                <div :class="['hover:text-purple-600 transition-colors', activeTab === '3' ? 'text-purple-600 font-semibold' : '']">
                    <span class="pi pi-chart-pie mr-3"></span>
                    <span>Statistika</span>
                </div>
            </Tab>
        </TabList>
        
        <TabPanels class="h-full">
            <TabPanel value="0" class="w-full h-full">
                <ShowUsers />
            </TabPanel>
            <TabPanel value="1" class="w-full h-auto">
                <p class="h-full border-black border-1 m-0">
                    Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim
                    ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Consectetur, adipisci velit, sed quia non numquam eius modi.
                </p>
            </TabPanel>
            <TabPanel value="2" class="w-full h-full">
                <p class="h-full border-black border-1 m-0">
                    At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa
                    qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus.
                </p>
            </TabPanel>
            <TabPanel value="3" class="w-full h-full">
                <div class="w-full h-full border-black border-1 m-0 flex items-center justify-center">
                    hahahha
                </div>
            </TabPanel>
        </TabPanels>
    </Tabs>
</template>

<style scoped>
/* Override PrimeVue's default active indicator */
:deep(.p-tab[data-p-active="true"]) {
    border-bottom: 2px solid transparent !important;
}

/* Custom active states for each tab */
:deep(.p-tab[data-pc-name="tab"][data-p-active="true"]:nth-child(1)) {
    border-top-color: rgb(37, 99, 235) !important; /* blue-600 */
}

:deep(.p-tab[data-pc-name="tab"][data-p-active="true"]:nth-child(2)) {
    border-top-color: rgb(217, 119, 6) !important; /* amber-600 */
}

:deep(.p-tab[data-pc-name="tab"][data-p-active="true"]:nth-child(3)) {
    border-top-color: rgb(220, 38, 38) !important; /* red-600 */
}

:deep(.p-tab[data-pc-name="tab"][data-p-active="true"]:nth-child(4)) {
    border-top-color: rgb(147, 51, 234) !important; /* purple-600 */
}

:deep(.p-tablist) {
    display: flex;
    justify-content: center;
}
</style>
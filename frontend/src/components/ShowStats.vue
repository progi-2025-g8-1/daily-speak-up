<script setup lang="ts">
import { ref } from 'vue';
import Card from 'primevue/card';
import UserGrowthChart from './UserGrowthChart.vue';
import SpeechesByInterestChart from './SpeechesByInterestChart.vue';
import DailySpeechActivityChart from './DailySpeechActivityChart.vue';
import Skeleton from 'primevue/skeleton';
import type { RefreshStatsInterface } from '../types/stats-types';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1';

const stats = ref({
    totalUsers: null,
    totalSpeeches: null,
    totalBans: null,
    pendingReports: null
});
const userGrowthChartRef = ref<RefreshStatsInterface | null>(null);
const speechesByInterestChartRef = ref<RefreshStatsInterface | null>(null);
const dailySpeechActivityChartRef = ref<RefreshStatsInterface | null>(null);
    
const refreshStats = async () => {
    stats.value = {
        totalUsers: null,
        totalSpeeches: null,
        totalBans: null,
        pendingReports: null
    };

    const response = await fetch(`${API_BASE_URL}/dashboard/stats/summary`);
    if (response.ok) {
        const data = await response.json();
        stats.value.totalUsers = data.total_users;
        stats.value.totalSpeeches = data.total_speeches;
        stats.value.totalBans = data.total_bans;
        stats.value.pendingReports = data.pending_reports;
    }

    if (userGrowthChartRef.value) {
        userGrowthChartRef.value.refreshStats();
    }
    if (speechesByInterestChartRef.value) {
        speechesByInterestChartRef.value.refreshStats();
    }
    if (dailySpeechActivityChartRef.value) {
        dailySpeechActivityChartRef.value.refreshStats();
    }
};

defineExpose({
    refreshStats
});

</script>

<template>
    <div class=" p-2 md:p-4 lg:p-6 min-h-full">

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <Card class="border-b-[0.2rem] border-blue-600 ">
                <template #content>
                    <div class="flex flex-row items-center gap-4">
                        <div v-if="stats.totalUsers !== null" class="stat-icon bg-blue-100 text-blue-600">
                            <i class="pi pi-users text-2xl"></i>
                        </div>
                        <Skeleton v-else size="3.7rem"></Skeleton>
                        <div class="flex flex-col justify-center items-start">
                            <div v-if="stats.totalUsers !== null" class="text-3xl font-bold text-gray-800">{{ stats.totalUsers }}</div>
                            <Skeleton v-else size="2.5rem" class="mr-2"></Skeleton>
                            <div v-if="stats.totalUsers !== null" class="text-sm text-gray-500">{{ t('admin_dashboard.stats.total_users') }}</div>
                            <Skeleton v-else width="5rem" height="0.7rem" class="mt-2"></Skeleton>
                        </div>
                    </div>
                </template>
            </Card>
            
            <Card class="border-b-[0.2rem] border-purple-600">
                <template #content>
                    <div class="flex flex-row items-center gap-4">
                        <div v-if="stats.totalSpeeches !== null" class="stat-icon bg-purple-100 text-purple-600">
                            <i class="pi pi-microphone text-2xl"></i>
                        </div>
                        <Skeleton v-else size="3.7rem"></Skeleton>
                        <div class="flex flex-col justify-center items-start">
                            <div v-if="stats.totalSpeeches !== null" class="text-3xl font-bold text-gray-800">{{ stats.totalSpeeches }}</div>
                            <Skeleton v-else size="2.5rem" class="mr-2"></Skeleton>
                            <div v-if="stats.totalSpeeches !== null" class="text-sm text-gray-500">{{ t('admin_dashboard.stats.total_speeches') }}</div>
                            <Skeleton v-else width="5rem" height="0.7rem" class="mt-2"></Skeleton>
                        </div>
                    </div>
                </template>
            </Card>

            <Card class="border-b-[0.2rem] border-amber-600">
                <template #content>
                    <div class="flex flex-row items-center gap-4">
                        <div v-if="stats.pendingReports !== null" class="stat-icon bg-amber-100 text-amber-600">
                            <i class="pi pi-flag text-2xl"></i>
                        </div>
                        <Skeleton v-else size="3.7rem"></Skeleton>
                        <div class="flex flex-col justify-center items-start">
                            <div v-if="stats.pendingReports !== null" class="text-3xl font-bold text-gray-800">{{ stats.pendingReports }}</div>
                            <Skeleton v-else size="2.5rem" class="mr-2"></Skeleton>
                            <div v-if="stats.pendingReports !== null" class="text-sm text-gray-500">{{ t('admin_dashboard.stats.pending_reports') }}</div>
                            <Skeleton v-else width="5rem" height="0.7rem" class="mt-2"></Skeleton>
                        </div>
                    </div>
                </template>
            </Card>
            
            <Card class="border-b-[0.2rem] border-red-600">
                <template #content>
                    <div class="flex flex-row items-center gap-4">
                        <div v-if="stats.totalBans !== null" class="stat-icon bg-red-100 text-red-600">
                            <i class="pi pi-times text-2xl"></i>
                        </div>
                        <Skeleton v-else size="3.7rem"></Skeleton>
                        <div class="flex flex-col justify-center items-start">
                            <div v-if="stats.totalBans !== null" class="text-3xl font-bold text-gray-800">{{ stats.totalBans }}</div>
                            <Skeleton v-else size="2.5rem" class="mr-2"></Skeleton>
                            <div v-if="stats.totalBans !== null" class="text-sm text-gray-500">{{ t('admin_dashboard.stats.total_bans') }}</div>
                            <Skeleton v-else width="5rem" height="0.7rem" class="mt-2"></Skeleton>
                        </div>
                    </div>
                </template>
            </Card>
        </div>

        <div class="flex flex-col gap-6">
            <div>
                <UserGrowthChart ref="userGrowthChartRef" />
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <SpeechesByInterestChart ref="speechesByInterestChartRef" />
                <DailySpeechActivityChart ref="dailySpeechActivityChartRef" />
            </div>
        </div>
    </div>
</template>

<style scoped>


.stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

:deep(.p-card-body) {
    padding: 1.25rem;
}

:deep(.p-card-content) {
    padding: 0;
}
</style>
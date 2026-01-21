<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Chart from 'primevue/chart';
import ProgressSpinner from 'primevue/progressspinner';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1';

const chartData = ref();
const chartOptions = ref();
const isLoaded = ref(false);

onMounted(async () => {
    chartOptions.value = {
        cutout: '60%',
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    color: getComputedStyle(document.documentElement).getPropertyValue('--p-text-color') || '#374151',
                    usePointStyle: true,
                    padding: 16,
                    font: {
                        size: 12
                    }
                }
            }
        }
    };
});

const refreshStats = async () => {
    isLoaded.value = false;

    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/stats/counts-by-topic`, {
            credentials: 'include'
        });

        if (response.ok) {
            const response_data = await response.json();
            
            if (response_data.counts && response_data.counts.length > 0) {
                chartData.value = {
                    labels: response_data.labels,
                    datasets: [
                        {
                            data: response_data.counts,
                            backgroundColor: [
                                '#3b82f6', 
                                '#10b981', 
                                '#f59e0b', 
                                '#ef4444', 
                                '#8b5cf6', 
                                '#ec4899', 
                                '#06b6d4', 
                                '#f97316', 
                                '#84cc16', 
                                '#6366f1', 
                                '#14b8a6', 
                                '#a855f7', 
                                '#eab308', 
                                '#22c55e', 
                                '#64748b'  
                            ],
                            hoverBackgroundColor: [
                                '#2563eb', 
                                '#059669', 
                                '#d97706', 
                                '#dc2626', 
                                '#7c3aed', 
                                '#db2777', 
                                '#0891b2', 
                                '#ea580c', 
                                '#65a30d', 
                                '#4f46e5', 
                                '#0d9488', 
                                '#9333ea', 
                                '#ca8a04', 
                                '#16a34a', 
                                '#475569'  
                            ],
                            borderWidth: 0
                        }
                    ]
                };
            }
        }
    } catch (error) {
        console.error('Failed to fetch speeches by interest:', error);
    } finally {
        isLoaded.value = true;
    }
};

defineExpose({
    refreshStats
});

</script>

<template>
    <div class="flex flex-col
                justify-center items-center
                chart-card rounded-xl shadow-sm p-5">
        <div class="mb-4">
            <h3 class="text-lg font-semibold chart-title">{{ t('stats.speeches_by_interest') }}</h3>
            <p class="text-sm chart-subtitle">{{ t('stats.freq_by_topic') }}</p>
        </div>
        <div class="flex items-center justify-center">
            <Chart v-if="chartData && chartOptions" type="doughnut" :data="chartData" :options="chartOptions" class="w-full max-w-md" />
            <div v-else-if="!isLoaded" class="h-64 flex items-center justify-center">
                <ProgressSpinner />
            </div>
            <div v-else class="h-64 flex items-center justify-center no-data-text">
                {{ t('stats.no_data') }}
            </div>
        </div>
    </div>
</template>

<style scoped>
.chart-card {
    background-color: var(--color-bg-card);
}

.chart-title {
    color: var(--color-text-dark);
}

.chart-subtitle {
    color: var(--color-text-muted);
}

.no-data-text {
    color: var(--color-text-muted);
}
</style>
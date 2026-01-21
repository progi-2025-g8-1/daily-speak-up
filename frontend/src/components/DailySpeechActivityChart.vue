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

const setChartOptions = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--p-text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
    const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

    return {
        maintainAspectRatio: false,
        aspectRatio: 0.8,
        plugins: {
            legend: {
                labels: {
                    color: textColor
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: textColorSecondary
                },
                grid: {
                    color: surfaceBorder
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    color: textColorSecondary
                },
                grid: {
                    color: surfaceBorder
                }
            }
        }
    };
};

onMounted(async () => {
    chartOptions.value = setChartOptions();
});

const refreshStats = async () => {
    isLoaded.value = false;

    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/stats/speeches-this-week`, {
            credentials: 'include'
        });

        if (response.ok) {
            const response_data = await response.json();
            
            if (response_data.counts && response_data.labels) {
                chartData.value = {
                    labels: response_data.labels,
                    datasets: [
                        {
                            label: t('stats.daily_activity.recorded_speeches'),
                            data: response_data.counts,
                            backgroundColor: 'rgba(139, 92, 246, 0.7)',
                            hoverBackgroundColor: 'rgba(139, 92, 246, 0.9)',
                            borderColor: 'rgb(139, 92, 246)',
                            borderWidth: 0,
                            borderRadius: 8,
                            borderSkipped: false
                        }
                    ]
                };
            }
        }
    } catch (error) {
        console.error('Failed to fetch daily speech activity:', error);
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
        <div class="flex flex-row items-center justify-between mb-4 w-full">
            <div class="flex flex-col
                        justify-center items-start" >
                <h3 class="text-lg font-semibold chart-title">{{ t('stats.daily_activity.title') }}</h3>
                <p class="text-sm chart-subtitle">{{ t('stats.daily_activity.subtitle') }}</p>
            </div>
            <div class="week-badge px-3 py-1 rounded-full text-sm font-medium">
                {{ t('stats.daily_activity.this_week') }}
            </div>
        </div>
        <Chart v-if="chartData && chartOptions" type="bar" :data="chartData" :options="chartOptions" class="h-64 w-full" />
        <div v-else-if="!isLoaded" class="h-64 flex items-center justify-center">
            <ProgressSpinner />
        </div>
        <div v-else class="h-64 flex items-center justify-center no-data-text">
            {{ t('stats.no_data') }}
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

.week-badge {
    background-color: rgba(139, 92, 246, 0.1);
    color: #8b5cf6;
}

.no-data-text {
    color: var(--color-text-muted);
}
</style>
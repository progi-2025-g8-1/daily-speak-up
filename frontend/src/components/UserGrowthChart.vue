<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Chart from 'primevue/chart';
import ProgressSpinner from 'primevue/progressspinner';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1';

const chartData = ref();
const chartOptions = ref();

onMounted(async () => {
    chartOptions.value = setChartOptions();
});

const setChartOptions = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--p-text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
    const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

    return {
        maintainAspectRatio: false,
        aspectRatio: 0.6,
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

const refreshStats = async () => {
    const response = await fetch(`${API_BASE_URL}/dashboard/stats/users-by-month`, {
        credentials: 'include'
    });

    if (response.ok) {
        const response_data = await response.json();
        if (response_data.counts && response_data.labels) {
            chartData.value = {
                labels: response_data.labels,
                datasets: [
                    {
                        label: t('stats.user_growth.total_users_label'),
                        data: response_data.counts,
                        fill: true,
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderColor: '#10b981',
                        tension: 0.4,
                        pointBackgroundColor: '#10b981',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }
                ]
            };
        }
    }
}

defineExpose({
    refreshStats
});
</script>

<template>
    <div class="flex flex-col
                justify-center
                bg-white rounded-xl shadow-sm p-5">
        <div class="flex items-center justify-between mb-4">
            <div class="flex flex-col
                        justify-center items-start">
                <h3 class="text-lg font-semibold text-gray-800">{{ t('stats.user_growth.title') }}</h3>
                <p class="text-sm text-gray-500">{{ t('stats.user_growth.subtitle') }}</p>
            </div>
        </div>
        <Chart v-if="chartData" type="line" :data="chartData" :options="chartOptions" class="h-72" />
        <div v-else class="h-72 flex items-center justify-center">
            <ProgressSpinner />
        </div>
    </div>
</template>

<style scoped>

</style>
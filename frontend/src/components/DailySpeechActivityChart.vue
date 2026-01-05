<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Chart from 'primevue/chart';
import ProgressSpinner from 'primevue/progressspinner';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1/';

const chartData = ref();
const chartOptions = ref();

onMounted(async () => {
    const data = {
        days: [],
        counts: []
    };

    const response = await fetch(`${API_BASE_URL}/dashboard/stats/speeches-this-week`);

    if (response.ok) {
        const response_data = await response.json();
        data.counts = response_data.counts;
        data.days = response_data.labels;
    }
    
    chartData.value = {
        labels: data.days,
        datasets: [
            {
                label: 'Snimljeni govori',
                data: data.counts,
                backgroundColor: 'rgba(139, 92, 246, 0.7)',
                hoverBackgroundColor: 'rgba(139, 92, 246, 0.9)',
                borderColor: 'rgb(139, 92, 246)',
                borderWidth: 0,
                borderRadius: 8,
                borderSkipped: false
            }
        ]
    };
    
    chartOptions.value = setChartOptions();
});

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
</script>

<template>
    <div class="flex flex-col
                justify-center items-center
                chart-card bg-white rounded-xl shadow-sm p-5">
        <div class="flex flex-row items-center justify-between mb-4 w-full">
            <div class="flex flex-col
                        justify-center items-start" >
                <h3 class="text-lg font-semibold text-gray-800">Dnevna aktivnost govora</h3>
                <p class="text-sm text-gray-500">Prikaz količine snimljenih govora tijekom tjedna</p>
            </div>
            <div class="bg-purple-100 text-purple-600 px-3 py-1 rounded-full text-sm font-medium">
                Ovaj tjedan
            </div>
        </div>
        <Chart v-if="chartData" type="bar" :data="chartData" :options="chartOptions" class="h-64" />
        <div v-else class="h-64 flex items-center justify-center">
            <ProgressSpinner />
        </div>
    </div>
</template>

<style scoped>
</style>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Chart from 'primevue/chart';
import ProgressSpinner from 'primevue/progressspinner';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1/';

const chartData = ref();
const chartOptions = ref();

onMounted(async () => {
    const data = {
        interests: [],
        counts: []
    };

    const response = await fetch(`${API_BASE_URL}/dashboard/stats/counts-by-topic`);

    if (response.ok) {
        const response_data = await response.json();
        data.counts = response_data.counts;
        data.interests = response_data.labels;
    }
    
    chartData.value = {
        labels: data.interests,
        datasets: [
            {
                data: data.counts,
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
</script>

<template>
    <div class="flex flex-col 
                justify-center items-center
                bg-white rounded-xl shadow-sm p-5">
        <div class="mb-4">
            <h3 class="text-lg font-semibold text-gray-800">Govori prema interesima</h3>
            <p class="text-sm text-gray-500">Frekvencije govora po svim temama</p>
        </div>
        <div class="flex items-center justify-center">
            <Chart v-if="chartData" type="doughnut" :data="chartData" :options="chartOptions" class="w-full max-w-md" />
            <div v-else class="h-64 flex items-center justify-center">
                <ProgressSpinner />
            </div>
        </div>
    </div>
</template>

<style scoped>
</style>
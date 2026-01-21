<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { api } from '../api';

interface Props {
  speechId: string;
  averageRating?: number | null;
  totalRatings?: number;
  readonly?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  averageRating: null,
  totalRatings: 0,
  readonly: false
});

const emit = defineEmits<{
  ratingUpdated: [rating: number, averageRating: number, totalRatings: number]
}>();

const userRating = ref<number | null>(null);
const hoveredStar = ref<number | null>(null);
const avgRating = ref<number | null>(props.averageRating);
const ratingsCount = ref<number>(props.totalRatings);

const fetchRatingInfo = async () => {
  if (!props.speechId) return;
  try {
    const data = await api(`/ratings/speech/${props.speechId}`);
    userRating.value = data.user_rating;
    avgRating.value = data.average_rating;
    ratingsCount.value = data.total_ratings;
  } catch (error) {
    console.error('Error fetching rating info:', error);
  }
};

watch(() => props.speechId, fetchRatingInfo, { immediate: true });

const displayRating = computed(() => {
  if (hoveredStar.value !== null) return hoveredStar.value;
  if (userRating.value !== null) return userRating.value;
  return avgRating.value || 0;
});

const handleStarClick = async (rating: number) => {
  if (props.readonly) return;
  
  try {
    await api('/ratings', {
      method: 'POST',
      body: JSON.stringify({ speech_id: props.speechId, rating })
    });
    
    userRating.value = rating;
    const data = await api(`/ratings/speech/${props.speechId}`);
    avgRating.value = data.average_rating;
    ratingsCount.value = data.total_ratings;
    emit('ratingUpdated', rating, data.average_rating || 0, data.total_ratings || 0);
  } catch (error) {
    console.error('Error submitting rating:', error);
  }
};

const getStarClass = (star: number) => {
  const isFilled = star <= displayRating.value;
  const isOriginal = userRating.value && star <= userRating.value && hoveredStar.value !== null;
  
  if (props.readonly) return isFilled ? 'text-yellow-400' : 'text-gray-300';
  
  if (isOriginal && star > (hoveredStar.value || 0)) {
    return 'text-yellow-300 opacity-40';
  }
  
  return isFilled ? 'text-yellow-400' : 'text-gray-300';
};
</script>

<template>
  <div class="flex items-center gap-3">
    <div class="flex gap-1" @mouseleave="hoveredStar = null">
      <span
        v-for="star in 5"
        :key="star"
        class="text-2xl select-none"
        :class="[getStarClass(star), readonly ? 'cursor-default' : 'cursor-pointer']"
        @click="handleStarClick(star)"
        @mouseenter="hoveredStar = readonly ? null : star"
      >★</span>
    </div>
    <p class="text-sm text-gray-600 dark:text-gray-400">
      {{ (avgRating !== null && avgRating > 0) ? `${avgRating.toFixed(1)} (${ratingsCount})` : 'No ratings' }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  rating: number | null;
  totalRatings?: number;
  size?: 'sm' | 'md' | 'lg';
  showCount?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  totalRatings: 0,
  size: 'sm',
  showCount: true
});

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'text-sm gap-0.5';
    case 'md':
      return 'text-base gap-1';
    case 'lg':
      return 'text-xl gap-1';
    default:
      return 'text-sm gap-0.5';
  }
});

const displayRating = computed(() => {
  if (props.rating === null || props.rating === 0) return 0;
  return props.rating;
});

const fullStars = computed(() => Math.floor(displayRating.value));
const hasHalfStar = computed(() => displayRating.value % 1 >= 0.5);
const emptyStars = computed(() => 5 - fullStars.value - (hasHalfStar.value ? 1 : 0));
</script>

<template>
  <div class="flex items-center gap-2">
    <div :class="['flex items-center', sizeClasses]">
      <!-- Full stars -->
      <span 
        v-for="i in fullStars" 
        :key="`full-${i}`" 
        class="text-yellow-400"
      >
        ★
      </span>
      <!-- Half star -->
      <span 
        v-if="hasHalfStar" 
        class="text-yellow-400"
      >
        ★
      </span>
      <!-- Empty stars -->
      <span 
        v-for="i in emptyStars" 
        :key="`empty-${i}`" 
        class="text-gray-300"
      >
        ★
      </span>
    </div>
    <span 
      v-if="showCount && totalRatings > 0" 
      class="text-xs text-gray-600 dark:text-gray-400"
    >
      ({{ totalRatings }})
    </span>
  </div>
</template>

<style scoped>
</style>

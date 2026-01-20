<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '../api'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import ProgressSpinner from 'primevue/progressspinner'

const emit = defineEmits<{(e:'done'): void}>()
const { locale, t } = useI18n()
type Interest = { slug: string; label: string }

const catalog = ref<Interest[]>([])
const picked = ref<string[]>([])
const loading = ref(true)
const saving = ref(false)

const isSelected = (slug: string) => picked.value.includes(slug)
const selectedCount = computed(() => picked.value.length)

onMounted(async () => {
  try {
    catalog.value = await api(`/interests?lang=${locale.value}`, { method: 'GET' })
  } catch (error) {
    console.error('Error loading interests:', error)
    catalog.value = [
      { slug: 'javascript', label: 'JavaScript' },
      { slug: 'react', label: 'React' },
      { slug: 'ai-ml', label: 'AI/ML' },
      { slug: 'devops', label: 'DevOps' },
    ]
  } finally {
    loading.value = false
  }
})

function toggle(slug: string) {
  picked.value = picked.value.includes(slug)
    ? picked.value.filter(s => s !== slug)
    : [...picked.value, slug]
}

async function save() {
  saving.value = true
  try {
    await api('/onboarding/interests', {
      method: 'PATCH',
      body: JSON.stringify({ interests: picked.value })
    })
    emit('done')
  } catch (error) {
    console.error('Error saving interests:', error)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="mb-6">
      <h2 class="text-2xl font-bold mb-2 text-primary">{{ $t('onboarding.phase2.title') }}</h2>
      <p class="text-secondary">{{ $t('onboarding.phase2.subtitle') }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <ProgressSpinner style="width: 40px; height: 40px" strokeWidth="4" />
    </div>

    <!-- Interests Grid -->
    <div v-else class="space-y-4">
      <!-- Selected Count -->
      <div v-if="selectedCount > 0" class="flex items-center gap-2">
        <Chip :label="`${selectedCount} ${$t('onboarding.phase2.selected')}`" class="bg-accent text-primary" />
      </div>

      <!-- Interest Buttons -->
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
        <button
          v-for="i in catalog"
          :key="i.slug"
          @click="toggle(i.slug)"
          type="button"
          class="relative group border-2 rounded-lg px-4 py-3 text-left font-medium transition-all duration-200 hover:shadow-md"
          :class="isSelected(i.slug) 
            ? 'border-primary bg-primary text-white shadow-md' 
            : 'border-light bg-card text-dark hover:border-primary'"
        >
          <div class="flex items-center justify-between">
            <span>{{ i.label }}</span>
            <i 
              v-if="isSelected(i.slug)"
              class="pi pi-check text-sm"
            ></i>
          </div>
        </button>
      </div>

      <!-- Empty State -->
      <div v-if="catalog.length === 0" class="text-center py-8">
        <i class="pi pi-info-circle text-4xl text-muted mb-3"></i>
        <p class="text-secondary">{{ t('onboarding.phase2.empty_state') }}</p>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-between items-center pt-6 border-t border-light">
      <p class="text-sm text-light">
        {{ selectedCount === 0 ? t('onboarding.phase2.select_at_least_one') : t('onboarding.phase2.selected_count', { count: selectedCount }) }}
      </p>
      <Button 
        :label="t('onboarding.phase2.finish_button')"
        icon="pi pi-check"
        iconPos="right"
        :disabled="selectedCount === 0"
        :loading="saving"
        @click="save"
        class="px-6"
        severity="success"
      />
    </div>
  </div>
</template>

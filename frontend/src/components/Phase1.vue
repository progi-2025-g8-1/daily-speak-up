<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../api'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import InlineMessage from 'primevue/inlinemessage'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const emit = defineEmits<{(e:'done'): void}>()
const name = ref('')
const handle = ref('')
const checking = ref(false)
const handleAvailable = ref<boolean | null>(null)
const submitting = ref(false)

function onHandleInput() {
  handleAvailable.value = null
}

async function checkHandle() {
  if (!handle.value) return
  checking.value = true
  try {
    const res = await api(`/handles/check?handle=${encodeURIComponent(handle.value)}`)
    handleAvailable.value = res.available
  } catch (error) {
    console.error('Error checking handle:', error)
  } finally {
    checking.value = false
  }
}

async function submit() {
  if (handleAvailable.value === null) {
    await checkHandle()
  }
  
  if (handleAvailable.value !== true) {
    return
  }
  
  submitting.value = true
  try {
    await api('/onboarding/profile', {
      method: 'PATCH',
      body: JSON.stringify({ name: name.value, handle: handle.value })
    })
    emit('done')
  } catch (error) {
    console.error('Error updating profile:', error)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form class="space-y-6" @submit.prevent="submit">
    <div class="mb-6">
      <h2 class="text-2xl font-bold mb-2 text-primary">{{ t('onboarding.phase1.title') }}</h2>
      <p class="text-secondary">{{ t('onboarding.phase1.subtitle') }}</p>
    </div>

    <!-- Name Field -->
    <div class="space-y-2">
      <label for="name" class="block text-sm font-semibold text-dark">
        {{ t('onboarding.phase1.name_label') }} <span style="color: var(--color-error);">*</span>
      </label>
      <InputText 
        id="name"
        v-model="name" 
        :placeholder="t('onboarding.phase1.name_placeholder')"
        class="w-full"
        required
        :disabled="submitting"
      />
      <small class="text-light">{{ t('onboarding.phase1.name_hint') }}</small>
    </div>

    <!-- Handle Field -->
    <div class="space-y-2">
      <label for="handle" class="block text-sm font-semibold text-dark">
        {{ t('onboarding.phase1.handle_label') }} <span style="color: var(--color-error);">*</span>
      </label>
      <div class="relative">
        <InputText 
          id="handle"
          v-model="handle" 
          :placeholder="t('onboarding.phase1.handle_placeholder')"
          class="w-full"
          required
          pattern="^[a-z0-9_]{3,20}$"
          @input="onHandleInput"
          @blur="checkHandle"
          :disabled="submitting"
        />
        <i 
          v-if="checking" 
          class="pi pi-spin pi-spinner absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
        ></i>
      </div>
      
      <!-- Handle validation messages -->
      <div v-if="handle && !checking" class="mt-2">
        <InlineMessage v-if="handleAvailable === false" severity="error" class="w-full">
          @{{ handle }} je već zauzeto
        </InlineMessage>
        <InlineMessage v-else-if="handleAvailable === true" severity="success" class="w-full">
          @{{ handle }} je dostupno!
        </InlineMessage>
      </div>
      
      <small class="text-light">
        3-20 znakova, dozvoljena slova, brojevi i donja crta
      </small>
    </div>

    <!-- Submit Button -->
    <div class="flex justify-end pt-4">
      <Button 
        type="submit" 
        label="Nastavi"
        icon="pi pi-arrow-right"
        iconPos="right"
        :loading="submitting || checking"
        :disabled="!name || !handle"
        class="px-6"
      />
    </div>
  </form>
</template>

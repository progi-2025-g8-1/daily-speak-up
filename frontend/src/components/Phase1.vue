<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../api'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import InlineMessage from 'primevue/inlinemessage'

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
      <h2 class="text-2xl font-bold mb-2 text-primary">Postavite svoj profil</h2>
      <p class="text-secondary">Recite nam nešto o sebi</p>
    </div>

    <!-- Name Field -->
    <div class="space-y-2">
      <label for="name" class="block text-sm font-semibold" style="color: var(--color-text-dark);">
        Ime <span style="color: var(--color-error);">*</span>
      </label>
      <InputText 
        id="name"
        v-model="name" 
        placeholder="Unesite svoje ime"
        class="w-full"
        required
        :disabled="submitting"
      />
      <small style="color: var(--color-text-light);">Vaše puno ime ili ime koje želite koristiti</small>
    </div>

    <!-- Handle Field -->
    <div class="space-y-2">
      <label for="handle" class="block text-sm font-semibold" style="color: var(--color-text-dark);">
        Korisničko ime (handle) <span style="color: var(--color-error);">*</span>
      </label>
      <div class="relative">
        <InputText 
          id="handle"
          v-model="handle" 
          placeholder="npr. john_doe123"
          class="w-full"
          required
          pattern="^[a-z0-9_]{3,20}$"
          @input="onHandleInput"
          @blur="checkHandle"
          :disabled="submitting"
        />
        <i 
          v-if="checking" 
          class="pi pi-spin pi-spinner absolute right-3 top-1/2 -translate-y-1/2"
          style="color: var(--color-text-light);"
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
      style="color: var(--color-text-light);
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

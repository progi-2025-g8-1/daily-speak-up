<template>
  <div>
    <Button 
      label="Sign in with Email" 
      icon="pi pi-envelope" 
      @click="visible = true"
      severity="secondary"
    />
    
    <Dialog v-model:visible="visible" modal header="Sign in with Email" :style="{ width: '25rem' }">
      <form v-if="!emailSent" @submit.prevent="handleSendMagicLink" class="flex flex-col gap-4">
        <p class="text-sm" style="color: var(--color-text-secondary);">We'll send you a magic link to sign in instantly.</p>
        
        <div class="flex flex-col gap-2">
          <label for="email" class="font-semibold">Email</label>
          <InputText 
            id="email" 
            v-model="email" 
            type="email" 
            required 
            placeholder="Enter your email"
            :disabled="loading"
          />
        </div>

        <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
        
        <div class="flex justify-end gap-2 mt-4">
          <Button type="button" label="Cancel" severity="secondary" @click="visible = false" :disabled="loading" />
          <Button type="submit" label="Send Magic Link" icon="pi pi-send" :loading="loading" />
        </div>
      </form>

      <!-- Success message after email sent -->
      <div v-else class="flex flex-col gap-4">
        <Message severity="success" :closable="false">
          Magic link sent! Check your email at <strong>{{ email }}</strong>
        </Message>
        
        <p class="text-sm" style="color: var(--color-text-secondary);">
          Click the link in your email to sign in. You can close this window.
        </p>
        
        <Button label="Close" @click="visible = false" class="mt-2" />
      </div>
    </Dialog>
  </div>
</template>

<script>
import { ref } from 'vue';
import { createPasswordlessCode } from '../auth';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';

export default {
  components: {
    Button,
    Dialog,
    InputText,
    Message
  },
  setup() {
    const visible = ref(false);
    const email = ref('');
    const emailSent = ref(false);
    const loading = ref(false);
    const error = ref('');

    const handleSendMagicLink = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        const result = await createPasswordlessCode(email.value);
        
        if (result.status === 'OK') {
          emailSent.value = true;
        } else {
          error.value = 'Failed to send magic link. Please try again.';
        }
      } catch (e) {
        error.value = 'An error occurred. Please try again.';
        console.error('Send magic link error:', e);
      } finally {
        loading.value = false;
      }
    };

    return {
      visible,
      email,
      emailSent,
      loading,
      error,
      handleSendMagicLink
    };
  }
};
</script>

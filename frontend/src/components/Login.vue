<template>
  <div>
    <Button
      label="Log in"
      icon="pi pi-sign-in"
      style="background-color: var(--color-primary); color: white; border: none;"
      class="!shadow-md"
      @click="visible = true"
    />
    
    <Dialog v-model:visible="visible" modal header="Log in" :style="{ width: '25rem' }" severity="primary">
      <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
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
        
        <div class="flex flex-col gap-2">
          <label for="password" class="font-semibold">Password</label>
          <InputText 
            id="password" 
            v-model="password" 
            type="password" 
            required 
            placeholder="Enter your password"
            :disabled="loading"
          />
        </div>

        <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
        
        <div class="flex justify-end gap-2 mt-4">
          <Button type="button" label="Cancel" severity="secondary" @click="visible = false" :disabled="loading" />
          <Button type="submit" label="Log in" icon="pi pi-sign-in" :loading="loading" severity="primary" />
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script>
import { ref } from 'vue';
import { signIn } from '../auth';
import { useRouter } from 'vue-router';
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
    const router = useRouter();
    const visible = ref(false);
    const email = ref('');
    const password = ref('');
    const loading = ref(false);
    const error = ref('');

    const handleLogin = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        const result = await signIn(email.value, password.value);
        
        if (result.status === 'OK') {
          visible.value = false;
          email.value = '';
          password.value = '';
          router.push('/');
        } else if (result.status === 'WRONG_CREDENTIALS_ERROR') {
          error.value = 'Invalid email or password';
        } else if (result.status === 'FIELD_ERROR') {
          error.value = result.formFields.map(f => f.error).join(', ');
        }
      } catch (e) {
        error.value = 'An error occurred during login. Please try again.';
        console.error('Login error:', e);
      } finally {
        loading.value = false;
      }
    };

    return {
      visible,
      email,
      password,
      loading,
      error,
      handleLogin
    };
  }
};
</script>

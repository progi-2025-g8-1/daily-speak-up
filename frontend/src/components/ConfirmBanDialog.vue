<script setup lang="ts">
    import { ref } from 'vue';
    import Dialog from 'primevue/dialog';
    import Select from 'primevue/select';
    import Button from 'primevue/button';
    import InputText from 'primevue/inputtext';

    const props = defineProps<{
        showDialog: boolean,
        handle: string | null | undefined,
        userId: string | null | undefined,
        reasons: any[] | undefined
    }>();

    const emit = defineEmits(['update:showDialog']);

    const selectedReason = ref<any | null>(null);   
    const disableConfirm = ref(true);
    const showInputField = ref(false);
    const customReason = ref<string | null | undefined>(null);

    const handleSelectReason = (value: any) => {
        if(value && value.name !== 'Prilagođeni razlog') {
            disableConfirm.value = false;
            showInputField.value = false;
            customReason.value = null;
        } else if (value && value.name === 'Prilagođeni razlog') {
            disableConfirm.value = true;
            showInputField.value = true;
        } 
    };

    const handleCustomReason = (newReason: any) => {
        if(newReason && newReason.trim() !== '') {
            disableConfirm.value = false;
            customReason.value = newReason.trim();
        } else {
            disableConfirm.value = true;
        }
    };

    const issueBan = () => {
        console.log('Issuing ban to user ID:', props.userId);
    };
</script>

<template>
    <Dialog :visible="props.showDialog" header="Potvrda uručivanja zabrane" modal :closable="false" class="lg:w-2/3 md:w-3/4 w-[95%]" >
        <div class="flex flex-col gap-4">
            <div>
                Jeste li sigurni da želite uručiti zabranu korisniku{{ props.handle ? ` @${props.handle}` : '' }}?
            </div>
            <Select id="reasonSelect" v-model="selectedReason" :options="props.reasons" option-label="name" placeholder="Odaberite razlog" @update:modelValue="handleSelectReason" />
            <InputText type="text" v-model="customReason" v-if="showInputField" placeholder="Unesite razlog" @update:modelValue="handleCustomReason" />
        </div>
        <template #footer>
            <div class="flex justify-end gap-4">
                <Button label="Otkaži" icon="pi pi-times" class="p-button-text" @click="$emit('update:showDialog', false)" severity="secondary" />
                <Button label="Potvrdi" icon="pi pi-check" @click="$emit('update:showDialog', false)" severity="danger" :disabled="disableConfirm" :onClick="issueBan" />
            </div>
        </template>
    </Dialog>
</template>

<style scoped>
</style>
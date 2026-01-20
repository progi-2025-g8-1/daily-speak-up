<script setup lang="ts">
    import { ref } from 'vue';
    import Dialog from 'primevue/dialog';
    import Select from 'primevue/select';
    import Button from 'primevue/button';
    import InputText from 'primevue/inputtext';
    import { useI18n } from 'vue-i18n';

    const { t } = useI18n(); 

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
        if(value && value.name !== t('admin_dashboard.custom_reason')) {
            disableConfirm.value = false;
            showInputField.value = false;
            customReason.value = null;
        } else if (value && value.name === t('admin_dashboard.custom_reason')) {
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
        let reason = selectedReason.value.name === t('admin_dashboard.custom_reason') ? customReason.value : selectedReason.value.name;
        fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'}/dashboard/ban-user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: props.userId,
                reason: reason
            })
        }).then(response => {
            if(!response.ok) {
                console.error('Failed to ban user:', response.statusText);
            }
        }).catch(error => {
            console.error('Error banning user:', error);
        });
    };
</script>

<template>
    <Dialog :visible="props.showDialog" :header="t('admin_dashboard.bans.confirm_ban_issue.header')" modal :closable="false" class="lg:w-2/3 md:w-3/4 w-[95%]" >
        <div class="flex flex-col gap-4">
            <div>
                {{ t('admin_dashboard.bans.confirm_ban_issue.message') }}{{ props.handle ? ` @${props.handle}` : '' }}?
            </div>
            <Select id="reasonSelect" v-model="selectedReason" :options="props.reasons" option-label="name" :placeholder="t('admin_dashboard.bans.confirm_ban_issue.select_reason_placeholder')" @update:modelValue="handleSelectReason" />
            <InputText type="text" v-model="customReason" v-if="showInputField" :placeholder="t('admin_dashboard.bans.confirm_ban_issue.input_reason_placeholder')" @update:modelValue="handleCustomReason" />
        </div>
        <template #footer>
            <div class="flex justify-end gap-4">
                <Button :label="t('common.cancel')" icon="pi pi-times" class="p-button-text" @click="$emit('update:showDialog', false)" severity="secondary" />
                <Button :label="t('common.confirm')" icon="pi pi-check" @click="$emit('update:showDialog', false)" severity="danger" :disabled="disableConfirm" :onClick="issueBan" />
            </div>
        </template>
    </Dialog>
</template>

<style scoped>
</style>
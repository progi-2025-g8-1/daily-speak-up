<script setup lang="ts">  
    import { ref } from 'vue';
    import Dialog from 'primevue/dialog';
    import Button from 'primevue/button';
    import DatePicker from 'primevue/datepicker';

    const props = defineProps<{
        showDialog: boolean,
        user: any | null | undefined
    }>();

    const emit = defineEmits(['update:showDialog']);

    const chosenMonth = ref<Date | null>(new Date());
    const month = ref<number>((new Date()).getMonth() + 1);
    const year = ref<number>(new Date().getFullYear());

    const handleDateChange = (date: Date | null) => {
        chosenMonth.value = date;
        month.value = date ? date.getMonth() + 1 : month.value;
        year.value = date ? date.getFullYear() : year.value;
        console.log('Odabrani mjesec', month.value);
        console.log('Odabrana godina', year.value);
    };

</script>

<template>

    <Dialog v-model:visible="props.showDialog" modal :closable="false" class="w-[85vw]" >
        <template #header>
            <div class="flex justify-between items-center w-full">
                <h3 class="m-0 text-xl font-bold">Videozapisi korisnika {{ props.user ? `@${props.user.handle}` : '' }}</h3>
                <Button icon="pi pi-times" class="p-button-text p-button-plain" @click="$emit('update:showDialog', false)" aria-label="Close" rounded />
            </div>
        </template>

        <div class="flex flex-row items-center gap-3">
            <div class="text-lg font-semibold">Odaberite mjesec i godinu:</div>
            <DatePicker v-model="chosenMonth" view="month" dateFormat="mm/yy" @update:modelValue="handleDateChange" />
        </div>

    </Dialog>
  
</template>

<style scoped>
</style>
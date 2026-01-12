<script setup lang="ts">  
    import { onMounted, ref } from 'vue';
    import Dialog from 'primevue/dialog';
    import Button from 'primevue/button';
    import DatePicker from 'primevue/datepicker';
    import Message from 'primevue/message';
    import Carousel from 'primevue/carousel';

    const props = defineProps<{
        showDialog: boolean,
        user: any | null | undefined
    }>();

    const emit = defineEmits(['update:showDialog']);

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'

    const chosenMonth = ref<Date | null>(new Date());
    const month = ref<number>((new Date()).getMonth() + 1);
    const year = ref<number>(new Date().getFullYear());
    const videos = ref<any[]>([]);

    const handleDateChange = async (date: Date | null) => {
        chosenMonth.value = date;
        month.value = date ? date.getMonth() + 1 : month.value;
        year.value = date ? date.getFullYear() : year.value;
        console.log('Odabrani mjesec', month.value);
        console.log('Odabrana godina', year.value);

        if(props.user) {
            const response = await fetch(`${API_BASE_URL}/user/${props.user.user_id}/${year.value}/${month.value}/videos`,
            {
                credentials: 'include'
            }
            );
            if(response.ok) {
                let data = await response.json();
                videos.value = data.videos;
                console.log('Dohvaćeni videozapisi korisnika:', videos.value);
                console.log('Ukupno videozapisa:', videos.value.length);
            } else {
                console.error('Greška pri dohvaćanju videozapisa korisnika');
            }
        }
    };

    onMounted(async () => {
        if(props.user) {
            const response = await fetch(`${API_BASE_URL}/users/${props.user.user_id}/${year.value}/${month.value}/videos`,
            {
                credentials: 'include'
            }
            );
            if(response.ok) {
                let data = await response.json();
                videos.value = data.videos;
                console.log('Dohvaćeni videozapisi korisnika:', videos.value);
            } else {
                console.error('Greška pri dohvaćanju videozapisa korisnika');
            }
        }
    });

</script>

<template>

    <Dialog v-model:visible="props.showDialog" modal :closable="false" class="w-[85vw]" >
        <template #header>
            <div class="flex justify-between items-center w-full">
                <h3 class="m-0 text-xl font-bold">Videozapisi korisnika {{ props.user ? `@${props.user.handle}` : '' }}</h3>
                <Button icon="pi pi-times" class="p-button-text p-button-plain" @click="$emit('update:showDialog', false)" aria-label="Close" rounded />
            </div>
        </template>

        <div class="flex flex-col justify-center gap-4 p-4">
            <div class="flex flex-row items-center gap-3">
                <div class="text-lg font-semibold">Odaberite mjesec i godinu:</div>
                <DatePicker v-model="chosenMonth" view="month" dateFormat="mm/yy" @update:modelValue="handleDateChange" />
            </div>

            <div v-if="videos.length === 0">
                <Message severity="error">Korisnik {{ props.user ? `@${props.user.handle}` : '' }} nema snimljenih videozapisa za odabrani mjesec.</Message>
            </div>

            <div v-else>
                <Carousel :value="videos" :numVisible="3" :numScroll="1" class="mt-4" :circular="true" :autoplayInterval="5000">
                    <template #item="slotProps">
                        <div class="flex flex-col items-center p-2">
                            <iframe 
                                :src="slotProps.data.url" 
                                class="w-[20vw] aspect-1/1"
                                width="320" 
                                height="180" 
                                frameborder="0" 
                                allow="autoplay; encrypted-media" 
                                allowfullscreen>
                            </iframe>
                            <div class="mt-2 text-center">
                                <div class="font-semibold">{{ new Date(year=slotProps.data.year, monthIndex=slotProps.data.month - 1, date=slotProps.data.day).toLocaleDateString() }}</div>
                                <div class="text-sm text-gray-500">{{ slotProps.data.caption }}</div>
                            </div>
                        </div>
                    </template>
                </Carousel>
            </div>
        </div>

    </Dialog>
  
</template>

<style scoped>
</style>
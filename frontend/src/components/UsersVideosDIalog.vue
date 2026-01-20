<script setup lang="ts">  
    import { ref, watch } from 'vue';
    import Dialog from 'primevue/dialog';
    import Button from 'primevue/button';
    import DatePicker from 'primevue/datepicker';
    import Message from 'primevue/message';
    import Carousel from 'primevue/carousel'; 
    import Card from 'primevue/card';
    import { useConfirm } from "primevue/useconfirm";
    import { useI18n } from 'vue-i18n';

    const { t } = useI18n();
    const props = defineProps<{
        showDialog: boolean,
        user: any | null | undefined
    }>();

    const emit = defineEmits(['update:showDialog']);

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'
    const confirm = useConfirm();

    const chosenMonth = ref<Date | null>(new Date());
    const month = ref<number>((new Date()).getMonth() + 1);
    const year = ref<number>(new Date().getFullYear());
    const videos = ref<any[]>([]);

    const handleDateChange = async (date: any) => {
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
                console.error(t('users_videos.error_fetch'));
            }
        }
    };

    watch(() => props.user, async (newUser: any) => {
        if(newUser) {
            const response = await fetch(`${API_BASE_URL}/user/${props.user.user_id}/${year.value}/${month.value}/videos`,
            {
                credentials: 'include'
            }
            );
            if(response.ok) {
                let data = await response.json();
                videos.value = data.videos;
                console.log('Dohvaćeni videozapisi korisnika:', videos.value);
            } else {
                 console.error(t('users_videos.error_fetch'));
            }
        }
    }, { immediate: true });

    const handleDeleteVideo = (video_id: string) => {
        confirm.require({
            message: t('users_videos.confirm_delete_msg'),
            header: t('users_videos.confirm_delete_title'),
            icon: 'pi pi-exclamation-triangle',
            acceptProps: { label: t('users_videos.delete_btn'), icon: 'pi pi-times', severity: 'danger' },
            rejectProps: { label: t('common.cancel'), outlined: true, severity: 'secondary' },
            accept: async () => {
                const response = await fetch(`${API_BASE_URL}/video/${video_id}`, {
                    method: 'DELETE',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    videos.value = videos.value.filter(video => video.video_id !== video_id);
                } else {
                    console.error('Failed to delete video:', response.statusText);
                }
            },
            reject: () => {
            }
        });

};

    const isYoutube = (url: string) => {
        if (!url) return false;
        return url.includes('youtube.com') || url.includes('youtu.be');
    };

</script>

<template>

    <Dialog v-model:visible="props.showDialog" modal :closable="false" class="w-[85vw]" >
        <template #header>
            <div class="flex justify-between items-center w-full">
                <h3 class="m-0 text-xl font-bold">{{ t('users_videos.title') }} {{ props.user ? `@${props.user.handle}` : '' }}</h3>
                <Button icon="pi pi-times" class="p-button-text p-button-plain" @click="$emit('update:showDialog', false)" aria-label="Close" rounded />
            </div>
        </template>

        <div class="flex flex-col justify-center gap-4 p-4">
            <div class="flex flex-row items-center gap-3">
                <div class="text-lg font-semibold">{{ t('users_videos.select_month') }}</div>
                <DatePicker v-model="chosenMonth" view="month" dateFormat="mm/yy" @update:modelValue="handleDateChange" />
            </div>

            <div v-if="videos.length === 0">
                <Message severity="error">{{ t('users_videos.no_videos', { handle: props.user ? `@${props.user.handle}` : '' }) }}</Message>
            </div>

            <div v-else>
                <Carousel :value="videos" :numVisible="3" :numScroll="1" class="mt-4" :circular="true" >
                    <template #item="slotProps">
                        <Card class="mx-2" :style="{ width: '300px' }">
                            <template #content>
                                <div class="flex flex-col items-center p-2">
                                    <iframe v-if="isYoutube(slotProps.data.url)"
                                        :src="slotProps.data.url" 
                                        class="w-full rounded-lg
                                                w-[75%] aspect-square"
                                        frameborder="0" 
                                        allow="encrypted-media" 
                                        allowfullscreen>
                                    </iframe>
                                    <video v-else
                                        :src="slotProps.data.url"
                                        class="w-full rounded-lg
                                               w-[75%] aspect-square
                                               object-cover bg-black"
                                        controls
                                        preload="metadata"
                                        playsinline
                                    ></video>
                                    <div class="mt-2 text-center">
                                        <div class="font-semibold">{{ new Date(slotProps.data.year, slotProps.data.month - 1, slotProps.data.day).toLocaleDateString() }}</div>
                                        <div class="text-sm text-gray-500">{{ slotProps.data.caption }}</div>
                                        <Button 
                                            :label="t('users_videos.delete_btn')"
                                            icon="pi pi-delete-left" 
                                            class="mt-6"  
                                            severity="danger" 
                                            rounded
                                            variant="outlined"
                                            @click="handleDeleteVideo(slotProps.data.video_id)" />
                                    </div>
                            </div>
                            </template>
                        </Card>
                    </template>
                </Carousel>
            </div>
        </div>

    </Dialog>
  
</template>

<style scoped>
</style>
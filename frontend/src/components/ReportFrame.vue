<script setup lang="ts">
    import Avatar from 'primevue/avatar';
    import Button from 'primevue/button';
    import type { ReportInfo } from '../types/report-info';
    
    const props = defineProps<{ reportInfo: ReportInfo }>();
    const emit = defineEmits<{
        (e: 'showReasons', reportInfo: ReportInfo): void;
    }>();

    const showReasons = () => {
        emit('showReasons', props.reportInfo);
    };

</script>

<template>
    <div class="rounded-2xl shadow-md bg-gray-50 flex flex-col justify-start items-center gap-4 p-4" >
        <div class="w-full flex flex-row justify-center items-center gap-6">
            <iframe
                :src="props.reportInfo.video_url"
                class="lg:w-[50%] w-[25%] aspect-square rounded-2xl"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowfullscreen
            ></iframe>
            <div class="w-full flex flex-col justify-start items-start gap-4">
                <div class="flex flex-row justify-start items-center lg:gap-4 md:gap-3 gap-1 bg-gray-200 shadow-sm rounded-full w-full">
                    <Avatar :image="props.reportInfo.user_info.profile_picture_url" shape="circle" size="xlarge" class="shadow-sm" />
                    <div class="flex flex-col justify-center items-start">
                        <div class="font-semibold lg:text-[1.1vw] md:text-[2vh] text-[1.5vh]">
                            @{{ props.reportInfo.user_info.handle }}
                        </div>
                        <div class="lg:text-[0.9vw] text-[1vh]">
                            {{ props.reportInfo.user_info.email }}
                        </div>
                    </div>
                </div>

                <div class="w-full text-left bg-gray-100 p-4 rounded-md shadow-inner lg:text-[1vw] md:text-[1.5vh] text-[1.2vh]">
                    <span class="font-semibold">Opis videa:</span>
                    {{ props.reportInfo.caption }}
                </div>

                <div class="w-full flex flex-row justify-between items-center gap-1">
                    <Button label="Obriši prijavu" icon="pi pi-angle-double-left" severity="help" variant="outlined" class="w-[75%]"/>
                    <Button icon="pi pi-question" variant="outlined" severity="contrast" class="w-[25%] h-[100%]" @click="showReasons" />
                </div>
                <Button label="Obriši video" icon="pi pi-delete-left" severity="warn" variant="outlined" class="w-full" />
                <Button label="Uruči zabranu" icon="pi pi-times" severity="danger" variant="outlined" class="w-full shadow-inner-sm" />
            </div>
        </div>
    </div>
</template>

<style scoped>
</style>
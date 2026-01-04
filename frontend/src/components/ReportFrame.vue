<script setup lang="ts">
    import { ref } from 'vue';
    import Avatar from 'primevue/avatar';
    import Button from 'primevue/button';
    import SpeedDial from 'primevue/speeddial';
    import type { ReportInfo } from '../types/report-info';
    
    const props = defineProps<{ reportInfo: ReportInfo }>();
    const emit = defineEmits<{
        (e: 'showReasons', reportInfo: ReportInfo): void;
    }>();

    const items = ref([
        {
            label: 'Prikaz razloga',
            icon: 'pi pi-question',
            command: () => {
                showReasons();
            }
        },
        {
            label: 'Obriši prijavu',
            icon: 'pi pi-angle-double-left',
            command: () => {
                console.log('Prijava obrisana');
            }
        },
        {
            label: 'Obriši video',
            icon: 'pi pi-delete-left',
            command: () => {
                console.log('Video obrisan');
            }
        },
        {
            label: 'Uruči zabranu',
            icon: 'pi pi-times',
            command: () => {
                console.log('Zabrana uručena');
            }
        }
    ])

    const showReasons = () => {
        emit('showReasons', props.reportInfo);
    };

</script>

<template>
    <div class="flex flex-col
                justify-start items-center 
                rounded-2xl shadow-md bg-gray-50  
                
                gap-4 py-6 px-4
                @container" >
        <div class="flex flex-col 
                    justify-center items-center 
                    gap-4 w-full">

            <div class="flex flex-row relative
                        justify-between items-center 
                        bg-gray-200 shadow-sm rounded-full w-full">

                <div class="flex flex-row 
                            justify-start items-center 
                            gap-4">

                    <Avatar unstyled :image="props.reportInfo.user_info.profile_picture_url" 
                            shape="circle" 
                            pt:root:class="lg:w-15 lg:h-15 lg:mr-2
                                            md:w-12 md:h-12 md:mr-3
                                            w-10 h-10 mr-4
                                            rounded-full overflow-hidden"
                            pt:image:class="w-full h-full" />

                    <div class="flex flex-col 
                                justify-center items-start">

                        <div class="font-semibold 
                                    lg:text-lg
                                    md:text-base 
                                    text-sm">
                            @{{ props.reportInfo.user_info.handle }}
                        </div>

                        <div class="lg:text-base
                                    md:text-sm
                                    text-xs">
                            {{ props.reportInfo.user_info.email }}
                        </div>
                    
                    </div>
                
                </div>

                <div class="md:block
                            hidden">

                    <Button icon="pi pi-question" 
                            variant="outlined" 
                            severity="contrast" 
                            rounded
                            pt:root:class="lg:!w-15 lg:!h-15
                                        md:!w-12 md:!h-12
                                        !w-10 !h-10"
                            pt:icon:class="lg:!text-lg
                                        md:!text-base
                                        !text-sm"
                            @click="showReasons" />

                </div>

                <div class="max-md:block
                            hidden absolute top-0 right-0">

                    <SpeedDial :model="items" 
                               direction="down"
                               :buttonProps="{ 
                                   class: '!w-10 !h-10',
                                   severity: 'contrast',
                                   variant: 'outlined',
                                   rounded: true 
                               }"
                               :actionButtonProps="{
                                    class: '!bg-sky-600/50 hover:!bg-sky-600/70 !text-white !w-10 !h-10 !border-sky-600/70',  
                                    rounded: true
                               }" />

                </div>

            </div>

            <div class="flex flex-col 
                        md:flex-row 
                        justify-center items-center 
                        gap-6 w-full">
                <iframe
                    :src="props.reportInfo.video_url"
                    class="@lg:w-[50%] 
                           @md:w-[50%]
                           lg:w-[50%]
                           w-[75%]
                           aspect-square rounded-2xl"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowfullscreen
                ></iframe>

                <div class="flex flex-col 
                            justify-jstart items-start 
                            gap-3 w-full h-full">
                    <div class="bg-gray-100 shadow-inner rounded-md
                                w-full p-4 
                                text-left  
                                lg:text-sm
                                md:text-sm 
                                text-xs">
                        <span class="font-semibold">Opis videa:</span>
                        {{ props.reportInfo.caption }}
                    </div>
                            
                    <div class="hidden 
                                md:flex md:flex-col 
                                justify-start items-start 
                                gap-3 w-full">
                            <Button label="Obriši prijavu" 
                                    icon="pi pi-angle-double-left" 
                                    severity="help" 
                                    variant="outlined" 
                                    class="w-full"
                                    pt:label:class="text-sm"/>
                            <Button label="Obriši video" 
                                    icon="pi pi-delete-left" 
                                    severity="warn" 
                                    variant="outlined" 
                                    class="w-full" 
                                    pt:label:class="text-sm" />
                            <Button label="Uruči zabranu" 
                                    icon="pi pi-times" 
                                    severity="danger" 
                                    variant="outlined" 
                                    class="w-full shadow-inner-sm"
                                    pt:label:class="text-sm" />
                    </div>

                </div>

            </div>

        </div>
    </div>
</template>

<style scoped>
    .p-button.lg {
        --p-button-sm-font-size: 0.5rem;
        --p-button-lg-font-size: 20rem;
    }
</style>
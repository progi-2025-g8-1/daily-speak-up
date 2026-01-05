<script setup lang="ts">
    import { ref } from 'vue';
    import Avatar from 'primevue/avatar';
    import Button from 'primevue/button';
    import SpeedDial from 'primevue/speeddial';
    import type { ReportInfo } from '../types/report-info';
    import ScrollPanel from 'primevue/scrollpanel';
    
    const props = defineProps<{ reportInfo: ReportInfo }>();
    const emit = defineEmits<{
        (e: 'showInstructions'): void,
        (e: 'banUser', user_id:string, handle:string, reasons:string[] | undefined): void
    }>();

    const items = ref([
        {
            label: 'Upute',
            icon: 'pi pi-question',
            severity: 'contrast',
            class: '!bg-gray-200/50',
            command: () => {
                showInstructions();
            }
        },
        {
            label: 'Obriši prijavu',
            icon: 'pi pi-angle-double-left',
            class: '!bg-purple-200/50',
            severity: 'help',
            command: () => {
                console.log('Prijava obrisana');
            }
        },
        {
            label: 'Obriši video',
            icon: 'pi pi-delete-left',
            class: '!bg-orange-200/50',
            severity: 'warn',
            command: () => {
                console.log('Video obrisan');
            }
        },
        {
            label: 'Uruči zabranu',
            icon: 'pi pi-times',
            severity: 'danger',
            class: '!bg-red-200/50',
            command: () => {
                showConfirmBanDialog()
            }
        }
    ])

    const showInstructions = () => {
        emit('showInstructions');
    };

    const showConfirmBanDialog = () => {
        emit('banUser', props.reportInfo.user_info.user_id, props.reportInfo.user_info.handle, props.reportInfo.report_reasons);
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
                            justify-start items-center">

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
                            @click="showInstructions" />

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
                               }" >

                        <template #item="{ item }">

                            <Button 
                                :icon="item.icon"
                                rounded
                                variant="outlined"
                                :severity="item.severity"
                                :onClick="item.command"
                                :pt:root:class="item.class"
                                v-tooltip.left="item.label" />

                        </template>

                    </SpeedDial>

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

                    <ScrollPanel class="bg-gray-100 shadow-inner rounded-md
                                w-full lg:h-[100px] md:h-[200px] h-[100px] p-4 
                                text-left  
                                lg:text-sm
                                md:text-sm 
                                text-xs">
                        <p>
                            <span class="font-semibold">Opis videa:</span>
                            {{ props.reportInfo.caption }}
                        </p>

                        <hr class="my-2" />

                        <div>
                            <span class="font-semibold">Razlozi prijave:</span>
                            <br />
                            <ul class="list-disc pl-5">
                                <li v-for="(reason, index) in props.reportInfo.report_reasons" :key="index">
                                    {{ reason }}
                                </li>
                            </ul>
                        </div>
                    </ScrollPanel>
                    
                            
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
                                    :onClick="showConfirmBanDialog" 
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
<script setup lang="ts">
    import { ref, onMounted } from 'vue';
    import DataTable from 'primevue/datatable';
    import Column from 'primevue/column';
    import ColumnGroup from 'primevue/columngroup';  
    import Row from 'primevue/row';   
    import { Avatar } from 'primevue';
    import Button from 'primevue/button';
    import Popover from 'primevue/popover';

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'

    const bans = ref();
    const infoPopover = ref();
    const bannedByHandle = ref('');
    const banReason = ref('');
    
    onMounted( async() => {
        const response = await fetch(`${API_BASE_URL}/dashboard/bans`);
        if(response.ok) {
            bans.value = await response.json();
        } else {
            console.error('Failed to fetch bans:', response.statusText);
        }
    });

    const toggleInfoPopover = (event: Event, data: any) => {
        infoPopover.value.toggle(event);
        bannedByHandle.value = data.banned_by.handle;
        banReason.value = data.ban_reason;
    };

</script>

<template>
    <DataTable :value="bans" 
               
               paginator :rows="5"
               paginatorTemplate="FirstPageLink PageLinks LastPageLink JumpToPageInput CurrentPageReport">
        <Column field="banned_user.handle" header="Korisnik">
            <template #body="slotProps">
                <div class="flex flex-row
                            items-center">
                    <Avatar :image="slotProps.data.banned_user.profile_picture_url" 
                            :label="!slotProps.data.banned_user.profile_picture_url ? slotProps.data.banned_user.handle[0].toUpperCase() : ''"
                            shape="circle" 
                            size="xlarge" 
                            class="mr-2"
                            :pt="{
                                    root: { class: '!w-9 !h-9 md:!w-12 md:!h-12' },
                                    label: { class: 'text-xl' },
                                    image: { class: '!w-9 !h-9 md:!w-12 md:!h-12' }
                                }" />
                    <div class="text-sm
                                md:text-base
                                lg:text-lg">
                                @{{ slotProps.data.banned_user.handle }}
                    </div>
                </div>
            </template>
        </Column>
        <Column field="banned_by.handle" 
                header="Uručitelj zabrane"
                class="max-lg:hidden">
            <template #body="slotProps">
                <div class="flex flex-row 
                            items-center">
                    <Avatar :image="slotProps.data.banned_by.profile_picture_url" 
                            :label="!slotProps.data.banned_by.profile_picture_url ? slotProps.data.banned_by.handle[0].toUpperCase() : ''" 
                            shape="circle" 
                            class="mr-2"
                            :pt="{
                                    root: { class: '!w-12 !h-12' },
                                    label: { class: 'text-xl' },
                                    image: { class: '!w-12 !h-12' }
                                }" />
                    <div>
                                @{{ slotProps.data.banned_by.handle }}
                    </div>
                </div>
            </template>
        </Column>
        <Column field="ban_reason" 
                header="Razlog zabrane"
                class="max-lg:hidden">
        </Column>
        <Column header="Detalji"
                class="lg:hidden">
            <template #body="slotProps">
                <div class="flex flex-row 
                            justify-center
                            w-full">
                    <Button icon="pi pi-info" 
                            severity="info" 
                            variant="text" 
                            raised 
                            rounded
                            @click="toggleInfoPopover($event, slotProps.data)"
                            pt:root:class="!w-9 !h-9
                                           md:!w-11 md:!h-11"
                            pt:icon:class="text-sm
                                           md:text-base" />
                    <Popover ref="infoPopover">
                        <div class="flex flex-col
                                    justify-center items-start">

                            <div class="font-semibold
                                        mb-2">
                                Zabranu je uručio:
                            </div>

                            <div class="flex flex-row 
                                        items-center">
                                <Avatar :image="slotProps.data.banned_by.profile_picture_url" 
                                        :label="!slotProps.data.banned_by.profile_picture_url ? slotProps.data.banned_by.handle[0].toUpperCase() : ''" 
                                        shape="circle" 
                                        class="mr-2"
                                        :pt="{
                                                root: { class: '!w-12 !h-12' },
                                                label: { class: 'text-xl' },
                                                image: { class: '!w-12 !h-12' }
                                            }" />
                                <div>
                                            @{{ bannedByHandle }}
                                </div>
                            </div>
                             <div class="border-b-3
                                        border-gray-300
                                        w-full
                                        my-4">

                            </div>

                            <div>
                                <span class="font-semibold">Razlog zabrane:</span>
                                <p>{{ banReason }}</p>
                            </div>
                        </div>
                    </Popover>
                </div>
            </template>
        </Column>
        <Column header="Poništi zabranu">
            <template #body="slotProps">
                <div class="flex flex-row 
                            justify-center
                            w-full">
                    <Button icon="pi pi-undo" 
                            severity="help" 
                            variant="text" 
                            raised 
                            rounded
                            pt:root:class="!w-9 !h-9
                                           md:!w-11 md:!h-11"
                            pt:icon:class="text-sm
                                           md:text-base" />
                </div>
            </template>
        </Column>
    </DataTable>
</template>

<style scoped>
</style>
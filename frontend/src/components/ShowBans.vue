<script setup lang="ts">
    import { ref, onMounted, computed, onBeforeUnmount, nextTick } from 'vue';
    import DataTable from 'primevue/datatable';
    import Column from 'primevue/column';
    import { Avatar } from 'primevue';
    import Button from 'primevue/button';
    import Popover from 'primevue/popover';
    import { useConfirm } from "primevue/useconfirm";
    import Skeleton from 'primevue/skeleton';
    import { useI18n } from 'vue-i18n';

    const { t } = useI18n();
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1';
    const confirm = useConfirm();

    const bans = ref();
    const infoPopover = ref();
    const bannedByHandle = ref('');
    const banReason = ref('');
    const selectedBanData = ref<any>(null);
    const rowHeight = ref(0);
    const paginatorHeight = ref(0);
    const tableHeaderHeight = ref(0);
    const containerHeight = ref(0);
    const isLoading = ref(true);
    
    onMounted( async() => {
      
        await nextTick();
        setTimeout(() => {
            measureDimensions();
        }, 100);

        isLoading.value = true
        bans.value = new Array(rowsPerPage.value);

        window.addEventListener('resize', measureDimensions);
    });

    onBeforeUnmount(() => {
        window.removeEventListener('resize', measureDimensions);
    });

    const toggleInfoPopover = (event: Event, data: any) => {
        selectedBanData.value = data;
        bannedByHandle.value = data.banned_by.handle;
        banReason.value = data.ban_reason;
        infoPopover.value.toggle(event);
    };

    const measureDimensions = () => {
        const firstRow = document.querySelector('.p-row-even');
        if (firstRow) {
            rowHeight.value = firstRow.getBoundingClientRect().height;
        }
        
        const paginator = document.querySelector('.p-datatable-paginator-bottom');
        if (paginator) {
            paginatorHeight.value = paginator.getBoundingClientRect().height;
        }

        const tableHeader = document.querySelector('.p-datatable-thead');
        if (tableHeader) {
            tableHeaderHeight.value = tableHeader.getBoundingClientRect().height;
        }

        const container = document.querySelector('.datatable-container');
        if (container) {
            containerHeight.value = container.getBoundingClientRect().height;
        }
    };

    const rowsPerPage = computed(() => {
        if (rowHeight.value === 0 || containerHeight.value === 0) return 5;
        const availableHeight = containerHeight.value - paginatorHeight.value - tableHeaderHeight.value;

        return Math.floor(availableHeight / rowHeight.value);
    });

    const confirmUnban = (userId: string, userHandle: string) => {
        console.log('Attempting to unban user with ID:', userId);
        confirm.require({
            message: `${t('admin_dashboard.bans.confirm_unban.message')} @${userHandle}?`,
            header: t('admin_dashboard.bans.confirm_unban.header'),
            icon: 'pi pi-exclamation-triangle',
            acceptProps: { label: t('admin_dashboard.bans.confirm_unban.accept'), icon: 'pi pi-check' },
            rejectProps: { label: t('admin_dashboard.bans.confirm_unban.reject'), icon: 'pi pi-times' },
            accept: async () => {
                const response = await fetch(`${API_BASE_URL}/dashboard/unban-user`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_id: userId }),
                });
                if (response.ok) {
                    bans.value = bans.value.filter((ban: any) => ban.banned_user.user_id !== userId);
                } else {
                    console.error('Failed to unban user:', response.statusText);
                }
            },
            reject: () => {
            }
        });
    };

    const refreshBans = async () => {

        const response = await fetch(`${API_BASE_URL}/dashboard/bans`);
        if(response.ok) {
            bans.value = await response.json();
            isLoading.value = false;
        } else {
            console.error('Failed to refetch bans:', response.statusText);
        }
    };

    defineExpose({
        refreshBans
    });

</script>

<template>

    <div class="datatable-container h-full" >
        <DataTable :value="bans"         
                    paginator :rows="rowsPerPage"
                    :pt="{
                        headerRow: { class: 'text-sm md:text-base lg:text-lg' }
                    }"
                    paginatorTemplate="FirstPageLink PageLinks LastPageLink JumpToPageInput CurrentPageReport">
            <Column field="banned_user.handle" :header="t('admin_dashboard.bans.table.user')">
                <template #body="slotProps">
                    <Skeleton v-if="isLoading" height="2rem" />
                    <div v-else class="flex flex-row
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
                    :header="t('admin_dashboard.bans.table.banned_by')"
                    class="max-lg:hidden">
                <template #body="slotProps">
                    <Skeleton v-if="isLoading" height="2rem" />
                    <div v-else class="flex flex-row 
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
                    :header="t('admin_dashboard.bans.table.reason')"
                    class="max-lg:hidden">
                <template #body="slotProps">
                    <Skeleton v-if="isLoading" height="2rem" />
                    <span v-else>{{ slotProps.data.ban_reason }}</span>
                </template>
            </Column>
            <Column :header="t('admin_dashboard.bans.table.details')"
                    class="lg:hidden">
                <template #body="slotProps">
                    <Skeleton v-if="isLoading" shape="circle" size="2rem" />
                    <div v-else class="flex flex-row 
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
                    </div>
                </template>
            </Column>
            <Column :header="t('admin_dashboard.bans.table.unban')">
                <template #body="slotProps">
                    <Skeleton v-if="isLoading" shape="circle" size="2rem" />
                    <div v-else class="flex flex-row 
                                justify-center
                                w-full">
                        <Button icon="pi pi-undo" 
                                severity="help" 
                                variant="text" 
                                raised 
                                rounded
                                :onClick="() => confirmUnban(slotProps.data.banned_user.user_id, slotProps.data.banned_user.handle)"
                                pt:root:class="!w-9 !h-9
                                            md:!w-11 md:!h-11"
                                pt:icon:class="text-sm
                                            md:text-base" />
                    </div>
                </template>
            </Column>
        </DataTable>

        <Popover ref="infoPopover">
            <div class="flex flex-col
                        justify-center items-start">

                <div class="font-semibold
                            mb-2">
                    {{ t('admin_dashboard.bans.popover.banned_by') }}
                </div>

                <div class="flex flex-row 
                            items-center">
                    <Avatar :image="selectedBanData?.banned_by?.profile_picture_url" 
                            :label="!selectedBanData?.banned_by?.profile_picture_url ? selectedBanData?.banned_by?.handle?.[0]?.toUpperCase() : ''" 
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

                <div class="border-divider w-full my-4">
                </div>

                <div>
                    <span class="font-semibold">{{ t('admin_dashboard.bans.popover.reason') }}</span>
                    <p>{{ banReason }}</p>
                </div>
            </div>
        </Popover>
    </div>
</template>

<style scoped>
.border-divider {
    border-bottom: 3px solid var(--color-border-light);
}
</style>
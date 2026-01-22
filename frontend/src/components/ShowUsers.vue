<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from 'vue';
import ConfirmBanDialog from './ConfirmBanDialog.vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Avatar from 'primevue/avatar';
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import Select from 'primevue/select';
import { FilterMatchMode } from '@primevue/core/api';
import UsersVideosDIalog from './UsersVideosDIalog.vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123/api/v1'
const users = ref([]);
const showUsers = ref([]);
const rowHeight = ref(0);
const containerHeight = ref(0);
const handles = ref<string[]>([]);
const searchValue = ref(null)
const banReasons = ref<any[] | undefined>(undefined);
const showBanConfirmDialog = ref(false);
const showUsersVideosDialog = ref(false);
const userInfo = ref<any | null | undefined>(null);
const banHandle = ref<string | null | undefined>(null);
const banUserId = ref<string | null | undefined>(null);
const userRoles = computed(() => [
    { name: t('admin_dashboard.users.roles.user'), code: import.meta.env.VITE_USER_ROLE },
    { name: t('admin_dashboard.users.roles.moderator'), code: import.meta.env.VITE_MODERATOR_ROLE },
    { name: t('admin_dashboard.users.roles.admin'), code: import.meta.env.VITE_ADMIN_ROLE },
])
const filters = ref({
    'user_role': { value: null, matchMode: FilterMatchMode.EQUALS }
});

const rowsPerPage = computed(() => {
    if (rowHeight.value === 0 || containerHeight.value === 0) return 5;
    const paginatorHeight = 60; 
    const availableHeight = containerHeight.value - paginatorHeight;
    
    return Math.floor(availableHeight / rowHeight.value);
});

onMounted(async () => {
    const response = await fetch(`${API_BASE_URL}/dashboard/users`,
    {
        credentials: 'include'
    }
    );
    if(response.ok) {
        let data = await response.json();

        for (let user of data) {
            user.onToggle = user.user_role === 'mod';
        }

        users.value = data;
        showUsers.value = data;
        handles.value = data.map((user: any) => user.handle);
        setTimeout(() => {
            measureDimensions();
        }, 100);
    } else {
        console.error('Failed to fetch users:', response.statusText);
    }
    
    window.addEventListener('resize', measureDimensions);
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', measureDimensions);
});

const search = (event: { query: string }) => {
    const query = event.query.toLowerCase();

    let query_result = users.value
        .map((user: any) => user.handle)
        .filter((handle: string) => handle.toLowerCase().includes(query));
    handles.value = query_result;
    showUsers.value = users.value.filter((user: any) => 
        user.handle.toLowerCase().includes(query)
    );
};

const resetUsers = () => {
    handles.value = users.value.map((user: any) => user.handle);
    showUsers.value = users.value;
};

const measureDimensions = () => {
    const firstRow = document.querySelector('.user-row');
    if (firstRow) {
        rowHeight.value = firstRow.getBoundingClientRect().height;
    }
    
    const container = document.querySelector('.dataview-container');
    if (container) {
        containerHeight.value = container.getBoundingClientRect().height;
    }
};

const showConfirmBanDialog = async (user: any) => {

    const response = await fetch(`${API_BASE_URL}/dashboard/report-reasons/${user.user_id}`, {credentials: 'include'});
    if(response.ok) {
        let data = await response.json();
        data.push(t('admin_dashboard.custom_reason'));
        let reasonObjectList = [];
        for (let reason of data) {
            reasonObjectList.push({name: reason});
        }
        banReasons.value = reasonObjectList;
    } else {
        console.error('Failed to fetch ban reasons:', response.statusText);
        banReasons.value = [{name: t('admin_dashboard.custom_reason')}];
    }

    banHandle.value = user.handle;
    banUserId.value = user.user_id;
    showBanConfirmDialog.value = true;
};

const handleUserRoleChange = async (role: any, item: any) => {
    if (role !== import.meta.env.VITE_USER_ROLE &&
        role !== import.meta.env.VITE_MODERATOR_ROLE &&
        role !== import.meta.env.VITE_ADMIN_ROLE) {
        console.error('Invalid role selected:', role);
        return;
    }

    const response = await fetch(`${API_BASE_URL}/dashboard/user-role`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: item.user_id,
            new_role: role
        }),
    });
};

const handleShowUsersVideosDialog = (user: any) => {
    userInfo.value = user;
    showUsersVideosDialog.value = true;
};

</script>

<template>
    <ConfirmBanDialog :reasons="banReasons"
                      :handle="banHandle"
                      :userId="banUserId"
                     v-model:showDialog="showBanConfirmDialog" />
    
    <UsersVideosDIalog 
                    v-model:showDialog="showUsersVideosDialog"
                    :user="userInfo" />

   <div class="flex flex-col justify-center items-center gap-2">
        <div class="w-full flex justify-center items-center">
            <AutoComplete v-model="searchValue" :placeholder="t('admin_dashboard.users.search_placeholder')" :suggestions="handles" :dropdown="false" @complete="search" @clear="resetUsers"/> 
        </div>

        <div class="dataview-container w-[90%]" style="height: calc(100vh - 215px)">
            <DataTable :value="showUsers" paginator :rows="rowsPerPage" v-model:filters="filters" filterDisplay="row">

                <Column :header="t('admin_dashboard.users.table.user')">
                    <template #body="slotProps">
                        <div class="flex flex-row items-center">
                            <div class="md:w-40 flex flex-col justify-center items-center">
                                <Avatar :image="slotProps.data.profile_picture_url" shape="circle" />
                            </div>
                            <div class="flex flex-col">
                                <span class="font-semibold text-lg">{{ slotProps.data.handle }}</span>
                                <span class="text-sm user-email">{{ slotProps.data.email }}</span>
                            </div>
                        </div>
                    </template>
                </Column>

                <Column>
                    <template #body="slotProps">
                        <Button icon="pi pi-video" rounded variant="outlined" aria-label="Videos" v-tooltip.top="{ value: t('admin_dashboard.users.table.videos_tooltip'), showDelay: 500, hideDelay: 100 }" :onClick="() => handleShowUsersVideosDialog(slotProps.data)" />
                    </template>
                </Column>

                <Column>
                    <template #body="slotProps">
                        <Button icon="pi pi-times" severity="danger" rounded variant="outlined" aria-label="Ban" v-tooltip.top="{ value: t('admin_dashboard.users.table.ban_tooltip'), showDelay: 500, hideDelay: 100 }" :onClick="() => showConfirmBanDialog(slotProps.data)" />
                    </template>
                </Column>

                <Column :header="t('admin_dashboard.users.table.role')" filterField="user_role" :showFilterMenu="false">
                    <template #body="slotProps">
                        <Select v-model="slotProps.data.user_role"
                                :options="userRoles"
                                optionLabel="name"
                                optionValue="code"
                                :placeholder="t('admin_dashboard.users.table.role')"
                                class="w-36"
                                v-tooltip.top="{ value: t('admin_dashboard.users.table.role_tooltip'), showDelay: 500, hideDelay: 100 }"
                                @update:modelValue="handleUserRoleChange($event, slotProps.data)" />
                    </template>
                    <template #filter="{ filterModel, filterCallback }">
                        <Select v-model="filterModel.value"
                                :options="userRoles"
                                optionLabel="name"
                                optionValue="code"
                                :placeholder="t('admin_dashboard.users.table.role_filter_placeholder')"
                                class="w-36"
                                :showClear="true"
                                @change="filterCallback()" />
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
</template>

<style scoped>
:deep(.p-autocomplete) {
    display: flex;
    justify-content: center;
    width: 100%;
}

:deep(.p-autocomplete .p-autocomplete-input) {
    width: 60%;
    --p-inputtext-border-color: gray;
}

.p-avatar {
    --p-avatar-width: 5vw;
    --p-avatar-height: 5vw;
}

.dataview-container {
    overflow: hidden;
}

.p-togglebutton {
    --p-togglebutton-checked-color: #7b3880;
    --p-togglebutton-checked-border-color: #7b3880;
    --p-togglebutton-icon-checked-color: #7b3880;
    --p-togglebutton-checked-background: #fef8fe;
}

.user-email {
    color: var(--color-text-muted);
}

</style>
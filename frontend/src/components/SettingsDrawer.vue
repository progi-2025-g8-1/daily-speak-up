<script setup>
    import Drawer from 'primevue/drawer';
    import Button from 'primevue/button';
    import Select from 'primevue/select';
    import { useConfirm } from "primevue/useconfirm";
    import MultiSelect from 'primevue/multiselect';
    import Panel from 'primevue/panel';
    import ToggleSwitch from 'primevue/toggleswitch';
    import ConfirmDialog from 'primevue/confirmdialog';
    import Login from './LoginModal.vue';
    import Logout from './Logout.vue';
    import User from './User.vue';
    import { RouterLink } from 'vue-router';
    import { ref, onMounted, watch } from 'vue';
    import { useThemeStore } from '../stores/themeStore';

    const visible = ref(false);
    const selectedTheme = ref('light');
    const themeStore = useThemeStore();
    const selectedLanguage = ref('hr');
    const selectedInterests = ref([]);
    const interests = ref([]);
    
    // Watch for theme changes and update theme store
    watch(selectedTheme, (newTheme) => {
        if (newTheme === 'light' || newTheme === 'dark') {
            themeStore.setTheme(newTheme);
        }
    });
    const emailNotifs = ref(false);
    const pushNotifs = ref(false);
    const streakNotifs = ref(false);
    const confirm = useConfirm();

    const confirm_account_deletion = () => {
        confirm.require({
        message: 'Jeste li sigurni da želite izbrisati svoj račun? Ova se radnja ne može poništiti.',
        header: 'Opasna radnja',
        icon: 'pi pi-exclamation-triangle',
        rejectLabel: 'Odustani',
        rejectProps: {
            label: 'Odustani',
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: 'Izbriši',
            severity: 'danger'
        },
        accept: async () => {
            try {
                const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/delete`, {
                    method: 'DELETE',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    window.location.reload();
                } else {
                    console.error('Failed to delete account');
                }
            } catch (error) {
                console.error('Error deleting account:', error);
            }
        },
        reject: () => {
            console.log('Account deletion rejected');
        }
    });
    }

    onMounted(async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/interests`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                const allInterests = await response.json();
                allInterests.forEach(interest => {
                    interests.value.push({ name: interest.label, code: interest.slug });
                });
            }

            const response2 = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/interests`, {
                method: 'GET',
                credentials: 'include'
            });

            if(response2.ok){
                const interestList = await response2.json();
                selectedInterests.value = interestList.interests
            }
        } catch (e) {
            console.error('Failed to fetch interests:', e);
        }

        try {
            const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/me`, {
                method: 'GET',
            });

            if (response.ok) {
                const data = await response.json()
                
                if(data.preferred_theme === 'system') {
                    selectedTheme.value = 'system';
                } else if (data.preferred_theme === 'light') {
                    selectedTheme.value = 'light';
                } else {
                    selectedTheme.value = 'dark';
                }
                
                if(data.preferred_lang === 'hr') {
                    selectedLanguage.value = 'hr';
                } else {
                    selectedLanguage.value = 'en';
                }

                if(data.email_notifications_enabled) {
                    emailNotifs.value = true;
                } else {
                    emailNotifs.value = false;
                }

                if (data.push_notifications_enabled) {
                    pushNotifs.value = true;
                } else {
                    pushNotifs.value = false;
                }

                if(data.streak_reminders_enabled) {
                    streakNotifs.value = true;
                } else {
                    streakNotifs.value = false;
                }
            }
        } catch(e) {
            console.error('Failed to fetch /user/me: ', e)
        }
    });

    const language = ref([
        { name: 'Hrvatski', code: 'hr' },
        { name: 'Engleski', code: 'en' },
    ]);

    const themes = ref([
        { name: 'Svijetla', code: 'light' },
        { name: 'Tamna', code: 'dark' },
        { name: 'Tema sustava', code: 'system' },
    ]);

    const updateEmailNotifs = async () => {
        const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/email-notifications`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ enabled: emailNotifs.value })
        });
    };

    const updatePushNotifs = async () => {
        const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/push-notifications`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ enabled: pushNotifs.value })
        });
    };

    const updateStreakNotifs = async () => {
        const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/streak-reminders`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ enabled: streakNotifs.value })
        });
    };

</script>

<template>
    <ConfirmDialog></ConfirmDialog>
    <div class="flex justify-center">
        <Drawer v-model:visible="visible" header="Postavke računa" position="left" 
                :dismissable="false" class="!w-full lg:!w-[40vw]">
            <div class="flex flex-row justify-between items-center mt-2">
                <User />
                <Button icon="pi pi-upload" v-tooltip="{ value: 'Prenesite novu profilnu fotografiju', showDelay: 300, hideDelay: 300 }" rounded aria-label="Profilna" />
            </div>

            <div class="flex flex-col justify-start items-stretch w-full">
                
                <Select v-model="selectedTheme" :options="themes" optionLabel="name" optionValue="code" placeholder="Odaberite temu" class="w-full mt-10" />
                <Select v-model="selectedLanguage" :options="language" optionLabel="name" optionValue="code" placeholder="Odaberite jezik" class="w-full mt-10" />
                <MultiSelect v-model="selectedInterests" :options="interests" optionLabel="name" optionValue="code" filter placeholder="Promijenite svoje interese"  class="w-full mt-10" />
                
                <Panel header="Postavke obavijesti" class="mt-10">
                    <div class="mt-8 flex flex-col justify-start items-start">
                        <div class="flex flex-row justify-between w-full mb-4">
                            <span class="text-md font-medium">e-mail obavijesti</span>
                            <ToggleSwitch v-model="emailNotifs" @update:modelValue="updateEmailNotifs" />
                        </div>

                        <div class="flex flex-row justify-between w-full mb-4">
                            <span class="text-md font-medium">push obavijesti</span>
                            <ToggleSwitch v-model="pushNotifs" @update:modelValue="updatePushNotifs" />
                        </div>
    
                        <div class="flex flex-row justify-between w-full mb-4">
                            <span class="text-md font-medium">streak podsjetnici</span>
                            <ToggleSwitch v-model="streakNotifs" @update:modelValue="updateStreakNotifs" />
                        </div>
                    </div>
                </Panel>
                
                <div class="flex flex-row w-full justify-between mt-10">
                    <Logout class="mt-10 w-[45%]" />
                    <Button @click="confirm_account_deletion()" label="Izbriši račun" severity="danger" icon="pi pi-trash" class="mt-10 w-[45%]" />
                </div>
            </div>
        </Drawer>
        <div class="flex flex-col justify-center items-center aspect-square rounded-full w-10 mr-1 h-10 hover:scale-105 cursor-pointer transition duration-200"
            style="border: 2px solid var(--color-primary);"
            @click="visible = true">
            <span class="pi pi-cog" style="color: var(--color-text-dark); font-size: 1.2rem;"></span>
        </div>
    </div>
</template>

<style scoped>
    .yMargin {
        margin: 1.3rem 0;
    }

</style>

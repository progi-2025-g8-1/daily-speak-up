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
    import { ref, onMounted, computed, watch } from 'vue';
    import { useI18n } from 'vue-i18n';
    import { useThemeStore } from '../stores/themeStore';

    const { t, locale } = useI18n();
    const visible = ref(false);
    const themeStore = useThemeStore();
    const selectedLanguage = ref('hr');
    const selectedInterests = ref([]);
    const interests = ref([]);
    const emailNotifs = ref(false);
    const pushNotifs = ref(false);
    const streakNotifs = ref(false);
    const confirm = useConfirm();
    const hideDeleteAccountBtn = ref(false);

    const getTranslatedInterestLabel = (slug) => {
        try {
            const translated = t(`interests.${slug}`);
            // If translation key doesn't exist, t() returns the key itself
            if (translated !== `interests.${slug}`) {
                return translated;
            }
        } catch (e) {
            // fallback
        }
        return slug.replace('_', ' ').charAt(0).toUpperCase() + slug.slice(1);
    };

    const updateInterestNames = () => {
        interests.value = interests.value.map(interest => ({
            name: getTranslatedInterestLabel(interest.code),
            code: interest.code
        }));
    };

    watch(locale, () => {
        updateInterestNames();
    });

    const confirm_account_deletion = () => {
        confirm.require({
        message: t('settings.delete_confirmation.message'),
        header: t('settings.delete_confirmation.header'),
        icon: 'pi pi-exclamation-triangle',
        rejectLabel: t('settings.delete_confirmation.cancel'),
        rejectProps: {
            label: t('settings.delete_confirmation.cancel'),
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: t('settings.delete_confirmation.delete'),
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
                    interests.value.push({ 
                        name: getTranslatedInterestLabel(interest.slug), 
                        code: interest.slug 
                    });
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
                
                // Theme selection removed; force language handling only
                
                if(data.preferred_lang === 'hr') {
                    selectedLanguage.value = 'hr';
                    locale.value = 'hr';
                } else {
                    selectedLanguage.value = 'en';
                    locale.value = 'en';
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

        let userRole = localStorage.getItem('userRole');
        if(userRole === undefined || userRole === null) {
            const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/me`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const userData = await response.json();
                localStorage.setItem('userRole', userData.role);
                userRole = userData.role;
            }
        }

        hideDeleteAccountBtn.value = userRole === import.meta.env.VITE_ROOT_ROLE;
    });

    const language = computed(() => [
        { name: t('settings.lang.croatian'), code: 'hr' },
        { name: t('settings.lang.english'), code: 'en' },
    ]);

    const themeOptions = computed(() => [
        { name: t('settings.theme.light'), code: 'light' },
        { name: t('settings.theme.dark'), code: 'dark' },
    ]);

    const updateTheme = (themeCode) => {
        themeStore.setTheme(themeCode);
    };

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

    const updateLanguage = async (langCode) => {
        selectedLanguage.value = langCode;
        locale.value = langCode;

        try {
            const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/preferred-language`, {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ lang: langCode })
            });

            if (!response.ok) {
                console.error('Failed to update preferred language');
            }
        } catch (error) {
            console.error('Error updating preferred language:', error);
        }
    };

</script>

<template>
    <ConfirmDialog></ConfirmDialog>
    <div class="flex justify-center">
        <Drawer v-model:visible="visible" :header="$t('settings.title')" position="left" 
                :dismissable="false" class="!w-full lg:!w-[40vw]">
            <div class="flex flex-row justify-between items-center mt-2">
                <User />
            </div>

            <div class="flex flex-col justify-start items-stretch w-full">
                
                <Select v-model="themeStore.themeMode" :options="themeOptions" optionLabel="name" optionValue="code" :placeholder="$t('settings.select_theme')" class="w-full mt-10" @update:modelValue="updateTheme" />
                <Select v-model="selectedLanguage" :options="language" optionLabel="name" optionValue="code" :placeholder="$t('settings.select_language')" class="w-full mt-10" @update:modelValue="updateLanguage" />
                <MultiSelect v-model="selectedInterests" :options="interests" optionLabel="name" optionValue="code" filter :placeholder="$t('settings.change_interests')"  class="w-full mt-10">
                    <template #value="slotProps">
                        <div v-if="slotProps.value && slotProps.value.length" class="flex flex-wrap gap-2">
                            <span v-for="code in slotProps.value" :key="code" class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">{{ getTranslatedInterestLabel(code) }}</span>
                        </div>
                        <span v-else class="text-gray-400">{{ $t('settings.change_interests') }}</span>
                    </template>
                    <template #item="slotProps">
                        <div class="flex items-center">
                            <span>{{ getTranslatedInterestLabel(slotProps.option.code) }}</span>
                        </div>
                    </template>
                </MultiSelect>
                
                <Panel :header="$t('settings.notifications.title')" class="mt-10">
                    <div class="mt-8 flex flex-col justify-start items-start">
                        <div class="flex flex-row justify-between w-full mb-4">
                            <span class="text-md font-medium">{{ $t('settings.notifications.email') }}</span>
                            <ToggleSwitch v-model="emailNotifs" @update:modelValue="updateEmailNotifs" />
                        </div>

                        <div class="flex flex-row justify-between w-full mb-4">
                            <span class="text-md font-medium">{{ $t('settings.notifications.push') }}</span>
                            <ToggleSwitch v-model="pushNotifs" @update:modelValue="updatePushNotifs" />
                        </div>
    
                        <div class="flex flex-row justify-between w-full mb-4">
                            <span class="text-md font-medium">{{ $t('settings.notifications.streak') }}</span>
                            <ToggleSwitch v-model="streakNotifs" @update:modelValue="updateStreakNotifs" />
                        </div>
                    </div>
                </Panel>
                
                <div class="flex flex-row w-full justify-between mt-10">
                    <Logout class="mt-10 w-[45%]" />
                    <Button v-if="!hideDeleteAccountBtn" @click="confirm_account_deletion()" :label="$t('settings.delete_account')" severity="danger" icon="pi pi-trash" class="mt-10 w-[45%]" />
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

<style>
    .yMargin {
        margin: 1.3rem 0;
    }

    .p-select:focus,
    .p-select:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25) !important;
    }

    .p-select-overlay .p-select-option:hover {
        background-color: #60a5fa !important;
        color: white !important;
    }

    .p-select-overlay .p-select-option.p-focus {
        background-color: #60a5fa !important;
        color: white !important;
    }

    .p-select-overlay .p-select-option.p-highlight {
        background-color: #3b82f6 !important;
        color: white !important;
    }

    .p-multiselect:focus,
    .p-multiselect:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25) !important;
    }

    .p-multiselect-overlay .p-multiselect-option:hover {
        background-color: #60a5fa !important;
        color: white !important;
    }

    .p-multiselect-overlay .p-multiselect-option.p-focus {
        background-color: #60a5fa !important;
        color: white !important;
    }

    .p-multiselect-overlay .p-multiselect-option.p-highlight {
        background-color: #3b82f6 !important;
        color: white !important;
    }

</style>

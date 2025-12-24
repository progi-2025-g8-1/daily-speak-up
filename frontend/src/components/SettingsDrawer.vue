<script setup>
    import Drawer from 'primevue/drawer';
    import Button from 'primevue/button';
    import Select from 'primevue/select';
    import MultiSelect from 'primevue/multiselect';
    import Panel from 'primevue/panel';
    import ToggleSwitch from 'primevue/toggleswitch';
    import Login from './LoginModal.vue';
    import Logout from './Logout.vue';
    import User from './User.vue';
    import { RouterLink } from 'vue-router';
    import { ref, onMounted } from 'vue';

    const visible = ref(false);
    const selectedTheme = ref();
    const selectedLanguage = ref();
    const selectedInterests = ref([]);
    const interests = ref([]);

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
        } catch (e) {
            console.error('Failed to fetch interests:', e);
        }
    });

    const language = ref([
        { name: 'Hrvatski', code: 'hr' },
        { name: 'Engleski', code: 'en' },
    ]);

    const themes = ref([
        { name: 'Svjetla', code: 'light' },
        { name: 'Tamna', code: 'dark' },
        { name: 'Tema sustava', code: 'system' },
    ]);

</script>

<template>
    <div class="flex justify-center">
        <Drawer v-model:visible="visible" header="Postavke računa" position="left" 
                :dismissable="false" class="!w-full lg:!w-[40vw]">
            <div class="flex flex-row justify-between items-center mt-2">
                <User />
                <Button icon="pi pi-upload" v-tooltip="{ value: 'Prenesite novu profilnu fotografiju', showDelay: 300, hideDelay: 300 }" rounded aria-label="Profilna" />
            </div>

            <div class="flex flex-col justify-start items-stretch w-full">
                
                <Select v-model="selectedTheme" :options="themes" optionLabel="name" placeholder="Odaberite temu" class="w-full mt-10" />
                <Select v-model="selectedLanguage" :options="language" optionLabel="name" placeholder="Odaberite jezik" class="w-full mt-10" />
                <MultiSelect v-model="selectedInterests" :options="interests" optionLabel="name" filter placeholder="Promijenite svoje interese"  class="w-full mt-10" />
                
                <Panel header="Postavke obavijesti" class="mt-10">
                    <div class="mt-8 flex flex-col justify-start items-start">
                        <div class="flex flex-row justify-between w-full mb-4">
                            <span class="text-md font-medium">e-mail obavijesti</span>
                            <ToggleSwitch :v-model="false" />
                        </div>

                        <div class="flex flex-row justify-between w-full mb-4">
                            <span class="text-md font-medium">push obavijesti</span>
                            <ToggleSwitch :v-model="false" />
                        </div>
    
                        <div class="flex flex-row justify-between w-full mb-4">
                            <span class="text-md font-medium">streak podsjetnici</span>
                            <ToggleSwitch :v-model="false" />
                        </div>
                    </div>
                </Panel>
                
                <div class="flex flex-row w-full justify-between mt-10">
                    <Logout class="mt-10 w-[45%]" />
                    <Button label="Delete account" severity="danger" icon="pi pi-trash" class="mt-10 w-[45%]" />
                </div>
            </div>
        </Drawer>
        <div class="flex flex-col justify-center items-center border-2 border-solid aspect-square
                    rounded-full border-blue w-10 mr-1 h-10 hover:scale-105 cursor-pointer transition duration-200"
            @click="visible = true">
            <span class="pi pi-cog" style="color:black; font-size: 1.2rem;"></span>
        </div>
    </div>
</template>

<style scoped>
    .yMargin {
        margin: 1.3rem 0;
    }

</style>

<script setup lang="ts">
  import MainFrame from '../components/MainFrame.vue';
  import FriendsFrame from '../components/FriendsFrame.vue';
  import Divider from 'primevue/divider';
</script>

<template>
  <div class="flex flex-col lg:flex-row w-full h-full">
    <MainFrame />
    <div class="hidden lg:block">
      <Divider layout="vertical" :pt="{root:{class:'divider'}}"/>
    </div>
    <div class="block lg:hidden">
      <Divider layout="horizontal"  :pt="{root:{class:'divider'}}" />
    </div>
    <FriendsFrame />
  </div>
</template>

<style scoped>
.divider{
  --p-divider-vertical-margin:0 0 0 0;
  --p-divider-horizontal-margin:0 0 0 0;
}
.btnmy {
  --p-button-border-radius: 9rem;
}
</style>

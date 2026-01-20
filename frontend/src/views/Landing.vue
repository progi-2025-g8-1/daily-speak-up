<script setup lang="ts">
import Avatar from 'primevue/avatar'
import { useRoute } from 'vue-router'
import { ref, computed } from 'vue'
import Login from '../components/LoginModal.vue'
import { useI18n } from 'vue-i18n'
import { useThemeStore } from '../stores/themeStore'

const isHome = computed(() => useRoute().path === '/')
const { locale, t } = useI18n()

const toggleLanguage = () => {
  locale.value = locale.value === 'hr' ? 'en' : 'hr'
  localStorage.setItem('app-language', locale.value)
}
const themeStore = useThemeStore()

const teamSet = ref([
  { url: 'https://avatars.githubusercontent.com/u/44684310?v=4', name: 'Kristijan Bilanović' },
  { url: 'https://avatars.githubusercontent.com/u/205453688?v=4', name: 'Lara Brečić' },
  { url: 'https://avatars.githubusercontent.com/u/236687211?v=4', name: 'Lara Desnica' },
  { url: 'https://avatars.githubusercontent.com/u/219036118?v=4', name: 'Mate Jakovljev' },
  { url: 'https://avatars.githubusercontent.com/u/74995193?v=4', name: 'Matej Jurasić' },
  { url: 'https://avatars.githubusercontent.com/u/104315710?v=4', name: 'Emil Popović' },
  { url: 'https://avatars.githubusercontent.com/u/153128323?v=4', name: 'Nika Valić' },
])
</script>

<template>
  <div class="min-h-screen flex flex-col bg-main">
  
    <header class="relative bg-card">
      <div class="max-w-6xl mx-auto px-6 pt-28 pb-20 sm:pt-32 sm:pb-24 flex flex-col items-center">
       <nav class="absolute inset-x-0 top-0 flex justify-end items-center gap-4 items-center gap-4 px-6 sm:px-10 py-4 z-10">
        <button 
          @click="toggleLanguage()"
          class="text-white font-semibold rounded-lg transition-all duration-200 shadow-sm hover:shadow-md flex items-center justify-center"
          style="background-color: #2563eb; width: 65px; height: 42px; padding: 0;"
          :title="locale === 'hr' ? 'Switch to English' : 'Prebaci na Hrvatski'"
        >
          {{ locale === 'hr' ? 'EN' : 'HR' }}
        </button>
        <button 
          @click="themeStore.toggleTheme()"
          class="text-white font-semibold rounded-lg transition-all duration-200 shadow-sm hover:shadow-md flex items-center justify-center"
          style="background-color: #2563eb; width: 65px; height: 42px; padding: 0;"
          :title="themeStore.themeMode.value === 'dark' ? 'Promijeni na svijetlu temu' : 'Promijeni na tamnu temu'"
        >
          <svg v-if="themeStore.themeMode.value === 'dark'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
          </svg>
          <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
          </svg>
        </button>
        <Login/>
       </nav>


        <!-- Logo -->
        <img
          src="../assets/DSU_logo.svg"
          alt="DailySpeakUp Logo"
          class="w-28 h-28 sm:w-40 sm:h-40 mb-8"
        />

        <!-- Naslov + opis -->
        <div class="text-center max-w-2xl">
          <h1 class="text-3xl sm:text-4xl font-semibold tracking-tight text-dark">
            {{ t('landing.hero_title') }}
          </h1>
          <p class="mt-8 text-base sm:text-lg text-secondary leading-relaxed">
            {{ t('landing.hero_subtitle_1') }}
          </p>
          <p class="mt-3 text-base text-secondary leading-relaxed">
            {{ t('landing.hero_subtitle_2') }}
          </p>
          <p class="mt-3 text-sm text-light leading-relaxed">
            {{ t('landing.hero_subtitle_3') }}
          </p>
        </div>
      </div>
    </header>

    <!-- KAKO RADI -->
    <section class="max-w-6xl mx-auto px-6 py-14 sm:py-16">
      <h2 class="text-2xl sm:text-3xl font-semibold text-center text-primary">{{ t('landing.how_it_works_title') }}</h2>
      <p class="text-secondary text-center mt-2">{{ t('landing.how_it_works_subtitle') }}</p>

      <div class="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div class="rounded-xl border border-light bg-card p-6 text-center">
          <div class="text-4xl">🎯</div>
          <h3 class="mt-3 font-semibold text-lg text-dark">{{ t('landing.step_1_title') }}</h3>
          <p class="mt-2 text-secondary leading-relaxed">{{ t('landing.step_1_desc') }}</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6 text-center">
          <div class="text-4xl">🎤</div>
          <h3 class="mt-3 font-semibold text-lg text-dark">{{ t('landing.step_2_title') }}</h3>
          <p class="mt-2 text-secondary leading-relaxed">{{ t('landing.step_2_desc') }}</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6 text-center">
          <div class="text-4xl">💬</div>
          <h3 class="mt-3 font-semibold text-lg text-dark">{{ t('landing.step_3_title') }}</h3>
          <p class="mt-2 text-secondary leading-relaxed">{{ t('landing.step_3_desc') }}</p>
        </div>
      </div>
    </section>

    <!-- BENEFITI -->
    <section class="max-w-6xl mx-auto px-6 py-14 sm:py-16">
      <h2 class="text-2xl sm:text-3xl font-semibold text-center text-primary">{{ t('landing.benefits_title') }}</h2>
      <div class="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="rounded-xl border border-light bg-card p-6">
          <div class="text-2xl">🗣️</div>
          <h3 class="mt-3 font-semibold text-dark">{{ t('landing.benefit_1_title') }}</h3>
          <p class="mt-2 text-secondary leading-relaxed">{{ t('landing.benefit_1_desc') }}</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6">
          <div class="text-2xl">⏰</div>
          <h3 class="mt-3 font-semibold text-dark">{{ t('landing.benefit_2_title') }}</h3>
          <p class="mt-2 text-secondary leading-relaxed">{{ t('landing.benefit_2_desc') }}</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6">
          <div class="text-2xl">🤖</div>
          <h3 class="mt-3 font-semibold text-dark">{{ t('landing.benefit_3_title') }}</h3>
          <p class="mt-2 text-secondary leading-relaxed">{{ t('landing.benefit_3_desc') }}</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6">
          <div class="text-2xl">🔒</div>
          <h3 class="mt-3 font-semibold text-dark">{{ t('landing.benefit_4_title') }}</h3>
          <p class="mt-2 text-secondary leading-relaxed">{{ t('landing.benefit_4_desc') }}</p>
        </div>
      </div>
    </section>


    <!-- FOOTER TEAM -->
    <footer v-if="isHome" class="bg-accent border-t border-light py-10">
      <div class="max-w-6xl mx-auto px-6">
        <div class="flex flex-wrap justify-center gap-x-10 gap-y-6">
          <div v-for="member in teamSet" :key="member.name" class="text-center">
            <Avatar :image="member.url" class="medium lg:xlarge" shape="circle" />
            <div class="mt-2 font-medium text-dark">{{ member.name }}</div>
          </div>
        </div>
        <div class="mt-10 text-center text-xs text-muted">
          © {{ new Date().getFullYear() }} {{ t('landing.footer_rights') }}
        </div>
      </div>
    </footer>
  </div>
</template>

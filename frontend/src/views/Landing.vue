<script setup lang="ts">
import Avatar from 'primevue/avatar'
import { useRoute } from 'vue-router'
import { ref, computed } from 'vue'
import Login from '../components/LoginModal.vue'
import { useI18n } from 'vue-i18n'

const isHome = computed(() => useRoute().path === '/')
const { locale } = useI18n()

const toggleLanguage = () => {
  locale.value = locale.value === 'hr' ? 'en' : 'hr'
  localStorage.setItem('app-language', locale.value)
}

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
       <nav class="absolute inset-x-0 top-0 flex justify-end items-center gap-4 px-6 sm:px-10 py-4 z-10">
        <button 
          @click="toggleLanguage()"
          class="px-6 py-2.5 text-white font-semibold rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
          style="background-color: var(--color-primary);"
          :title="locale === 'hr' ? 'Switch to English' : 'Prebaci na Hrvatski'"
        >
          {{ locale === 'hr' ? 'EN' : 'HR' }}
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
            DailySpeakUp
          </h1>
          <p class="mt-8 text-base sm:text-lg text-secondary leading-relaxed">
            U današnjem akademskom i poslovnom okruženju, mnogi se i dalje suočavaju s izazovima javnog nastupa i jasne, samouvjerene komunikacije – ključne vještine za osobni i profesionalni uspjeh.
          </p>
          <p class="mt-3 text-base text-secondary leading-relaxed">
            DailySpeakUp nudi jednostavno i pristupačno rješenje — svakodnevne govorne izazove od jedne minute koji ti pomažu da s vremenom postaneš sigurniji i tečniji govornik.
          </p>
          <p class="mt-3 text-sm text-light leading-relaxed">
            Bez potrebe za skupim tečajevima ili mentorima, možeš svakodnevno vježbati, pratiti vlastiti napredak i dobivati povratne informacije od zajednice koja uči i napreduje zajedno s tobom.
          </p>
        </div>
      </div>
    </header>

    <!-- KAKO RADI -->
    <section class="max-w-6xl mx-auto px-6 py-14 sm:py-16">
      <h2 class="text-2xl sm:text-3xl font-semibold text-center text-primary">Kako to izgleda u praksi</h2>
      <p class="text-secondary text-center mt-2">Tri jednostavna koraka</p>

      <div class="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div class="rounded-xl border border-light bg-card p-6 text-center">
          <div class="text-4xl">🎯</div>
          <h3 class="mt-3 font-semibold text-lg text-dark">Odabir teme</h3>
          <p class="mt-2 text-secondary leading-relaxed">Označi svoje interese i odaberi temu od ponuđenih opcija.</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6 text-center">
          <div class="text-4xl">🎤</div>
          <h3 class="mt-3 font-semibold text-lg text-dark">Kratko snimanje</h3>
          <p class="mt-2 text-secondary leading-relaxed">1 minuta govora na webu ili mobitelu.</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6 text-center">
          <div class="text-4xl">💬</div>
          <h3 class="mt-3 font-semibold text-lg text-dark">Povratna informacija</h3>
          <p class="mt-2 text-secondary leading-relaxed">Dobivaš detaljne komentare od zajednice.</p>
        </div>
      </div>
    </section>

    <!-- BENEFITI -->
    <section class="max-w-6xl mx-auto px-6 py-14 sm:py-16">
      <h2 class="text-2xl sm:text-3xl font-semibold text-center text-primary">Što dobiješ</h2>
      <div class="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="rounded-xl border border-light bg-card p-6">
          <div class="text-2xl">🗣️</div>
          <h3 class="mt-3 font-semibold text-dark">Redovitu praksu</h3>
          <p class="mt-2 text-secondary leading-relaxed">Svakodnevne vježbe koje stanu u jedan dan.</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6">
          <div class="text-2xl">⏰</div>
          <h3 class="mt-3 font-semibold text-dark">Mali koraci</h3>
          <p class="mt-2 text-secondary leading-relaxed">Dovoljno je pet minuta.</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6">
          <div class="text-2xl">🤖</div>
          <h3 class="mt-3 font-semibold text-dark">Jasan feedback</h3>
          <p class="mt-2 text-secondary leading-relaxed">Jasan i konkretan feedback za tvoj napredak.</p>
        </div>
        <div class="rounded-xl border border-light bg-card p-6">
          <div class="text-2xl">🔒</div>
          <h3 class="mt-3 font-semibold text-dark">Privatnost</h3>
          <p class="mt-2 text-secondary leading-relaxed">Tvoje snimke i podaci su zaštićeni i neće biti dijeljeni bez tvog pristanka.</p>
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
          © {{ new Date().getFullYear() }} DailySpeakUp — Privacy • Contact • About
        </div>
      </div>
    </footer>
  </div>
</template>

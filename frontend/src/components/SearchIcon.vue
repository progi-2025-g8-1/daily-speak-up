<script setup>
    import { useRouter } from 'vue-router'
    
    const router = useRouter()
    </script>
    
    <template>
      <button
        class="icon-button"
        title="Search"
        @click="router.push('/search')"
      >
        <i class="pi pi-search text-black text-lg"></i>
      </button>
    </template>
    
import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

export type ThemeMode = 'light' | 'dark' | 'auto';

export const useThemeStore = defineStore('theme', () => {
  // Current theme mode
  const themeMode = ref<ThemeMode>('light');
  
  // Initialize theme from localStorage
  const initializeTheme = () => {
    const savedTheme = localStorage.getItem('app-theme') as ThemeMode | null;
    if (savedTheme) {
      themeMode.value = savedTheme;
    }
    applyTheme();
  };

  // Apply theme to document
  const applyTheme = () => {
    const htmlElement = document.documentElement;
    
    if (themeMode.value === 'dark') {
      htmlElement.classList.add('dark');
      document.body.classList.add('dark-mode');
    } else if (themeMode.value === 'light') {
      htmlElement.classList.remove('dark');
      document.body.classList.remove('dark-mode');
    }
  };

  // Set theme mode
  const setTheme = (mode: ThemeMode) => {
    themeMode.value = mode;
    localStorage.setItem('app-theme', mode);
    applyTheme();
  };

  // Toggle between light and dark
  const toggleTheme = () => {
    const newMode = themeMode.value === 'dark' ? 'light' : 'dark';
    setTheme(newMode);
  };

  // Watch for theme changes
  watch(themeMode, () => {
    applyTheme();
  });

  return {
    themeMode,
    initializeTheme,
    setTheme,
    toggleTheme,
    applyTheme
  };
});

import { createRouter, createWebHistory } from 'vue-router'

import Landing from '../views/Landing.vue'
import HomeView from '../views/HomeView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import AuthCallbackView from '../views/AuthCallbackView.vue'
import PasswordlessCallbackView from '../views/PasswordlessCallbackView.vue'
import OnboardingView from '../views/OnboardingView.vue'
import Profile from '../views/Profile.vue'
import DashboardView from '../views/DashboardView.vue'
import BannedView from '../views/BannedView.vue'
import { isAuthenticated } from '../auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: Landing,
      meta: { requiresGuest: true }
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/auth/callback/google',
      name: 'auth-callback',
      component: AuthCallbackView
    },
    {
      path: '/auth/verify',
      name: 'passwordless-callback',
      component: PasswordlessCallbackView
    },
    {
      path: '/banned',
      name: 'banned',
      component: BannedView
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: OnboardingView,
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
      beforeEnter: async () => {
        try {
          const response = await fetch(`${import.meta.env.VITE_API_DOMAIN}/api/v1/user/me`, {
            credentials: 'include',
          });

          if (!response.ok) {
            return { path: '/' };
          }
          
          const userData = await response.json();

          if (userData.role === import.meta.env.VITE_ADMIN_ROLE ||
              userData.role === import.meta.env.VITE_MODERATOR_ROLE ||
              userData.role === import.meta.env.VITE_ROOT_ROLE) {
            return true
          }
          return { path: '/' };
        } catch {
          return { path: '/' };
        }
      }
    },
    {
      path: '/:handle',
      name: 'Profile',
      component: Profile,
      meta: { requiresAuth: true }
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('../views/SearchView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView
    }
  ]
});

async function isOnboardingComplete(): Promise<boolean | null> {
  try {
    const apiDomain = import.meta.env.VITE_API_DOMAIN || (window as any).ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
    const response = await fetch(`${apiDomain}/api/v1/user/me`, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (response.ok) {
      const userData = await response.json();
      return userData.onboarding_status === 'completed';
    }
    return null;
  } catch (_error) {
    // Backend might be offline; treat as unknown instead of throwing
    console.warn('Onboarding check skipped: backend unreachable');
    return null;
  }
}

async function isUserBanned(): Promise<{ banned: boolean; reason?: string; expires_at?: string } | null> {
  try {
    const apiDomain = import.meta.env.VITE_API_DOMAIN || (window as any).ENV?.VITE_API_DOMAIN || 'http://localhost:8123';
    const response = await fetch(`${apiDomain}/api/v1/user/amibanned`, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (response.ok) {
      return await response.json();
    }
    return null;
  } catch (_error) {
    // Backend might be offline; treat as not banned to avoid hard lock
    console.warn('Ban check skipped: backend unreachable');
    return null;
  }
}

router.beforeEach(async (to, _from, next) => {
  const authenticated = await isAuthenticated();

  if (to.meta.requiresAuth && !authenticated) {
    return next('/');
  }

  if (authenticated) {
    const banStatus = await isUserBanned();
    // If backend unreachable (null), skip ban redirect
    if (banStatus?.banned) {
      if (to.path !== '/banned') {
        return next('/banned');
      }
      return next();
    }
  }

  if (authenticated && to.meta.requiresAuth) {
    const onboardingCompleted = await isOnboardingComplete();
    const isOnboardingRoute = to.path === '/onboarding';

    // If we couldn't fetch the onboarding status, redirect to onboarding to be safe
    if (onboardingCompleted === null) {
      if (!isOnboardingRoute) {
        return next('/onboarding');
      }
    } else {
      // If onboarding is not complete and user is trying to access any protected route except onboarding
      if (!onboardingCompleted && !isOnboardingRoute) {
        return next('/onboarding');
      }

      // If onboarding is complete and user is trying to access onboarding page
      if (onboardingCompleted && isOnboardingRoute) {
        return next('/home');
      }
    }
  }

  // If user is authenticated and trying to access landing page
  if (authenticated && to.meta.requiresGuest) {
    const onboardingCompleted = await isOnboardingComplete();
    
    // Redirect based on onboarding status
    if (onboardingCompleted === false) {
      return next('/onboarding');
    } else {
      // If completed or unknown, redirect to home (home will handle further checks)
      return next('/home');
    }
  }

  // Otherwise, proceed as normal
  next();
});

export default router;
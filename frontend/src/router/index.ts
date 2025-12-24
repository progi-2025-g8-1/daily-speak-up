import { createRouter, createWebHistory } from 'vue-router'

import Landing from '../views/Landing.vue'
import HomeView from '../views/HomeView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import AuthCallbackView from '../views/AuthCallbackView.vue'
import PasswordlessCallbackView from '../views/PasswordlessCallbackView.vue'
import OnboardingView from '../views/OnboardingView.vue'
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
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: OnboardingView,
      meta: { requiresAuth: true }
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
  } catch (error) {
    console.error('Error checking onboarding status:', error);
    return null;
  }
}

router.beforeEach(async (to, _from, next) => {
  const authenticated = await isAuthenticated();

  if (to.meta.requiresAuth && !authenticated) {
    return next('/');
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
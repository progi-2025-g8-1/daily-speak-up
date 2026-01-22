import Session from 'supertokens-web-js/recipe/session';
import ThirdParty from 'supertokens-web-js/recipe/thirdparty';
import Passwordless from 'supertokens-web-js/recipe/passwordless';
import EmailPassword from 'supertokens-web-js/recipe/emailpassword';

export async function signInWithGoogle() {
  try {
    // Clear any existing session before starting new login
    try {
      if (await Session.doesSessionExist()) {
        await Session.signOut();
      }
    } catch (clearError) {
      // Ignore errors when clearing, continue with login
      console.log('Cleared stale session before login');
    }
    
    const authUrl = await ThirdParty.getAuthorisationURLWithQueryParamsAndSetState({
      thirdPartyId: 'google',
      frontendRedirectURI: `${window.location.origin}/auth/callback/google`
    });
    
    // Redirect to Google OAuth
    window.location.assign(authUrl);
  } catch (err) {
    console.error('Error initiating Google sign-in:', err);
    throw err;
  }
}

export async function createPasswordlessCode(email: string) {
  try {
    // Clear any existing session before starting new login
    try {
      if (await Session.doesSessionExist()) {
        await Session.signOut();
      }
    } catch (clearError) {
      // Ignore errors when clearing, continue with login
      console.log('Cleared stale session before login');
    }
    
    const response = await Passwordless.createCode({
      email
    });
    return response;
  } catch (err) {
    console.error('Error creating passwordless code:', err);
    throw err;
  }
}

export async function consumePasswordlessCode(userInputCode: string) {
  try {
    const response = await Passwordless.consumeCode({
      userInputCode
    });
    return response;
  } catch (err) {
    console.error('Error consuming passwordless code:', err);
    throw err;
  }
}

export async function resendPasswordlessCode() {
  try {
    const response = await Passwordless.resendCode();
    return response;
  } catch (err) {
    console.error('Error resending passwordless code:', err);
    throw err;
  }
}

export async function signInWithEmailPassword(email: string, password: string) {
  try {
    // Clear any existing session before starting new login
    try {
      if (await Session.doesSessionExist()) {
        await Session.signOut();
      }
    } catch (clearError) {
      // Ignore errors when clearing, continue with login
      console.log('Cleared stale session before login');
    }
    
    const response = await EmailPassword.signIn({
      formFields: [
        { id: 'email', value: email },
        { id: 'password', value: password }
      ]
    });
    
    if (response.status === 'OK') {
      return response;
    } else if (response.status === 'WRONG_CREDENTIALS_ERROR') {
      throw new Error('Invalid email or password');
    } else {
      throw new Error('Sign in failed');
    }
  } catch (err) {
    console.error('Error signing in with email/password:', err);
    throw err;
  }
}

export async function isAuthenticated(): Promise<boolean> {
  try {
    return await Session.doesSessionExist();
  } catch (error) {
    // If there's an error checking session (e.g., invalid cookies), clear it
    console.warn('Session check failed, clearing invalid session:', error);
    try {
      await Session.signOut();
    } catch (signOutError) {
      // Ignore sign out errors
    }
    return false;
  }
}

let internalUserId: string | undefined = undefined;

export async function getUserId(): Promise<string | undefined> {
  if (internalUserId) {
    return internalUserId;
  }

  if (await Session.doesSessionExist()) {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/user/me`);
      if (response.ok) {
        const userData = await response.json();
        internalUserId = userData.id;
        return internalUserId;
      }
    } catch (error) {
      console.error('Failed to fetch user ID:', error);
    }
  }
  return undefined;
}

// For backward compatibility with existing code
export async function getAccessToken(): Promise<string | null> {
  // SuperTokens handles auth via cookies, no need for access tokens
  return null;
}

export async function getUser(): Promise<any | null> {
  if (await Session.doesSessionExist()) {
    const userId = await getUserId();
    if (userId) {
      return { id: userId };
    }
  }
  return null;
}

export async function logout() {
  await Session.signOut();
  internalUserId = undefined;
  window.location.href = '/';
}

import SuperTokens from 'supertokens-web-js';
import Session from 'supertokens-web-js/recipe/session';
import ThirdParty from 'supertokens-web-js/recipe/thirdparty';
import Passwordless from 'supertokens-web-js/recipe/passwordless';
import EmailPassword from 'supertokens-web-js/recipe/emailpassword';

export function initSuperTokens() {
  const env = {
    VITE_API_DOMAIN: import.meta.env.VITE_API_DOMAIN || (window as any).ENV?.VITE_API_DOMAIN || 'http://localhost:8123',
    VITE_WEBSITE_DOMAIN: import.meta.env.VITE_WEBSITE_DOMAIN || (window as any).ENV?.VITE_WEBSITE_DOMAIN || 'http://localhost:5173',
  };

  SuperTokens.init({
    appInfo: {
      appName: 'DailySpeakUp',
      apiDomain: env.VITE_API_DOMAIN,
      apiBasePath: '/auth'
    },
    recipeList: [
      ThirdParty.init(),
      Passwordless.init(),
      EmailPassword.init(),
      Session.init()
    ]
  });
}

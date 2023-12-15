import { SvelteKitAuth } from '@auth/sveltekit';
import GoogleProvider from '@auth/core/providers/google';
import SteamProvider from "next-auth-steam"
import {
    env 
} from '$env/dynamic/private';

export const handle = SvelteKitAuth({
    trustHost: true,
 providers: [
     GoogleProvider({ clientId: env.GOOGLE_CLIENT_ID, clientSecret: env.GOOGLE_CLIENT_SECRET }),
      SteamProvider(req, {
        clientSecret: env.STEAM_SECRET!,
        callbackUrl: 'https://cs-stats.labs.brainless.institute/auth/callback'
      })
 ]
});

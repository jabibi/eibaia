import { type FirebaseApp, initializeApp } from "firebase/app";
import { type Auth, GoogleAuthProvider, getAuth } from "firebase/auth";

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();

  const firebaseApp: FirebaseApp = initializeApp(config.public.firebase);
  const firebaseAuth: Auth = getAuth(firebaseApp);
  const googleProvider = new GoogleAuthProvider();

  return {
    provide: {
      firebaseAuth,
      googleProvider,
    },
  };
});

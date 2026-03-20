import { PropsWithChildren, createContext, useContext, useMemo } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { queryClient } from "../../lib/queryClient";
import type { LanguageCode } from '../../lib/language';
import { CurrentUser, LoginPayload, fetchCurrentUser, login, logout, setSessionLanguage } from "./api";

type AuthContextValue = {
  user: CurrentUser | null;
  isLoading: boolean;
  loginAction: (payload: LoginPayload) => Promise<CurrentUser>;
  logoutAction: () => Promise<void>;
  setSessionLanguageAction: (language: LanguageCode) => Promise<CurrentUser>;
  refreshMe: () => Promise<CurrentUser | null>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const meQuery = useQuery({
    queryKey: ["auth", "me"],
    queryFn: fetchCurrentUser,
  });

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: (user) => {
      queryClient.setQueryData(["auth", "me"], user);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.setQueryData(["auth", "me"], null);
      queryClient.removeQueries({ queryKey: ["users"] });
    },
  });

  const setSessionLanguageMutation = useMutation({
    mutationFn: (language: LanguageCode) => setSessionLanguage({ language }),
    onSuccess: (user) => {
      queryClient.setQueryData(['auth', 'me'], user);
    },
  });

  const value = useMemo<AuthContextValue>(
    () => ({
      user: meQuery.data ?? null,
      isLoading: meQuery.isLoading,
      loginAction: async (payload) => loginMutation.mutateAsync(payload),
      logoutAction: async () => {
        await logoutMutation.mutateAsync();
      },
      setSessionLanguageAction: async (language) => setSessionLanguageMutation.mutateAsync(language),
      refreshMe: async () => queryClient.fetchQuery({ queryKey: ["auth", "me"], queryFn: fetchCurrentUser }),
    }),
    [loginMutation, logoutMutation, meQuery.data, meQuery.isLoading, setSessionLanguageMutation],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

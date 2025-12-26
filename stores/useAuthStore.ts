import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  user: { username: string; is_super_admin: boolean } | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (username, password) => {
        const response = await fetch(
          "http://localhost:8000/api/v1/token",
          {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ username, password }),
          }
        );

        if (!response.ok) throw new Error("Login failed");

        const data = await response.json();

        set({
          token: data.access_token,
          isAuthenticated: true,
          user: { username, is_super_admin: true },
        });
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },
    }),
    {
      name: "auth-storage",
    }
  )
);

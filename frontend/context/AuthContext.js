import Cookies from "js-cookie";
import { useRouter } from "next/router";
import { createContext, useContext, useEffect, useState } from "react";

import api from "@/lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchMe = async () => {
    try {
      const { data } = await api.get("/auth/me/");
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (Cookies.get("access_token")) {
      fetchMe();
    } else {
      setLoading(false);
    }
  }, []);

  const setTokens = ({ access, refresh }) => {
    Cookies.set("access_token", access, { expires: 1 });
    if (refresh) Cookies.set("refresh_token", refresh, { expires: 7 });
  };

  const login = async (username, password) => {
    const { data } = await api.post("/auth/login/", { username, password });
    setTokens(data);
    setUser(data.user);
    return data;
  };

  const register = async (payload) => {
    const { data } = await api.post("/auth/register/", payload);
    return data;
  };

  const requestOtp = async (phone, purpose = "register") => {
    const { data } = await api.post("/auth/otp/request/", { phone, purpose });
    return data;
  };

  const verifyOtp = async (phone, code, purpose = "register") => {
    const { data } = await api.post("/auth/otp/verify/", { phone, code, purpose });
    setTokens(data);
    setUser(data.user);
    return data;
  };

  const logout = () => {
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, requestOtp, verifyOtp, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

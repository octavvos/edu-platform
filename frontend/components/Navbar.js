import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

export default function Navbar() {
  const { user, logout } = useAuth();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!user) {
      setUnread(0);
      return;
    }
    api
      .get("/notifications/", { params: { is_read: false } })
      .then(({ data }) => setUnread((data.results ?? data).length))
      .catch(() => {});
  }, [user]);

  return (
    <header className="navbar">
      <div className="navbar-inner container">
        <Link href="/" className="brand">
          Edu Platform
        </Link>
        <nav className="nav-links">
          <Link href="/">Katalog</Link>
          {user ? (
            <>
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/certificates">Sertifikatlar</Link>
              {(user.role === "teacher" || user.role === "mentor" || user.role === "admin" || user.role === "super_admin") && (
                <Link href="/dashboard/submissions">Tekshirish</Link>
              )}
              {(user.role === "admin" || user.role === "super_admin") && (
                <Link href="/dashboard/moderation">Moderatsiya</Link>
              )}
              <Link href="/notifications">
                Bildirishnomalar{unread > 0 ? ` (${unread})` : ""}
              </Link>
              <button className="link-btn" onClick={logout}>
                Chiqish
              </button>
            </>
          ) : (
            <>
              <Link href="/login">Kirish</Link>
              <Link href="/register">Ro&apos;yxatdan o&apos;tish</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

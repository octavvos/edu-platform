import Link from "next/link";

import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

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

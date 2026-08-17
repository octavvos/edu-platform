import { AuthProvider } from "@/context/AuthContext";
import Navbar from "@/components/Navbar";
import "@/styles/globals.css";

export default function App({ Component, pageProps }) {
  return (
    <AuthProvider>
      <Navbar />
      <main className="container">
        <Component {...pageProps} />
      </main>
    </AuthProvider>
  );
}

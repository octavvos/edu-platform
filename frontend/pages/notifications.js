import { useEffect, useState } from "react";

import ProtectedRoute from "@/components/ProtectedRoute";
import api from "@/lib/api";

function NotificationsContent() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    api
      .get("/notifications/")
      .then(({ data }) => setItems(data.results ?? data))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const markRead = async (id) => {
    setItems(items.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    try {
      await api.post(`/notifications/${id}/mark-read/`);
    } catch {
      load();
    }
  };

  return (
    <div>
      <h1>Bildirishnomalar</h1>
      {loading && <p>Yuklanmoqda...</p>}
      {!loading && items.length === 0 && <p className="muted">Bildirishnomalar yo&apos;q.</p>}
      <ul className="list">
        {items.map((n) => (
          <li key={n.id} style={{ alignItems: "flex-start", flexDirection: "column", gap: 4 }}>
            <div style={{ display: "flex", width: "100%", justifyContent: "space-between" }}>
              <strong>{n.is_read ? "" : "🔵 "}{n.title}</strong>
              <span className="muted" style={{ fontSize: "0.8rem" }}>
                {new Date(n.created_at).toLocaleString("uz-UZ")}
              </span>
            </div>
            <p className="muted" style={{ margin: 0 }}>{n.body}</p>
            {!n.is_read && (
              <button type="button" className="secondary" onClick={() => markRead(n.id)}>
                O&apos;qildi deb belgilash
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function NotificationsPage() {
  return (
    <ProtectedRoute>
      <NotificationsContent />
    </ProtectedRoute>
  );
}

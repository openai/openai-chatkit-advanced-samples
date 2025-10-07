// src/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// 🔽 ChatKit React provider
import { ChatKitProvider } from "@openai/chatkit-react";

// Frontend'e verdiğin domain key (public olabilir)
const domainKey = import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY as string;

if (!domainKey) {
  // Geliştirici dostu uyarı; prod'da sessiz geçmek istersen kaldırabilirsin
  console.warn("VITE_CHATKIT_API_DOMAIN_KEY is not set.");
}

const container = document.getElementById("root");
if (!container) {
  throw new Error("Root element with id 'root' not found");
}

createRoot(container).render(
  <StrictMode>
    <ChatKitProvider
      domainKey={domainKey}
      api={{
        // 🔑 Session tabanlı kimlik doğrulama:
        // İlk açılışta backend'ine POST /chatkit yapıp client_secret alıyoruz
        async getClientSecret(current?: string) {
          if (current) return current; // süresi dolmadıysa mevcut secret'ı kullan
          const res = await fetch("/chatkit", { method: "POST" });
          if (!res.ok) {
            const text = await res.text();
            throw new Error(`Failed to get client_secret: ${res.status} ${text}`);
          }
          const { client_secret } = await res.json();
          return client_secret;
        },
      }}
    >
      <App />
    </ChatKitProvider>
  </StrictMode>
);

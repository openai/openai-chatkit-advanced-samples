// frontend/src/components/Home.tsx
import { ChatKit, useChatKit } from "@openai/chatkit-react";

type Props = {
  scheme: "light" | "dark";
  handleThemeChange: (v: "light" | "dark") => void;
};

export default function Home({ scheme }: Props) {
  const domainKey = import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY as string;

  const { control } = useChatKit({
    // ✅ domain key'i mutlaka ver
    domainKey,

    // ✅ Hosted mod: client secret'ı backend'inden al
    api: {
      // 1) İlk token
      getClientSecret: async () => {
        const r = await fetch("/api/chatkit/start", { method: "POST" });
        if (!r.ok) throw new Error(`start failed: ${r.status}`);
        const data = await r.json();
        // 🔑 Bazı sürümlerde sadece STRING beklenir
        return data.client_secret as string;
        // Eğer yine hata alırsan şu alternatife dön:
        // return { clientSecret: data.client_secret, expiresAt: data.expires_at };
      },

      // 2) (Opsiyonel) Yenileme
      refreshClientSecret: async ({ currentClientSecret }) => {
        const r = await fetch("/api/chatkit/refresh", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ currentClientSecret }),
        });
        if (!r.ok) throw new Error(`refresh failed: ${r.status}`);
        const data = await r.json();
        // Aynı tip kuralı burada da geçerli:
        return data.client_secret as string;
        // Alternatif (gerekirse):
        // return { clientSecret: data.client_secret, expiresAt: data.expires_at };
      },
    },

    theme: { colorScheme: scheme },
  });

  return <ChatKit control={control} className="h-[100dvh]" />;
}

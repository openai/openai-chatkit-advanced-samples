// frontend/src/components/Home.tsx
import { ChatKit, useChatKit } from "@openai/chatkit-react";

type Props = {
  scheme: "light" | "dark";
  handleThemeChange: (v: "light" | "dark") => void;
};

export default function Home({ scheme, handleThemeChange }: Props) {
  const { control } = useChatKit({
    // Hosted ChatKit: client token'ı kendi sunucundan al
    api: {
      // İlk token
      getClientSecret: async () => {
        const r = await fetch("/api/chatkit/start", { method: "POST" });
        const data = await r.json();
        return { clientSecret: data.client_secret, expiresAt: data.expires_at };
      },
      // Süre dolmadan yenileme (opsiyonel ama önerilir)
      refreshClientSecret: async ({ currentClientSecret }) => {
        const r = await fetch("/api/chatkit/refresh", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ currentClientSecret }),
        });
        const data = await r.json();
        return { clientSecret: data.client_secret, expiresAt: data.expires_at };
      },
      // (İsteğe bağlı) domain doğrulama anahtarı — allowlist’ten aldığın KEY
      // domainVerification: { id: import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY },
    },
    theme: { colorScheme: scheme },
  });

  return (
    <div className="h-[100dvh]">
      <ChatKit control={control} className="h-full" />
    </div>
  );
}

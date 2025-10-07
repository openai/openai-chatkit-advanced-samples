// frontend/src/components/Home.tsx
import { ChatKit, useChatKit } from "@openai/chatkit-react";

type Props = {
  scheme: "light" | "dark";
  handleThemeChange: (v: "light" | "dark") => void;
};

export default function Home({ scheme }: Props) {
  const { control } = useChatKit({
    api: {
      // İlk token
      getClientSecret: async () => {
        const r = await fetch("/api/chatkit/start", { method: "POST" });
        if (!r.ok) throw new Error(`start failed: ${r.status}`);
        const data = await r.json();
        return data.client_secret as string; // <-- string döndür
      },
      // Yenileme (opsiyonel ama iyi pratik)
      refreshClientSecret: async ({ currentClientSecret }) => {
        const r = await fetch("/api/chatkit/refresh", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ currentClientSecret }),
        });
        if (!r.ok) throw new Error(`refresh failed: ${r.status}`);
        const data = await r.json();
        return data.client_secret as string; // <-- string döndür
      },
    },
    theme: { colorScheme: scheme },
  });

  return <ChatKit control={control} className="h-[100dvh]" />;
}

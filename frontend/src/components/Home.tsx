// frontend/src/components/Home.tsx
import { ChatKit, useChatKit } from "@openai/chatkit-react";

type Props = {
  scheme: "light" | "dark";
  handleThemeChange: (v: "light" | "dark") => void;
};

export default function Home({ scheme }: Props) {
  const { control } = useChatKit({
    api: {
      getClientSecret: async (currentClientSecret) => {
        const isRefresh =
          typeof currentClientSecret === "string" &&
          currentClientSecret.length > 0;
        const endpoint = isRefresh
          ? "/api/chatkit/refresh"
          : "/api/chatkit/start";

        const response = await fetch(endpoint, {
          method: "POST",
          headers: isRefresh
            ? { "Content-Type": "application/json" }
            : undefined,
          body: isRefresh
            ? JSON.stringify({ currentClientSecret })
            : undefined,
        });

        if (!response.ok) {
          throw new Error(
            `${isRefresh ? "refresh" : "start"} failed: ${
              response.status
            }`,
          );
        }

        const data: unknown = await response.json();
        const clientSecret =
          data && typeof data === "object"
            ? (data as { client_secret?: unknown }).client_secret
            : undefined;

        if (typeof clientSecret !== "string" || clientSecret.length === 0) {
          throw new Error("Response missing client_secret");
        }

        return clientSecret;
      },
    },
    theme: { colorScheme: scheme },
  });

  return <ChatKit control={control} className="h-[100dvh]" />;
}

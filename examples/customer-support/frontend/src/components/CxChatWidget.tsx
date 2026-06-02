import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import clsx from "clsx";
import { MessageCircleQuestion, Send, Star, X } from "lucide-react";

type ChatStage =
  | "initial"
  | "answering"
  | "awaiting_rephrase"
  | "limit_reached"
  | "escalated";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type ChatbotApiResponse = {
  answer: string;
  response_id?: string | null;
  handoffSuggested?: boolean;
};

export type ChatHandoffContext = {
  userType: string | null;
  originalQuestion: string;
  restatedQuestion: string | null;
  transcript: ChatMessage[];
};

type CxChatWidgetProps = {
  onEscalate: (context: ChatHandoffContext) => void;
};

const GREETING = "Hi! How can I help you today?";
const CHATBOT_USERTYPE = " ";
const MAX_MESSAGES_EXCHANGED = 50;
const LIMIT_REACHED_MESSAGE =
  "Sorry, I can't help with this request anymore. Please connect with the TPT CX team at teacherspayteachers.com/Contact for further assistance.";

function buildId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function CxChatWidget({ onEscalate }: CxChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showTooltip, setShowTooltip] = useState(true);
  const [stage, setStage] = useState<ChatStage>("initial");
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: buildId(), role: "assistant", content: GREETING },
  ]);
  const [modelMessages, setModelMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [originalQuestion, setOriginalQuestion] = useState("");
  const [restatedQuestion, setRestatedQuestion] = useState<string | null>(null);
  const [rating, setRating] = useState<number | null>(null);
  const [previousResponseId, setPreviousResponseId] = useState<string | null>(null);
  const [pendingExitAction, setPendingExitAction] = useState<"close" | "reset" | null>(
    null,
  );
  const [feedbackChoice, setFeedbackChoice] = useState<"yes" | "no" | null>(null);
  const [feedbackReason, setFeedbackReason] = useState("");
  const [feedbackRating, setFeedbackRating] = useState<number | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    const timer = window.setTimeout(() => setShowTooltip(false), 3500);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, pendingExitAction, stage]);

  useEffect(() => {
    if (
      isOpen &&
      !pendingExitAction &&
      (stage === "initial" || stage === "awaiting_rephrase")
    ) {
      window.setTimeout(() => inputRef.current?.focus(), 80);
    }
  }, [isOpen, pendingExitAction, stage]);

  const transcriptForLogging = useMemo(
    () => ({
      rating,
      originalQuestion,
      restatedQuestion,
      messages,
      feedbackChoice,
      feedbackReason,
    }),
    [feedbackChoice, feedbackReason, messages, originalQuestion, rating, restatedQuestion],
  );

  function appendMessage(role: ChatMessage["role"], content: string) {
    setMessages((current) => [...current, { id: buildId(), role, content }]);
  }

  function clearExitFeedback() {
    setPendingExitAction(null);
    setFeedbackChoice(null);
    setFeedbackReason("");
    setFeedbackRating(null);
  }

  function resetConversation() {
    setStage("initial");
    setMessages([{ id: buildId(), role: "assistant", content: GREETING }]);
    setModelMessages([]);
    setInput("");
    setIsLoading(false);
    setOriginalQuestion("");
    setRestatedQuestion(null);
    setRating(null);
    setPreviousResponseId(null);
    clearExitFeedback();
  }

  function finalizeExit(action: "close" | "reset") {
    if (action === "close") {
      clearExitFeedback();
      setIsOpen(false);
      return;
    }

    resetConversation();
  }

  function handleExitIntent(action: "close" | "reset") {
    const hasConversation = modelMessages.length > 0 || Boolean(originalQuestion.trim());
    if (!hasConversation) {
      finalizeExit(action);
      return;
    }

    setPendingExitAction(action);
    setFeedbackChoice(null);
    setFeedbackReason("");
    setFeedbackRating(null);
  }

  async function requestAnswer(question: string) {
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      return;
    }

    if (modelMessages.length >= MAX_MESSAGES_EXCHANGED) {
      appendMessage("assistant", LIMIT_REACHED_MESSAGE);
      setStage("limit_reached");
      return;
    }

    const nextModelMessages = [
      ...modelMessages,
      { id: buildId(), role: "user" as const, content: trimmedQuestion },
    ];

    setIsLoading(true);
    setStage("answering");

    try {
      const response = await fetch("/support/chatbot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: nextModelMessages.map(({ role, content }) => ({ role, content })),
          usertype: CHATBOT_USERTYPE,
          question: trimmedQuestion,
          previous_response_id: previousResponseId,
        }),
      });

      if (!response.ok) {
        let detail = `Chatbot request failed with status ${response.status}`;
        try {
          const errorPayload = (await response.json()) as { detail?: string };
          if (errorPayload.detail) {
            detail = errorPayload.detail;
          }
        } catch {
          // Keep the status fallback when the response body is not JSON.
        }
        throw new Error(detail);
      }

      const data = (await response.json()) as ChatbotApiResponse;
      const answer =
        data.answer?.trim() ||
        "I couldn't find a reliable answer just now. Please restate the question and I’ll try again.";

      const updatedModelMessages = [
        ...nextModelMessages,
        { id: buildId(), role: "assistant" as const, content: answer },
      ];

      setModelMessages(updatedModelMessages);
      setPreviousResponseId(data.response_id ?? null);
      appendMessage("assistant", answer);

      if (data.handoffSuggested) {
        appendMessage(
          "assistant",
          "I should hand this over to the contact form so the CX team can follow up directly.",
        );
        const context: ChatHandoffContext = {
          userType: CHATBOT_USERTYPE,
          originalQuestion: originalQuestion || trimmedQuestion,
          restatedQuestion,
          transcript: [...messages, { id: buildId(), role: "user", content: trimmedQuestion }],
        };
        onEscalate(context);
        setStage("escalated");
        return;
      }

      setStage("initial");
    } catch (error) {
      console.error("TPT CX chatbot error", error);
      appendMessage(
        "assistant",
        error instanceof Error
          ? `I’m having trouble responding right now: ${error.message}`
          : "Something went wrong reaching the bot. Please restate the question or use the contact form below.",
      );
      setStage("awaiting_rephrase");
    } finally {
      setIsLoading(false);
    }
  }

  function handleSend(event: FormEvent) {
    event.preventDefault();

    if (stage !== "initial" && stage !== "awaiting_rephrase") {
      return;
    }

    const text = input.trim();
    if (!text || isLoading) {
      return;
    }

    appendMessage("user", text);
    setInput("");

    if (!originalQuestion) {
      setOriginalQuestion(text);
    }

    if (stage === "awaiting_rephrase") {
      setRestatedQuestion(text);
      void requestAnswer(text);
      return;
    }

    void requestAnswer(text);
  }

  function submitExitFeedback() {
    if (!pendingExitAction || !feedbackChoice) {
      return;
    }

    const nextRating = feedbackChoice === "yes" ? feedbackRating : null;
    if (feedbackChoice === "yes" && nextRating === null) {
      return;
    }

    setRating(nextRating);
    console.log("TPT CX chatbot transcript", {
      ...transcriptForLogging,
      rating: nextRating,
      feedbackChoice,
      feedbackReason,
    });
    finalizeExit(pendingExitAction);
  }

  const canType =
    !pendingExitAction &&
    (stage === "initial" || stage === "awaiting_rephrase") &&
    !isLoading;

  return (
    <>
      {!isOpen ? (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
          {showTooltip && !isOpen ? (
            <div className="max-w-[240px] rounded-2xl bg-white px-4 py-3 text-sm leading-6 text-slate-700 shadow-[0_20px_50px_-24px_rgba(15,23,42,0.3)]">
              I&apos;m the TPT CX Bot. Ask me a question for instant support.
            </div>
          ) : null}

          <button
            type="button"
            aria-label={isOpen ? "Close TPT CX chat" : "Open TPT CX chat"}
            className="flex h-16 w-16 items-center justify-center rounded-full bg-[#14473f] text-white shadow-[0_22px_50px_-18px_rgba(20,71,63,0.65)] transition hover:bg-[#1d5d53]"
            onClick={() => setIsOpen((current) => !current)}
            onMouseEnter={() => !isOpen && setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
          >
            <MessageCircleQuestion className="size-7" />
          </button>
        </div>
      ) : null}

      {isOpen ? (
        <section className="fixed bottom-28 left-3 right-3 z-50 flex h-[620px] flex-col overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-[0_40px_90px_-42px_rgba(15,23,42,0.45)] sm:left-auto sm:right-6 sm:w-[390px]">
          <header className="flex items-center justify-between gap-3 bg-[#14473f] px-5 py-4 text-white">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10">
                <span className="text-sm font-bold">T</span>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-100">
                  TPT CX Bot
                </p>
                <p className="text-sm text-emerald-50/90">Instant support</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="rounded-full border border-white/10 bg-white/10 px-3 py-2 text-xs font-medium text-white transition hover:bg-white/15"
                onClick={() => handleExitIntent("reset")}
              >
                Reset
              </button>
              <button
                type="button"
                aria-label="Close TPT CX chat"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/10 text-white transition hover:bg-white/15"
                onClick={() => handleExitIntent("close")}
              >
                <X className="size-5" />
              </button>
            </div>
          </header>

          <div className="flex-1 space-y-4 overflow-y-auto bg-[#f8faf8] px-4 py-4">
            {messages.map((message) => {
              const isAssistant = message.role === "assistant";
              return (
                <div
                  key={message.id}
                  className={clsx("flex", isAssistant ? "justify-start" : "justify-end")}
                >
                  <div
                    className={clsx(
                      "max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm",
                      isAssistant
                        ? "rounded-tl-sm bg-white text-slate-700"
                        : "rounded-tr-sm bg-[#14473f] text-white",
                    )}
                  >
                    {message.content}
                  </div>
                </div>
              );
            })}

            {isLoading ? (
              <div className="flex justify-start">
                <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-sm">
                  {[0, 1, 2].map((dot) => (
                    <span
                      key={dot}
                      className="h-2 w-2 animate-bounce rounded-full bg-emerald-500"
                      style={{ animationDelay: `${dot * 0.15}s` }}
                    />
                  ))}
                </div>
              </div>
            ) : null}

            {stage === "escalated" ? (
              <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-slate-700">
                Your transcript is ready for the contact form below. Continue there so CX can follow up directly.
              </div>
            ) : null}

            <div ref={bottomRef} />
          </div>

          <form
            onSubmit={handleSend}
            className="border-t border-slate-100 bg-white px-4 py-4"
          >
            <div className="flex items-center gap-2">
              <input
                ref={inputRef}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder={
                  canType
                    ? stage === "awaiting_rephrase"
                      ? "Restate your question..."
                      : "Ask a question..."
                    : "Use the buttons above to continue"
                }
                disabled={!canType || isLoading}
                className="flex-1 rounded-full border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
              />
              <button
                type="submit"
                disabled={!canType || !input.trim() || isLoading}
                className="flex h-11 w-11 items-center justify-center rounded-full bg-[#14473f] text-white transition hover:bg-[#1d5d53] disabled:cursor-not-allowed disabled:bg-slate-300"
                aria-label="Send message"
              >
                <Send className="size-4" />
              </button>
            </div>
          </form>

          {pendingExitAction ? (
            <div className="absolute inset-0 z-10 flex items-end bg-slate-950/30 p-3 sm:items-center sm:p-4">
              <div className="w-full rounded-[1.75rem] bg-white p-5 shadow-[0_30px_80px_-40px_rgba(15,23,42,0.65)]">
                <div className="space-y-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                      Before you {pendingExitAction}
                    </p>
                    <h3 className="mt-1 text-lg font-semibold text-slate-900">
                      Did we answer your question?
                    </h3>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      className={clsx(
                        "rounded-full px-4 py-3 text-sm font-semibold transition",
                        feedbackChoice === "yes"
                          ? "bg-[#63E0A5] text-slate-950"
                          : "border border-slate-300 bg-white text-slate-700 hover:border-slate-400",
                      )}
                      onClick={() => {
                        setFeedbackChoice("yes");
                        setFeedbackReason("");
                      }}
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      className={clsx(
                        "rounded-full px-4 py-3 text-sm font-semibold transition",
                        feedbackChoice === "no"
                          ? "bg-slate-900 text-white"
                          : "border border-slate-300 bg-white text-slate-700 hover:border-slate-400",
                      )}
                      onClick={() => {
                        setFeedbackChoice("no");
                        setFeedbackRating(null);
                      }}
                    >
                      No
                    </button>
                  </div>

                  {feedbackChoice === "yes" ? (
                    <div className="space-y-3">
                      <p className="text-sm text-slate-600">Rate the response out of 5.</p>
                      <div className="flex items-center justify-center gap-2">
                        {[1, 2, 3, 4, 5].map((value) => (
                          <button
                            key={value}
                            type="button"
                            className={clsx(
                              "rounded-full border p-3 transition",
                              feedbackRating === value
                                ? "border-amber-300 bg-amber-50 text-amber-500"
                                : "border-amber-200 bg-white text-amber-400 hover:bg-amber-50",
                            )}
                            onClick={() => setFeedbackRating(value)}
                            aria-label={`Rate ${value} stars`}
                          >
                            <Star className="size-5 fill-current" />
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : null}

                  {feedbackChoice === "no" ? (
                    <div className="space-y-2">
                      <label
                        htmlFor="chat-feedback-reason"
                        className="block text-sm font-medium text-slate-700"
                      >
                        Tell us why, if you&apos;d like.
                      </label>
                      <textarea
                        id="chat-feedback-reason"
                        value={feedbackReason}
                        onChange={(event) => setFeedbackReason(event.target.value)}
                        rows={4}
                        placeholder="Optional feedback"
                        className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
                      />
                    </div>
                  ) : null}

                  <div className="flex items-center justify-end gap-2">
                    <button
                      type="button"
                      className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400"
                      onClick={clearExitFeedback}
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      className="rounded-full bg-[#14473f] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#1d5d53] disabled:cursor-not-allowed disabled:bg-slate-300"
                      onClick={submitExitFeedback}
                      disabled={
                        !feedbackChoice ||
                        (feedbackChoice === "yes" && feedbackRating === null)
                      }
                    >
                      {pendingExitAction === "close" ? "Close chat" : "Reset chat"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : null}
        </section>
      ) : null}
    </>
  );
}

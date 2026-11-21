import { useEffect, useRef, useState } from "react";
import { NETWORK_ERROR_MESSAGE, checkBackendHealth, sendChatMessage } from "./api";
import ChatHeader from "./components/ChatHeader";
import ChatInput from "./components/ChatInput";
import MessageList from "./components/MessageList";
import SessionSettings from "./components/SessionSettings";
import { createSessionId } from "./utils/session";

function App() {
  const [sessionId, setSessionId] = useState(createSessionId);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [simulateFailure, setSimulateFailure] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [backendStatus, setBackendStatus] = useState("connecting");
  const nextMessageId = useRef(1);
  const inputRef = useRef(null);

  const hasAssistantReply = messages.some((message) => message.role === "assistant");

  useEffect(() => {
    checkBackendHealth().then((isOnline) => setBackendStatus(isOnline ? "online" : "offline"));
  }, []);

  function addMessage(message) {
    const id = nextMessageId.current;
    nextMessageId.current += 1;
    setMessages((currentMessages) => [...currentMessages, { id, ...message }]);
  }

  function handlePickExample(prompt) {
    setInput(prompt);
    inputRef.current?.focus();
  }

  async function handleSend() {
    if (isSending || input === "") {
      return;
    }
    const messageText = input;
    const failureToSimulate = simulateFailure;
    setInput("");
    setSimulateFailure("");
    inputRef.current?.focus();
    addMessage({ role: "user", content: messageText });
    setIsSending(true);
    try {
      const data = await sendChatMessage({
        sessionId,
        message: messageText,
        systemPrompt,
        simulateFailure: failureToSimulate,
      });
      addMessage({ role: "assistant", content: data.reply, metadata: data.metadata });
      setBackendStatus("online");
    } catch (error) {
      addMessage({ role: "error", content: error.message });
      if (error.message === NETWORK_ERROR_MESSAGE) {
        setBackendStatus("offline");
      }
    } finally {
      setIsSending(false);
    }
  }

  function handleNewChat() {
    setSessionId(createSessionId());
    setMessages([]);
    setInput("");
  }

  return (
    <div className="min-h-dvh bg-slate-100 text-slate-800">
      <div className="mx-auto flex h-dvh max-w-3xl flex-col gap-3 px-3 py-3 sm:gap-4 sm:px-4 sm:py-5">
        <ChatHeader backendStatus={backendStatus} onNewChat={handleNewChat} isSending={isSending} />
        <SessionSettings
          sessionId={sessionId}
          systemPrompt={systemPrompt}
          onSystemPromptChange={setSystemPrompt}
          isLocked={hasAssistantReply}
          simulateFailure={simulateFailure}
          onSimulateFailureChange={setSimulateFailure}
        />
        <MessageList messages={messages} isSending={isSending} onPickExample={handlePickExample} />
        <ChatInput inputRef={inputRef} value={input} onChange={setInput} onSend={handleSend} isSending={isSending} />
      </div>
    </div>
  );
}

export default App;

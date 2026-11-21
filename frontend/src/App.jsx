import { useRef, useState } from "react";
import { sendChatMessage } from "./api";
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
  const nextMessageId = useRef(1);

  const hasAssistantReply = messages.some((message) => message.role === "assistant");

  function addMessage(message) {
    const id = nextMessageId.current;
    nextMessageId.current += 1;
    setMessages((currentMessages) => [...currentMessages, { id, ...message }]);
  }

  async function handleSend() {
    if (isSending || input === "") {
      return;
    }
    const messageText = input;
    const failureToSimulate = simulateFailure;
    setInput("");
    setSimulateFailure("");
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
    } catch (error) {
      addMessage({ role: "error", content: error.message });
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
    <div className="min-h-screen bg-slate-100 text-slate-800">
      <div className="mx-auto flex h-dvh max-w-3xl flex-col gap-4 p-4">
        <ChatHeader sessionId={sessionId} onNewChat={handleNewChat} isSending={isSending} />
        <SessionSettings
          systemPrompt={systemPrompt}
          onSystemPromptChange={setSystemPrompt}
          isLocked={hasAssistantReply}
          simulateFailure={simulateFailure}
          onSimulateFailureChange={setSimulateFailure}
        />
        <MessageList messages={messages} isSending={isSending} />
        <ChatInput value={input} onChange={setInput} onSend={handleSend} isSending={isSending} />
      </div>
    </div>
  );
}

export default App;

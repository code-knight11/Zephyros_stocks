import React, { useContext, useState, useEffect, useRef } from "react";
import ThemeContext from "../context/ThemeContext";
import SideNav from "../components/SideNav";
import BouncingDotsLoader from "../assets/DotsLoader"; // Your inline loader component

const Chatbot = () => {
  const { darkMode } = useContext(ThemeContext);
  const [message, setMessage] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const userId = localStorage.getItem("user_id");

  const bottomRef = useRef(null);

  // Add a bot message to the conversation.
  const addBotMessage = (content) => {
    const newBotMessage = { id: Date.now(), sender: "bot", content };
    setChatMessages((prev) => [...prev, newBotMessage]);
  };

  // Scroll to the bottom whenever chatMessages updates.
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages]);

  const loadConversation = async (threadId) => {
    console.log(threadId);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/thread/${threadId}`);
      if (!response.ok) {
        throw new Error("Failed to fetch conversation");
      }
      const data = await response.json();
      const relevantMessages = data.messages.filter((msg) =>
        msg.role === "user" ||
        ((msg.role === "assistant2" || msg.role === "rag_assistant") && msg.content.trim() !== "")
      );
      const formattedMessages = relevantMessages.map((msg) => ({
        id: msg.id,
        sender: msg.role === "user" ? "user" : "bot",
        content: msg.content,
      }));
      setChatMessages(formattedMessages);
      setCurrentThreadId(threadId);
    } catch (error) {
      console.error("Error loading conversation:", error);
      addBotMessage("Error: Could not load conversation history.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;
  
    const newUserMessage = { id: Date.now(), sender: "user", content: message };
    setChatMessages((prev) => [...prev, newUserMessage]);
    
    // Clear the input immediately
    setMessage("");
    
    setIsLoading(true);
  
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/chat/${userId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          thread_id: currentThreadId, // Include current thread ID if exists
        }),
      });
      if (!response.ok) {
        throw new Error("Failed to fetch chat response");
      }
      const data = await response.json();
      
      const assistantResponse = data.responses.find((response) =>
        (response.role === "assistant2" || response.role === "rag_assistant") &&
        response.content.trim() !== ""
      );
      
      if (assistantResponse) {
        addBotMessage(assistantResponse.content);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      addBotMessage("Error: Could not fetch response.");
    }
    setIsLoading(false);
  };
  
  return (
    <div
      className={`h-screen flex ${
        darkMode ? "bg-gray-900 text-gray-300" : "bg-neutral-100 text-gray-800"
      }`}
    >
      <SideNav 
        addBotMessage={addBotMessage} 
        onConversationSelect={loadConversation}
        currentThreadId={currentThreadId}
      />

      <div className="flex-1 ml-64 flex flex-col">
        <div
          className={`flex-1 overflow-y-auto p-4 custom-scrollbar ${
            darkMode ? "custom-scrollbar-dark" : ""
          }`}
        >
          <div className="mx-auto space-y-4">
            {chatMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex w-full ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`${
                    React.isValidElement(msg.content)
                      ? "min-w-[500px] max-w-[800px]"
                      : "max-w-sm"
                  } px-6 py-6 rounded-2xl ${
                    msg.sender === "user"
                      ? "bg-indigo-600 text-white rounded-br-none text-lg"
                      : darkMode
                      ? "bg-gray-800 text-gray-100 rounded-bl-none text-lg"
                      : "bg-white text-gray-900 rounded-bl-none shadow-sm text-lg"
                  }`}
                >
                  {React.isValidElement(msg.content) ? (
                    <div className="w-full">{msg.content}</div>
                  ) : (
                    <pre className="whitespace-pre-wrap text-sm">{msg.content}</pre>
                  )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* Bottom container with input and loader */}
        <div className="p-8 relative">
          {isLoading && (
            <div className="absolute bottom-24 mb-1 ml-2">
               <BouncingDotsLoader /> 
            </div>
          )}
          <form onSubmit={handleSubmit} className="max-w-5xl mx-auto flex gap-4">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              className={`flex-1 px-4 py-5 rounded-xl border focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                darkMode
                  ? "bg-gray-800 border-gray-700 text-gray-100"
                  : "bg-white border-gray-300 text-gray-900"
              }`}
            />
            <button
              type="submit"
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;

import React, { useState, useEffect, useRef, useCallback } from 'react';
import type { Chat } from "@google/genai";
import { createChatSession } from '../services/geminiService';
import type { ChatMessage } from '../types';
import { PaperAirplaneIcon } from './icons/PaperAirplaneIcon';
import Spinner from './ui/Spinner';
import { RefreshIcon } from './icons/RefreshIcon';

/**
 * A component that provides a chatbot interface for interacting with the Gemini API.
 */
const Chatbot: React.FC = () => {
  // State to hold the chat session instance from the Gemini API
  const [chatSession, setChatSession] = useState<Chat | null>(null);
  // State to store the history of chat messages
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  // State for the user's current input message
  const [currentMessage, setCurrentMessage] = useState<string>('');
  // State to track if the bot is currently generating a response
  const [isLoading, setIsLoading] = useState<boolean>(false);
  // Ref to the end of the messages container, for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Effect to initialize the chat session when the component mounts
  useEffect(() => {
    const initChat = () => {
      const session = createChatSession();
      setChatSession(session);
      // Set an initial welcome message from the model
      setMessages([
        { role: 'model', text: 'Hello! I am your AI assistant. How can I help you today?', timestamp: new Date() },
      ]);
    };
    initChat();
  }, []);

  // Effect to scroll to the latest message whenever the messages array is updated
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Handles sending the user's message to the chat API and updating the chat history.
   */
  const handleSendMessage = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading || !currentMessage.trim() || !chatSession) return;

    // Add user's message to the chat history
    const userMessage: ChatMessage = { role: 'user', text: currentMessage, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      // Send the message to the Gemini API
      const response = await chatSession.sendMessage({ message: currentMessage });
      const modelMessage: ChatMessage = { role: 'model', text: response.text, timestamp: new Date() };
      // Add the model's response to the chat history
      setMessages(prev => [...prev, modelMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      // Add an error message to the chat history if the API call fails
      const errorMessage: ChatMessage = { 
        role: 'model', 
        text: "Sorry, I encountered an error. Please check your connection and try again.", 
        timestamp: new Date(),
        error: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, currentMessage, chatSession]);

  /**
   * Handles the retry logic when a message fails to send.
   * It finds the last user message and attempts to send it again.
   */
  const handleRetry = useCallback(async () => {
    // Find the last message sent by the user
    const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
    if (!lastUserMessage || isLoading || !chatSession) return;

    // Remove the previous error message from the UI before retrying
    setMessages(prev => prev.filter(m => !m.error));
    setIsLoading(true);

    try {
        const response = await chatSession.sendMessage({ message: lastUserMessage.text });
        const modelMessage: ChatMessage = { role: 'model', text: response.text, timestamp: new Date() };
        setMessages(prev => [...prev, modelMessage]);
    } catch (error) {
        console.error("Error on retry:", error);
        const errorMessage: ChatMessage = {
            role: 'model',
            text: "The retry also failed. Please try again later.",
            timestamp: new Date(),
            error: true
        };
        setMessages(prev => [...prev, errorMessage]);
    } finally {
        setIsLoading(false);
    }
}, [messages, isLoading, chatSession]);

  return (
    <div className="min-h-[70vh] flex flex-col p-3 sm:p-4 md:p-6">
      {/* Messages container */}
      <div className="flex-grow overflow-y-auto mb-4 pr-1 sm:pr-2 space-y-4 scroll-smooth">
        {messages.map((msg, index) => (
          <div key={index} className={`flex items-start gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {/* AI Avatar */}
            {msg.role === 'model' && (
              <div className="w-8 h-8 rounded-full bg-teal-500 flex items-center justify-center flex-shrink-0 text-white font-bold text-sm">
                AI
              </div>
            )}
            <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              {/* Message Bubble */}
              <div
                className={`max-w-xs md:max-w-md lg:max-w-lg px-4 py-3 rounded-2xl shadow ${
                  msg.role === 'user'
                    ? 'bg-cyan-700 text-white rounded-br-none'
                    : msg.error
                    ? 'bg-red-800/60 border border-red-600/50 text-red-200 rounded-bl-none'
                    : 'bg-gray-700 text-gray-200 rounded-bl-none'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
              </div>

              {/* Timestamp and Retry Button */}
              <div className="flex items-center gap-3 mt-1.5 px-1">
                {msg.error && msg.role === 'model' && (
                  <button 
                      onClick={handleRetry} 
                      disabled={isLoading}
                      className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-gray-600 hover:bg-gray-500 text-white transition-colors disabled:bg-gray-700 disabled:cursor-not-allowed"
                  >
                      <RefreshIcon className="w-3 h-3" />
                      Retry
                  </button>
                )}
                <p className="text-xs text-gray-500">
                    {msg.timestamp.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}
                </p>
              </div>
            </div>
             {/* User Avatar */}
             {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0 text-white font-bold text-sm">
                You
              </div>
            )}
          </div>
        ))}
        {/* Loading indicator for when the model is typing */}
        {isLoading && (
          <div className="flex items-start gap-3">
             <div className="w-8 h-8 rounded-full bg-teal-500 flex items-center justify-center flex-shrink-0 text-white font-bold text-sm">AI</div>
             <div className="max-w-xs md:max-w-md lg:max-w-lg px-4 py-3 rounded-2xl shadow bg-gray-700 text-gray-200 rounded-bl-none">
              <Spinner/>
            </div>
          </div>
        )}
        {/* Empty div to which the view scrolls */}
        <div ref={messagesEndRef} />
      </div>

      {/* Message input form */}
      <form onSubmit={handleSendMessage} className="flex items-center gap-2 md:gap-4 mt-auto">
        <input
          type="text"
          value={currentMessage}
          onChange={(e) => setCurrentMessage(e.target.value)}
          placeholder="Ask a question about your document..."
          className="flex-grow p-3 bg-gray-800 border border-gray-700 rounded-full focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-shadow placeholder:text-gray-500"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !currentMessage.trim()}
          className="flex-shrink-0 w-12 h-12 flex items-center justify-center bg-cyan-600 text-white rounded-full hover:bg-cyan-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-cyan-500/30"
        >
          <PaperAirplaneIcon className="w-6 h-6" />
        </button>
      </form>
    </div>
  );
};

export default Chatbot;
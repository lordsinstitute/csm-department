// src/components/ChatbotPanel.js — Premium redesign
import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ─── Layout ───────────────────────────────────────────────────────────────────

const Container = styled.div`
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
`;

const TopAccent = styled.div`
  height: 2px;
  background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
  flex-shrink: 0;
`;

// ─── Header ───────────────────────────────────────────────────────────────────

const Header = styled.div`
  padding: 13px 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

const AiAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
`;

const HeaderInfo = styled.div``;

const HeaderTitle = styled.div`
  font-size: 0.88rem;
  font-weight: 700;
  color: rgba(226, 232, 240, 0.92);
  letter-spacing: -0.2px;
  line-height: 1;
  margin-bottom: 3px;
`;

const HeaderStatus = styled.div`
  font-size: 0.63rem;
  font-weight: 500;
  color: ${props => props.$online ? '#10b981' : 'rgba(226, 232, 240, 0.3)'};
  display: flex;
  align-items: center;
  gap: 5px;
  letter-spacing: 0.2px;

  &::before {
    content: '';
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: currentColor;
    display: inline-block;
    animation: ${props => props.$online ? 'blink 2.5s ease infinite' : 'none'};
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 5px;
`;

const IconBtn = styled(motion.button)`
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.09);
  color: rgba(226, 232, 240, 0.5);
  width: 28px;
  height: 28px;
  border-radius: 7px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;

  &:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.11);
    color: rgba(226, 232, 240, 0.85);
  }

  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
`;

// ─── Messages ─────────────────────────────────────────────────────────────────

const MessagesArea = styled.div`
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 14px;

  &::-webkit-scrollbar { width: 3px; }
  &::-webkit-scrollbar-track { background: transparent; }
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
  }
`;

// User message — right aligned
const UserMsgRow = styled(motion.div)`
  display: flex;
  justify-content: flex-end;
`;

const UserBubble = styled.div`
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: #fff;
  padding: 8px 12px;
  border-radius: 16px 16px 4px 16px;
  max-width: 82%;
  font-size: 0.78rem;
  line-height: 1.5;
  word-wrap: break-word;
  box-shadow: 0 2px 12px rgba(99, 102, 241, 0.22);
`;

// Assistant message — left aligned
const AsstMsgRow = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 9px;
`;

const AsstIcon = styled.div`
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: rgba(6, 182, 212, 0.12);
  border: 1px solid rgba(6, 182, 212, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
  margin-top: 1px;
`;

const AsstBubbleWrap = styled.div`
  max-width: calc(100% - 35px);
`;

const AsstBubble = styled.div`
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(226, 232, 240, 0.9);
  padding: 9px 12px;
  border-radius: 4px 16px 16px 16px;
  font-size: 0.78rem;
  line-height: 1.55;
  word-wrap: break-word;
`;

const MsgMeta = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 5px;
  font-size: 0.65rem;
  color: rgba(226, 232, 240, 0.28);
  padding-left: 2px;
`;

// System / error message
const SystemMsg = styled(motion.div)`
  text-align: center;
  font-size: 0.78rem;
  color: rgba(245, 158, 11, 0.7);
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.15);
  border-radius: 8px;
  padding: 7px 12px;
  margin: 0 auto;
  max-width: 90%;
`;

// ─── Sources ──────────────────────────────────────────────────────────────────

const SourcesSection = styled.div`
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
`;

const SourcesLabel = styled.div`
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: rgba(226, 232, 240, 0.28);
  font-weight: 700;
  margin-bottom: 6px;
`;

const SourceItem = styled.div`
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-left: 2px solid #06b6d4;
  border-radius: 0 6px 6px 0;
  margin-bottom: 4px;

  .title {
    font-size: 0.74rem;
    color: rgba(226, 232, 240, 0.78);
    font-weight: 600;
    margin-bottom: 2px;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .meta {
    font-size: 0.65rem;
    color: rgba(226, 232, 240, 0.36);
    display: flex;
    gap: 8px;
  }
`;

// ─── Typing indicator ─────────────────────────────────────────────────────────

const TypingRow = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 9px;
`;

const TypingBubble = styled.div`
  display: flex;
  gap: 5px;
  align-items: center;
  padding: 9px 14px;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px 16px 16px 16px;
`;

const Dot = styled.div`
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(226, 232, 240, 0.35);
  animation: bounce 1.4s infinite ease-in-out;
  animation-delay: ${props => props.$d};

  @keyframes bounce {
    0%, 80%, 100% { transform: scale(0.5); opacity: 0.35; }
    40% { transform: scale(1.1); opacity: 0.9; }
  }
`;

// ─── Input area ───────────────────────────────────────────────────────────────

const InputArea = styled.div`
  padding: 12px 13px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
`;

const SuggestionsRow = styled(motion.div)`
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  margin-bottom: 9px;
`;

const Chip = styled(motion.button)`
  background: rgba(99, 102, 241, 0.09);
  border: 1px solid rgba(99, 102, 241, 0.18);
  color: rgba(165, 180, 252, 0.75);
  padding: 4px 10px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.69rem;
  font-weight: 500;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  white-space: nowrap;

  &:hover:not(:disabled) {
    background: rgba(99, 102, 241, 0.18);
    border-color: rgba(99, 102, 241, 0.35);
    color: #a5b4fc;
  }

  &:disabled { opacity: 0.35; cursor: not-allowed; }
`;

const InputRow = styled.div`
  display: flex;
  gap: 8px;
  align-items: flex-end;
`;

const TextArea = styled.textarea`
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 10px;
  padding: 9px 12px;
  color: rgba(226, 232, 240, 0.9);
  font-family: inherit;
  font-size: 0.78rem;
  line-height: 1.45;
  resize: none;
  min-height: 38px;
  max-height: 120px;
  transition: border-color 0.15s, box-shadow 0.15s;

  &::placeholder { color: rgba(226, 232, 240, 0.28); }

  &:focus {
    outline: none;
    border-color: rgba(99, 102, 241, 0.45);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
  }

  &:disabled { opacity: 0.45; }
`;

const SendBtn = styled(motion.button)`
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
  color: white;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.28);
  transition: box-shadow 0.15s;

  &:hover:not(:disabled) {
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.45);
  }

  &:disabled { opacity: 0.38; cursor: not-allowed; }
`;

// ─── Markdown renderer ────────────────────────────────────────────────────────

const MdParagraph = styled.p`
  margin: 0 0 6px 0;
  &:last-child { margin-bottom: 0; }
`;

const MdOl = styled.ol`
  margin: 4px 0 6px 0;
  padding-left: 18px;
  &:last-child { margin-bottom: 0; }
`;

const MdLi = styled.li`
  margin-bottom: 5px;
  line-height: 1.5;
  &:last-child { margin-bottom: 0; }
`;

/** Parse inline markdown: **bold**, *italic*, `code` */
function parseInline(text) {
  const parts = [];
  const re = /(\*\*(.+?)\*\*|\*(.+?)\*|`([^`]+)`)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    if (m[2] !== undefined) parts.push(<strong key={m.index}>{m[2]}</strong>);
    else if (m[3] !== undefined) parts.push(<em key={m.index}>{m[3]}</em>);
    else if (m[4] !== undefined) parts.push(<code key={m.index} style={{ fontSize: '0.75em', background: 'rgba(255,255,255,0.08)', padding: '1px 4px', borderRadius: 3 }}>{m[4]}</code>);
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

function renderMarkdown(text) {
  if (!text) return null;
  const lines = text.split('\n');
  const out = [];
  let listItems = [];

  const flushList = () => {
    if (listItems.length) {
      out.push(<MdOl key={`ol-${out.length}`}>{listItems}</MdOl>);
      listItems = [];
    }
  };

  lines.forEach((line, i) => {
    const numbered = line.match(/^(\d+)\.\s+(.*)/);
    if (numbered) {
      listItems.push(<MdLi key={i}>{parseInline(numbered[2])}</MdLi>);
    } else {
      flushList();
      const trimmed = line.trim();
      if (trimmed) {
        out.push(<MdParagraph key={i}>{parseInline(trimmed)}</MdParagraph>);
      }
    }
  });
  flushList();
  return out;
}

// ─── Component ────────────────────────────────────────────────────────────────

const ChatbotPanel = ({ graphData }) => {
  const [messages, setMessages]           = useState([]);
  const [inputValue, setInputValue]       = useState('');
  const [isLoading, setIsLoading]         = useState(false);
  const [isOnline, setIsOnline]           = useState(false);
  const [suggestions, setSuggestions]     = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(true);

  const messagesEndRef = useRef(null);
  const inputRef       = useRef(null);

  // Health check
  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch('/api/chat/health');
        const data = await res.json();
        setIsOnline(data.status === 'healthy');
      } catch {
        setIsOnline(false);
      }
    };
    check();
    const iv = setInterval(check, 30000);
    return () => clearInterval(iv);
  }, []);

  // Load suggestions
  useEffect(() => {
    if (messages.length !== 0) return;
    const load = async () => {
      try {
        const res = await fetch('/api/chat/suggestions?limit=5');
        const data = await res.json();
        setSuggestions(data.suggestions || []);
        setIsOnline(true);
      } catch {
        /* ignore */
      }
    };
    load();
  }, [messages.length]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: "Hi! I'm your AI knowledge assistant. Ask me anything about your browsing history, saved content, or topics in your graph.",
        timestamp: new Date(),
      }]);
    }
  }, [messages.length]);

  const sendMessage = async (content) => {
    if (!content.trim() || isLoading) return;

    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);
    setShowSuggestions(false);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content.trim(),
          conversation_history: messages.map(m => ({
            role: m.role,
            content: m.content,
            timestamp: m.timestamp,
          })),
          use_rag: true,
          max_context_items: 5,
          similarity_threshold: 0.3,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setIsOnline(true);

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        sources: data.sources || [],
        confidence: data.confidence || 0,
        processingTime: data.processing_time || 0,
      }]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please ensure the backend is running and try again.',
        timestamp: new Date(),
        isError: true,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setShowSuggestions(true);
  };

  const exportChat = () => {
    const blob = new Blob(
      [JSON.stringify({ messages, timestamp: new Date().toISOString() }, null, 2)],
      { type: 'application/json' }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mindcanvas-chat-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Container>
      <TopAccent />

      {/* Header */}
      <Header>
        <HeaderLeft>
          <AiAvatar>✦</AiAvatar>
          <HeaderInfo>
            <HeaderTitle>MindCanvas AI</HeaderTitle>
            <HeaderStatus $online={isOnline}>
              {isOnline ? 'Online' : 'Offline'}
            </HeaderStatus>
          </HeaderInfo>
        </HeaderLeft>

        <HeaderActions>
          <IconBtn
            whileTap={{ scale: 0.9 }}
            onClick={clearChat}
            disabled={isLoading}
            title="Clear conversation"
          >
            ↺
          </IconBtn>
          <IconBtn
            whileTap={{ scale: 0.9 }}
            onClick={exportChat}
            disabled={messages.length === 0}
            title="Export chat"
          >
            ↓
          </IconBtn>
        </HeaderActions>
      </Header>

      {/* Messages */}
      <MessagesArea>
        <AnimatePresence initial={false}>
          {messages.map(msg => {
            if (msg.role === 'user') {
              return (
                <UserMsgRow
                  key={msg.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.22 }}
                >
                  <UserBubble>{msg.content}</UserBubble>
                </UserMsgRow>
              );
            }

            if (msg.role === 'system') {
              return (
                <SystemMsg
                  key={msg.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  {msg.content}
                </SystemMsg>
              );
            }

            // assistant
            return (
              <AsstMsgRow
                key={msg.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.22 }}
              >
                <AsstIcon>✦</AsstIcon>
                <AsstBubbleWrap>
                  <AsstBubble>
                    {renderMarkdown(msg.content)}

                    {msg.sources && msg.sources.length > 0 && (
                      <SourcesSection>
                        <SourcesLabel>Sources · {msg.sources.length}</SourcesLabel>
                        {msg.sources.map((src, idx) => (
                          <SourceItem key={idx}>
                            <div className="title">{src.title}</div>
                            <div className="meta">
                              <span>{src.content_type}</span>
                              <span>{(src.similarity * 100).toFixed(0)}% match</span>
                            </div>
                          </SourceItem>
                        ))}
                      </SourcesSection>
                    )}
                  </AsstBubble>

                  {!msg.isError && (msg.confidence > 0 || msg.processingTime > 0) && (
                    <MsgMeta>
                      {msg.confidence > 0 && (
                        <span>Confidence {(msg.confidence * 100).toFixed(0)}%</span>
                      )}
                      {msg.processingTime > 0 && (
                        <span>{msg.processingTime.toFixed(2)}s</span>
                      )}
                    </MsgMeta>
                  )}
                </AsstBubbleWrap>
              </AsstMsgRow>
            );
          })}
        </AnimatePresence>

        {/* Typing indicator */}
        {isLoading && (
          <TypingRow
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <AsstIcon>✦</AsstIcon>
            <TypingBubble>
              <Dot $d="0s" />
              <Dot $d="0.2s" />
              <Dot $d="0.4s" />
            </TypingBubble>
          </TypingRow>
        )}

        <div ref={messagesEndRef} />
      </MessagesArea>

      {/* Input */}
      <InputArea>
        {showSuggestions && suggestions.length > 0 && (
          <SuggestionsRow
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {suggestions.slice(0, 3).map((s, i) => (
              <Chip
                key={i}
                whileTap={{ scale: 0.95 }}
                onClick={() => sendMessage(s)}
                disabled={isLoading}
              >
                {s}
              </Chip>
            ))}
          </SuggestionsRow>
        )}

        <InputRow>
          <TextArea
            ref={inputRef}
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isOnline ? 'Ask me about your knowledge…' : 'Connecting…'}
            disabled={isLoading}
            rows={1}
          />
          <SendBtn
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.94 }}
            onClick={() => sendMessage(inputValue)}
            disabled={isLoading || !inputValue.trim()}
          >
            →
          </SendBtn>
        </InputRow>
      </InputArea>
    </Container>
  );
};

export default ChatbotPanel;

import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';
import { useAuth } from './AuthContext';

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const { user } = useAuth();
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingChats, setLoadingChats] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);

  // Load chat session index when user changes
  useEffect(() => {
    if (user) {
      loadChats();
    } else {
      setChats([]);
      setActiveChatId(null);
      setMessages([]);
    }
  }, [user]);

  // Load message logs when active chat room changes
  useEffect(() => {
    if (activeChatId) {
      loadMessages(activeChatId);
    } else {
      setMessages([]);
    }
  }, [activeChatId]);

  const loadChats = async () => {
    setLoadingChats(true);
    try {
      const res = await apiClient.get('/chats');
      setChats(res.data);
    } catch (err) {
      console.error("Error loading chat histories:", err);
    } finally {
      setLoadingChats(false);
    }
  };

  const createChat = async (title = "New Farming Discussion") => {
    try {
      const res = await apiClient.post('/chats', { title });
      setChats((prev) => [res.data, ...prev]);
      setActiveChatId(res.data.id);
      return res.data;
    } catch (err) {
      console.error("Error creating new chat:", err);
      return null;
    }
  };

  const loadMessages = async (chatId) => {
    setLoadingMessages(true);
    try {
      const res = await apiClient.get(`/chats/${chatId}/messages`);
      setMessages(res.data);
    } catch (err) {
      console.error("Error loading message streams:", err);
    } finally {
      setLoadingMessages(false);
    }
  };

  // Auto-detect live browser geolocation on startup
  useEffect(() => {
    if (!localStorage.getItem('user_location') && typeof navigator !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          const { latitude, longitude } = pos.coords;
          localStorage.setItem('user_lat', latitude);
          localStorage.setItem('user_lon', longitude);
          try {
            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json&accept-language=en`);
            const data = await res.json();
            if (data && data.address) {
              const city = data.address.city || data.address.town || data.address.village || data.address.suburb || "Local Farm";
              const state = data.address.state || "India";
              localStorage.setItem('user_location', `${city}, ${state}`);
            }
          } catch (e) {
            localStorage.setItem('user_location', 'Maharashtra');
          }
        },
        async () => {
          try {
            const res = await fetch('https://ipapi.co/json/');
            const data = await res.json();
            if (data && data.city) {
              localStorage.setItem('user_location', `${data.city}, ${data.region || 'India'}`);
              if (data.latitude) localStorage.setItem('user_lat', data.latitude);
              if (data.longitude) localStorage.setItem('user_lon', data.longitude);
            }
          } catch (e) {}
        }
      );
    }
  }, []);

  const sendMessage = async (content, attachments = []) => {
    let currentChatId = activeChatId;
    if (!currentChatId) {
      const newChat = await createChat();
      if (!newChat) return;
      currentChatId = newChat.id;
    }
    
    setSendingMessage(true);

    // Auto-inject live user location coordinates if available
    let finalAttachments = [...attachments];
    const savedLoc = localStorage.getItem('user_location');
    const savedLat = localStorage.getItem('user_lat');
    const savedLon = localStorage.getItem('user_lon');
    if (savedLoc || (savedLat && savedLon)) {
      const hasLoc = finalAttachments.some(a => a.file_type === 'location_coords');
      if (!hasLoc) {
        finalAttachments.push({
          file_type: 'location_coords',
          url: '',
          location: savedLoc || '',
          lat: savedLat ? parseFloat(savedLat) : null,
          lon: savedLon ? parseFloat(savedLon) : null
        });
      }
    }
    
    // Optimistically update UI with user's message
    const tempUserMsg = {
      id: `temp_${Date.now()}`,
      chat_id: currentChatId,
      sender: 'user',
      content,
      attachments: finalAttachments,
      tool_calls: [],
      created_at: new Date().toISOString()
    };
    
    setMessages((prev) => [...prev, tempUserMsg]);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/chats/${currentChatId}/messages/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content, attachments: finalAttachments })
      });

      if (!response.ok) {
        throw new Error("HTTP error " + response.status);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let botContent = '';
      
      const tempBotMsg = {
        id: `temp_bot_${Date.now()}`,
        chat_id: currentChatId,
        sender: 'assistant',
        content: '',
        attachments: [],
        tool_calls: [],
        created_at: new Date().toISOString()
      };

      setMessages((prev) => [...prev, tempBotMsg]);

      let done = false;
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunkStr = decoder.decode(value, { stream: !done });
          const lines = chunkStr.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = json_parse_or_null(line.slice(6));
                if (data && data.token) {
                  botContent += data.token;
                  setMessages((prev) => 
                    prev.map(m => m.id === tempBotMsg.id ? { ...m, content: botContent } : m)
                  );
                } else if (data && data.final_payload) {
                  setMessages((prev) => 
                    prev.map(m => m.id === tempBotMsg.id ? data.final_payload : m)
                  );
                  if (data.chat_title) {
                    setChats((prev) =>
                      prev.map(c => c.id === currentChatId ? { ...c, title: data.chat_title } : c)
                    );
                  }
                }
              } catch (e) {
                // Ignore partial JSON parsing errors
              }
            }
          }
        }
      }
    } catch (err) {
      console.error("Error dispatching message stream payload:", err);
    } finally {
      setSendingMessage(false);
      loadChats();
    }
  };

  // Helper function to parse json safely
  const json_parse_or_null = (str) => {
    try {
      return JSON.parse(str);
    } catch (e) {
      return null;
    }
  };

  const deleteChat = async (chatId) => {
    try {
      await apiClient.delete(`/chats/${chatId}`);
      setChats((prev) => {
        const updated = prev.filter((c) => c.id !== chatId);
        if (activeChatId === chatId) {
          setActiveChatId(updated.length > 0 ? updated[0].id : null);
        }
        return updated;
      });
    } catch (err) {
      console.error("Error deleting chat session:", err);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        chats,
        activeChatId,
        setActiveChatId,
        messages,
        loadingChats,
        loadingMessages,
        sendingMessage,
        createChat,
        deleteChat,
        loadChats,
        sendMessage
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);

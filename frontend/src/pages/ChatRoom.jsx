import React, { useState } from 'react';
import AppLayout from '../components/layout/AppLayout';
import ChatWindow from '../components/chat/ChatWindow';
import { useChat } from '../contexts/ChatContext';
import { Search, Plus, Trash2, Edit, Pin, MessageCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import Modal from '../components/common/Modal';
import Toast from '../components/common/Toast';

const ChatRoom = () => {
  const { chats, activeChatId, setActiveChatId, createChat, deleteChat } = useChat();
  const [chatSearch, setChatSearch] = useState('');
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [selectedChatForRename, setSelectedChatForRename] = useState(null);
  const [renameInput, setRenameInput] = useState('');
  
  // Custom Delete Modal states
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedChatForDelete, setSelectedChatForDelete] = useState(null);

  // Toast notification state
  const [showToast, setShowToast] = useState(false);
  const [toastMsg, setToastMsg] = useState('');
  const [toastType, setToastType] = useState('success');
  
  // Custom dummy pinned status
  const [pinnedChats, setPinnedChats] = useState(['chat_1']); 

  const handleRenameClick = (chat, e) => {
    e.stopPropagation();
    setSelectedChatForRename(chat);
    setRenameInput(chat.title);
    setShowRenameModal(true);
  };

  const handleDeleteClick = (chat, e) => {
    e.stopPropagation();
    setSelectedChatForDelete(chat);
    setShowDeleteModal(true);
  };

  const confirmDelete = () => {
    if (selectedChatForDelete) {
      const deletedTitle = selectedChatForDelete.title || 'Discussion';
      deleteChat(selectedChatForDelete.id);
      setShowDeleteModal(false);
      setSelectedChatForDelete(null);
      
      setToastMsg(`Discussion "${deletedTitle}" deleted successfully.`);
      setToastType('success');
      setShowToast(true);
    }
  };

  const handleRenameSave = (e) => {
    e.preventDefault();
    if (selectedChatForRename && renameInput.trim()) {
      selectedChatForRename.title = renameInput.trim();
      setShowRenameModal(false);
    }
  };

  const togglePin = (chatId, e) => {
    e.stopPropagation();
    setPinnedChats(prev => 
      prev.includes(chatId) ? prev.filter(id => id !== chatId) : [...prev, chatId]
    );
  };

  const filteredChats = chats.filter(c => 
    c.title.toLowerCase().includes(chatSearch.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="h-full w-full flex">
        
        {/* Chat conversations sub-sidebar */}
        <aside className="w-72 h-full border-r border-gray-200 dark:border-dark-border bg-white/40 dark:bg-dark-surface/40 flex flex-col shrink-0">
          
          <div className="p-4 border-b border-gray-200 dark:border-dark-border space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="font-extrabold text-sm text-gray-800 dark:text-white">Chat Rooms</h3>
              <button
                onClick={() => createChat("New Farming Discussion")}
                className="p-2 bg-primary/10 hover:bg-primary/20 text-primary dark:bg-primary/20 dark:text-green-400 rounded-xl transition-all"
                title="Create New Room"
              >
                <Plus size={16} />
              </button>
            </div>
            
            {/* Search chats */}
            <div className="relative flex items-center bg-gray-100 dark:bg-dark-bg/60 border border-transparent rounded-xl px-3 py-1.5">
              <Search size={14} className="text-gray-400 mr-2 shrink-0" />
              <input
                type="text"
                value={chatSearch}
                onChange={e => setChatSearch(e.target.value)}
                placeholder="Search conversations..."
                className="bg-transparent border-none outline-none text-xs w-full placeholder-gray-450"
              />
            </div>
          </div>

          {/* Chats index scroll container */}
          <div className="flex-1 overflow-y-auto p-3 space-y-4">
            
            {/* Pinned section */}
            {pinnedChats.length > 0 && (
              <div className="space-y-1">
                <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider px-3 mb-1">Pinned Chats</div>
                {filteredChats.filter(c => pinnedChats.includes(c.id)).map(c => (
                  <div
                    key={c.id}
                    onClick={() => setActiveChatId(c.id)}
                    className={`group w-full flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                      c.id === activeChatId
                        ? 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-green-400 font-bold border-l-4 border-primary'
                        : 'hover:bg-gray-100 dark:hover:bg-dark-bg/50 text-gray-600 dark:text-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0 flex-1">
                      <Pin size={12} className="text-accent-gold rotate-45 shrink-0" />
                      <span className="text-xs truncate">{c.title}</span>
                    </div>
                    
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={(e) => handleRenameClick(c, e)} className="p-1 hover:text-primary" title="Rename"><Edit size={12} /></button>
                      <button onClick={(e) => togglePin(c.id, e)} className="p-1 hover:text-accent-gold" title="Unpin"><Pin size={12} /></button>
                      <button onClick={(e) => handleDeleteClick(c, e)} className="p-1 hover:text-red-500 transition-colors" title="Delete Chat"><Trash2 size={12} /></button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Recents section */}
            <div className="space-y-1">
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider px-3 mb-1">Recent Chats</div>
              {filteredChats.filter(c => !pinnedChats.includes(c.id)).map(c => (
                <div
                  key={c.id}
                  onClick={() => setActiveChatId(c.id)}
                  className={`group w-full flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                    c.id === activeChatId
                      ? 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-green-400 font-bold border-l-4 border-primary'
                      : 'hover:bg-gray-100 dark:hover:bg-dark-bg/50 text-gray-600 dark:text-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0 flex-1">
                    <MessageCircle size={12} className="text-gray-400 shrink-0" />
                    <span className="text-xs truncate">{c.title}</span>
                  </div>
                  
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={(e) => handleRenameClick(c, e)} className="p-1 hover:text-primary" title="Rename"><Edit size={12} /></button>
                    <button onClick={(e) => togglePin(c.id, e)} className="p-1 hover:text-accent-gold" title="Pin"><Pin size={12} /></button>
                    <button onClick={(e) => handleDeleteClick(c, e)} className="p-1 hover:text-red-500 transition-colors" title="Delete Chat"><Trash2 size={12} /></button>
                  </div>
                </div>
              ))}
            </div>

          </div>

        </aside>

        {/* Chat Window Panel */}
        <div className="flex-1 h-full relative overflow-hidden bg-transparent">
          <ChatWindow />
        </div>

      </div>

      {/* Rename Dialog Modal */}
      <Modal show={showRenameModal} title="Rename Conversation" onClose={() => setShowRenameModal(false)}>
        <form onSubmit={handleRenameSave} className="space-y-4">
          <input
            type="text"
            value={renameInput}
            onChange={e => setRenameInput(e.target.value)}
            className="w-full px-4 py-3 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-sm outline-none"
            placeholder="Farming dialogue topic..."
          />
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setShowRenameModal(false)} className="px-4 py-2 bg-gray-100 dark:bg-dark-bg text-gray-500 rounded-xl text-xs font-bold">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-primary text-white rounded-xl text-xs font-bold shadow-md">Save Title</button>
          </div>
        </form>
      </Modal>

      {/* Professional Delete Confirmation Modal */}
      <Modal show={showDeleteModal} title="Delete Discussion" onClose={() => setShowDeleteModal(false)}>
        <div className="space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Are you sure you want to delete <strong className="text-gray-900 dark:text-white">"{selectedChatForDelete?.title}"</strong>? This will permanently remove all messages in this room.
          </p>
          <div className="flex justify-end gap-2 pt-2">
            <button 
              type="button" 
              onClick={() => setShowDeleteModal(false)} 
              className="px-4 py-2 bg-gray-100 dark:bg-dark-bg text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-dark-surface rounded-xl text-xs font-bold transition-all"
            >
              Cancel
            </button>
            <button 
              type="button" 
              onClick={confirmDelete} 
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-md transition-all flex items-center gap-1.5"
            >
              <Trash2 size={14} />
              Delete Chat
            </button>
          </div>
        </div>
      </Modal>

      {/* Animated Toast Notification */}
      <Toast 
        show={showToast} 
        message={toastMsg} 
        type={toastType} 
        onClose={() => setShowToast(false)} 
      />

    </AppLayout>
  );
};

export default ChatRoom;

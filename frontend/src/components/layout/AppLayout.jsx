import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../contexts/ChatContext';
import { useAppTheme } from '../../contexts/ThemeContext';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sun, Moon, LogOut, MessageSquare, Plus, User, Compass, Settings, 
  Tractor, Activity, CloudSun, ShoppingCart, Landmark, BookOpen, 
  FileText, Bell, Search, Globe, ChevronDown, Sparkles, MessageCircle, X, ChevronLeft, ChevronRight, LayoutDashboard, ShieldCheck
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const AppLayout = ({ children }) => {
  const { user, logout, profile } = useAuth();
  const { chats, activeChatId, setActiveChatId, createChat } = useChat();
  const { themeMode, toggleTheme } = useAppTheme();
  const navigate = useNavigate();
  const location = useLocation();

  // State configurations
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showNotificationMenu, setShowNotificationMenu] = useState(false);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showQuickAssistant, setShowQuickAssistant] = useState(false);
  const [quickAssistantInput, setQuickAssistantInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [lang, setLang] = useState('English');

  const handleNewChat = async () => {
    navigate('/chat');
    await createChat();
  };

  const menuItems = [
    { label: 'Dashboard', path: '/dashboard', icon: Compass },
    { label: 'AI Chat', path: '/chat', icon: MessageSquare },
    { label: 'Crop Recommend', path: '/crop-recommendation', icon: Tractor },
    { label: 'Disease Detect', path: '/disease-detection', icon: Activity },
    { label: 'Weather Forecast', path: '/weather', icon: CloudSun },
    { label: 'Market Prices', path: '/market', icon: ShoppingCart },
    { label: 'Gov Schemes', path: '/government-schemes', icon: Landmark },
    { label: 'Profile', path: '/profile', icon: User },
    { label: 'Settings', path: '/settings', icon: Settings },
    { label: 'Admin Panel', path: '/admin', icon: ShieldCheck, adminOnly: true },
  ];

  // Dummy notification data
  const dummyNotifications = [
    { id: 1, title: 'Leaf Rust Alert', desc: 'Alert for your Wheat crop in near regions.', type: 'warning' },
    { id: 2, title: 'Price Increase', desc: 'Maize prices jumped by 5% today.', type: 'success' },
    { id: 3, title: 'Weather warning', desc: 'Heavy rains projected in 48 hours.', type: 'info' }
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#F8FAF8] dark:bg-dark-bg text-gray-900 dark:text-gray-100 transition-colors duration-300">
      
      {/* 1. ANIMATED LEFT SIDEBAR */}
      <motion.aside 
        animate={{ width: sidebarCollapsed ? 76 : 280 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="h-full flex flex-col border-r border-gray-200 dark:border-dark-border bg-white/70 dark:bg-[#121e16]/70 backdrop-blur-xl relative z-20 shrink-0"
      >
        {/* Toggle Collapse Trigger */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="absolute top-6 -right-3 w-6 h-6 rounded-full bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border flex items-center justify-center text-gray-400 hover:text-primary hover:shadow-md transition-all z-30"
        >
          {sidebarCollapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
        </button>

        {/* Logo / Header */}
        <div className="p-6 border-b border-gray-100 dark:border-dark-border flex items-center gap-3">
          <span className="text-2xl shrink-0">🌱</span>
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.h1 
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                className="font-extrabold text-xl tracking-tight grad-text truncate"
              >
                AgriGenius
              </motion.h1>
            )}
          </AnimatePresence>
        </div>

        {/* Create Chat Action Button */}
        <div className="px-4 py-4 shrink-0">
          <button
            onClick={handleNewChat}
            className={`w-full py-3 px-3 bg-primary hover:bg-primary-light text-white rounded-2xl font-bold flex items-center gap-2 justify-center transition-all shadow-md shadow-primary/20 hover:scale-[1.01] ${sidebarCollapsed ? 'px-2' : ''}`}
          >
            <Plus size={18} />
            {!sidebarCollapsed && <span>New Discussion</span>}
          </button>
        </div>

        {/* Side Scrollable Menus */}
        <nav className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            // Check admin roles
            if (item.adminOnly && !user?.roles?.includes('admin')) return null;

            return (
              <div key={item.path} className="relative group">
                <button
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-2xl font-semibold text-xs transition-all ${
                    isActive 
                      ? 'bg-primary text-white shadow-md shadow-primary/20' 
                      : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-surface/60 hover:text-primary dark:hover:text-green-400'
                  } ${sidebarCollapsed ? 'justify-center px-0' : ''}`}
                >
                  <Icon size={18} className="shrink-0" />
                  {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                  
                  {/* Active bar */}
                  {isActive && !sidebarCollapsed && (
                    <motion.div 
                      layoutId="activeSideBarTab" 
                      className="absolute right-2 w-1.5 h-6 bg-accent-gold rounded-full"
                    />
                  )}
                </button>

                {/* Collapsed Tooltip */}
                {sidebarCollapsed && (
                  <div className="absolute left-20 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-[10px] font-bold py-1.5 px-3 rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg z-50">
                    {item.label}
                  </div>
                )}
              </div>
            );
          })}
        </nav>
      </motion.aside>

      {/* 2. MAIN CONTAINER & TOP NAVBAR */}
      <div className="flex-1 h-full flex flex-col overflow-hidden relative">
        
        {/* TOP NAVBAR CONTAINER */}
        <header className="h-20 border-b border-gray-200 dark:border-dark-border bg-white/75 dark:bg-dark-surface/75 backdrop-blur-xl px-8 flex items-center justify-between z-10 shrink-0">
          
          {/* Left search */}
          <div className="w-80 relative flex items-center bg-gray-100 dark:bg-dark-bg/60 border border-transparent focus-within:border-primary/25 rounded-2xl px-4 py-2 transition-all">
            <Search size={16} className="text-gray-400 mr-2 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search features, schemes, or reports..."
              className="bg-transparent border-none outline-none text-xs w-full text-gray-800 dark:text-gray-200 placeholder-gray-400"
            />
          </div>

          {/* Right navbar controls */}
          <div className="flex items-center gap-4 relative">
            
            {/* Language Selector */}
            <div className="relative">
              <button 
                onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl hover:bg-gray-100 dark:hover:bg-dark-surface transition-all text-xs font-bold text-gray-600 dark:text-gray-300"
              >
                <Globe size={14} />
                <span>{lang}</span>
                <ChevronDown size={12} />
              </button>
              {showLanguageMenu && (
                <div className="absolute right-0 mt-2 w-36 rounded-2xl bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border p-1.5 shadow-xl z-30">
                  {['English', 'Español', 'हिन्दी', 'తెలుగు'].map((l) => (
                    <button
                      key={l}
                      onClick={() => { setLang(l); setShowLanguageMenu(false); }}
                      className="w-full text-left px-3 py-2 rounded-xl text-xs font-semibold hover:bg-gray-50 dark:hover:bg-dark-bg transition-colors"
                    >
                      {l}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Dark Mode Toggle */}
            <button 
              onClick={toggleTheme}
              className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-dark-surface transition-all text-gray-500"
            >
              {themeMode === 'dark' ? <Sun size={18} className="text-accent-gold" /> : <Moon size={18} className="text-primary" />}
            </button>

            {/* Notification Bell */}
            <div className="relative">
              <button 
                onClick={() => setShowNotificationMenu(!showNotificationMenu)}
                className="p-2.5 rounded-xl hover:bg-gray-100 dark:hover:bg-dark-surface transition-all text-gray-500 relative"
              >
                <Bell size={18} />
                <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-red-500"></span>
              </button>
              {showNotificationMenu && (
                <div className="absolute right-0 mt-2 w-80 rounded-3xl bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border p-4 shadow-2xl z-30">
                  <h4 className="font-extrabold text-sm mb-3">Farm Notifications</h4>
                  <div className="space-y-2.5">
                    {dummyNotifications.map((n) => (
                      <div key={n.id} className="p-3 bg-gray-50 dark:bg-dark-bg/60 border border-gray-100 dark:border-dark-border rounded-2xl text-xs">
                        <p className="font-bold flex items-center justify-between text-gray-800 dark:text-gray-200">
                          {n.title}
                          <span className={`w-1.5 h-1.5 rounded-full ${n.type === 'warning' ? 'bg-red-500' : 'bg-primary'}`}></span>
                        </p>
                        <p className="text-gray-500 mt-1">{n.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* User Profile Dropdown */}
            <div className="relative">
              <button 
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-gray-100 dark:hover:bg-dark-surface transition-all"
              >
                <div className="w-8 h-8 rounded-full bg-primary/20 dark:bg-primary/30 flex items-center justify-center font-bold text-primary dark:text-green-400">
                  {user?.email[0].toUpperCase()}
                </div>
              </button>
              {showProfileMenu && (
                <div className="absolute right-0 mt-2 w-56 rounded-3xl bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border p-2 shadow-2xl z-30">
                  <div className="p-3 border-b border-gray-100 dark:border-dark-border">
                    <p className="text-xs font-bold truncate text-gray-800 dark:text-gray-200">{profile?.fullname || user?.email}</p>
                    <p className="text-[10px] text-gray-400 mt-0.5 truncate">{user?.email}</p>
                  </div>
                  <div className="p-1 space-y-0.5">
                    <button onClick={() => { navigate('/profile'); setShowProfileMenu(false); }} className="w-full text-left px-3 py-2 text-xs font-semibold hover:bg-gray-50 dark:hover:bg-dark-bg rounded-xl transition-colors">Profile Details</button>
                    <button onClick={() => { navigate('/settings'); setShowProfileMenu(false); }} className="w-full text-left px-3 py-2 text-xs font-semibold hover:bg-gray-50 dark:hover:bg-dark-bg rounded-xl transition-colors">System Settings</button>
                    <button onClick={logout} className="w-full text-left px-3 py-2 text-xs font-semibold hover:bg-red-50 dark:hover:bg-red-950/20 text-red-500 rounded-xl transition-colors">Logout</button>
                  </div>
                </div>
              )}
            </div>

          </div>

        </header>

        {/* VIEWPORT CONTENT WINDOW */}
        <main className="flex-1 overflow-hidden relative bg-[#F8FAF8] dark:bg-dark-bg">
          {children}
        </main>

      </div>



    </div>
  );
};

export default AppLayout;

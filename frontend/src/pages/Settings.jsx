import React, { useState } from 'react';
import AppLayout from '../components/layout/AppLayout';
import { useAppTheme } from '../contexts/ThemeContext';
import { Settings, Shield, Volume2, Globe, Sliders, Bell } from 'lucide-react';
import Toast from '../components/common/Toast';

const SettingsPage = () => {
  const { themeMode, toggleTheme } = useAppTheme();
  const [voiceSpeed, setVoiceSpeed] = useState('1.0');
  const [voiceGender, setVoiceGender] = useState('Female');
  const [lang, setLang] = useState('English');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  
  const [showToast, setShowToast] = useState(false);

  const handleSaveSettings = (e) => {
    e.preventDefault();
    setShowToast(true);
  };

  return (
    <AppLayout>
      <div className="p-8 h-full overflow-y-auto space-y-8 pb-20 max-w-4xl">
        
        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight grad-text flex items-center gap-2">
            <Settings />
            System Settings
          </h1>
          <p className="text-sm text-gray-500 font-medium mt-1">
            Configure default speech assistant characteristics, dark mode settings, and notification alerts.
          </p>
        </div>

        <form onSubmit={handleSaveSettings} className="space-y-6">
          
          {/* Visual Preferences */}
          <div className="bg-white dark:bg-dark-surface p-6 border border-gray-200 dark:border-dark-border rounded-3xl space-y-4">
            <h3 className="font-extrabold text-sm text-gray-800 dark:text-white flex items-center gap-2">
              <Sliders size={16} className="text-primary" />
              Visual Preferences
            </h3>
            
            <div className="flex items-center justify-between p-3.5 bg-gray-50 dark:bg-dark-bg/60 rounded-2xl border border-gray-100 dark:border-dark-border">
              <div>
                <p className="font-bold text-xs">Dark Theme Mode</p>
                <p className="text-[10px] text-gray-400 mt-0.5">Toggle interface shadows and background lights</p>
              </div>
              <button
                type="button"
                onClick={toggleTheme}
                className={`w-12 h-6 rounded-full p-1 transition-colors ${themeMode === 'dark' ? 'bg-primary' : 'bg-gray-300'}`}
              >
                <div className={`w-4 h-4 rounded-full bg-white transition-transform ${themeMode === 'dark' ? 'translate-x-6' : ''}`} />
              </button>
            </div>
          </div>

          {/* Voice Assistant Parameters */}
          <div className="bg-white dark:bg-dark-surface p-6 border border-gray-200 dark:border-dark-border rounded-3xl space-y-4">
            <h3 className="font-extrabold text-sm text-gray-800 dark:text-white flex items-center gap-2">
              <Volume2 size={16} className="text-primary" />
              TTS & Speech Parameters
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold uppercase text-gray-400">Assistant Voice Profile</label>
                <select
                  value={voiceGender}
                  onChange={e => setVoiceGender(e.target.value)}
                  className="w-full px-4 py-2.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none"
                >
                  <option>Female (Default)</option>
                  <option>Male</option>
                  <option>Earthy / Deep Tone</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold uppercase text-gray-400">Speech Playback Speed</label>
                <select
                  value={voiceSpeed}
                  onChange={e => setVoiceSpeed(e.target.value)}
                  className="w-full px-4 py-2.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none"
                >
                  <option>0.75x</option>
                  <option>1.0x</option>
                  <option>1.25x</option>
                  <option>1.5x</option>
                </select>
              </div>
            </div>
          </div>

          {/* Notification toggles */}
          <div className="bg-white dark:bg-dark-surface p-6 border border-gray-200 dark:border-dark-border rounded-3xl space-y-4">
            <h3 className="font-extrabold text-sm text-gray-800 dark:text-white flex items-center gap-2">
              <Bell size={16} className="text-primary" />
              Subscribers Alerts
            </h3>
            
            <div className="flex items-center justify-between p-3.5 bg-gray-50 dark:bg-dark-bg/60 rounded-2xl border border-gray-100 dark:border-dark-border">
              <div>
                <p className="font-bold text-xs">Enable Push Alerts</p>
                <p className="text-[10px] text-gray-400 mt-0.5">Dispatches weather warnings and leaf blight reports instantly</p>
              </div>
              <button
                type="button"
                onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                className={`w-12 h-6 rounded-full p-1 transition-colors ${notificationsEnabled ? 'bg-primary' : 'bg-gray-300'}`}
              >
                <div className={`w-4 h-4 rounded-full bg-white transition-transform ${notificationsEnabled ? 'translate-x-6' : ''}`} />
              </button>
            </div>
          </div>

          {/* Save Button */}
          <button
            type="submit"
            className="py-3 px-6 bg-primary hover:bg-primary-light text-white font-bold rounded-2xl transition-all shadow-md"
          >
            Save System Configurations
          </button>

        </form>

      </div>

      <Toast 
        show={showToast} 
        message="System configurations saved successfully!" 
        type="success" 
        onClose={() => setShowToast(false)} 
      />

    </AppLayout>
  );
};

export default SettingsPage;

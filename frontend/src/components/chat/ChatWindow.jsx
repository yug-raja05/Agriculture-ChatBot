import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../../contexts/ChatContext';
import { useLocation } from '../../contexts/LocationContext';
import MessageItem from './MessageItem';
import { Send, Paperclip, Mic, Image, Sparkles, Camera, X, Play, Volume2, MapPin, RefreshCw, Edit2, Check } from 'lucide-react';
import Modal from '../common/Modal';

const ChatWindow = () => {
  const { messages, sendMessage, sendingMessage, loadingMessages } = useChat();
  const { userLocation, locationReady, detecting, refreshLocation, updateLocationManually } = useLocation();
  const [inputValue, setInputValue] = useState('');
  const [editingLoc, setEditingLoc] = useState(false);
  const [locInputVal, setLocInputVal] = useState('');
  const messagesEndRef = useRef(null);

  // Attachment & media modal simulator states
  const [showCameraModal, setShowCameraModal] = useState(false);
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [cameraUploading, setCameraUploading] = useState(false);
  const [audioRecording, setAudioRecording] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, sendingMessage]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!inputValue.trim() || sendingMessage) return;
    sendMessage(inputValue.trim());
    setInputValue('');
  };

  const insertSuggestion = (text) => {
    setInputValue(text);
  };

  // Simulate Leaf Camera diagnosis upload
  const triggerCameraDiagnosis = () => {
    setCameraUploading(true);
    setTimeout(() => {
      setCameraUploading(false);
      setShowCameraModal(false);
      sendMessage("Analyze Leaf Rust in Wheat Crop", [
        { file_type: "image", url: "https://example.com/leaf_rust.jpg" }
      ]);
    }, 2000);
  };

  // Simulate voice assistant transcript
  const toggleRecording = () => {
    if (audioRecording) {
      setAudioRecording(false);
      setRecordedAudio(true);
    } else {
      setAudioRecording(true);
      setRecordedAudio(null);
    }
  };

  const triggerVoiceSubmit = () => {
    setShowVoiceModal(false);
    sendMessage("Analyze current location weather forecast");
  };

  const suggestions = [
    { text: "What is my detected farm location and today's weather?", label: "Location & Weather" },
    { text: "Recommend best rotation crops for sandy clay.", label: "Crop Advisor" },
    { text: "Diagnose tomato leaf yellowing spot symptoms.", label: "Disease Scan" },
    { text: "Verify today's wholesale pricing trends for Maize.", label: "Wholesale Value" }
  ];

  return (
    <div className="flex flex-col h-full w-full bg-transparent">
      
      {/* Dynamic Location indicator bar */}
      <div className="px-6 py-2 border-b border-gray-100 dark:border-dark-border bg-white/70 dark:bg-dark-surface/70 backdrop-blur-md flex items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 min-w-0">
          <MapPin size={13} className={`shrink-0 ${detecting ? 'animate-pulse text-amber-500' : 'text-primary dark:text-green-400'}`} />
          {editingLoc ? (
            <div className="flex items-center gap-1.5">
              <input
                type="text"
                value={locInputVal}
                onChange={(e) => setLocInputVal(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    if (locInputVal.trim()) updateLocationManually(locInputVal);
                    setEditingLoc(false);
                  } else if (e.key === 'Escape') {
                    setEditingLoc(false);
                  }
                }}
                placeholder="Enter city/district..."
                className="px-2 py-0.5 text-xs rounded-lg border border-primary/40 bg-white dark:bg-dark-bg text-gray-800 dark:text-gray-100 outline-none w-44"
                autoFocus
              />
              <button
                onClick={() => {
                  if (locInputVal.trim()) updateLocationManually(locInputVal);
                  setEditingLoc(false);
                }}
                className="p-1 text-primary hover:bg-primary/10 rounded-md transition-colors"
                title="Save Location"
              >
                <Check size={13} />
              </button>
              <button
                onClick={() => setEditingLoc(false)}
                className="p-1 text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-bg rounded-md transition-colors"
                title="Cancel"
              >
                <X size={13} />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 truncate">
              <span className="font-semibold text-gray-500 dark:text-gray-400 text-[11px]">Farm Location:</span>
              <span className="font-bold text-gray-800 dark:text-gray-200 truncate text-[11px]">
                {detecting ? 'Detecting GPS...' : (userLocation || 'Detecting location...')}
              </span>
              <button
                onClick={() => {
                  setLocInputVal(userLocation && userLocation !== 'Detecting location...' ? userLocation : '');
                  setEditingLoc(true);
                }}
                className="p-1 text-gray-400 hover:text-primary transition-colors"
                title="Edit location"
              >
                <Edit2 size={11} />
              </button>
            </div>
          )}
        </div>

        <button
          onClick={refreshLocation}
          disabled={detecting}
          className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold text-primary dark:text-green-400 hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors shrink-0 disabled:opacity-50"
          title="Re-detect GPS location from browser"
        >
          <RefreshCw size={10} className={detecting ? 'animate-spin' : ''} />
          <span>{detecting ? 'Detecting...' : 'Detect GPS'}</span>
        </button>
      </div>

      {/* Scrollable conversation bubble streams */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {loadingMessages ? (
          <div className="h-full w-full flex flex-col items-center justify-center gap-3">
            <span className="text-3xl animate-bounce">🌱</span>
            <p className="text-xs text-gray-400 font-semibold">Loading conversation stream...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full w-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto gap-8">
            <span className="text-6xl animate-pulse">🌱</span>
            <div className="space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight grad-text">AgriGenius Intelligence</h2>
              <p className="text-xs text-gray-500 font-medium max-w-md mx-auto leading-relaxed">
                Enterprise AI farming workspace specialized in crop yield optimization, soil chemistry evaluations, and visual leaves blight assessments.
              </p>
            </div>
            
            {/* Quick Suggestion chips */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => insertSuggestion(s.text)}
                  className="p-4 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-2xl text-left text-xs font-semibold hover:border-primary dark:hover:border-primary-light transition-all hover:scale-[1.01]"
                >
                  <p className="text-primary dark:text-green-400 mb-1 flex items-center gap-1.5 font-extrabold uppercase text-[10px]">
                    <Sparkles size={12} />
                    {s.label}
                  </p>
                  <p className="text-gray-500 dark:text-gray-400 font-normal leading-relaxed">{s.text}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageItem key={msg.id} message={msg} />
          ))
        )}

        {sendingMessage && (
          <div className="flex gap-4 p-4 items-center">
            <div className="w-10 h-10 rounded-2xl bg-primary text-white flex items-center justify-center shrink-0 animate-bounce">
              🌱
            </div>
            <div className="space-y-2 flex-1">
              <div className="h-4 bg-gray-200 dark:bg-dark-border rounded w-2/5 animate-pulse"></div>
              <div className="h-3 bg-gray-200 dark:bg-dark-border rounded w-3/5 animate-pulse"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input container pane */}
      <div className="p-6 border-t border-gray-200 dark:border-dark-border bg-white/40 dark:bg-dark-surface/40 backdrop-blur-md">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto flex gap-3 relative">
          
          <div className="flex-1 relative flex items-center bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-2xl px-4 py-2 shadow-sm focus-within:ring-2 focus-within:ring-primary/20 transition-all">
            
            {/* Input Action controls */}
            <button 
              type="button" 
              onClick={() => setShowCameraModal(true)}
              className="p-2 text-gray-400 hover:text-primary transition-colors shrink-0" 
              title="Camera Scan Leaf disease"
            >
              <Camera size={18} />
            </button>
            <button 
              type="button" 
              className="p-2 text-gray-405 hover:text-primary transition-colors shrink-0" 
              title="Upload photo"
            >
              <Image size={18} />
            </button>
            
            {/* Main Input */}
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask AgriGenius: 'Recommend fertilizer dosage' or upload crop leaf disease photo..."
              className="flex-1 bg-transparent border-0 outline-none text-xs px-2 py-2 text-gray-800 dark:text-gray-100 placeholder-gray-400"
            />
            
            {/* Audio Voice controls */}
            <button 
              type="button" 
              onClick={() => setShowVoiceModal(true)}
              className="p-2 text-gray-400 hover:text-primary transition-colors shrink-0 mr-2" 
              title="Voice memo record"
            >
              <Mic size={18} />
            </button>

            {/* Send */}
            <button
              type="submit"
              disabled={!inputValue.trim() || sendingMessage}
              className={`p-2.5 rounded-xl transition-all ${
                inputValue.trim() && !sendingMessage
                  ? 'bg-primary text-white hover:bg-primary-light scale-[1.02]'
                  : 'bg-gray-100 dark:bg-dark-bg text-gray-300 dark:text-gray-650'
              }`}
            >
              <Send size={16} />
            </button>

          </div>
          
        </form>
      </div>

      {/* Leaf camera scanner modal */}
      <Modal show={showCameraModal} title="Visual Leaf Diagnostician" onClose={() => setShowCameraModal(false)}>
        <div className="space-y-6 text-center">
          <div className="w-full h-64 bg-gray-100 dark:bg-dark-bg rounded-3xl border-2 border-dashed border-gray-200 dark:border-dark-border flex flex-col items-center justify-center relative overflow-hidden">
            {cameraUploading ? (
              <div className="space-y-3">
                <span className="text-3xl animate-spin block">🌀</span>
                <p className="text-xs text-gray-400 font-bold">Scanning leaf structural patterns...</p>
              </div>
            ) : (
              <div className="space-y-3 p-6 text-center">
                <span className="text-5xl block">📸</span>
                <p className="text-xs text-gray-500 font-medium">Position crop leaf in front of camera lenses</p>
                <span className="text-[10px] text-gray-400 block italic">Accepts Tomato, Maize, Wheat, Grape leaf images</span>
              </div>
            )}
          </div>
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowCameraModal(false)} className="px-4 py-2 bg-gray-150 text-gray-500 rounded-xl text-xs font-bold">Cancel</button>
            <button onClick={triggerCameraDiagnosis} disabled={cameraUploading} className="px-4 py-2 bg-primary text-white rounded-xl text-xs font-bold shadow-md">Capture & Diagnose</button>
          </div>
        </div>
      </Modal>

      {/* Voice Assistant Modal */}
      <Modal show={showVoiceModal} title="AI Voice Transcriber" onClose={() => setShowVoiceModal(false)}>
        <div className="space-y-6 text-center">
          <div className="flex justify-center items-center h-40 relative">
            {audioRecording && (
              <div className="absolute flex gap-1 items-center justify-center">
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{ height: [20, 60, 20] }}
                    transition={{ repeat: Infinity, duration: 1, delay: i * 0.15 }}
                    className="w-1 bg-primary rounded-full"
                  />
                ))}
              </div>
            )}
            {!audioRecording && !recordedAudio && (
              <p className="text-xs text-gray-400 font-bold">Tap mic to begin speaking...</p>
            )}
            {!audioRecording && recordedAudio && (
              <div className="flex items-center gap-2 p-3 bg-primary/10 text-primary rounded-2xl border border-primary/20">
                <Volume2 size={16} />
                <span className="text-xs font-semibold">Recording complete (0:04)</span>
              </div>
            )}
          </div>

          <div className="flex justify-center gap-3">
            <button
              onClick={toggleRecording}
              className={`p-4 rounded-full flex items-center justify-center transition-all ${
                audioRecording 
                  ? 'bg-red-500 text-white animate-pulse' 
                  : 'bg-primary text-white hover:scale-105'
              }`}
            >
              <Mic size={22} />
            </button>
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-gray-100 dark:border-dark-border">
            <button onClick={() => setShowVoiceModal(false)} className="px-4 py-2 bg-gray-100 text-gray-500 rounded-xl text-xs font-bold">Cancel</button>
            <button onClick={triggerVoiceSubmit} disabled={!recordedAudio} className="px-4 py-2 bg-primary text-white rounded-xl text-xs font-bold disabled:opacity-50">Submit Speech</button>
          </div>
        </div>
      </Modal>

    </div>
  );
};

export default ChatWindow;

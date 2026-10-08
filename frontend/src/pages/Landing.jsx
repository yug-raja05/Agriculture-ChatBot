import React from 'react';
import { motion } from 'framer-motion';
import { Sprout, Compass, Sparkles, Activity, ShieldCheck, HeartHandshake, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Landing = () => {
  const navigate = useNavigate();

  const features = [
    { icon: Compass, title: "Intelligent AI Chat", desc: "Intelligent agent capable of interpreting weather conditions, soil chemistry inputs, and crop diagnostics." },
    { icon: Sprout, title: "Crop & Fertilizer Recommender", desc: "Deep analytical recommendations based on NPK soil profiles and expected yield optimizations." },
    { icon: Activity, title: "Leaf Disease Diagnostician", desc: "Instant camera upload leaf scans powered by advanced computer vision classifiers." },
    { icon: ShieldCheck, title: "Government Schemes Finder", desc: "Audits and recommends state subsidies and schemes tailored to your farm location size." },
  ];

  const faqs = [
    { q: "How accurate is the disease prediction model?", a: "The crop leaf classifier is built on pre-trained computer vision datasets, matching crop pathologists with a 94% precision rate on standard early/late blight symptoms." },
    { q: "Is my farm profiles data secure?", a: "Absolutely. All transactions, chemical measurements, and coordinates are hashed and isolated inside a secure MongoDB vault." },
    { q: "Can I use it offline on the farm?", a: "The voice and text chat logs support local caching, and synchronization occurs automatically once cellular networks reconnect." }
  ];

  return (
    <div className="min-h-screen w-screen bg-[#F8FAF8] text-gray-900 overflow-y-auto">
      
      {/* 1. Navbar */}
      <header className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-3xl">🌱</span>
          <span className="font-extrabold text-2xl tracking-tight text-primary">AgriGenius AI</span>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/login')}
            className="text-xs font-bold text-gray-600 hover:text-primary px-4 py-2 transition-colors"
          >
            Sign In
          </button>
          <button 
            onClick={() => navigate('/register')}
            className="text-xs font-bold bg-primary hover:bg-primary-dark text-white px-5 py-2.5 rounded-xl transition-all shadow-md"
          >
            Get Started
          </button>
        </div>
      </header>

      {/* 2. Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="space-y-6"
        >
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider">
            <Sparkles size={14} />
            <span>Agriculture Revolutionized</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-black tracking-tight text-gray-900 leading-tight">
            AI-Powered <span className="text-primary">Farming</span> Companion
          </h1>
          <p className="text-sm text-gray-500 font-medium leading-relaxed">
            AgriGenius provides instant AI diagnostics, soil analysis, weather indicators mapping, and wholesale pricing. Specialized tools helping farmers improve yields and combat leaf blights.
          </p>
          <div className="flex gap-4">
            <button
              onClick={() => navigate('/register')}
              className="py-4 px-8 bg-primary hover:bg-primary-dark text-white rounded-2xl font-bold flex items-center gap-2 shadow-lg transition-all hover:scale-[1.01]"
            >
              Start Free Trial
              <ArrowRight size={18} />
            </button>
            <button
              onClick={() => navigate('/login')}
              className="py-4 px-8 bg-white border border-gray-200 text-gray-700 rounded-2xl font-bold transition-all hover:bg-gray-50"
            >
              Sign In
            </button>
          </div>
        </motion.div>

        {/* Animated illustration area */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex justify-center"
        >
          <div className="relative w-full max-w-md h-96 rounded-[40px] bg-gradient-to-br from-primary/10 to-primary/20 flex items-center justify-center border border-primary/20 overflow-hidden shadow-2xl">
            {/* Spinning decorative background */}
            <div className="absolute w-80 h-80 rounded-full border border-primary/10 animate-spin" style={{ animationDuration: '30s' }}></div>
            <div className="absolute w-60 h-60 rounded-full border-2 border-dashed border-primary/25 animate-spin" style={{ animationDuration: '15s' }}></div>
            
            <div className="z-10 text-center space-y-4">
              <span className="text-8xl block animate-bounce" style={{ animationDuration: '3s' }}>🌱</span>
              <div className="bg-white/90 backdrop-blur border border-primary/10 rounded-2xl p-4 shadow-xl text-left max-w-xs mx-auto">
                <p className="text-xs font-bold text-primary uppercase">Active Diagnosis</p>
                <p className="text-xs text-gray-600 mt-1 font-semibold">"Early Blight detected. Apply copper fungicides immediately."</p>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* 3. Features Section */}
      <section className="bg-white py-20 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <h2 className="text-3xl font-extrabold tracking-tight text-gray-900">Platform Features</h2>
            <p className="text-sm text-gray-500 font-medium leading-relaxed">
              Designed from the ground up for high productivity and simple accessibility on the field.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {features.map((f, idx) => {
              const Icon = f.icon;
              return (
                <div key={idx} className="p-6 rounded-3xl bg-[#F8FAF8] border border-gray-100 hover:border-primary/20 transition-all space-y-4 hover:scale-[1.01]">
                  <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <Icon size={20} />
                  </div>
                  <h3 className="font-extrabold text-sm text-gray-900">{f.title}</h3>
                  <p className="text-xs text-gray-500 leading-relaxed">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 4. FAQ Section */}
      <section className="max-w-4xl mx-auto px-6 py-20 space-y-12">
        <h2 className="text-3xl font-extrabold text-center tracking-tight">Frequently Asked Questions</h2>
        <div className="space-y-4">
          {faqs.map((faq, idx) => (
            <div key={idx} className="p-6 bg-white border border-gray-200 rounded-2xl">
              <h4 className="font-bold text-sm text-gray-900 mb-2">{faq.q}</h4>
              <p className="text-xs text-gray-500 leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 5. Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6 text-xs font-semibold">
          <div className="flex items-center gap-2">
            <span>🌱</span>
            <span className="text-white font-extrabold tracking-tight">AgriGenius AI</span>
          </div>
          <p>© 2026 AgriGenius AI. All rights reserved.</p>
          <div className="flex gap-4">
            <span className="hover:text-white cursor-pointer">Terms of Use</span>
            <span className="hover:text-white cursor-pointer">Privacy Policy</span>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default Landing;

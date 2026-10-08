import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, ShieldCheck, Mail, Lock, KeySquare } from 'lucide-react';
import Toast from '../components/common/Toast';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  // Forgot password & OTP states
  const [stage, setStage] = useState('login'); // 'login', 'forgot', 'otp'
  const [otpCode, setOtpCode] = useState('');
  const [toastMsg, setToastMsg] = useState('');
  const [showToast, setShowToast] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSubmitting(true);
    
    // Simulate login wrapper
    const res = await login(email, password);
    setSubmitting(false);
    
    if (res.success) {
      navigate('/dashboard');
    } else {
      setErrorMsg(res.error);
    }
  };

  const handleForgotSubmit = (e) => {
    e.preventDefault();
    setStage('otp');
    setToastMsg('OTP verification code dispatched to email!');
    setShowToast(true);
  };

  const handleOtpVerify = (e) => {
    e.preventDefault();
    if (otpCode.length === 6) {
      setToastMsg('Code verified! Redirecting to setup password...');
      setShowToast(true);
      setTimeout(() => {
        setStage('login');
      }, 2000);
    } else {
      setErrorMsg('Invalid code length. Please input a 6-digit OTP.');
    }
  };

  return (
    <div className="min-h-screen w-screen flex items-center justify-center bg-gradient-to-br from-green-950 via-[#0F172A] to-emerald-950 p-6 relative overflow-hidden">
      
      {/* Decorative background vectors */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-primary/10 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-secondary/10 blur-[120px] pointer-events-none"></div>

      <AnimatePresence mode="wait">
        
        {/* LOGIN STAGE */}
        {stage === 'login' && (
          <motion.div
            key="login"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="w-full max-w-md p-8 rounded-[32px] glass-panel bg-white/10 text-white border border-white/10 shadow-2xl relative z-10"
          >
            <div className="text-center mb-8">
              <span className="text-4xl">🌱</span>
              <h2 className="text-3xl font-extrabold tracking-tight mt-3">Welcome Back</h2>
              <p className="text-xs text-gray-400 mt-1.5 font-semibold">Access your AgriGenius farming dashboard</p>
            </div>

            {errorMsg && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-2xl text-xs font-semibold">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <label className="block text-[10px] font-extrabold uppercase tracking-wider text-gray-400">Email Address</label>
                <div className="relative flex items-center">
                  <Mail size={16} className="absolute left-4 text-gray-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="farmer@example.com"
                    className="w-full pl-11 pr-4 py-3 bg-white/5 dark:bg-dark-surface/30 border border-white/10 rounded-xl outline-none focus:border-primary text-xs transition-colors"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="block text-[10px] font-extrabold uppercase tracking-wider text-gray-400">Password</label>
                  <button 
                    type="button"
                    onClick={() => setStage('forgot')}
                    className="text-[10px] font-bold text-green-400 hover:underline"
                  >
                    Forgot?
                  </button>
                </div>
                <div className="relative flex items-center">
                  <Lock size={16} className="absolute left-4 text-gray-400" />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-11 pr-12 py-3 bg-white/5 dark:bg-dark-surface/30 border border-white/10 rounded-xl outline-none focus:border-primary text-xs transition-colors"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 text-gray-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-4 bg-primary hover:bg-primary-light text-white font-bold rounded-2xl transition-all shadow-lg shadow-primary/20 mt-4"
              >
                {submitting ? 'Authenticating...' : 'Sign In'}
              </button>
            </form>

            <div className="text-center mt-6 text-xs text-gray-400 font-semibold">
              New to AgriGenius?{' '}
              <Link to="/register" className="text-green-400 font-extrabold hover:underline">
                Create Account
              </Link>
            </div>
          </motion.div>
        )}

        {/* FORGOT PASSWORD STAGE */}
        {stage === 'forgot' && (
          <motion.div
            key="forgot"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="w-full max-w-md p-8 rounded-[32px] glass-panel bg-white/10 text-white border border-white/10 shadow-2xl relative z-10"
          >
            <div className="text-center mb-8">
              <span className="text-4xl">🔑</span>
              <h2 className="text-3xl font-extrabold tracking-tight mt-3">Reset Password</h2>
              <p className="text-xs text-gray-400 mt-1.5 font-semibold">Input your registered email to receive an OTP code</p>
            </div>

            <form onSubmit={handleForgotSubmit} className="space-y-5">
              <div className="space-y-2">
                <label className="block text-[10px] font-extrabold uppercase tracking-wider text-gray-400">Email Address</label>
                <div className="relative flex items-center">
                  <Mail size={16} className="absolute left-4 text-gray-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="farmer@example.com"
                    className="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl outline-none focus:border-primary text-xs"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-4 bg-primary text-white font-bold rounded-2xl transition-all shadow-lg mt-4"
              >
                Send Verification OTP
              </button>

              <button
                type="button"
                onClick={() => setStage('login')}
                className="w-full text-center text-xs font-semibold text-gray-400 hover:text-white"
              >
                Back to Sign In
              </button>
            </form>
          </motion.div>
        )}

        {/* OTP VERIFICATION STAGE */}
        {stage === 'otp' && (
          <motion.div
            key="otp"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="w-full max-w-md p-8 rounded-[32px] glass-panel bg-white/10 text-white border border-white/10 shadow-2xl relative z-10"
          >
            <div className="text-center mb-8">
              <span className="text-4xl">🛡️</span>
              <h2 className="text-3xl font-extrabold tracking-tight mt-3">Enter OTP Code</h2>
              <p className="text-xs text-gray-400 mt-1.5 font-semibold">We dispatched a 6-digit confirmation key to {email}</p>
            </div>

            <form onSubmit={handleOtpVerify} className="space-y-5">
              <div className="space-y-2">
                <label className="block text-[10px] font-extrabold uppercase tracking-wider text-gray-400">Security PIN Code</label>
                <div className="relative flex items-center">
                  <KeySquare size={16} className="absolute left-4 text-gray-400" />
                  <input
                    type="text"
                    required
                    maxLength={6}
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                    placeholder="123456"
                    className="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl outline-none focus:border-primary text-xs text-center tracking-widest font-bold"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-4 bg-primary text-white font-bold rounded-2xl transition-all shadow-lg mt-4"
              >
                Verify Code
              </button>

              <button
                type="button"
                onClick={() => setStage('forgot')}
                className="w-full text-center text-xs font-semibold text-gray-400 hover:text-white"
              >
                Resend Code
              </button>
            </form>
          </motion.div>
        )}

      </AnimatePresence>

      {/* Reusable Toast */}
      <Toast 
        show={showToast} 
        message={toastMsg} 
        type="success" 
        onClose={() => setShowToast(false)} 
      />

    </div>
  );
};

export default Login;

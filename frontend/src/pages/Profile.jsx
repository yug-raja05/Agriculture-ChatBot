import React, { useState, useEffect } from 'react';
import AppLayout from '../components/layout/AppLayout';
import { useAuth } from '../contexts/AuthContext';
import { User, Tractor, Activity, ShieldCheck, Award, MessageSquare, Flame } from 'lucide-react';
import Toast from '../components/common/Toast';

const Profile = () => {
  const { profile, createOrUpdateProfile, user } = useAuth();
  
  const [fullname, setFullname] = useState('');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [farmSize, setFarmSize] = useState('');
  const [primaryCrops, setPrimaryCrops] = useState('');
  
  // Soil chemistry parameters
  const [nitrogen, setNitrogen] = useState('');
  const [phosphorus, setPhosphorus] = useState('');
  const [potassium, setPotassium] = useState('');
  const [ph, setPh] = useState('');
  const [moisture, setMoisture] = useState('');

  const [saving, setSaving] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  // Dummy stats
  const stats = [
    { label: "AI Discussions", value: "32", icon: MessageSquare },
    { label: "Disease Scans", value: "8", icon: Activity },
    { label: "Active Crops", value: "2", icon: Tractor },
    { label: "Queries Streak", value: "5 days", icon: Flame }
  ];

  // Dummy achievements
  const badges = [
    { name: "Eco-Farmer", desc: "For utilizing organic composting recommendations.", icon: "🏅" },
    { name: "Leaf Protector", desc: "For running 5 successful disease scan assessments.", icon: "🛡️" },
    { name: "Soil Guardian", desc: "For submitting complete soil chemical profile data.", icon: "🧪" }
  ];

  useEffect(() => {
    if (profile) {
      setFullname(profile.fullname || '');
      setPhone(profile.phone || '');
      setLocation(profile.location || '');
      setFarmSize(profile.farm_size_hectares ? String(profile.farm_size_hectares) : '');
      setPrimaryCrops(profile.primary_crops ? profile.primary_crops.join(', ') : '');
      
      if (profile.soil_profile) {
        setNitrogen(String(profile.soil_profile.nitrogen || ''));
        setPhosphorus(String(profile.soil_profile.phosphorus || ''));
        setPotassium(String(profile.soil_profile.potassium || ''));
        setPh(String(profile.soil_profile.ph || ''));
        setMoisture(String(profile.soil_profile.moisture || ''));
      }
    }
  }, [profile]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setToastMsg('');

    const payload = {
      fullname,
      phone,
      location,
      farm_size_hectares: farmSize ? parseFloat(farmSize) : null,
      primary_crops: primaryCrops ? primaryCrops.split(',').map(c => c.trim()) : [],
      soil_profile: {
        nitrogen: nitrogen ? parseFloat(nitrogen) : null,
        phosphorus: phosphorus ? parseFloat(phosphorus) : null,
        potassium: potassium ? parseFloat(potassium) : null,
        ph: ph ? parseFloat(ph) : null,
        moisture: moisture ? parseFloat(moisture) : null,
      }
    };

    const isNew = !profile;
    const res = await createOrUpdateProfile(payload, isNew);
    setSaving(false);
    
    if (res.success) {
      setToastMsg("Profile details saved successfully!");
      setShowToast(true);
    } else {
      setToastMsg(res.error);
      setShowToast(true);
    }
  };

  return (
    <AppLayout>
      <div className="p-8 h-full overflow-y-auto space-y-8 pb-20 max-w-6xl">
        
        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight grad-text flex items-center gap-2">
            <User />
            Profile Workspace
          </h1>
          <p className="text-sm text-gray-500 font-medium mt-1">
            Manage your personal farm details, analyze platform activity, and track diagnostic milestones.
          </p>
        </div>

        {/* Stats Summary Rows */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((s, idx) => {
            const Icon = s.icon;
            return (
              <div key={idx} className="p-6 rounded-3xl border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-surface shadow-xs flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
                  <Icon size={18} />
                </div>
                <div>
                  <span className="text-[10px] text-gray-400 font-bold uppercase block">{s.label}</span>
                  <span className="text-lg font-black">{s.value}</span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Settings forms panels */}
          <div className="md:col-span-2 bg-white dark:bg-dark-surface p-6 border border-gray-200 dark:border-dark-border rounded-3xl space-y-6">
            <h3 className="font-extrabold text-sm border-b border-gray-100 dark:border-dark-border pb-3 text-gray-800 dark:text-white">Farm Specifications</h3>
            
            <form onSubmit={handleSave} className="space-y-6">
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-bold uppercase text-gray-400">Full Name</label>
                  <input
                    type="text"
                    required
                    value={fullname}
                    onChange={e => setFullname(e.target.value)}
                    className="w-full px-4 py-2.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none"
                    placeholder="John Doe"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-bold uppercase text-gray-400">Contact Number</label>
                  <input
                    type="text"
                    value={phone}
                    onChange={e => setPhone(e.target.value)}
                    className="w-full px-4 py-2.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none"
                    placeholder="+1 234 567 890"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-bold uppercase text-gray-400">Regional Location</label>
                  <input
                    type="text"
                    value={location}
                    onChange={e => setLocation(e.target.value)}
                    className="w-full px-4 py-2.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none"
                    placeholder="District, State"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-bold uppercase text-gray-400">Farm Size (Hectares)</label>
                  <input
                    type="number"
                    step="any"
                    value={farmSize}
                    onChange={e => setFarmSize(e.target.value)}
                    className="w-full px-4 py-2.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none"
                    placeholder="10"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold uppercase text-gray-400">Primary Crops (comma separated)</label>
                <input
                  type="text"
                  value={primaryCrops}
                  onChange={e => setPrimaryCrops(e.target.value)}
                  className="w-full px-4 py-2.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none"
                  placeholder="Wheat, Maize, Rice"
                />
              </div>

              <h3 className="font-extrabold text-sm border-b border-gray-100 dark:border-dark-border pb-3 pt-4 text-gray-800 dark:text-white">Soil Chemistry Parameters</h3>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                <div className="space-y-1">
                  <label className="block text-[9px] font-bold uppercase text-gray-400">Nitrogen</label>
                  <input type="number" value={nitrogen} onChange={e => setNitrogen(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none" placeholder="N" />
                </div>
                <div className="space-y-1">
                  <label className="block text-[9px] font-bold uppercase text-gray-400">Phosphorus</label>
                  <input type="number" value={phosphorus} onChange={e => setPhosphorus(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none" placeholder="P" />
                </div>
                <div className="space-y-1">
                  <label className="block text-[9px] font-bold uppercase text-gray-400">Potassium</label>
                  <input type="number" value={potassium} onChange={e => setPotassium(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none" placeholder="K" />
                </div>
                <div className="space-y-1">
                  <label className="block text-[9px] font-bold uppercase text-gray-400">Soil pH</label>
                  <input type="number" step="any" value={ph} onChange={e => setPh(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none" placeholder="pH" />
                </div>
                <div className="space-y-1">
                  <label className="block text-[9px] font-bold uppercase text-gray-400">Moisture (%)</label>
                  <input type="number" value={moisture} onChange={e => setMoisture(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none" placeholder="%" />
                </div>
              </div>

              <button
                type="submit"
                disabled={saving}
                className="py-3 px-6 bg-primary hover:bg-primary-light text-white font-bold rounded-2xl transition-all shadow-md mt-4"
              >
                {saving ? 'Saving Profile...' : 'Save Farming Profile'}
              </button>

            </form>
          </div>

          {/* Badges achievements Columns */}
          <div className="bg-white dark:bg-dark-surface p-6 border border-gray-200 dark:border-dark-border rounded-3xl space-y-4 shadow-xs">
            <h3 className="font-extrabold text-sm text-gray-800 dark:text-white flex items-center gap-2">
              <Award size={16} className="text-accent-gold" />
              Farmer Achievements
            </h3>
            
            <div className="space-y-4">
              {badges.map((b, idx) => (
                <div key={idx} className="flex gap-3.5 p-3.5 bg-gray-50 dark:bg-dark-bg/60 border border-gray-100 dark:border-dark-border rounded-2xl">
                  <span className="text-3xl shrink-0">{b.icon}</span>
                  <div>
                    <h4 className="font-bold text-xs text-gray-800 dark:text-gray-200">{b.name}</h4>
                    <p className="text-[10px] text-gray-400 mt-1 leading-relaxed">{b.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

      <Toast 
        show={showToast} 
        message={toastMsg} 
        type="success" 
        onClose={() => setShowToast(false)} 
      />

    </AppLayout>
  );
};

export default Profile;

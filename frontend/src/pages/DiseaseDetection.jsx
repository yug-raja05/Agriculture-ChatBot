import React, { useState } from 'react';
import AppLayout from '../components/layout/AppLayout';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, UploadCloud, Camera, Eye, Trash2, ShieldCheck, HeartHandshake, CheckCircle } from 'lucide-react';
import Toast from '../components/common/Toast';

const DiseaseDetection = () => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState(null);
  const [showToast, setShowToast] = useState(false);

  // Dummy history database
  const [history, setHistory] = useState([
    { id: 1, crop: "Wheat", diagnosis: "Powdery Mildew", date: "2026-07-12", conf: 0.89, status: "Treated" },
    { id: 2, crop: "Tomato", diagnosis: "Late Blight", date: "2026-07-08", conf: 0.94, status: "Treated" }
  ]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedImage(URL.createObjectURL(file));
      triggerDiagnosis();
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(URL.createObjectURL(file));
      triggerDiagnosis();
    }
  };

  const triggerDiagnosis = () => {
    setLoading(true);
    setDiagnosis(null);
    
    setTimeout(() => {
      setLoading(false);
      setDiagnosis({
        crop: "Tomato",
        disease: "Early Blight (Alternaria solani)",
        confidence: 0.95,
        remedy: [
          "Prune lower infected foliage to suppress spore spread.",
          "Apply liquid copper fungicide weekly during wet periods.",
          "Maintain wider row spacing to facilitate swift leaf drying."
        ],
        medicines: ["Copper Fungicide", "Chlorothalonil spray"]
      });
      
      // Update history audit trail
      setHistory(prev => [
        { id: Date.now(), crop: "Tomato", diagnosis: "Early Blight", date: new Date().toISOString().split('T')[0], conf: 0.95, status: "Detected" },
        ...prev
      ]);
      setShowToast(true);
    }, 1800);
  };

  return (
    <AppLayout>
      <div className="p-8 h-full overflow-y-auto space-y-8 pb-20 max-w-6xl">
        
        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight grad-text flex items-center gap-2">
            <Activity />
            Leaf Disease Detection
          </h1>
          <p className="text-sm text-gray-500 font-medium mt-1">
            Upload leaves photo scans or drag files to trigger neural-network diagnostic checks.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* File Upload / Camera Simulator pane */}
          <div className="md:col-span-2 bg-white dark:bg-dark-surface p-6 border border-gray-200 dark:border-dark-border rounded-3xl space-y-6">
            <h3 className="font-extrabold text-sm border-b border-gray-100 dark:border-dark-border pb-3 text-gray-800 dark:text-white">Leaf Image Upload</h3>

            {!selectedImage ? (
              <div 
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                className={`w-full h-72 rounded-3xl border-2 border-dashed flex flex-col items-center justify-center p-6 transition-all ${
                  dragActive ? 'border-primary bg-primary/5' : 'border-gray-200 dark:border-dark-border hover:border-primary bg-gray-50/50 dark:bg-dark-bg/30'
                }`}
              >
                <UploadCloud size={44} className="text-gray-350 mb-3" />
                <p className="text-xs font-bold text-gray-600 dark:text-gray-300">Drag leaf image here, or select files</p>
                <p className="text-[10px] text-gray-400 mt-1">Supports JPG, PNG file formats up to 5MB</p>
                
                <input 
                  type="file" 
                  onChange={handleFileChange} 
                  className="hidden" 
                  id="leafFileInput" 
                  accept="image/*"
                />
                <label 
                  htmlFor="leafFileInput" 
                  className="mt-4 px-4 py-2 bg-white dark:bg-dark-bg text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-dark-border rounded-xl text-xs font-bold shadow-sm hover:bg-gray-50 cursor-pointer"
                >
                  Browse Files
                </label>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative w-full h-72 rounded-3xl overflow-hidden border border-gray-200 dark:border-dark-border">
                  <img src={selectedImage} className="w-full h-full object-cover" alt="Selected Leaf Scan" />
                  <button 
                    onClick={() => { setSelectedImage(null); setDiagnosis(null); }}
                    className="absolute top-4 right-4 p-2 bg-black/60 hover:bg-black text-white rounded-xl transition-all"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                
                {!diagnosis && !loading && (
                  <button
                    onClick={triggerDiagnosis}
                    className="w-full py-3 bg-primary hover:bg-primary-light text-white font-bold rounded-2xl transition-all shadow-md"
                  >
                    Diagnose Leaf Disease
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Predictions, remedies and treatments widgets */}
          <div className="space-y-6">
            <AnimatePresence mode="wait">
              
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="p-6 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-3xl text-center space-y-4 h-64 flex flex-col items-center justify-center"
                >
                  <span className="text-4xl animate-spin">🌱</span>
                  <p className="text-xs text-gray-400 font-bold">Diagnosing leaf spore patterns...</p>
                </motion.div>
              )}

              {!loading && !diagnosis && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="p-6 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-3xl text-center space-y-2 h-64 flex flex-col items-center justify-center text-gray-450"
                >
                  <Activity size={36} className="text-gray-300 animate-pulse" />
                  <p className="text-xs font-semibold">Ready for diagnosis</p>
                  <p className="text-[10px] max-w-xs text-gray-400">Load a leaf image to generate confidence reports and remedies.</p>
                </motion.div>
              )}

              {!loading && diagnosis && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-4"
                >
                  {/* Results Card */}
                  <div className="p-6 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-3xl space-y-4">
                    <h3 className="font-extrabold text-sm text-gray-800 dark:text-white flex items-center gap-1.5">
                      <CheckCircle size={16} className="text-primary" />
                      Neural Network Assessment
                    </h3>

                    <div className="space-y-3.5">
                      <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-500 rounded-2xl">
                        <span className="text-[10px] uppercase font-bold tracking-wider block">Diagnosis</span>
                        <span className="text-sm font-extrabold block mt-0.5">{diagnosis.disease}</span>
                      </div>

                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px] text-gray-400 font-bold uppercase">
                          <span>Classifier Accuracy</span>
                          <span>{Math.round(diagnosis.confidence * 100)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-dark-bg h-1.5 rounded-full overflow-hidden">
                          <div className="bg-red-500 h-full" style={{ width: `${diagnosis.confidence * 100}%` }}></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Treatments remedies list */}
                  <div className="p-6 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-3xl space-y-3">
                    <h4 className="font-bold text-xs text-gray-800 dark:text-white">Recommended Remediation</h4>
                    <ul className="list-disc pl-4 text-[11px] text-gray-500 space-y-2.5 leading-relaxed">
                      {diagnosis.remedy.map((r, idx) => (
                        <li key={idx}>{r}</li>
                      ))}
                    </ul>
                  </div>

                </motion.div>
              )}

            </AnimatePresence>
          </div>

        </div>

        {/* History Audit Trails Table */}
        <div className="bg-white dark:bg-dark-surface p-6 border border-gray-200 dark:border-dark-border rounded-3xl space-y-4">
          <h3 className="font-extrabold text-sm text-gray-800 dark:text-white">Recent Leaf Assessments History</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-semibold text-gray-500">
              <thead className="bg-gray-50 dark:bg-dark-bg text-gray-400 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="p-3">Crop</th>
                  <th className="p-3">Diagnosis</th>
                  <th className="p-3">Tested Date</th>
                  <th className="p-3">Confidence</th>
                  <th className="p-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-dark-border">
                {history.map(item => (
                  <tr key={item.id} className="hover:bg-gray-50/50 dark:hover:bg-dark-bg/25">
                    <td className="p-3 text-gray-800 dark:text-gray-200 font-bold">{item.crop}</td>
                    <td className="p-3">{item.diagnosis}</td>
                    <td className="p-3 text-gray-400">{item.date}</td>
                    <td className="p-3 text-primary dark:text-green-400">{Math.round(item.conf * 100)}%</td>
                    <td className="p-3 text-right">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        item.status === 'Treated' ? 'bg-primary/10 text-primary' : 'bg-red-500/10 text-red-500'
                      }`}>
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <Toast 
        show={showToast} 
        message="Neural classification check complete!" 
        type="success" 
        onClose={() => setShowToast(false)} 
      />

    </AppLayout>
  );
};

export default DiseaseDetection;

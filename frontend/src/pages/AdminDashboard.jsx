import React, { useState } from 'react';
import AppLayout from '../components/layout/AppLayout';
import { motion } from 'framer-motion';
import { ShieldCheck, Users, BookOpen, Database, Activity, FilePlus, Search, Download } from 'lucide-react';
import Toast from '../components/common/Toast';

const AdminDashboard = () => {
  const [showToast, setShowToast] = useState(false);
  const [toastMsg, setToastMsg] = useState('');
  const [pdfFile, setPdfFile] = useState('');

  const stats = [
    { label: "Registered Farmers", value: "1,204", icon: Users },
    { label: "RAG PDFs Indexed", value: "48", icon: BookOpen },
    { label: "Chroma Collections", value: "3", icon: Database },
    { label: "Model Checks/sec", value: "24.5", icon: Activity }
  ];

  // Dummy farmer records database
  const farmers = [
    { name: "John Doe", email: "john@valleyfarm.com", size: "12 ha", location: "District A", joined: "2026-06-12" },
    { name: "Marcus Aurelius", email: "marcus@romeagri.it", size: "45 ha", location: "District B", joined: "2026-05-18" },
    { name: "Suresh Patel", email: "suresh@gujaratfarm.in", size: "8 ha", location: "District C", joined: "2026-07-02" }
  ];

  const handlePdfUpload = (e) => {
    e.preventDefault();
    if (pdfFile) {
      setToastMsg(`Document: ${pdfFile} uploaded and chunk-indexed into Chroma Cloud!`);
      setShowToast(true);
      setPdfFile('');
    }
  };

  return (
    <AppLayout>
      <div className="p-8 h-full overflow-y-auto space-y-8 pb-20 max-w-6xl">
        
        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight grad-text flex items-center gap-2">
            <ShieldCheck />
            Admin Operations Portal
          </h1>
          <p className="text-sm text-gray-500 font-medium mt-1">
            Audit farmer profiles registration, manage vector database PDF uploads, and inspect LLM loads.
          </p>
        </div>

        {/* Admin stats */}
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

        {/* Farmer management & RAG document uploads */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Farmer lists */}
          <div className="md:col-span-2 bg-white dark:bg-dark-surface p-6 border border-gray-200 dark:border-dark-border rounded-3xl space-y-4">
            <h3 className="font-extrabold text-sm text-gray-800 dark:text-white">Registered Farmers Index</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-semibold text-gray-500">
                <thead className="bg-gray-50 dark:bg-dark-bg text-gray-400 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="p-3">Farmer</th>
                    <th className="p-3">Email Address</th>
                    <th className="p-3">Farm Area</th>
                    <th className="p-3">Joined Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-dark-border">
                  {farmers.map((f, idx) => (
                    <tr key={idx} className="hover:bg-gray-50/50 dark:hover:bg-dark-bg/25">
                      <td className="p-3 text-gray-800 dark:text-gray-200 font-bold">{f.name}</td>
                      <td className="p-3 text-gray-400">{f.email}</td>
                      <td className="p-3">{f.size}</td>
                      <td className="p-3 text-primary dark:text-green-400">{f.joined}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* RAG PDF Manager */}
          <div className="bg-white dark:bg-dark-surface p-6 border border-gray-200 dark:border-dark-border rounded-3xl space-y-4">
            <h3 className="font-extrabold text-sm text-gray-800 dark:text-white flex items-center gap-2">
              <FilePlus size={16} className="text-primary" />
              RAG PDF Indexer
            </h3>
            
            <form onSubmit={handlePdfUpload} className="space-y-4">
              <div className="space-y-1">
                <label className="block text-[10px] font-bold uppercase text-gray-400">Knowledge Guide Name</label>
                <input
                  type="text"
                  required
                  value={pdfFile}
                  onChange={e => setPdfFile(e.target.value)}
                  placeholder="Wheat_Rust_Cure_Guide"
                  className="w-full px-4 py-2.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl text-xs outline-none"
                />
              </div>

              <div className="border border-dashed border-gray-200 dark:border-dark-border rounded-2xl p-4 text-center bg-gray-50/50 text-[10px] text-gray-400 font-medium">
                Drag PDF document here to slice & index
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-primary hover:bg-primary-light text-white font-bold rounded-xl text-xs shadow-md"
              >
                Upload and Segment Guide
              </button>
            </form>
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

export default AdminDashboard;

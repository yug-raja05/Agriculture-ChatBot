import React, { useState } from 'react';
import AppLayout from '../components/layout/AppLayout';
import { motion } from 'framer-motion';
import { Landmark, Search, Bookmark, Download, Filter, Eye, X } from 'lucide-react';
import Modal from '../components/common/Modal';
import Toast from '../components/common/Toast';

const GovernmentSchemes = () => {
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [bookmarkedIds, setBookmarkedIds] = useState([1]);

  // Details Modal states
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  const schemes = [
    {
      id: 1,
      title: "PM-KISAN Subsidies Scheme",
      category: "Financial Support",
      desc: "Direct financial payout of $80 annually in three equal installments to small scale farming families.",
      benefits: "$80 Direct Benefit Payout per annum, divided into three cycles.",
      eligibility: "Landholding farmer families with cultivable land holdings in rural zones."
    },
    {
      id: 2,
      title: "Crop Insurance Program (PMFBY)",
      category: "Insurance",
      desc: "Yield damage safeguards for natural calamities, pests, and leaf disease outbreaks.",
      benefits: "Minimal premium rates (1.5% to 2%) with quick claim settlements.",
      eligibility: "Farmers growing notified crops in notified areas during crop seasons."
    },
    {
      id: 3,
      title: "Organic Fertilizer Development",
      category: "Subsidies",
      desc: "Subsidized compost fertilizers distribution networks for organic soil builders.",
      benefits: "50% rebate on purchase of certified vermicompost bins and organic blocks.",
      eligibility: "Registered organic farmers or groups converting to organic certifications."
    }
  ];

  const toggleBookmark = (id, e) => {
    e.stopPropagation();
    setBookmarkedIds(prev =>
      prev.includes(id) ? prev.filter(bId => bId !== id) : [...prev, id]
    );
    setToastMsg(bookmarkedIds.includes(id) ? "Bookmark removed." : "Scheme bookmarked successfully!");
    setShowToast(true);
  };

  const handleDownload = (title, e) => {
    e.stopPropagation();
    setToastMsg(`Downloading brochure: ${title}.pdf`);
    setShowToast(true);
  };

  const filteredSchemes = schemes.filter(s => {
    const matchesSearch = s.title.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === 'All' || s.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <AppLayout>
      <div className="p-8 h-full overflow-y-auto space-y-8 pb-20 max-w-6xl">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight grad-text flex items-center gap-2">
              <Landmark />
              Government Schemes
            </h1>
            <p className="text-sm text-gray-500 font-medium mt-1">
              Federal subsidies, seed allocations, and disaster compensation programs tracker.
            </p>
          </div>

          {/* Search & Filter */}
          <div className="flex gap-3">
            <div className="w-60 relative flex items-center bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-2xl px-4 py-2 shadow-xs">
              <Search size={16} className="text-gray-400 mr-2 shrink-0" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search programs..."
                className="bg-transparent border-none outline-none text-xs w-full"
              />
            </div>

            <select
              value={categoryFilter}
              onChange={e => setCategoryFilter(e.target.value)}
              className="px-4 py-2 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-2xl text-xs font-bold outline-none cursor-pointer"
            >
              <option>All</option>
              <option>Financial Support</option>
              <option>Insurance</option>
              <option>Subsidies</option>
            </select>
          </div>
        </div>

        {/* Schemes list Cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {filteredSchemes.map(s => {
            const isBookmarked = bookmarkedIds.includes(s.id);
            return (
              <div
                key={s.id}
                onClick={() => setSelectedScheme(s)}
                className="p-6 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-3xl space-y-4 hover:border-primary/20 hover:scale-[1.01] transition-all cursor-pointer flex flex-col justify-between h-64 shadow-xs"
              >
                <div className="space-y-2">
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] font-extrabold uppercase bg-primary/10 text-primary dark:bg-primary/20 dark:text-green-400 px-2 py-0.5 rounded-md">
                      {s.category}
                    </span>
                    <div className="flex items-center gap-1">
                      <button onClick={(e) => toggleBookmark(s.id, e)} className={isBookmarked ? "text-primary" : "text-gray-300"}>
                        <Bookmark size={14} fill={isBookmarked ? 'currentColor' : 'none'} />
                      </button>
                    </div>
                  </div>
                  <h3 className="font-extrabold text-xs text-gray-800 dark:text-white truncate">{s.title}</h3>
                  <p className="text-[11px] text-gray-400 leading-relaxed line-clamp-3">{s.desc}</p>
                </div>

                <div className="flex justify-between items-center pt-3 border-t border-gray-100 dark:border-dark-border">
                  <span className="text-[10px] text-gray-400 font-bold flex items-center gap-1">
                    <Eye size={12} />
                    View Details
                  </span>
                  <button
                    onClick={(e) => handleDownload(s.title, e)}
                    className="p-2 bg-gray-100 dark:bg-dark-bg text-gray-500 rounded-xl hover:bg-primary/10 hover:text-primary transition-all"
                    title="Download Brochure"
                  >
                    <Download size={12} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

      </div>

      {/* Details Modal */}
      <Modal show={!!selectedScheme} title={selectedScheme?.title || ""} onClose={() => setSelectedScheme(null)}>
        {selectedScheme && (
          <div className="space-y-5">
            <div>
              <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Benefit Provisions</span>
              <p className="text-xs text-gray-700 dark:text-gray-300 mt-1 leading-relaxed">{selectedScheme.benefits}</p>
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Eligible Beneficiaries</span>
              <p className="text-xs text-gray-700 dark:text-gray-300 mt-1 leading-relaxed">{selectedScheme.eligibility}</p>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-gray-100 dark:border-dark-border">
              <button onClick={() => setSelectedScheme(null)} className="px-4 py-2 bg-gray-100 text-gray-500 rounded-xl text-xs font-bold">Close Drawer</button>
              <button
                onClick={(e) => { handleDownload(selectedScheme.title, e); setSelectedScheme(null); }}
                className="px-4 py-2 bg-primary text-white rounded-xl text-xs font-bold shadow-md flex items-center gap-1"
              >
                <Download size={12} />
                Download PDF
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Reusable Toast */}
      <Toast
        show={showToast}
        message={toastMsg}
        type="success"
        onClose={() => setShowToast(false)}
      />

    </AppLayout>
  );
};

export default GovernmentSchemes;

import React from 'react';
import { motion } from 'framer-motion';
import { Bot, User, CloudSun, Activity, ShoppingCart, Tractor, ThumbsUp, ThumbsDown, Copy, Share2, Download } from 'lucide-react';

// Sub-component to render Weather Advisor outputs
const WeatherWidget = ({ data, parentMessage }) => {
  // 1. Safely unwrap data.output whether it is a string, object, or nested result
  let rawOutput = data?.output !== undefined ? data.output : data;
  if (typeof rawOutput === 'string') {
    try {
      rawOutput = JSON.parse(rawOutput);
    } catch (e) {}
  }
  let result = rawOutput?.result || rawOutput?.data || rawOutput;
  if (typeof result === 'string') {
    try {
      result = JSON.parse(result);
    } catch (e) {}
  }
  if (result && typeof result === 'object' && result.result) {
    result = result.result;
  }

  // Safe number parser
  const parseNum = (val) => {
    if (val === undefined || val === null) return undefined;
    const num = parseFloat(String(val).replace(/[^0-9.-]/g, ''));
    return isNaN(num) ? undefined : num;
  };

  // Extract metrics from tool data
  let rawTemp = parseNum(result?.temperature ?? result?.temp ?? result?.temp_c ?? result?.temperature_2m);
  let rawHumidity = parseNum(result?.humidity ?? result?.relative_humidity_2m ?? result?.humidity_percentage);
  let rawRain = parseNum(result?.rain_probability ?? result?.daily_chance_of_rain ?? result?.precipitation_probability_max ?? result?.rainfall_probability);
  if (rawRain !== undefined && rawRain <= 1 && rawRain > 0) {
    rawRain = rawRain * 100;
  }

  let location = result?.location || data?.parameters?.location || null;

  // 2. Intelligent fallback from parentMessage.content if metrics were missing from the tool log
  if (parentMessage?.content) {
    if (rawTemp === undefined) {
      const tempMatch = parentMessage.content.match(/(?:Temperature|Temp)[*:\s]+[*]*([0-9.]+)\s*°?C/i);
      if (tempMatch) rawTemp = parseFloat(tempMatch[1]);
    }
    if (rawHumidity === undefined) {
      const humMatch = parentMessage.content.match(/(?:Humidity)[*:\s]+[*]*([0-9.]+)\s*%/i);
      if (humMatch) rawHumidity = parseFloat(humMatch[1]);
    }
    if (rawRain === undefined) {
      const rainMatch = parentMessage.content.match(/(?:Rainfall Probability|Rain Prob|Rain)[*:\s]+[*]*([0-9.]+)\s*%/i);
      if (rainMatch) rawRain = parseFloat(rainMatch[1]);
    }
    if (!location || ["today", "tomorrow", "local area", "unknown location"].includes(location.toLowerCase())) {
      const locMatch = parentMessage.content.match(/Advisory for\s+([^\n*#]+)/i);
      if (locMatch && locMatch[1].trim()) {
        location = locMatch[1].trim();
      }
    }
  }

  // Sanitize location name
  if (!location || ["today", "tomorrow", "unknown location"].includes(location.toLowerCase())) {
    location = "Local Area";
  }

  // Default fallbacks if completely unavailable
  const tempDisplay = rawTemp !== undefined ? `${Math.round(rawTemp)}°C` : "27°C";
  const humidityDisplay = rawHumidity !== undefined ? `${Math.round(rawHumidity)}%` : "65%";
  const rainDisplay = rawRain !== undefined ? `${Math.round(rawRain)}%` : "20%";

  const weatherCond = result?.weather_condition || result?.weather_description || "Partly Cloudy";

  return (
    <div className="mt-3 p-4 rounded-2xl bg-sky-50 dark:bg-sky-950/20 border border-sky-200 dark:border-sky-850 flex flex-col gap-3">
      <div className="flex items-center justify-between text-sky-700 dark:text-sky-400 font-semibold">
        <div className="flex items-center gap-2 text-sm">
          <CloudSun size={18} />
          <h4>Weather Metrics ({location})</h4>
        </div>
        {weatherCond && (
          <span className="text-xs bg-sky-100 dark:bg-sky-900/50 text-sky-800 dark:text-sky-300 px-2.5 py-0.5 rounded-full font-semibold">
            {weatherCond}
          </span>
        )}
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-white dark:bg-dark-surface p-3 rounded-xl text-center border border-sky-100 dark:border-sky-900/40 shadow-sm">
          <p className="text-[11px] text-gray-500 dark:text-gray-400 font-semibold uppercase tracking-wider">Temp</p>
          <p className="text-xl font-extrabold text-sky-900 dark:text-sky-200 mt-0.5">{tempDisplay}</p>
        </div>
        <div className="bg-white dark:bg-dark-surface p-3 rounded-xl text-center border border-sky-100 dark:border-sky-900/40 shadow-sm">
          <p className="text-[11px] text-gray-500 dark:text-gray-400 font-semibold uppercase tracking-wider">Humidity</p>
          <p className="text-xl font-extrabold text-sky-900 dark:text-sky-200 mt-0.5">{humidityDisplay}</p>
        </div>
        <div className="bg-white dark:bg-dark-surface p-3 rounded-xl text-center border border-sky-100 dark:border-sky-900/40 shadow-sm">
          <p className="text-[11px] text-gray-500 dark:text-gray-400 font-semibold uppercase tracking-wider">Rain Prob</p>
          <p className="text-xl font-extrabold text-sky-900 dark:text-sky-200 mt-0.5">{rainDisplay}</p>
        </div>
      </div>
      {result?.warning && (
        <p className="text-xs text-sky-800 dark:text-sky-300 mt-1 italic font-medium">{result.warning}</p>
      )}
    </div>
  );
};

// Sub-component to render Disease Detector outputs
const DiseaseWidget = ({ data }) => {
  let rawOutput = data?.output !== undefined ? data.output : data;
  if (typeof rawOutput === 'string') {
    try { rawOutput = JSON.parse(rawOutput); } catch (e) {}
  }
  let result = rawOutput?.result || rawOutput?.data || rawOutput;
  if (typeof result === 'string') {
    try { result = JSON.parse(result); } catch (e) {}
  }
  if (result?.result) result = result.result;
  if (!result || (!result.diagnosis && !result.disease_name)) return null;

  const diagnosisName = result.diagnosis || result.disease_name || "Leaf Blight";
  const confidence = result.confidence !== undefined ? Math.round(result.confidence * 100) : 92;

  return (
    <div className="mt-3 p-4 rounded-2xl bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-850 flex flex-col gap-2">
      <div className="flex items-center gap-2 text-red-700 dark:text-red-400 font-semibold">
        <Activity size={18} />
        <h4>Plant Health Diagnosis</h4>
      </div>
      <div className="mt-1">
        <span className="text-xs uppercase bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300 px-2.5 py-1 rounded-full font-bold">
          {diagnosisName} ({confidence}% confidence)
        </span>
      </div>
      <div className="mt-2 text-xs text-red-800 dark:text-red-300 space-y-1.5">
        <p className="font-semibold text-gray-700 dark:text-gray-200">Recommended Treatment:</p>
        <ul className="list-disc pl-4 space-y-0.5">
          {result.treatment?.map((t, idx) => <li key={idx}>{t}</li>) || (
            <li>Apply organic Neem Oil spray (3ml/L) and ensure optimal canopy ventilation.</li>
          )}
        </ul>
      </div>
    </div>
  );
};

// Sub-component to render Crop Recommender outputs
const CropWidget = ({ data }) => {
  let rawOutput = data?.output !== undefined ? data.output : data;
  if (typeof rawOutput === 'string') {
    try { rawOutput = JSON.parse(rawOutput); } catch (e) {}
  }
  let result = rawOutput?.result || rawOutput?.data || rawOutput;
  if (typeof result === 'string') {
    try { result = JSON.parse(result); } catch (e) {}
  }
  if (result?.result) result = result.result;
  if (!result || !result.recommended_crops) return null;

  return (
    <div className="mt-3 p-4 rounded-2xl bg-green-50 dark:bg-green-950/10 border border-green-200 dark:border-green-850 flex flex-col gap-2">
      <div className="flex items-center gap-2 text-green-700 dark:text-green-400 font-semibold">
        <Tractor size={18} />
        <h4>Crop & Soil Recommendations</h4>
      </div>
      <div className="mt-1 space-y-1">
        <p className="text-xs text-gray-500 font-semibold mb-1">Recommended Crops:</p>
        <div className="flex flex-wrap gap-2">
          {result.recommended_crops?.map((c, idx) => (
            <div key={idx} className="bg-white dark:bg-dark-surface border border-green-100 dark:border-green-900/40 px-3 py-1.5 rounded-xl flex items-center gap-2">
              <span className="text-sm font-bold text-green-700 dark:text-green-400">{c.crop}</span>
              <span className="text-[10px] bg-green-100 dark:bg-green-950/50 px-1.5 py-0.5 rounded text-green-700 dark:text-green-400">
                {Math.round(c.confidence * 100)}%
              </span>
            </div>
          ))}
        </div>
      </div>
      {result.fertilizer_advice && (
        <p className="text-xs text-green-800 dark:text-green-300 mt-2 font-medium">
          <strong>Advice:</strong> {result.fertilizer_advice}
        </p>
      )}
    </div>
  );
};

// Sub-component to render Market Price outputs
const MarketWidget = ({ data }) => {
  let rawOutput = data?.output !== undefined ? data.output : data;
  if (typeof rawOutput === 'string') {
    try { rawOutput = JSON.parse(rawOutput); } catch (e) {}
  }
  let result = rawOutput?.result || rawOutput?.data || rawOutput;
  if (typeof result === 'string') {
    try { result = JSON.parse(result); } catch (e) {}
  }
  if (result?.result) result = result.result;
  if (!result) return null;

  const rawPrice = result.modal_price_per_quintal || result.average_wholesale_price_inr_quintal || result.average_wholesale_price_usd_ton || result.average_wholesale_price || 2500;
  const numPrice = Number(rawPrice);
  const formattedPrice = !isNaN(numPrice) ? numPrice.toLocaleString('en-IN') : rawPrice;
  const unitStr = result.unit || "/quintal";

  return (
    <div className="mt-3 p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/15 border border-amber-200 dark:border-amber-850 flex flex-col gap-2">
      <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 font-semibold">
        <ShoppingCart size={18} />
        <h4>Market Valuation ({result.crop || 'Agricultural Produce'})</h4>
      </div>
      <div className="mt-1 flex items-baseline gap-4">
        <div>
          <span className="text-xs text-gray-500 block">Avg Price</span>
          <span className="text-xl font-extrabold text-amber-800 dark:text-amber-400">₹{formattedPrice}{unitStr}</span>
        </div>
        <div>
          <span className="text-xs text-gray-500 block">Weekly Trend</span>
          <span className="text-sm font-bold uppercase text-green-600">{result.weekly_trend || 'STABLE'}</span>
        </div>
      </div>
      {result.recommended_sales_strategy && (
        <p className="text-xs text-amber-900 dark:text-amber-300 mt-2 font-medium bg-white dark:bg-dark-surface/40 p-2 rounded-xl border border-amber-100 dark:border-amber-900/20">
          <strong>Strategy:</strong> {result.recommended_sales_strategy}
        </p>
      )}
    </div>
  );
};

const MessageItem = ({ message }) => {
  const isBot = message.sender === 'assistant';

  // Tool log renderer dispatcher
  const renderToolLog = (log) => {
    switch (log.tool_name) {
      case 'weather_advisor':
        return <WeatherWidget key={log.tool_name} data={log} parentMessage={message} />;
      case 'plant_disease_detector':
        return <DiseaseWidget key={log.tool_name} data={log} />;
      case 'crop_recommender':
        return <CropWidget key={log.tool_name} data={log} />;
      case 'market_price_assistant':
        return <MarketWidget key={log.tool_name} data={log} />;
      default:
        return (
          <div key={log.tool_name} className="mt-2 p-2 text-xs bg-gray-100 dark:bg-dark-surface rounded-xl border border-gray-200 dark:border-dark-border">
            Executing: <strong>{log.tool_name}</strong>...
          </div>
        );
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-4 p-4 ${isBot ? 'bg-transparent' : 'bg-primary/5 dark:bg-primary/5 rounded-2xl'}`}
    >
      {/* Sender Icon */}
      <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-sm ${isBot
          ? 'bg-primary text-white'
          : 'bg-secondary text-white'
        }`}>
        {isBot ? <Bot size={20} /> : <User size={20} />}
      </div>

      {/* Message content panel */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-bold">{isBot ? 'AgriGenius Advisor' : 'Farmer'}</span>
          <span className="text-[10px] text-gray-400">
            {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        {/* Main Text Content */}
        <div className="text-sm leading-relaxed text-gray-800 dark:text-gray-200 space-y-1">
          {(() => {
            if (!message.content) return null;
            return message.content.split('\n').map((line, lineIdx) => {
              let cleanLine = line.replace(/^###\s*/, '').replace(/^-\s*\*\*/, '• ').replace(/^-\s*/, '• ');
              const parts = cleanLine.split(/(\*\*.*?\*\*)/g);

              const isHeader = line.startsWith('###');
              return (
                <div key={lineIdx} className={isHeader ? "font-extrabold text-base text-primary dark:text-green-400 mt-2 mb-1" : "min-h-[1.25rem]"}>
                  {parts.map((part, idx) => {
                    if (part.startsWith('**') && part.endsWith('**')) {
                      return (
                        <strong key={idx} className="font-extrabold text-gray-900 dark:text-white">
                          {part.slice(2, -2)}
                        </strong>
                      );
                    }
                    return <span key={idx}>{part}</span>;
                  })}
                </div>
              );
            });
          })()}
        </div>

        {/* Dynamic Tool Visualizations */}
        {isBot && (
          <div className="mt-1 space-y-2">
            {message.tool_calls && message.tool_calls.map(renderToolLog)}
            {(!message.tool_calls || !message.tool_calls.some(l => l.tool_name === 'weather_advisor')) &&
             (message.content?.includes("Live Weather") || message.content?.includes("Weather Forecast") || message.content?.includes("Weather Metrics")) && (
              <WeatherWidget data={{}} parentMessage={message} />
            )}
          </div>
        )}

        {/* Message Action Controls (Like, Dislike, Copy, Share, Export) */}
        {isBot && (
          <div className="flex items-center gap-1.5 mt-3 pt-2.5 border-t border-gray-100 dark:border-dark-border text-gray-400 shrink-0">
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-dark-surface hover:text-gray-600 dark:hover:text-gray-250 rounded-xl transition-all" title="Like response">
              <ThumbsUp size={13} />
            </button>
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-dark-surface hover:text-gray-600 dark:hover:text-gray-250 rounded-xl transition-all" title="Dislike response">
              <ThumbsDown size={13} />
            </button>
            <button
              onClick={() => navigator.clipboard.writeText(message.content)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-dark-surface hover:text-gray-600 dark:hover:text-gray-250 rounded-xl transition-all"
              title="Copy to clipboard"
            >
              <Copy size={13} />
            </button>
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-dark-surface hover:text-gray-600 dark:hover:text-gray-250 rounded-xl transition-all" title="Share with others">
              <Share2 size={13} />
            </button>
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-dark-surface hover:text-gray-600 dark:hover:text-gray-250 rounded-xl transition-all" title="Export as PDF/TXT">
              <Download size={13} />
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default MessageItem;

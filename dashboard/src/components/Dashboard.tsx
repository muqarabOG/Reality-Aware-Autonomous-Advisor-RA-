import React, { useState, useEffect } from 'react';
import {
    Activity,
    Shield,
    Cpu,
    Eye,
    AlertTriangle,
    Terminal,
    Zap,
    Box,
    BrainCircuit,
    RefreshCw,
    Navigation
} from 'lucide-react';
import {
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import NavigationGrid from './NavigationGrid';

const Dashboard = () => {
    const [telemetry, setTelemetry] = useState<any>(null);
    const [history, setHistory] = useState<any[]>([]);
    const [logs, setLogs] = useState<string[]>([]);
    const [isResetting, setIsResetting] = useState(false);

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/ws/telemetry');
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (!data || !data.perception || !data.reasoning) return;

                setTelemetry(data);
                setHistory(prev => [...prev.slice(-20), {
                    time: new Date().toLocaleTimeString(),
                    safety: data.reasoning.safety_score ?? 0,
                    vibration: data.perception.sensor_data?.vibration ?? 0,
                    proximity: (data.perception.sensor_data?.proximity ?? 0) / 50
                }]);

                if (data.reasoning.logic_conclusions?.length > 0) {
                    setLogs(prev => [...data.reasoning.logic_conclusions, ...prev].slice(0, 10));
                }
            } catch (err) {
                console.error("Telemetry parse error", err);
            }
        };
        return () => ws.close();
    }, []);

    const handleResetSafety = async () => {
        setIsResetting(true);
        try {
            await fetch('http://localhost:8000/reset_safety', { method: 'POST' });
        } catch (e) {
            console.error("Reset failed", e);
        }
        setTimeout(() => setIsResetting(false), 2000);
    };

    const handleSetGoal = async (x: number, y: number) => {
        try {
            await fetch('http://localhost:8000/set_goal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ x, y })
            });
        } catch (err) {
            console.error("Failed to set goal:", err);
        }
    };

    if (!telemetry) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center text-cyan-500">
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                >
                    <Cpu size={48} />
                </motion.div>
                <span className="ml-4 text-xl font-mono animate-pulse">CONNECTING TO RA³ BRAIN...</span>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-6 font-mono">
            {/* Header */}
            <header className="flex justify-between items-center mb-8 border-b border-cyan-900 pb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-cyan-500/10 rounded-lg text-cyan-400 border border-cyan-500/20">
                        <BrainCircuit size={32} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tighter text-cyan-400">RA³ ADVISOR <span className="text-xs font-normal border border-cyan-500/50 px-1 rounded ml-2">v0.1.0-ALPHA</span></h1>
                        <p className="text-xs text-slate-500 lowercase">reality-aware autonomous advisor</p>
                    </div>
                </div>
                <div className="flex gap-4">
                    <button
                        disabled={isResetting}
                        onClick={handleResetSafety}
                        className={`flex items-center gap-2 px-3 py-1 border rounded-lg transition-all text-xs font-bold ${isResetting ? 'bg-green-500/20 border-green-500/50 text-green-500' : 'bg-red-500/20 border-red-500/50 text-red-500 hover:bg-red-500/30'
                            }`}
                    >
                        <RefreshCw size={14} className={isResetting ? 'animate-spin' : ''} />
                        {isResetting ? 'RESETTING...' : 'RESET SAFETY'}
                    </button>
                    <div className="text-right">
                        <div className="text-xs text-slate-500">SYSTEM STATUS</div>
                        <div className="text-sm text-green-400 flex items-center gap-1">
                            <Zap size={14} /> ACTIVE / {telemetry.feedback_loop_status}
                        </div>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-12 gap-6">
                {/* Left Column: Perception & Entities */}
                <div className="col-span-12 lg:col-span-4 space-y-6">
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 backdrop-blur-sm">
                        <div className="flex items-center gap-2 mb-4 text-cyan-400">
                            <Eye size={18} />
                            <h2 className="text-sm font-bold uppercase tracking-wider">Perception Feed</h2>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-slate-950 p-3 rounded border border-slate-800">
                                <span className="text-xs text-slate-500 block mb-1">PROXIMITY</span>
                                <span className={`text-2xl font-bold ${telemetry.perception.sensor_data.proximity < 10 ? 'text-red-500' : 'text-cyan-400'}`}>
                                    {telemetry.perception.sensor_data.proximity.toFixed(1)}m
                                </span>
                            </div>
                            <div className="bg-slate-950 p-3 rounded border border-slate-800">
                                <span className="text-xs text-slate-500 block mb-1">VIBRATION</span>
                                <span className={`text-2xl font-bold ${telemetry.perception.sensor_data.vibration > 0.8 ? 'text-orange-500' : 'text-cyan-400'}`}>
                                    {(telemetry.perception.sensor_data.vibration * 100).toFixed(0)}%
                                </span>
                            </div>
                        </div>

                        <div className="mt-4 p-3 bg-cyan-950/20 border border-cyan-500/20 rounded shadow-inner">
                            <h3 className="text-[10px] text-cyan-500 mb-1 font-bold uppercase">Visual Logic Interpretation (Path G)</h3>
                            <p className="text-[11px] text-slate-300 leading-relaxed italic">
                                "{telemetry.scene_description || "Analyzing environment..."}"
                            </p>
                        </div>

                        <div className="mt-4">
                            <h3 className="text-xs text-slate-500 mb-2">DETECTED ENTITIES</h3>
                            <div className="space-y-2 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
                                {telemetry.perception.entities?.map((ent: any, idx: number) => (
                                    <div key={idx} className="flex justify-between items-center bg-slate-800/30 p-2 rounded text-xs border border-slate-700/50">
                                        <span className="flex items-center gap-2 uppercase">
                                            <Box size={12} className="text-cyan-500" />
                                            {ent.label}
                                        </span>
                                        <span className="text-cyan-600">{(ent.confidence * 100).toFixed(0)}% CONF</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2 text-cyan-400">
                                <Terminal size={18} />
                                <h2 className="text-sm font-bold uppercase tracking-wider">Reasoning Logs</h2>
                            </div>
                            {telemetry.snapshot_captured && (
                                <span className="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded border border-cyan-500/50 animate-pulse">
                                    SNAPSHOT CAPTURED
                                </span>
                            )}
                        </div>
                        <div className="space-y-2 font-mono text-[10px] h-64 overflow-y-auto custom-scrollbar">
                            <AnimatePresence initial={false}>
                                {logs.map((log, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className={`p-2 rounded border-l-2 ${log.includes('CRITICAL') ? 'bg-red-500/10 border-red-500 text-red-400' :
                                            log.includes('ALERT') ? 'bg-orange-500/10 border-orange-500 text-orange-400' :
                                                'bg-slate-800/50 border-cyan-500 text-cyan-100'
                                            }`}
                                    >
                                        {log}
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>

                {/* Middle Column: Visualizations */}
                <div className="col-span-12 lg:col-span-8 space-y-6">
                    {/* Top Row: Mission Status */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
                            <div className="flex justify-between items-start">
                                <span className="text-xs text-slate-500 font-bold uppercase">Safety Score</span>
                                <Shield className={telemetry.reasoning.safety_score < 0.6 ? 'text-red-500' : 'text-green-500'} size={20} />
                            </div>
                            <div className="mt-2">
                                <div className="text-3xl font-bold">{(telemetry.reasoning.safety_score * 100).toFixed(0)}%</div>
                                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2">
                                    <div
                                        className={`h-full rounded-full transition-all duration-500 ${telemetry.reasoning.safety_score < 0.6 ? 'bg-red-500' : 'bg-green-500'}`}
                                        style={{ width: `${telemetry.reasoning.safety_score * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 md:col-span-2 relative overflow-hidden">
                            <AnimatePresence>
                                {telemetry.reasoning.active_alerts?.map((alert: string, idx: number) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ y: -50, opacity: 0 }}
                                        animate={{ y: 0, opacity: 1 }}
                                        exit={{ y: -50, opacity: 0 }}
                                        className="absolute top-0 left-0 w-full bg-red-600 text-white text-center py-1 text-[10px] font-bold z-10"
                                    >
                                        <AlertTriangle size={10} className="inline mr-2" /> {alert}
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                            <div className="absolute top-0 right-0 p-4 opacity-10">
                                <Activity size={80} />
                            </div>
                            <span className="text-xs text-slate-500 font-bold uppercase">Current Decision</span>
                            <div className="mt-2">
                                <div className="text-xl font-bold text-cyan-400 flex items-center gap-2 uppercase">
                                    <span className="animate-pulse">●</span> {telemetry.decision.action_id.replace('_', ' ')}
                                </div>
                                <p className="text-xs text-slate-400 mt-1 uppercase tracking-tight line-clamp-2">
                                    {telemetry.decision.description}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Visualizations Area */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-[400px]">
                        {/* Tactical Radar */}
                        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 flex flex-col">
                            <div className="flex items-center gap-2 mb-4">
                                <Navigation size={18} className="text-cyan-400" />
                                <h2 className="text-sm font-bold uppercase tracking-wider text-cyan-100">Tactical Radar</h2>
                            </div>
                            <div className="flex-1 min-h-[300px]">
                                <NavigationGrid
                                    currentPos={telemetry.current_position || [0, 0]}
                                    goalPos={telemetry.goal_position || [0, 0]}
                                    onGridClick={handleSetGoal}
                                />
                            </div>
                        </div>

                        {/* Chart Area */}
                        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                            <div className="flex justify-between items-center mb-4">
                                <div className="flex items-center gap-2">
                                    <Activity size={18} className="text-cyan-400" />
                                    <h2 className="text-sm font-bold uppercase tracking-wider text-cyan-100">World Model</h2>
                                </div>
                                <div className="flex gap-2 text-[8px]">
                                    <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 bg-cyan-500 rounded-full"></span> SAF</span>
                                    <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 bg-orange-500 rounded-full"></span> VIB</span>
                                </div>
                            </div>
                            <ResponsiveContainer width="100%" height="90%">
                                <AreaChart data={history}>
                                    <defs>
                                        <linearGradient id="colorSafety" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                    <XAxis dataKey="time" hide />
                                    <YAxis stroke="#475569" fontSize={8} domain={[0, 1]} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', fontSize: '10px' }}
                                    />
                                    <Area type="monotone" dataKey="safety" stroke="#06b6d4" fillOpacity={1} fill="url(#colorSafety)" strokeWidth={2} />
                                    <Line type="monotone" dataKey="vibration" stroke="#f97316" dot={false} strokeWidth={2} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Footer / Meta */}
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 flex justify-between items-center text-[10px] text-slate-500 uppercase tracking-widest">
                        <span>Latent Logic: Neuro-Symbolic Inference Engine</span>
                        <div className="flex gap-4">
                            <span>FPS: 30</span>
                            <span>CPU: 12%</span>
                            <span>MEM: 512MB</span>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 4px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: #1e293b;
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: #334155;
                }
            `}</style>
        </div >
    );
};

export default Dashboard;

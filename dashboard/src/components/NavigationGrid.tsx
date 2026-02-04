import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { Target, Navigation } from 'lucide-react';

interface NavigationGridProps {
    currentPos: [number, number];
    goalPos: [number, number];
    onGridClick?: (x: number, y: number) => void;
}

const NavigationGrid: React.FC<NavigationGridProps> = ({ currentPos, goalPos, onGridClick }) => {
    const gridRef = useRef<HTMLDivElement>(null);

    // Coordinate mapping: -20 to 20 range -> 0 to 100%
    const scale = (val: number) => ((val + 20) / 40) * 100;

    const handleClick = (e: React.MouseEvent) => {
        if (!onGridClick || !gridRef.current) return;

        const rect = gridRef.current.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        // Translate pixel click to mission coordinates (-20 to 20)
        const gridX = (mouseX / rect.width) * 40 - 20;
        const gridY = (mouseY / rect.height) * 40 - 20;

        onGridClick(gridX, gridY);
    };

    return (
        <div
            ref={gridRef}
            onClick={handleClick}
            className="relative w-full h-full bg-slate-950 rounded-lg overflow-hidden border border-slate-800 shadow-inner cursor-crosshair group/grid"
        >
            {/* Grid Lines */}
            <div className="absolute inset-0 opacity-10"
                style={{
                    backgroundImage: 'linear-gradient(#06b6d4 1px, transparent 1px), linear-gradient(90deg, #06b6d4 1px, transparent 1px)',
                    backgroundSize: '20px 20px'
                }}
            />

            {/* Click Help */}
            <div className="absolute top-2 right-2 text-[8px] text-cyan-500/40 font-mono opacity-0 group-hover/grid:opacity-100 transition-opacity pointer-events-none">
                CLICK TO SET MISSION TARGET
            </div>

            {/* Center Axis */}
            <div className="absolute top-1/2 w-full h-[1px] bg-slate-800 opacity-50" />
            <div className="absolute left-1/2 h-full w-[1px] bg-slate-800 opacity-50" />

            {/* Goal Marker */}
            <motion.div
                className="absolute text-red-500 z-10"
                initial={false}
                animate={{
                    left: `${scale(goalPos[0])}%`,
                    top: `${scale(goalPos[1])}%`
                }}
                style={{ transform: 'translate(-50%, -50%)' }}
            >
                <div className="relative">
                    <Target size={24} className="animate-pulse" />
                    <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-[8px] font-bold bg-red-500/20 px-1 rounded whitespace-nowrap">MISSION TARGET</span>
                </div>
            </motion.div>

            {/* Agent Marker */}
            <motion.div
                className="absolute text-cyan-400 z-20"
                initial={false}
                animate={{
                    left: `${scale(currentPos[0])}%`,
                    top: `${scale(currentPos[1])}%`
                }}
                style={{ transform: 'translate(-50%, -50%)' }}
            >
                <div className="relative group">
                    <div className="absolute -inset-2 bg-cyan-500/20 blur-md rounded-full" />
                    <Navigation size={20} className="relative transition-transform" />
                    <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[8px] font-bold bg-cyan-500/20 px-1 rounded whitespace-nowrap uppercase">RA3 Agent</span>
                </div>
            </motion.div>

            {/* Scale Info */}
            <div className="absolute bottom-2 right-2 flex flex-col items-end gap-1 pointer-events-none">
                <div className="text-[10px] text-slate-500 font-mono">X: {currentPos[0].toFixed(2)} | Y: {currentPos[1].toFixed(2)}</div>
                <div className="text-[8px] text-slate-600 uppercase tracking-widest border-t border-slate-800 pt-1">Tactical Grid [40m x 40m]</div>
            </div>
        </div>
    );
};

export default NavigationGrid;

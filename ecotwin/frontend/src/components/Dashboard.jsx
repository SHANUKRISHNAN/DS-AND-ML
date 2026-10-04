// src/components/Dashboard.jsx
import { useState } from 'react';
import { useSimulationSocket } from '../hooks/useSimulationSocket';
import StatusBar from './StatusBar';
import LayerToggle from './LayerToggle';
import HeatmapLegend from './HeatmapLegend';
import StatCard from './StatCard';
import VehicleTooltip from './VehicleTooltip';

const VIEWBOX = "0 0 620 620";
const CELL_SIZE = 62;

function co2ToColor(co2, maxCo2) {
    const intensity = Math.min(co2 / maxCo2, 1);
    const alpha = intensity * 0.6;
    return `rgba(255, ${Math.floor(180 * (1 - intensity))}, 0, ${alpha})`;
}

export default function Dashboard() {
    const [showHeatmap, setShowHeatmap] = useState(true);
    const [showVehicles, setShowVehicles] = useState(true);
    const [hoveredVehicle, setHoveredVehicle] = useState(null);
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
    const [connected, setConnected] = useState(false);

    const { vehicles, heatmap, metricHistory } = useSimulationSocket(
        'ws://localhost:8000/ws/simulation',
        setConnected
    );

    const values = Object.values(heatmap || {});
    const maxCo2 = values.length ? Math.max(...values) : 1;
    const totalCo2 = vehicles.reduce((sum, v) => sum + v.co2, 0);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0d0d0d', fontFamily: 'system-ui, sans-serif' }}>
            <StatusBar connected={connected} stepCount={metricHistory.length} vehicleCount={vehicles.length} />

            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                    <div style={{ position: 'absolute', top: 12, left: 12, zIndex: 2, display: 'flex', gap: 8 }}>
                        <LayerToggle label="Heatmap" active={showHeatmap} onToggle={() => setShowHeatmap(!showHeatmap)} color="#ff8c00" />
                        <LayerToggle label="Vehicles" active={showVehicles} onToggle={() => setShowVehicles(!showVehicles)} color="#4fc3f7" />
                    </div>

                    {showHeatmap && (
                        <div style={{ position: 'absolute', bottom: 16, left: 12, zIndex: 2 }}>
                            <HeatmapLegend />
                        </div>
                    )}

                    <svg viewBox={VIEWBOX} style={{ width: '100%', height: '100%', background: '#111' }}>
                        {[0, 200, 400, 600].map((pos) => (
                            <g key={pos}>
                                <line x1={pos} y1="0" x2={pos} y2="600" stroke="#2a2a2a" strokeWidth="2" />
                                <line x1="0" y1={pos} x2="600" y2={pos} stroke="#2a2a2a" strokeWidth="2" />
                            </g>
                        ))}
                        {showHeatmap && Object.entries(heatmap || {}).map(([key, co2]) => {
                            const [cx, cy] = key.split(',').map(Number);
                            return (
                                <rect key={key} x={cx * CELL_SIZE} y={cy * CELL_SIZE}
                                    width={CELL_SIZE} height={CELL_SIZE} fill={co2ToColor(co2, maxCo2)} />
                            );
                        })}
                        {showVehicles && vehicles.map((v) => (
                            <circle
                                key={v.id} cx={v.x} cy={v.y} r="5" fill="#ff8c00"
                                style={{ transition: 'cx 0.15s linear, cy 0.15s linear', cursor: 'pointer' }}
                                onMouseEnter={(e) => { setHoveredVehicle(v); setMousePos({ x: e.clientX, y: e.clientY }); }}
                                onMouseLeave={() => setHoveredVehicle(null)}
                            />
                        ))}
                    </svg>

                    <VehicleTooltip vehicle={hoveredVehicle} x={mousePos.x} y={mousePos.y} />
                </div>

                <div style={{ width: 280, borderLeft: '1px solid #2a2a2a', padding: 16, display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                        <StatCard label="Total CO2" value={totalCo2.toFixed(0)} unit="mg/s" />
                        <StatCard label="Vehicles" value={vehicles.length} />
                    </div>
                </div>
            </div>
        </div>
    );
}
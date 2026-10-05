// src/components/HeatmapLegend.jsx
export default function HeatmapLegend() {
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#888' }}>
            <span>Low CO2</span>
            <div style={{
                width: 80, height: 8, borderRadius: 4,
                background: 'linear-gradient(90deg, rgba(255,180,0,0) 0%, rgba(255,90,0,0.6) 100%)',
            }} />
            <span>High CO2</span>
        </div>
    );
}
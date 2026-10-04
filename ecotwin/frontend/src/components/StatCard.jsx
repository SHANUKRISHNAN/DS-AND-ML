// src/components/StatCard.jsx
export default function StatCard({ label, value, unit, trend }) {
    return (
        <div style={{
            background: '#1a1a1a', border: '1px solid #2a2a2a', borderRadius: 8,
            padding: '12px 16px', minWidth: 110,
        }}>
            <div style={{ color: '#777', fontSize: 11, marginBottom: 4 }}>{label}</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
                <span style={{ color: '#eee', fontSize: 20, fontWeight: 600 }}>{value}</span>
                {unit && <span style={{ color: '#666', fontSize: 11 }}>{unit}</span>}
            </div>
            {trend != null && (
                <div style={{ color: trend >= 0 ? '#f87171' : '#4ade80', fontSize: 11, marginTop: 2 }}>
                    {trend >= 0 ? '▲' : '▼'} {Math.abs(trend).toFixed(1)}%
                </div>
            )}
        </div>
    );
}
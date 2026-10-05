// src/components/StatusBar.jsx
export default function StatusBar({ connected, stepCount, vehicleCount }) {
    return (
        <div style={{
            display: 'flex', alignItems: 'center', gap: 24,
            padding: '10px 20px', background: '#1a1a1a', borderBottom: '1px solid #2a2a2a',
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: connected ? '#4ade80' : '#f87171',
                    boxShadow: connected ? '0 0 6px #4ade80' : 'none',
                }} />
                <span style={{ color: '#aaa', fontSize: 13 }}>
                    {connected ? 'Live' : 'Disconnected'}
                </span>
            </div>
            <span style={{ color: '#666', fontSize: 13 }}>Simulation Step {stepCount}</span>
            <span style={{ color: '#666', fontSize: 13 }}>{vehicleCount} vehicles active</span>
        </div>
    );
}
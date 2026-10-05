// src/components/LayerToggle.jsx
export default function LayerToggle({ label, active, onToggle, color }) {
    return (
        <button
            onClick={onToggle}
            style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '6px 12px', borderRadius: 6, border: '1px solid #333',
                background: active ? '#2a2a2a' : 'transparent',
                color: active ? '#eee' : '#666', fontSize: 13, cursor: 'pointer',
            }}
        >
            <span style={{
                width: 10, height: 10, borderRadius: 3,
                background: active ? color : '#444',
            }} />
            {label}
        </button>
    );
}
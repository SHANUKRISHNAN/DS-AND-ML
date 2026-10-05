export default function VehicleTooltip({ vehicle, x, y }) {
    if (!vehicle) return null;
    return (
        <div style={{
            position: 'absolute', left: x + 12, top: y + 12,
            background: '#1a1a1a', border: '1px solid #333', borderRadius: 6,
            padding: '8px 12px', fontSize: 12, color: '#ccc', pointerEvents: 'none',
            boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
        }}>
            <div style={{ color: '#fff', fontWeight: 600, marginBottom: 2 }}>Vehicle {vehicle.id}</div>
            <div>CO2: {vehicle.co2.toFixed(1)} mg/s</div>
        </div>
    );
}

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function MetricCharts({ metricHistory }) {
    return (
        <div style={{ position: 'absolute', top: 10, right: 10, width: 320, background: 'rgba(20,20,20,0.85)', padding: 10, borderRadius: 8 }}>
            <p style={{ color: '#ccc', margin: '0 0 4px', fontSize: 12 }}>Total CO2 (live)</p>
            <ResponsiveContainer width="100%" height={100}>
                <LineChart data={metricHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="step" tick={false} />
                    <YAxis tick={{ fill: '#888', fontSize: 10 }} />
                    <Tooltip contentStyle={{ background: '#222', border: 'none' }} />
                    <Line type="monotone" dataKey="totalCo2" stroke="#ff8c00" dot={false} strokeWidth={2} />
                </LineChart>
            </ResponsiveContainer>

            <p style={{ color: '#ccc', margin: '8px 0 4px', fontSize: 12 }}>Active Vehicles</p>
            <ResponsiveContainer width="100%" height={100}>
                <LineChart data={metricHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="step" tick={false} />
                    <YAxis tick={{ fill: '#888', fontSize: 10 }} />
                    <Tooltip contentStyle={{ background: '#222', border: 'none' }} />
                    <Line type="monotone" dataKey="vehicleCount" stroke="#4fc3f7" dot={false} strokeWidth={2} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
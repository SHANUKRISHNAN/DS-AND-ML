const VIEWBOX = "0 0 620 620";

export default function GridMap() {
  return (
    <svg viewBox={VIEWBOX} style={{ width: '100vw', height: '100vh', background: '#111' }}>
      {[0, 200, 400, 600].map((pos) => (
        <g key={pos}>
          <line x1={pos} y1="0" x2={pos} y2="600" stroke="#333" strokeWidth="2" />
          <line x1="0" y1={pos} x2="600" y2={pos} stroke="#333" strokeWidth="2" />
        </g>
      ))}
    </svg>
  );
}
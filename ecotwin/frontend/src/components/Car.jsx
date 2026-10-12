export default function Car({ x, y, angle = 0, onMouseEnter, onMouseLeave }) {
    // SUMO's angle: 0 = north/up, clockwise. SVG rotate(): 0 = east/right,
    // clockwise. Offsetting by -90 aligns the car's drawn "front" (pointing
    // right by default) with SUMO's heading convention.
    const rotation = angle - 90;

    return (
        <g
            transform={`translate(${x}, ${y}) rotate(${rotation})`}
            style={{ transition: 'transform 0.15s linear', cursor: 'pointer' }}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
        >
            <rect x="-5" y="-3" width="10" height="6" rx="1.5" fill="#ff8c00" />
            <rect x="0" y="-2.2" width="3.5" height="4.4" rx="0.5" fill="#1a1a1a" opacity="0.6" />
        </g>
    );
}
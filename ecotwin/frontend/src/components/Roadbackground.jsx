const ROAD_POSITIONS = [0, 200, 400, 600];
const ROAD_WIDTH = 24;
const GRID_MAX = 620;

// Fixed, deterministic tree positions per block so they don't jitter on
// every re-render (Math.random() in render would reshuffle trees each frame).
const TREE_OFFSETS = [
    [30, 30], [160, 45], [90, 150], [40, 160], [150, 100],
];

function Tree({ x, y }) {
    return (
        <g transform={`translate(${x}, ${y})`}>
            <rect x="-2" y="4" width="4" height="10" fill="#4a3728" />
            <circle cx="0" cy="0" r="9" fill="#2d5a2d" />
            <circle cx="-4" cy="-3" r="6" fill="#336633" />
            <circle cx="4" cy="-3" r="6" fill="#336633" />
        </g>
    );
}

export default function RoadBackground() {
    const blockStarts = [0, 224, 424]; // between road positions, accounting for road width
    const blockSize = 176; // 200 - ROAD_WIDTH

    return (
        <g>
            {/* City blocks (greenery) */}
            {blockStarts.map((bx) =>
                blockStarts.map((by) => (
                    <g key={`${bx}-${by}`}>
                        <rect x={bx} y={by} width={blockSize} height={blockSize} fill="#16231a" />
                        {TREE_OFFSETS.map(([ox, oy], i) => (
                            <Tree key={i} x={bx + ox} y={by + oy} />
                        ))}
                    </g>
                ))
            )}

            {/* Roads (asphalt strips) */}
            {ROAD_POSITIONS.map((pos) => (
                <g key={`v-${pos}`}>
                    <rect x={pos - ROAD_WIDTH / 2} y="0" width={ROAD_WIDTH} height={GRID_MAX} fill="#3a3a3a" />
                    <line x1={pos} y1="0" x2={pos} y2={GRID_MAX} stroke="#888" strokeWidth="1.5" strokeDasharray="10,8" />
                </g>
            ))}
            {ROAD_POSITIONS.map((pos) => (
                <g key={`h-${pos}`}>
                    <rect x="0" y={pos - ROAD_WIDTH / 2} width={GRID_MAX} height={ROAD_WIDTH} fill="#3a3a3a" />
                    <line x1="0" y1={pos} x2={GRID_MAX} y2={pos} stroke="#888" strokeWidth="1.5" strokeDasharray="10,8" />
                </g>
            ))}
        </g>
    );
}
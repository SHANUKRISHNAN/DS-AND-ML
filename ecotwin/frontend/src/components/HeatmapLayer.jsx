// src/components/HeatmapLayer.jsx (new file)
const GRID_SIZE = 620;
const CELL_SIZE = 62;

function co2ToColor(co2, maxCo2) {
    // 0 = transparent, ramping through yellow to red as concentration rises
    const intensity = Math.min(co2 / maxCo2, 1);
    const alpha = intensity * 0.6;
    return `rgba(255, ${Math.floor(180 * (1 - intensity))}, 0, ${alpha})`;
}

export default function HeatmapLayer({ heatmap }) {
    const values = Object.values(heatmap || {});
    const maxCo2 = values.length ? Math.max(...values) : 1;

    return (
        <g>
            {Object.entries(heatmap || {}).map(([key, co2]) => {
                const [cx, cy] = key.split(',').map(Number);
                return (
                    <rect
                        key={key}
                        x={cx * CELL_SIZE}
                        y={cy * CELL_SIZE}
                        width={CELL_SIZE}
                        height={CELL_SIZE}
                        fill={co2ToColor(co2, maxCo2)}
                    />
                );
            })}
        </g>
    );
}
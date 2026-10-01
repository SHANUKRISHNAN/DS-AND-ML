// useSimulationSocket.js must now return both fields, not just vehicles:
import { useEffect, useState } from 'react';

export function useSimulationSocket(url) {
  const [data, setData] = useState({ vehicles: [], heatmap: {} });

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      setData({ vehicles: parsed.vehicles, heatmap: parsed.heatmap });
    };
    ws.onerror = () => console.error('Simulation socket error');
    return () => ws.close();
  }, [url]);

  return data;
}
// src/hooks/useSimulationSocket.js — extended to report connection status
import { useEffect, useState, useRef } from 'react';

const MAX_HISTORY_POINTS = 100;

export function useSimulationSocket(url, onConnectionChange) {
  const [data, setData] = useState({ vehicles: [], heatmap: {} });
  const [metricHistory, setMetricHistory] = useState([]);
  const stepCount = useRef(0);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => onConnectionChange?.(true);
    ws.onclose = () => onConnectionChange?.(false);
    ws.onerror = () => onConnectionChange?.(false);

    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      setData({ vehicles: parsed.vehicles, heatmap: parsed.heatmap || {} });

      const totalCo2 = parsed.vehicles.reduce((sum, v) => sum + v.co2, 0);
      stepCount.current += 1;

      setMetricHistory((prev) => {
        const next = [...prev, { step: stepCount.current, totalCo2, vehicleCount: parsed.vehicles.length }];
        return next.length > MAX_HISTORY_POINTS ? next.slice(-MAX_HISTORY_POINTS) : next;
      });
    };

    return () => ws.close();
  }, [url]);

  return { ...data, metricHistory };
}
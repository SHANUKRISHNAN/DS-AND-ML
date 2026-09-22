import { useEffect, useState } from 'react';

export function useSimulationSocket(url) {
  const [vehicles, setVehicles] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setVehicles(data.vehicles);
    };
    ws.onerror = () => console.error('Simulation socket error');
    return () => ws.close();
  }, [url]);

  return vehicles;
}

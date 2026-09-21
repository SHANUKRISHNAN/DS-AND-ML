import { useState } from "react";
import "./App.css";

function App() {
  const [vehicles, setVehicles] = useState(150);
  const [capacity, setCapacity] = useState(200);
  const [emission, setEmission] = useState(18);
  const refreshData = () => {
  setVehicles(150);
  setCapacity(200);
  setEmission(18);
};
  return (
    <div className="dashboard">
      <h1>EcoTwin Dashboard</h1>
      <h2>Urban Carbon Dispersion Monitoring System</h2>
      <button onClick={refreshData}>Refresh Data</button>

      <div className="cards">
        <div className="card">
          <h3>Traffic Monitoring</h3>
          <label>Vehicle Count:</label>
<input
  type="number"
  value={vehicles}
  onChange={(e) => setVehicles(Number(e.target.value))}
/>
          <p>Vehicles: {vehicles}</p>
          <p>Road Capacity: {capacity}</p>
          <label>Update Road Capacity:</label>
<input
  type="number"
  value={capacity}
  onChange={(e) => setCapacity(Number(e.target.value))}
/>
          <p className={vehicles / capacity >= 0.8 ? "high" : vehicles / capacity >= 0.5 ? "moderate" : "action"}>
  Traffic Level: {vehicles / capacity >= 0.8 ? "High" : vehicles / capacity >= 0.5 ? "Medium" : "Low"}
</p>
          <p>Traffic Density: {capacity > 0 ? Math.round((vehicles / capacity) * 100) : 0}%</p>
          <div className="progress-bar">
  <div className="progress-fill"></div>
</div>
        </div>

        <div className="card">
          <h3>Carbon Emission</h3>
          <p>Total Emission: {emission} kg</p>
          <label>Update Emission:</label>
<input
  type="number"
  value={emission}
  onChange={(e) => setEmission(Number(e.target.value))}
/>
          <p className={emission >= 25 ? "high" : emission >= 15 ? "moderate" : "action"}>
  Emission Level: {emission >= 25 ? "High" : emission >= 15 ? "Moderate" : "Low"}
</p>
          <div className="emission-bar">
  <div className="emission-fill"></div>
</div>
        </div>

        <div className="card">
          <h3>Traffic Optimization</h3>
          <p>Recommended Action:</p>
          <p className="action">
  {vehicles / capacity >= 0.8
    ? "Increase Green Signal Time"
    : vehicles / capacity >= 0.5
    ? "Optimize Traffic Flow"
    : "Maintain Current Signal Timing"}
</p>
        </div>
      </div>
    </div>
  );
}

export default App;
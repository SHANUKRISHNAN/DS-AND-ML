import { useState } from "react";
import "./App.css";

function App() {
  const [vehicles, setVehicles] = useState(150);
  return (
    <div className="dashboard">
      <h1>EcoTwin Dashboard</h1>
      <h2>Urban Carbon Dispersion Monitoring System</h2>

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
          <p>Road Capacity: 200</p>
          <p className="high">Traffic Level: High</p>
          <p>Traffic Density: {Math.round((vehicles / 200) * 100)}%</p>
          <div className="progress-bar">
  <div className="progress-fill"></div>
</div>
        </div>

        <div className="card">
          <h3>Carbon Emission</h3>
          <p>Total Emission: 18 kg</p>
          <p className="moderate">Emission Level: Moderate</p>
          <div className="emission-bar">
  <div className="emission-fill"></div>
</div>
        </div>

        <div className="card">
          <h3>Traffic Optimization</h3>
          <p>Recommended Action:</p>
          <p className="action">Increase Green Signal Time</p>
        </div>
      </div>
    </div>
  );
}

export default App;
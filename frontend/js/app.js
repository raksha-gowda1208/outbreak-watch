/**
 * OutbreakWatch Frontend Application
 * Interacts with FastAPI backend to render maps, Chart.js trends, and anomaly feeds.
 */

const API_BASE = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1") 
  ? "/api" 
  : "http://127.0.0.1:8000/api";

let map = null;
let markersLayer = null;
let trendChart = null;
let currentDistrict = "Pune";
let currentSyndrome = "SYN-ADD";
let applyDP = true;

document.addEventListener("DOMContentLoaded", () => {
  initClock();
  initMap();
  initChart();
  setupEventListeners();
  refreshAllData();
  
  // Refresh feed every 15 seconds
  setInterval(fetchAnomaliesAndKPIs, 15000);
});

function initClock() {
  const clockEl = document.getElementById("clock");
  function update() {
    const now = new Date();
    clockEl.innerText = now.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    }) + " IST";
  }
  update();
  setInterval(update, 1000);
}

function initMap() {
  // Center on Maharashtra
  map = L.map("map-container", {
    zoomControl: true,
    attributionControl: false
  }).setView([19.2, 75.0], 6.5);

  // CartoDB Dark Matter Tiles
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 18,
    subdomains: "abcd"
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
}

function initChart() {
  const ctx = document.getElementById("trendChart").getContext("2d");
  trendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Primary Care Consultations (DP Anonymized)",
          data: [],
          borderColor: "#2DD4BF", // Teal
          backgroundColor: "rgba(45, 212, 191, 0.15)",
          borderWidth: 2.5,
          tension: 0.3,
          fill: true,
          yAxisID: "y"
        },
        {
          label: "Pharmacy OTC Medication Sales (Lead Signal)",
          data: [],
          borderColor: "#FB923C", // Orange
          backgroundColor: "transparent",
          borderWidth: 2,
          borderDash: [4, 4],
          tension: 0.2,
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          labels: { color: "#94a3b8", font: { size: 11 } }
        },
        tooltip: {
          backgroundColor: "#0f172a",
          titleColor: "#f8fafc",
          bodyColor: "#cbd5e1",
          borderColor: "#334155",
          borderWidth: 1,
          padding: 10
        }
      },
      scales: {
        x: {
          grid: { color: "#1e293b" },
          ticks: { color: "#64748b", font: { size: 10 } }
        },
        y: {
          type: "linear",
          display: true,
          position: "left",
          grid: { color: "#1e293b" },
          ticks: { color: "#94a3b8", font: { size: 10 } },
          title: { display: true, text: "Consultations", color: "#64748b", font: { size: 10 } }
        },
        y1: {
          type: "linear",
          display: true,
          position: "right",
          grid: { drawOnChartArea: false },
          ticks: { color: "#fb923c", font: { size: 10 } },
          title: { display: true, text: "OTC Units Sold", color: "#fb923c", font: { size: 10 } }
        }
      }
    }
  });
}

function setupEventListeners() {
  document.getElementById("district-select").addEventListener("change", (e) => {
    currentDistrict = e.target.value;
    refreshTrends();
  });

  document.getElementById("syndrome-select").addEventListener("change", (e) => {
    currentSyndrome = e.target.value;
    refreshTrends();
    refreshMap();
  });
}

async function refreshAllData() {
  await Promise.all([
    refreshMap(),
    refreshTrends(),
    fetchAnomaliesAndKPIs()
  ]);
}

async function refreshMap() {
  try {
    const res = await fetch(`${API_BASE}/map/hotspots?syndrome_id=${currentSyndrome}`);
    if (!res.ok) return;
    const hotspots = await res.json();

    markersLayer.clearLayers();

    hotspots.forEach(spot => {
      const isCritical = spot.alert_level === "CRITICAL";
      const isElevated = spot.alert_level === "ELEVATED";

      const marker = L.circleMarker([spot.lat, spot.lon], {
        radius: spot.radius,
        fillColor: spot.color,
        color: "#ffffff",
        weight: 1.5,
        opacity: 0.9,
        fillOpacity: 0.75,
        className: isCritical ? "radar-critical" : ""
      });

      const popupContent = `
        <div class="text-xs p-1">
          <h4 class="font-bold text-sm text-white mb-1 flex items-center justify-between">
            <span>${spot.district_name}</span>
            <span class="px-1.5 py-0.5 rounded text-[10px] font-bold" style="background:${spot.color}33; color:${spot.color}">
              ${spot.alert_level}
            </span>
          </h4>
          <p class="text-slate-400 mb-1">Max Aberration: <strong class="text-white">Z = ${spot.max_z_score.toFixed(2)}</strong></p>
          <p class="text-slate-400">PHC Facilities: <strong class="text-white">${spot.phcs_count}</strong></p>
          ${spot.flagged_syndromes.length > 0 ? `
            <div class="mt-2 pt-1 border-t border-slate-700">
              <span class="text-rose-400 font-semibold">Active Flags:</span>
              <ul class="list-disc pl-4 mt-0.5 text-slate-300">
                ${spot.flagged_syndromes.map(s => `<li>${s}</li>`).join("")}
              </ul>
            </div>
          ` : ""}
        </div>
      `;

      marker.bindPopup(popupContent);
      marker.on("click", () => {
        document.getElementById("district-select").value = spot.district_name;
        currentDistrict = spot.district_name;
        refreshTrends();
      });

      markersLayer.addLayer(marker);
    });
  } catch (err) {
    console.error("Map fetch failed", err);
  }
}

async function refreshTrends() {
  try {
    const res = await fetch(`${API_BASE}/trends?district_name=${encodeURIComponent(currentDistrict)}&syndrome_id=${currentSyndrome}&apply_dp=${applyDP}`);
    if (!res.ok) return;
    const data = await res.json();

    // Update Chart
    const labels = data.series.map(r => r.date.slice(5)); // MM-DD
    const phcValues = data.series.map(r => r.display_phc_consultations);
    const otcValues = data.series.map(r => r.pharmacy_otc_sales);

    trendChart.data.labels = labels;
    trendChart.data.datasets[0].data = phcValues;
    trendChart.data.datasets[1].data = otcValues;
    trendChart.update();

    // Update Chart Title
    document.getElementById("chart-title").innerHTML = `
      <i class="fa-solid fa-chart-line text-teal-400 mr-2"></i>
      <span>${data.district_name}: ${data.syndrome_name} Trajectory</span>
    `;

    // Update Advisory Section
    updateAdvisory(data.analysis);
  } catch (err) {
    console.error("Trends fetch failed", err);
  }
}

function updateAdvisory(analysis) {
  if (!analysis) return;

  const badgeEl = document.getElementById("advisory-badge");
  const districtEl = document.getElementById("advisory-district");
  const zEl = document.getElementById("advisory-z");
  const recEl = document.getElementById("advisory-recommendation");
  const otcEl = document.getElementById("advisory-otc");
  const cusumEl = document.getElementById("advisory-cusum");

  badgeEl.innerText = analysis.alert_level;
  badgeEl.style.backgroundColor = `${analysis.color_code}33`;
  badgeEl.style.color = analysis.color_code;
  badgeEl.style.borderColor = `${analysis.color_code}66`;

  districtEl.innerText = `${analysis.district_name} (${analysis.syndrome_name})`;
  zEl.innerText = `EARS Z-Score: ${analysis.ears_c2?.z_score > 0 ? "+" : ""}${analysis.ears_c2?.z_score || 0}`;
  recEl.innerText = analysis.recommendation;

  if (analysis.otc_signal?.lead_indicator_detected) {
    otcEl.innerHTML = `<span class="text-amber-400 font-bold"><i class="fa-solid fa-arrow-trend-up mr-1"></i>Spike (+${analysis.otc_signal.otc_z_score}&sigma;)</span>`;
  } else {
    otcEl.innerHTML = `<span class="text-slate-400">Baseline (${analysis.otc_signal.otc_z_score}&sigma;)</span>`;
  }

  if (analysis.cusum?.is_alarm) {
    cusumEl.innerHTML = `<span class="text-rose-400 font-bold"><i class="fa-solid fa-bell mr-1"></i>Shift Alert</span>`;
  } else {
    cusumEl.innerHTML = `<span class="text-slate-400">Stable (S=${analysis.cusum?.cusum_value})</span>`;
  }
}

async function fetchAnomaliesAndKPIs() {
  try {
    const res = await fetch(`${API_BASE}/anomalies`);
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("kpi-anomalies").innerText = `${data.critical_count} Critical / ${data.elevated_count} Elevated`;
    document.getElementById("alerts-count-badge").innerText = `${data.total_active_anomalies} Active`;

    const listEl = document.getElementById("anomalies-list");
    listEl.innerHTML = "";

    if (data.anomalies.length === 0) {
      listEl.innerHTML = `<p class="text-xs text-slate-500 text-center py-4">No critical aberrations detected across monitored districts.</p>`;
      return;
    }

    data.anomalies.forEach(anom => {
      const isCrit = anom.alert_level === "CRITICAL";
      const card = document.createElement("div");
      card.className = "pt-2.5 cursor-pointer hover:bg-slate-800/40 p-2 rounded-lg transition";
      card.innerHTML = `
        <div class="flex items-center justify-between mb-1">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full ${isCrit ? "bg-red-500 animate-ping" : "bg-amber-500"}"></span>
            <span class="text-xs font-bold text-white">${anom.district_name}</span>
          </div>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded font-semibold" style="background:${anom.color_code}22; color:${anom.color_code}; border:1px solid ${anom.color_code}44">
            ${anom.alert_level} | Z=${anom.ears_c2.z_score}
          </span>
        </div>
        <p class="text-xs text-slate-300">${anom.syndrome_name}</p>
        <p class="text-[11px] text-slate-400 mt-1 line-clamp-2">${anom.recommendation}</p>
      `;

      card.addEventListener("click", () => {
        document.getElementById("district-select").value = anom.district_name;
        document.getElementById("syndrome-select").value = anom.syndrome_id;
        currentDistrict = anom.district_name;
        currentSyndrome = anom.syndrome_id;
        refreshTrends();
        refreshMap();
      });

      listEl.appendChild(card);
    });
  } catch (err) {
    console.error("Anomalies fetch failed", err);
  }
}

/**
 * OutbreakWatch Chaos Simulation & Privacy Controls
 */

document.addEventListener("DOMContentLoaded", () => {
  setupSimulationModal();
  setupPrivacyModal();
});

function setupSimulationModal() {
  const modal = document.getElementById("simulate-modal");
  const openBtn = document.getElementById("open-simulate-modal");
  const closeBtn = document.getElementById("close-simulate-modal");
  const cancelBtn = document.getElementById("cancel-sim-btn");
  const execBtn = document.getElementById("execute-sim-btn");
  const spikeSlider = document.getElementById("sim-spike");
  const spikeVal = document.getElementById("sim-spike-val");

  openBtn.addEventListener("click", () => modal.classList.remove("hidden"));
  closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
  cancelBtn.addEventListener("click", () => modal.classList.add("hidden"));

  const presetSelect = document.getElementById("sim-preset");
  const districtSelect = document.getElementById("sim-district");
  const syndromeSelect = document.getElementById("sim-syndrome");

  if (presetSelect) {
    presetSelect.addEventListener("change", (e) => {
      const val = e.target.value;
      if (val === "dengue") {
        districtSelect.value = "Pune";
        syndromeSelect.value = "SYN-VBD";
        spikeSlider.value = 320;
        spikeVal.innerText = "+320%";
      } else if (val === "cholera") {
        districtSelect.value = "Nashik";
        syndromeSelect.value = "SYN-ADD";
        spikeSlider.value = 420;
        spikeVal.innerText = "+420%";
      } else if (val === "flu") {
        districtSelect.value = "Nagpur";
        syndromeSelect.value = "SYN-ARI";
        spikeSlider.value = 260;
        spikeVal.innerText = "+260%";
      }
    });
  }

  spikeSlider.addEventListener("input", (e) => {
    spikeVal.innerText = `+${e.target.value}%`;
  });

  execBtn.addEventListener("click", async () => {
    const district = document.getElementById("sim-district").value;
    const syndrome = document.getElementById("sim-syndrome").value;
    const spike = parseInt(spikeSlider.value, 10);

    execBtn.disabled = true;
    execBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1"></i> Injecting...`;

    try {
      const res = await fetch(`${API_BASE}/simulate/inject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          district_name: district,
          syndrome_id: syndrome,
          spike_percentage: spike,
          days_duration: 3
        })
      });

      if (!res.ok) throw new Error("Injection failed");

      modal.classList.add("hidden");
      
      // Select the injected scenario in the UI to demonstrate
      document.getElementById("district-select").value = district;
      document.getElementById("syndrome-select").value = syndrome;
      currentDistrict = district;
      currentSyndrome = syndrome;

      // Force immediate refresh
      await refreshAllData();

      alert(`🚨 OUTBREAK SCENARIO INDUCED!\n\nInjected +${spike}% surge in ${district}.\nCDC EARS algorithm and GIS cluster map have updated in real time.`);
    } catch (err) {
      alert("Error injecting simulation: " + err.message);
    } finally {
      execBtn.disabled = false;
      execBtn.innerHTML = `<i class="fa-solid fa-radiation mr-1"></i> Inject Outbreak Scenario`;
    }
  });
}

function setupPrivacyModal() {
  const modal = document.getElementById("privacy-modal");
  const openBtn = document.getElementById("open-privacy-modal");
  const closeBtn = document.getElementById("close-privacy-modal");
  const applyBtn = document.getElementById("apply-privacy-btn");
  const epsSlider = document.getElementById("epsilon-slider");
  const epsVal = document.getElementById("epsilon-val");

  openBtn.addEventListener("click", () => modal.classList.remove("hidden"));
  closeBtn.addEventListener("click", () => modal.classList.add("hidden"));

  epsSlider.addEventListener("input", (e) => {
    epsVal.innerText = `\u03B5=${parseFloat(e.target.value).toFixed(1)}`;
  });

  applyBtn.addEventListener("click", async () => {
    const epsilon = parseFloat(epsSlider.value);
    try {
      const res = await fetch(`${API_BASE}/privacy/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          epsilon: epsilon,
          k_threshold: 5
        })
      });

      if (!res.ok) throw new Error("Privacy config failed");

      document.getElementById("privacy-badge").innerHTML = `
        <i class="fa-solid fa-shield-halved text-teal-400 mr-1"></i> Differential Privacy: &epsilon; = ${epsilon.toFixed(1)} (Active)
      `;

      modal.classList.add("hidden");
      await refreshTrends();
    } catch (err) {
      alert("Error configuring privacy: " + err.message);
    }
  });
}

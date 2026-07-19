/**
 * FanFlow AI — Staff Operations Dashboard Client
 *
 * Polls /api/crowd/status every 5 seconds for live crowd data.
 * Renders gate cards, incident feed, and AI recommendations.
 * All styling via class toggling — zero inline styles.
 */

(function () {
  "use strict";

  // ── DOM References ────────────────────────────────────────
  const stadiumSelect = document.getElementById("dash-stadium-select");
  const overallDensity = document.getElementById("overall-density");
  const overallStatusBadge = document.getElementById("overall-status-badge");
  const overallStatusText = document.getElementById("overall-status-text");
  const activeGates = document.getElementById("active-gates");
  const activeIncidentsCount = document.getElementById("active-incidents-count");
  const stadiumNameDisplay = document.getElementById("stadium-name-display");
  const stadiumCityDisplay = document.getElementById("stadium-city-display");
  const gatesGrid = document.getElementById("gates-grid");
  const incidentsFeed = document.getElementById("incidents-feed");
  const incidentsEmpty = document.getElementById("incidents-empty");
  const recommendationsFeed = document.getElementById("recommendations-feed");
  const recommendationsEmpty = document.getElementById("recommendations-empty");
  const wasteGrid = document.getElementById("waste-grid");
  const signageFeed = document.getElementById("signage-feed");
  const heatmapPanel = document.getElementById("heatmap-panel");
  const analyzeBtn = document.getElementById("analyze-btn");
  const lastUpdated = document.getElementById("last-updated");

  // Ops Chat
  const opsChatForm = document.getElementById("ops-chat-form");
  const opsChatInput = document.getElementById("ops-chat-input");
  const opsChatMessages = document.getElementById("ops-chat-messages");

  let currentStadium = "metlife";
  let pollInterval = null;

  // ── Stadium Loader ────────────────────────────────────────
  async function loadStadiums() {
    try {
      const res = await fetch("/api/stadiums");
      if (!res.ok) return;
      const stadiums = await res.json();
      stadiumSelect.innerHTML = "";
      stadiums.forEach(function (s) {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = s.name + " — " + s.city;
        stadiumSelect.appendChild(opt);
      });
      if (stadiums.length > 0) {
        currentStadium = stadiums[0].id;
        stadiumSelect.value = currentStadium;
      }
    } catch (err) {
      console.error("Failed to load stadiums:", err);
    }
  }

  // ── Crowd Status Polling ──────────────────────────────────
  async function fetchCrowdStatus() {
    try {
      const res = await fetch("/api/crowd/status?stadium_id=" + currentStadium);
      if (!res.ok) return;
      const data = await res.json();
      renderCrowdStatus(data);
    } catch (err) {
      console.error("Failed to fetch crowd status:", err);
    }
    // Fetch signage and heatmap in parallel (non-blocking)
    fetchSignage();
    fetchHeatmap();
  }

  function renderCrowdStatus(data) {
    // Overview cards
    overallDensity.textContent = data.overall_density_pct.toFixed(1) + "%";
    overallDensity.className = "overview-card__value overview-card__value--" + data.overall_status;

    overallStatusBadge.className = "badge badge--" + data.overall_status;
    overallStatusText.textContent = data.overall_status.toUpperCase();

    activeGates.textContent = data.gates.length;
    activeIncidentsCount.textContent = data.incidents.length;
    stadiumNameDisplay.textContent = data.stadium_name;

    // Last updated
    var time = new Date(data.last_updated);
    lastUpdated.textContent = "Updated: " + time.toLocaleTimeString();

    // Gate cards
    renderGates(data.gates);

    // Waste / Sustainability
    if (data.waste_levels && wasteGrid) {
      renderWaste(data.waste_levels);
    }

    // Incidents
    renderIncidents(data.incidents);
  }

  function renderGates(gates) {
    gatesGrid.innerHTML = "";
    gates.forEach(function (gate) {
      var card = document.createElement("article");
      card.className = "gate-card gate-card--" + gate.status;
      card.setAttribute("role", "listitem");
      card.setAttribute("aria-label", gate.name + ": " + gate.congestion_pct.toFixed(1) + "% congestion, status " + gate.status);

      card.innerHTML =
        '<div class="gate-card__header">' +
          '<span class="gate-card__name">' + escapeHtml(gate.name) + '</span>' +
          '<span class="badge badge--' + gate.status + '">' +
            '<span class="badge__dot" aria-hidden="true"></span>' +
            gate.status.toUpperCase() +
          '</span>' +
        '</div>' +
        '<div class="gate-card__zone">' + escapeHtml(gate.zone) + '</div>' +
        '<div class="gate-card__meter" role="progressbar" aria-valuenow="' + gate.congestion_pct.toFixed(0) + '" aria-valuemin="0" aria-valuemax="100" aria-label="Congestion level">' +
          '<div class="gate-card__meter-fill" style="width: ' + Math.min(gate.congestion_pct, 100).toFixed(0) + '%"></div>' +
        '</div>' +
        '<div class="gate-card__pct">' + gate.congestion_pct.toFixed(1) + '%</div>';

      gatesGrid.appendChild(card);
    });
  }

  function renderWaste(wasteLevels) {
    if (!wasteGrid) return;
    wasteGrid.innerHTML = "";
    Object.keys(wasteLevels).forEach(function (zone) {
      var pct = wasteLevels[zone];
      var status = pct >= 80 ? "red" : (pct >= 60 ? "yellow" : "green");
      
      var card = document.createElement("article");
      card.className = "gate-card gate-card--" + status;
      card.setAttribute("role", "listitem");
      card.setAttribute("aria-label", "Waste bin " + zone + ": " + pct.toFixed(1) + "% full");

      card.innerHTML =
        '<div class="gate-card__header">' +
          '<span class="gate-card__name">' + escapeHtml(zone) + '</span>' +
          '<span class="badge badge--' + status + '">' +
            '<span class="badge__dot" aria-hidden="true"></span>' +
            status.toUpperCase() +
          '</span>' +
        '</div>' +
        '<div class="gate-card__zone">Waste / Recycling</div>' +
        '<div class="gate-card__meter" role="progressbar" aria-valuenow="' + pct.toFixed(0) + '" aria-valuemin="0" aria-valuemax="100" aria-label="Fill level">' +
          '<div class="gate-card__meter-fill" style="width: ' + Math.min(pct, 100).toFixed(0) + '%"></div>' +
        '</div>' +
        '<div class="gate-card__pct">' + pct.toFixed(1) + '%</div>';

      wasteGrid.appendChild(card);
    });
  }

  function renderIncidents(incidents) {
    incidentsFeed.innerHTML = "";

    if (incidents.length === 0) {
      incidentsFeed.innerHTML =
        '<div class="empty-state">' +
          '<div class="empty-state__icon" aria-hidden="true">✅</div>' +
          '<p>No active incidents</p>' +
        '</div>';
      return;
    }

    // Sort by severity (critical first)
    var severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    incidents.sort(function (a, b) {
      return (severityOrder[a.severity] || 4) - (severityOrder[b.severity] || 4);
    });

    incidents.forEach(function (inc) {
      var item = document.createElement("article");
      item.className = "incident-item";
      item.setAttribute("role", "article");
      item.setAttribute("aria-label", inc.severity + " " + inc.type + " incident at " + inc.location);

      var time = new Date(inc.timestamp);
      var timeStr = time.toLocaleTimeString();

      item.innerHTML =
        '<div class="incident-item__header">' +
          '<span class="incident-item__type">' + escapeHtml(inc.type) + '</span>' +
          '<span class="incident-item__severity incident-item__severity--' + inc.severity + '">' +
            escapeHtml(inc.severity) +
          '</span>' +
        '</div>' +
        '<p class="incident-item__desc">' + escapeHtml(inc.description) + '</p>' +
        '<p class="incident-item__meta">' + escapeHtml(inc.location) + ' · ' + timeStr + '</p>';

      incidentsFeed.appendChild(item);
    });
  }

  // ── AI Analysis ───────────────────────────────────────────
  async function analyzeConditions() {
    analyzeBtn.disabled = true;
    analyzeBtn.classList.add("analyze-btn--loading");
    analyzeBtn.innerHTML = '<span aria-hidden="true">⏳</span> Analyzing...';

    try {
      const res = await fetch("/api/crowd/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stadium_id: currentStadium }),
      });

      if (!res.ok) {
        throw new Error("Analysis request failed");
      }

      const data = await res.json();
      renderRecommendations(data);
    } catch (err) {
      console.error("Analysis failed:", err);
      recommendationsFeed.innerHTML =
        '<div class="empty-state">' +
          '<div class="empty-state__icon" aria-hidden="true">⚠️</div>' +
          '<p>Analysis failed. Please try again.</p>' +
        '</div>';
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.classList.remove("analyze-btn--loading");
      analyzeBtn.innerHTML = '<span aria-hidden="true">🧠</span> Analyze Crowd Conditions';
    }
  }

  function renderRecommendations(data) {
    recommendationsFeed.innerHTML = "";

    // Analysis text
    if (data.analysis) {
      var analysisDiv = document.createElement("div");
      analysisDiv.className = "recommendation-item";
      analysisDiv.setAttribute("role", "article");
      analysisDiv.innerHTML =
        '<span class="recommendation-item__icon" aria-hidden="true">📊</span>' +
        '<span>' + escapeHtml(data.analysis) + '</span>';
      recommendationsFeed.appendChild(analysisDiv);
    }

    // Recommendations
    data.recommendations.forEach(function (rec, index) {
      var recDiv = document.createElement("div");
      recDiv.className = "recommendation-item";
      recDiv.setAttribute("role", "article");
      recDiv.setAttribute("aria-label", "Recommendation " + (index + 1));
      recDiv.innerHTML =
        '<span class="recommendation-item__icon" aria-hidden="true">💡</span>' +
        '<span>' + escapeHtml(rec) + '</span>';
      recommendationsFeed.appendChild(recDiv);
    });
  }

  // ── Utilities ─────────────────────────────────────────────
  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // ── Event Listeners ───────────────────────────────────────
  stadiumSelect.addEventListener("change", function () {
    currentStadium = stadiumSelect.value;
    // Clear recommendations on stadium change
    recommendationsFeed.innerHTML =
      '<div class="empty-state" id="recommendations-empty">' +
        '<div class="empty-state__icon" aria-hidden="true">💡</div>' +
        '<p>Click "Analyze" to generate AI-powered recommendations</p>' +
      '</div>';
    fetchCrowdStatus();
  });

  analyzeBtn.addEventListener("click", analyzeConditions);

  // ── Ops Chat ──────────────────────────────────────────────
  function addOpsChatMessage(text, role) {
    var msgDiv = document.createElement("div");
    msgDiv.className = "message message--" + role;
    msgDiv.innerHTML = '<div class="message__bubble">' + escapeHtml(text) + '</div>';
    opsChatMessages.appendChild(msgDiv);
    opsChatMessages.scrollTop = opsChatMessages.scrollHeight;
  }

  opsChatForm.addEventListener("submit", async function(e) {
    e.preventDefault();
    var msg = opsChatInput.value.trim();
    if (!msg) return;

    opsChatInput.value = "";
    opsChatInput.disabled = true;

    // Add user message
    addOpsChatMessage(msg, "user");

    try {
      const res = await fetch("/api/crowd/ops/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          stadium_id: currentStadium
        })
      });

      if (!res.ok) throw new Error("Chat request failed");
      const data = await res.json();
      
      // Add assistant response
      addOpsChatMessage(data.reply, "assistant");
    } catch (err) {
      console.error(err);
      addOpsChatMessage("Sorry, I am having trouble connecting to the network.", "assistant");
    } finally {
      opsChatInput.disabled = false;
      opsChatInput.focus();
    }
  });

  // Keyboard shortcut: R to refresh
  document.addEventListener("keydown", function (e) {
    if (e.key === "r" && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {
      fetchCrowdStatus();
    }
  });

  // ── Dynamic Signage ──────────────────────────────────────
  async function fetchSignage() {
    try {
      var res = await fetch("/api/crowd/signage?stadium_id=" + currentStadium);
      if (!res.ok) return;
      var signs = await res.json();
      renderSignage(signs);
    } catch (err) {
      console.error("Failed to fetch signage:", err);
    }
  }

  function renderSignage(signs) {
    if (!signageFeed) return;
    signageFeed.innerHTML = "";
    if (!signs || signs.length === 0) {
      signageFeed.innerHTML = '<div class="empty-state"><p>No signage data</p></div>';
      return;
    }
    signs.forEach(function (sign) {
      var item = document.createElement("article");
      item.className = "incident-item";
      item.setAttribute("role", "listitem");
      item.setAttribute("aria-label", "Signage for " + sign.board_location);
      var priClass = sign.priority === "high" ? "critical" : (sign.priority === "medium" ? "medium" : "low");
      item.innerHTML =
        '<div class="incident-item__header">' +
          '<span class="incident-item__type">' + escapeHtml(sign.board_location) + '</span>' +
          '<span class="incident-item__severity incident-item__severity--' + priClass + '">' +
            escapeHtml(sign.priority) +
          '</span>' +
        '</div>' +
        '<p class="incident-item__desc">' + escapeHtml(sign.message) + '</p>';
      signageFeed.appendChild(item);
    });
  }

  // ── Predictive Heatmap ───────────────────────────────────
  async function fetchHeatmap() {
    try {
      var res = await fetch("/api/crowd/heatmap/predict?stadium_id=" + currentStadium);
      if (!res.ok) return;
      var data = await res.json();
      renderHeatmap(data);
    } catch (err) {
      console.error("Failed to fetch heatmap:", err);
    }
  }

  function renderHeatmap(data) {
    if (!heatmapPanel) return;
    heatmapPanel.innerHTML = "";

    // Bottleneck warning
    if (data.predicted_bottlenecks && data.predicted_bottlenecks.length > 0) {
      var warning = document.createElement("div");
      warning.className = "incident-item";
      warning.setAttribute("role", "alert");
      warning.innerHTML =
        '<div class="incident-item__header">' +
          '<span class="incident-item__type">⚠️ Predicted Bottleneck</span>' +
          '<span class="incident-item__severity incident-item__severity--critical">WARNING</span>' +
        '</div>' +
        '<p class="incident-item__desc">Gates ' + escapeHtml(data.predicted_bottlenecks.join(", ")) +
        ' are predicted to become congested within 30 minutes.</p>';
      heatmapPanel.appendChild(warning);
    }

    // Table of predictions
    var table = document.createElement("table");
    table.className = "heatmap-table";
    table.setAttribute("role", "table");
    table.setAttribute("aria-label", "Gate congestion forecast");
    table.innerHTML =
      '<thead><tr>' +
        '<th scope="col">Gate</th>' +
        '<th scope="col">Now</th>' +
        '<th scope="col">+15 min</th>' +
        '<th scope="col">+30 min</th>' +
      '</tr></thead>';
    var tbody = document.createElement("tbody");
    Object.keys(data.current || {}).forEach(function (gateId) {
      var row = document.createElement("tr");
      var now = data.current[gateId];
      var f15 = data.forecast_15min[gateId];
      var f30 = data.forecast_30min[gateId];
      row.innerHTML =
        '<td>Gate ' + escapeHtml(gateId) + '</td>' +
        '<td class="heatmap-cell heatmap-cell--' + classifyDensity(now) + '">' + now.toFixed(1) + '%</td>' +
        '<td class="heatmap-cell heatmap-cell--' + classifyDensity(f15) + '">' + f15.toFixed(1) + '%</td>' +
        '<td class="heatmap-cell heatmap-cell--' + classifyDensity(f30) + '">' + f30.toFixed(1) + '%</td>';
      tbody.appendChild(row);
    });
    table.appendChild(tbody);
    heatmapPanel.appendChild(table);
  }

  function classifyDensity(pct) {
    if (pct >= 80) return "red";
    if (pct >= 60) return "yellow";
    return "green";
  }

  // ── Initialize ────────────────────────────────────────────
  loadStadiums().then(function () {
    fetchCrowdStatus();
    // Poll every 5 seconds
    pollInterval = setInterval(fetchCrowdStatus, 5000);
  });

  // Cleanup on page unload
  window.addEventListener("beforeunload", function () {
    if (pollInterval) clearInterval(pollInterval);
  });
})();

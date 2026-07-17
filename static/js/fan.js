/**
 * FanFlow AI — Fan Chat Client
 *
 * Handles SSE streaming from /api/chat/stream, DOM manipulation for
 * chat messages, language/stadium selectors, quick actions, and i18n.
 * All styling via class toggling — zero inline styles.
 */

(function () {
  "use strict";

  // ── DOM References ────────────────────────────────────────
  const chatFeed = document.getElementById("chat-feed");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");
  const typingIndicator = document.getElementById("typing-indicator");
  const welcomeCard = document.getElementById("welcome-card");
  const languageSelect = document.getElementById("language-select");
  const stadiumSelect = document.getElementById("stadium-select");
  const quickActionBtns = document.querySelectorAll(".quick-actions__btn");

  // ── i18n Map (loaded from API) ────────────────────────────
  let currentLang = "en";
  let currentStadium = "metlife";
  let isStreaming = false;
  let mapInitialized = false;

  // Client-side i18n fallback (mirrors server translations)
  const i18nFallback = {
    en: {
      chat_placeholder: "Ask me about the stadium, directions, accessibility...",
      send_button: "Send",
      welcome_message: "I'm your FIFA World Cup 2026 stadium assistant. Ask me about directions, accessibility, gates, transport, or anything else about the venue.",
      quick_restroom: "Nearest restroom",
      quick_accessible: "Accessible routes",
      quick_gates: "Gate information",
      quick_food: "Food & drinks",
      quick_transport: "Transport options",
      quick_quiet: "Quiet zones",
    },
  };

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

  // ── i18n Loader ───────────────────────────────────────────
  async function loadTranslations(lang) {
    try {
      const res = await fetch("/api/translations/" + lang);
      if (!res.ok) return i18nFallback[lang] || i18nFallback.en;
      return await res.json();
    } catch (err) {
      console.error("Failed to load translations:", err);
      return i18nFallback.en;
    }
  }

  async function updateLanguage(lang) {
    currentLang = lang;
    const strings = await loadTranslations(lang);

    // Update HTML dir attribute for RTL languages
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";

    // Update UI strings
    if (strings.chat_placeholder) chatInput.placeholder = strings.chat_placeholder;
    if (strings.app_title) {
      var titleEl = document.getElementById("app-title");
      if (titleEl) titleEl.textContent = strings.app_title;
    }
    if (strings.app_subtitle) {
      var subEl = document.getElementById("app-subtitle");
      if (subEl) subEl.textContent = strings.app_subtitle;
    }

    // Quick action labels
    var qaMap = {
      "qa-restroom-text": "quick_restroom",
      "qa-accessible-text": "quick_accessible",
      "qa-gates-text": "quick_gates",
      "qa-food-text": "quick_food",
      "qa-transport-text": "quick_transport",
      "qa-quiet-text": "quick_quiet",
    };
    Object.keys(qaMap).forEach(function (elId) {
      var el = document.getElementById(elId);
      if (el && strings[qaMap[elId]]) el.textContent = strings[qaMap[elId]];
    });

    // Welcome message
    if (strings.welcome_message) {
      var welcomeText = document.getElementById("welcome-text");
      if (welcomeText) welcomeText.textContent = strings.welcome_message;
    }

    // Navigation labels
    if (strings.nav_fan) {
      var navFan = document.getElementById("nav-fan");
      if (navFan) navFan.textContent = strings.nav_fan;
    }
    if (strings.nav_dashboard) {
      var navDash = document.getElementById("nav-dashboard");
      if (navDash) navDash.textContent = strings.nav_dashboard;
    }
  }

  // ── Map Integration ───────────────────────────────────────
  async function showMap(stadiumId) {
    if (mapInitialized || typeof google === "undefined" || !google.maps) return;
    try {
      const { Map } = await google.maps.importLibrary("maps");
      const mapSection = document.getElementById("map-section");
      
      // Default to MetLife, ideally we would fetch coords from stadium list
      let center = { lat: 40.812840, lng: -74.074208 };
      if (stadiumId === "azteca") center = { lat: 19.3029, lng: -99.1505 };
      if (stadiumId === "att") center = { lat: 32.7473, lng: -97.0945 };
      
      mapSection.style.display = "block";
      const map = new Map(document.getElementById("map"), {
        center: center,
        zoom: 16,
        mapId: 'DEMO_MAP_ID',
      });
      mapInitialized = true;

      // Ensure scroll to bottom so map is visible
      scrollToBottom();
    } catch (e) {
      console.error("Map initialization failed", e);
    }
  }

  // ── Chat Message Rendering ────────────────────────────────
  function addMessage(text, isUser) {
    // Hide welcome card on first message
    if (welcomeCard && welcomeCard.parentNode) {
      welcomeCard.remove();
    }

    var msgDiv = document.createElement("div");
    msgDiv.className = "chat-message " + (isUser ? "chat-message--user" : "chat-message--ai");
    msgDiv.setAttribute("role", "article");
    msgDiv.setAttribute("aria-label", isUser ? "Your message" : "AI response");

    var avatarDiv = document.createElement("div");
    avatarDiv.className = "chat-message__avatar";
    avatarDiv.setAttribute("aria-hidden", "true");
    avatarDiv.textContent = isUser ? "👤" : "🤖";

    var bubbleDiv = document.createElement("div");
    bubbleDiv.className = "chat-message__bubble";

    // Simple markdown-like rendering
    var formatted = formatMessage(text);
    bubbleDiv.innerHTML = formatted;

    msgDiv.appendChild(avatarDiv);
    msgDiv.appendChild(bubbleDiv);
    chatFeed.appendChild(msgDiv);
    scrollToBottom();

    return bubbleDiv;
  }

  function createStreamingMessage() {
    if (welcomeCard && welcomeCard.parentNode) {
      welcomeCard.remove();
    }

    var msgDiv = document.createElement("div");
    msgDiv.className = "chat-message chat-message--ai";
    msgDiv.setAttribute("role", "article");
    msgDiv.setAttribute("aria-label", "AI response");

    var avatarDiv = document.createElement("div");
    avatarDiv.className = "chat-message__avatar";
    avatarDiv.setAttribute("aria-hidden", "true");
    avatarDiv.textContent = "🤖";

    var bubbleDiv = document.createElement("div");
    bubbleDiv.className = "chat-message__bubble";
    bubbleDiv.textContent = "";

    msgDiv.appendChild(avatarDiv);
    msgDiv.appendChild(bubbleDiv);
    chatFeed.appendChild(msgDiv);
    scrollToBottom();

    return bubbleDiv;
  }

  function formatMessage(text) {
    // Escape HTML
    var escaped = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Bold
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Line breaks
    escaped = escaped.replace(/\n/g, "<br>");

    // Bullet points
    escaped = escaped.replace(/^[-•]\s+(.+)/gm, "<li>$1</li>");
    if (escaped.includes("<li>")) {
      escaped = escaped.replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>");
    }

    return escaped;
  }

  function scrollToBottom() {
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function showTyping() {
    typingIndicator.classList.add("typing-indicator--visible");
    scrollToBottom();
  }

  function hideTyping() {
    typingIndicator.classList.remove("typing-indicator--visible");
  }

  // ── Send Message ──────────────────────────────────────────
  async function sendMessage(text) {
    if (!text || !text.trim() || isStreaming) return;

    var message = text.trim();
    chatInput.value = "";
    chatInput.style.height = "auto";
    sendBtn.disabled = true;
    isStreaming = true;

    // Show user message
    addMessage(message, true);
    showTyping();

    // Show map if location-related keywords are detected
    if (/gate|transport|bus|train|restroom/i.test(message)) {
      showMap(currentStadium);
    }

    try {
      // Try SSE streaming first
      var response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message,
          language: currentLang,
          stadium_id: currentStadium,
        }),
      });

      if (response.ok && response.headers.get("content-type")?.includes("text/event-stream")) {
        hideTyping();
        var bubbleDiv = createStreamingMessage();
        var fullText = "";

        var reader = response.body.getReader();
        var decoder = new TextDecoder();
        var buffer = "";

        while (true) {
          var result = await reader.read();
          if (result.done) break;

          buffer += decoder.decode(result.value, { stream: true });
          var lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (var i = 0; i < lines.length; i++) {
            var line = lines[i].replace(/\r$/, "");
            if (!line.startsWith("data: ")) continue;

            var data = line.substring(6);
            if (data === "[DONE]") break;

            fullText += data;
            bubbleDiv.innerHTML = formatMessage(fullText);
            scrollToBottom();
          }
        }

        if (!fullText) {
          bubbleDiv.innerHTML = formatMessage("No response received. Please try again.");
        }
      } else {
        // Fallback to regular POST
        hideTyping();
        var jsonRes = await response.json();
        addMessage(jsonRes.reply || jsonRes.detail || "Error occurred.", false);
      }
    } catch (err) {
      hideTyping();
      console.error("Chat error:", err);

      // Fallback to non-streaming endpoint
      try {
        var fallbackRes = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: message,
            language: currentLang,
            stadium_id: currentStadium,
          }),
        });
        var fallbackData = await fallbackRes.json();
        addMessage(fallbackData.reply || "Sorry, something went wrong.", false);
      } catch (fallbackErr) {
        addMessage("Sorry, something went wrong. Please try again.", false);
      }
    } finally {
      isStreaming = false;
      sendBtn.disabled = false;
      chatInput.focus();
    }
  }

  // ── Auto-resize textarea ──────────────────────────────────
  function autoResize() {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
  }

  // ── Event Listeners ───────────────────────────────────────

  // Send on click
  sendBtn.addEventListener("click", function () {
    sendMessage(chatInput.value);
  });

  // Send on Enter (Shift+Enter for newline)
  chatInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(chatInput.value);
    }
    if (e.key === "Escape") {
      chatInput.value = "";
      autoResize();
    }
  });

  // Auto-resize on input
  chatInput.addEventListener("input", autoResize);

  // Quick action buttons
  quickActionBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var query = btn.getAttribute("data-query");
      if (query) sendMessage(query);
    });
  });

  // Language change
  languageSelect.addEventListener("change", function () {
    updateLanguage(languageSelect.value);
  });

  // Stadium change
  stadiumSelect.addEventListener("change", function () {
    currentStadium = stadiumSelect.value;
  });

  // ── Initialize ────────────────────────────────────────────
  loadStadiums();
  updateLanguage("en");
})();

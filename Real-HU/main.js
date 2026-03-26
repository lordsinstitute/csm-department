const navMarkup = `
  <header class="header-shell">
    <div class="container navbar">
      <a class="brand" href="./" aria-label="HackUnion home">
        <img class="brand-logo" src="images/HU%20logo.png" alt="HU logo" loading="eager" decoding="async" />
      </a>
      <button class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="siteNav" aria-label="Toggle navigation menu">☰</button>
      <ul class="nav-links" id="siteNav">
        <li><a href="./" data-route="home">Home</a></li>
        <li><a href="about/" data-route="about">About</a></li>
        <li><a href="programs/" data-route="programs">Programs</a></li>
        <li><a href="community/" data-route="community">Community</a></li>
        <li><a href="insights/" data-route="insights">Insights</a></li>
        <li><a href="contact/" data-route="contact">Contact</a></li>
      </ul>
    </div>
  </header>
`;

const footerMarkup = `
  <footer>
    <div class="container footer-content">
      <div class="footer-top">
        <div class="footer-section">
          <div class="footer-brand">
            <img class="footer-logo" src="images/HU%20logo.png" alt="HU logo" loading="lazy" decoding="async" />
          </div>
          <p class="footer-tagline">Where Builders Learn by Building</p>
          <p class="footer-description">Independent builders community affiliated with Lords Skill Academy.</p>
        </div>
        <div class="footer-section">
          <h3 class="footer-heading">Quick Links</h3>
          <ul class="footer-nav">
            <li><a href="./" data-route="home">Home</a></li>
            <li><a href="about/" data-route="about">About</a></li>
            <li><a href="programs/" data-route="programs">Programs</a></li>
            <li><a href="community/" data-route="community">Community</a></li>
            <li><a href="insights/" data-route="insights">Insights</a></li>
            <li><a href="./coc/" data-route="coc">Code of Conduct</a></li>
            <li><a href="contact/" data-route="contact">Contact</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="container">
        <p class="footer-credit">© 2026 HackUnion. All rights reserved | Website developed by <span class="developer-credit">RV Projects</span></p>
      </div>
    </div>
  </footer>
`;

function mountSharedLayout() {
  const headerRoot = document.getElementById("site-header");
  const footerRoot = document.getElementById("site-footer");

  if (headerRoot) {
    headerRoot.innerHTML = navMarkup;
  }

  if (footerRoot) {
    footerRoot.innerHTML = footerMarkup;
  }

  const navToggle = document.getElementById("navToggle");
  const nav = document.getElementById("siteNav");

  if (navToggle && nav) {
    navToggle.addEventListener("click", () => {
      const isExpanded = navToggle.getAttribute("aria-expanded") === "true";
      navToggle.setAttribute("aria-expanded", String(!isExpanded));
      nav.classList.toggle("open");
    });
  }

  const currentRoute = getCurrentRoute();
  document.querySelectorAll(".nav-links a, .footer-nav a").forEach((link) => {
    const linkRoute = link.dataset.route;
    if (linkRoute === currentRoute) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

function getCurrentRoute() {
  const pathname = window.location.pathname;
  const trimmedPath = pathname.replace(/\/+$/, "");

  if (!trimmedPath) {
    return "home";
  }

  const segments = trimmedPath.split("/").filter(Boolean);
  const lastSegment = segments[segments.length - 1] || "";

  if (lastSegment === "index.html") {
    return segments.length > 1 ? segments[segments.length - 2] : "home";
  }

  if (lastSegment.endsWith(".html")) {
    return lastSegment.slice(0, -5);
  }

  if (pathname.endsWith("/")) {
    return segments.length === 1 ? "home" : lastSegment;
  }

  return lastSegment;
}

document.addEventListener("DOMContentLoaded", mountSharedLayout);

// Render events from centralized data source
function initializeEventRendering() {
  // Check if on index page (has countdown functionality)
  const isIndexPage = getCurrentRoute() === "home";
  
  // Render events if events-data.js is loaded
  if (typeof renderUpcomingEvents === "function") {
    renderUpcomingEvents("upcoming-events-container", isIndexPage);
  }
}

// Real-time event countdown timer
function initEventCountdowns() {
  const eventCards = document.querySelectorAll(".event-list-card[data-event-date]");
  
  function updateEventStatus() {
    eventCards.forEach((card) => {
      const eventDateStr = card.getAttribute("data-event-date");
      const eventEndStr = card.getAttribute("data-event-end");
      const daysLeftSpan = card.querySelector(".days-left");
      const countdownDiv = card.querySelector(".event-countdown");
      
      if (!eventDateStr || !eventEndStr || !daysLeftSpan) return;
      
      // Parse ISO format dates
      const eventStart = new Date(eventDateStr);
      const eventEnd = new Date(eventEndStr);
      const now = new Date();
      
      // Calculate time differences in milliseconds
      const timeToStart = eventStart - now;
      const timeToEnd = eventEnd - now;
      
      // Event has ended
      if (timeToEnd <= 0) {
        daysLeftSpan.textContent = "Event Ended";
        daysLeftSpan.style.background = "#999";
        if (countdownDiv) {
          countdownDiv.textContent = "✓ Event Ended";
          countdownDiv.classList.remove("happening-now");
          countdownDiv.classList.add("event-passed");
          countdownDiv.style.display = "block";
        }
        return;
      }
      
      // Event is currently happening
      if (timeToStart <= 0 && timeToEnd > 0) {
        daysLeftSpan.textContent = "🎉 NOW!";
        daysLeftSpan.style.background = "var(--accent-orange)";
        if (countdownDiv) {
          countdownDiv.textContent = "🎉 Event is Happening Now!";
          countdownDiv.classList.add("happening-now");
          countdownDiv.classList.remove("event-passed");
          countdownDiv.style.display = "block";
        }
        return;
      }
      
      // Event is in the future
      const hoursRemaining = timeToStart / (1000 * 60 * 60);
      const daysRemaining = Math.ceil(timeToStart / (1000 * 60 * 60 * 24));
      
      // More than 12 hours away - show days remaining
      if (hoursRemaining > 12) {
        daysLeftSpan.textContent = daysRemaining === 1 ? "1 Day Left" : `${daysRemaining} Days Left`;
        daysLeftSpan.style.background = "var(--accent-cyan)";
        if (countdownDiv) {
          countdownDiv.style.display = "none";
        }
      } 
      // 12 hours or less - show live countdown
      else {
        const totalSeconds = Math.floor(timeToStart / 1000);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        daysLeftSpan.textContent = `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
        daysLeftSpan.style.background = "var(--accent-orange)";
        
        if (countdownDiv) {
          countdownDiv.textContent = `⏱️ Starts in ${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
          countdownDiv.classList.remove("happening-now", "event-passed");
          countdownDiv.style.display = "block";
        }
      }
    });
  }
  
  // Update immediately and then every second for smooth countdown
  updateEventStatus();
  setInterval(updateEventStatus, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
  initializeEventRendering();
  initEventCountdowns();
});
// Scroll-triggered counter animation for stats
function initCounterAnimation() {
  const statNumbers = document.querySelectorAll(".stat-number");
  
  if (statNumbers.length === 0) return;

  const observerOptions = {
    threshold: 0.5,
    rootMargin: "0px"
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        entry.target.dataset.animated = "true";
        const target = parseInt(entry.target.dataset.target, 10);
        animateCounter(entry.target, target, 0, 1200);
      }
    });
  }, observerOptions);

  statNumbers.forEach((el) => {
    observer.observe(el);
  });
}

function animateCounter(element, target, current, duration) {
  const increment = target / (duration / 16);
  const startTime = Date.now();
  
  const updateCounter = () => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const value = Math.floor(current + progress * (target - current));
    
    element.textContent = value + "+";
    
    if (progress < 1) {
      requestAnimationFrame(updateCounter);
    } else {
      element.textContent = target + "+";
    }
  };
  
  updateCounter();
}

document.addEventListener("DOMContentLoaded", () => {
  initCounterAnimation();
});

// HackUnion Ecosystem Branch Network - GitHub-Style Interactions
function initEcosystemAnimation() {
  const svg = document.querySelector('.ecosystem-svg');
  if (!svg) return;

  const nodes = document.querySelectorAll('.eco-node');
  const paths = document.querySelectorAll('.eco-path');
  const tooltip = document.getElementById('ecoTooltip');
  
  const tooltipWidth = 220;
  const tooltipHeight = 75;
  const tooltipOffset = 10; // Distance above element

  // Function to position tooltip using getBoundingClientRect
  function positionTooltip(element, isMobile = false) {
    if (!tooltip) return;

    const rect = element.getBoundingClientRect();
    let x = rect.left + rect.width / 2 - tooltipWidth / 2;
    let y = rect.top - tooltipHeight - tooltipOffset;

    // Keep tooltip within screen boundaries
    const minX = 10;
    const maxX = window.innerWidth - tooltipWidth - 10;
    const minY = 10;
    const maxY = window.innerHeight - tooltipHeight - 10;

    x = Math.max(minX, Math.min(maxX, x));
    
    // If tooltip would go above screen, position it below element
    if (y < minY) {
      y = rect.bottom + tooltipOffset;
    }
    y = Math.max(minY, Math.min(maxY, y));

    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }

  // Function to show tooltip
  function showTooltip(title, description, element) {
    if (!tooltip) return;

    const tooltipTitle = tooltip.querySelector('.tooltip-title');
    const tooltipDesc = tooltip.querySelector('.tooltip-desc');
    
    if (tooltipTitle) tooltipTitle.textContent = title;
    if (tooltipDesc) tooltipDesc.textContent = description;
    
    positionTooltip(element);
    tooltip.classList.remove('hidden');
    tooltip.classList.add('visible');
    tooltip.style.display = 'block';
  }

  // Function to hide tooltip
  function hideTooltip() {
    if (!tooltip) {
      return;
    }
    tooltip.classList.remove('visible');
    tooltip.classList.add('hidden');
    tooltip.style.display = 'none';
  }

  // Add hover listeners to nodes
  nodes.forEach(node => {
    node.addEventListener('mouseenter', (e) => {
      const title = node.getAttribute('data-title');
      const description = node.getAttribute('data-description');
      
      if (!title || !description) return;

      showTooltip(title, description, node);
    });

    node.addEventListener('mouseleave', hideTooltip);
    
    node.addEventListener('mousemove', (e) => {
      // Update tooltip position as mouse moves
      if (tooltip.classList.contains('visible')) {
        positionTooltip(node);
      }
    });
  });

  // Add hover listeners to paths
  paths.forEach(path => {
    path.addEventListener('mouseenter', (e) => {
      const title = path.getAttribute('data-title');
      const description = path.getAttribute('data-description');
      
      if (!title || !description) return;

      showTooltip(title, description, path);
    });

    path.addEventListener('mouseleave', hideTooltip);
    
    path.addEventListener('mousemove', (e) => {
      // Update tooltip position as mouse moves
      if (tooltip.classList.contains('visible')) {
        positionTooltip(path);
      }
    });
  });

  // Add click handler for mobile tooltip display
  [...nodes, ...paths].forEach(element => {
    element.addEventListener('click', (e) => {
      e.stopPropagation();
      const title = element.getAttribute('data-title');
      const description = element.getAttribute('data-description');
      
      if (title && description) {
        const isVisible = tooltip.classList.contains('visible');
        
        if (!isVisible) {
          showTooltip(title, description, element);
        } else {
          hideTooltip();
        }
      }
    });
  });

  // Close tooltip when clicking outside SVG
  document.addEventListener('click', (e) => {
    if (!svg.contains(e.target) && !tooltip.contains(e.target)) {
      hideTooltip();
    }
  });
}

// Trigger animation when section scrolls into view
document.addEventListener("DOMContentLoaded", () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animationTriggered) {
        entry.target.dataset.animationTriggered = 'true';
        // Animation is triggered via CSS, just call init for interaction
        requestAnimationFrame(() => {
          initEcosystemAnimation();
        });
      }
    });
  }, { threshold: 0.15 });

  const ecoContainer = document.querySelector('.ecosystem-diagram');
  if (ecoContainer) {
    observer.observe(ecoContainer);
    // Also initialize if already in view
    const rect = ecoContainer.getBoundingClientRect();
    if (rect.top < window.innerHeight && rect.bottom > 0) {
      ecoContainer.dataset.animationTriggered = 'true';
      initEcosystemAnimation();
    }
  }
});

// Event card expand/collapse toggle
function toggleEventDetails(card) {
  const details = card.querySelector(".event-details");
  const btn = card.querySelector(".learn-more-btn");
  const isOpen = details.style.display === "block";
  
  // Close all other cards
  document.querySelectorAll(".event-card").forEach((c) => {
    if (c !== card) {
      c.querySelector(".event-details").style.display = "none";
      c.querySelector(".learn-more-btn").textContent = "Learn more";
    }
  });
  
  // Toggle current card
  details.style.display = isOpen ? "none" : "block";
  btn.textContent = isOpen ? "Learn more" : "Learn less";
}

// Project card expand/collapse toggle
function toggleProjectDetails(card) {
  const details = card.querySelector(".project-details");
  const learnBtn = card.querySelector(".learn-more-btn");
  const isOpen = details.style.display === "block";
  
  // If already open, close it
  if (isOpen) {
    details.style.display = "none";
    learnBtn.style.display = "inline-block";
    return;
  }
  
  // Close all other project cards
  document.querySelectorAll(".project-card").forEach((c) => {
    if (c !== card) {
      c.querySelector(".project-details").style.display = "none";
      c.querySelector(".learn-more-btn").style.display = "inline-block";
    }
  });
  
  // Open current card and hide button
  details.style.display = "block";
  learnBtn.style.display = "none";
}

// Close project details when clicking outside
document.addEventListener("DOMContentLoaded", () => {
  document.addEventListener("click", (e) => {
    const projectCard = e.target.closest(".project-card");
    const learnBtn = e.target.closest(".learn-more-btn");
    const githubLink = e.target.closest(".project-details a");
    
    // If clicking on GitHub link, let it open in new tab
    if (githubLink) return;
    
    // Only process clicks on project cards
    if (projectCard && !learnBtn) {
      // Toggle if details are open, close otherwise
      const details = projectCard.querySelector(".project-details");
      const btn = projectCard.querySelector(".learn-more-btn");
      if (details.style.display === "block") {
        details.style.display = "none";
        btn.style.display = "inline-block";
      }
    }
  });
});
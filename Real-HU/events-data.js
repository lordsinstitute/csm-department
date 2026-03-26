// Shared Events Data - Used across index.html and programs.html
const upcomingEvents = [
  {
    id: 'feb-meetup',
    title: 'HackUnion February Meetup 2026',
    date: 'Saturday, February 26, 2026',
    time: '09:30 AM - 12:30 PM',
    location: '1st Year Block, Seminar Hall, LIET Campus',
    eventDate: '2026-02-28T09:30:00',
    eventEnd: '2026-02-28T12:30:00',
    description: 'Collaborative coding challenge to prototype ideas fast.',
    image: 'images/Events/HU Meetup.jpg',
    isFlagship: false,
    alt: 'Students attending a coding workshop event'
  },
  {
    id: 'copilot-dev-days',
    title: 'GitHub Copilot Dev Days',
    date: 'Saturday, March 28, 2026',
    time: '09:30 AM - 01:00 PM',
    location: 'Hybrid (In-person + Online)<br/><b>Offline:</b> 4th Floor, Main Seminar Hall, LIET Campus, Hyderabad',
    eventDate: '2026-03-28T09:30:00',
    eventEnd: '2026-03-28T13:00:00',
    description: 'Builders share practical lessons from live projects.',
    image: 'images/Events/copilot dev days.jpg',
    isFlagship: true,
    alt: 'Students joining a technical meetup discussion'
  },
  {
    id: 'builder-day',
    title: 'Builder Day',
    date: 'Saturday, April 4, 2026',
    time: '08:30 AM - 09:00 PM',
    location: 'Lords Skill Academy, Innovation Hall',
    eventDate: '2026-04-04T08:30:00',
    eventEnd: '2026-04-04T21:00:00',
    description: 'Present progress and receive mentor and peer feedback.',
    image: 'https://images.unsplash.com/photo-1551818255-e6e10975bc17?auto=format&fit=crop&w=1200&q=80',
    isFlagship: false,
    alt: 'Student teams presenting projects during upcoming showcase'
  }
];

// Function to generate event HTML for index.html (with countdown)
function generateEventCardHTML(event) {
  const flagshipClass = event.isFlagship ? ' flagship-event' : '';
  const flagshipBadge = event.isFlagship 
    ? '<span class="flagship-label">Flagship</span>' 
    : '';
  
  return `
    <article class="card event-list-card${flagshipClass}" data-event-date="${event.eventDate}" data-event-end="${event.eventEnd}">
      <div class="event-status-badge${event.isFlagship ? ' flagship-badge' : ''}">
        ${flagshipBadge}
        <span class="days-left"></span>
      </div>
      <div class="media-16x9">
        <img src="${event.image}" loading="lazy" decoding="async" alt="${event.alt}" />
      </div>
      <h3>${event.title}</h3>
      <div class="event-meta">
        <p class="event-date">${event.date}</p>
        <p class="event-time">${event.time}</p>
        <p class="event-location">${event.location}</p>
      </div>
      <p>${event.description}</p>
      <div class="event-countdown" style="display: none;"></div>
      <p class="registration-closing" style="display: none;"></p>
      <button class="learn-more-btn">Register Now</button>
    </article>
  `;
}

// Function to generate event HTML for programs.html (simple cards)
// Function to generate event HTML for programs.html (simple cards)
function generateProgramEventCardHTML(event) {
  return `
    <article>
      <div class="media-16x9">
        <img src="${event.image}" loading="lazy" decoding="async" alt="${event.alt}" />
      </div>
      <h3>${event.title}</h3>
      <p class="muted">${event.date.replace('Saturday, ', '').replace(', 2026', '')} · Hyderabad</p>
      <button class="btn btn-secondary">Register Now</button>
    </article>
  `;
}

// Function to render events on a page
function renderUpcomingEvents(containerId, isIndexPage = false) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  if (isIndexPage) {
    // For index.html - show all 3 events with countdown
    container.innerHTML = upcomingEvents.map(event => generateEventCardHTML(event)).join('');
  } else {
    // For programs.html - show simple cards
    container.innerHTML = upcomingEvents.map(event => generateProgramEventCardHTML(event)).join('');
  }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { upcomingEvents, generateEventCardHTML, generateProgramEventCardHTML, renderUpcomingEvents };
}

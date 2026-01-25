import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import './i18n/config';

// Ensure direction is always LTR for consistent alignment
document.documentElement.dir = 'ltr';
document.body.dir = 'ltr';

// Disable browser scroll restoration to prevent unwanted scroll on navigation
if ('scrollRestoration' in window.history) {
  window.history.scrollRestoration = 'manual';
}

// Function to reset scroll position (only called on page load/navigation, not blocking user scroll)
const resetScroll = () => {
  window.scrollTo(0, 0);
  if (document.documentElement) {
    document.documentElement.scrollTop = 0;
  }
  if (document.body) {
    document.body.scrollTop = 0;
  }
};

// Reset scroll on initial load
resetScroll();

// Reset scroll on page load events (only once per event, not blocking)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    resetScroll();
    setTimeout(resetScroll, 10);
    setTimeout(resetScroll, 50);
  }, { once: true });
} else {
  resetScroll();
  setTimeout(resetScroll, 10);
  setTimeout(resetScroll, 50);
}

// Reset scroll on window load (only once)
window.addEventListener('load', () => {
  resetScroll();
  setTimeout(resetScroll, 10);
  setTimeout(resetScroll, 50);
}, { once: true });

// Reset scroll on pageshow (handles back/forward navigation and reload)
window.addEventListener('pageshow', (e) => {
  // Reset scroll on page reload or back/forward navigation
  resetScroll();
  setTimeout(resetScroll, 10);
  setTimeout(resetScroll, 50);
  setTimeout(resetScroll, 100);
}, { once: false });

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);




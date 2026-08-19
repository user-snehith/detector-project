// Popup script for Phishing URL Detector extension

document.addEventListener('DOMContentLoaded', function() {
  // Load current settings
  loadSettings();

  // Load stats
  loadStats();

  // Set up event listeners
  setupEventListeners();
});

// Load extension settings
function loadSettings() {
  chrome.storage.sync.get({
    enabled: true,
    autoRedirect: false,
    showWarnings: true,
    detectorUrl: 'http://localhost:8501'
  }, function(settings) {
    document.getElementById('enabled').checked = settings.enabled;
    document.getElementById('autoRedirect').checked = settings.autoRedirect;
    document.getElementById('showWarnings').checked = settings.showWarnings;
    document.getElementById('detectorUrl').value = settings.detectorUrl;

    updateStatus(settings.enabled);
  });
}

// Load usage statistics
function loadStats() {
  chrome.storage.local.get({
    urlsChecked: 0,
    phishingBlocked: 0,
    lastReset: Date.now()
  }, function(stats) {
    // Reset stats if it's a new day
    const now = new Date();
    const lastReset = new Date(stats.lastReset);
    if (now.toDateString() !== lastReset.toDateString()) {
      stats.urlsChecked = 0;
      stats.phishingBlocked = 0;
      stats.lastReset = now.getTime();
      chrome.storage.local.set(stats);
    }

    document.getElementById('urlsChecked').textContent = stats.urlsChecked;
    document.getElementById('phishingBlocked').textContent = stats.phishingBlocked;
  });
}

// Update status display
function updateStatus(enabled) {
  const statusEl = document.getElementById('status');
  if (enabled) {
    statusEl.textContent = 'Extension is ENABLED';
    statusEl.className = 'status enabled';
  } else {
    statusEl.textContent = 'Extension is DISABLED';
    statusEl.className = 'status disabled';
  }
}

// Set up event listeners
function setupEventListeners() {
  // Enable/disable toggle
  document.getElementById('enabled').addEventListener('change', function(e) {
    const enabled = e.target.checked;
    chrome.storage.sync.set({enabled: enabled});
    updateStatus(enabled);
  });

  // Open detector button
  document.getElementById('openDetector').addEventListener('click', function() {
    chrome.storage.sync.get({detectorUrl: 'http://localhost:8501'}, function(settings) {
      chrome.tabs.create({url: settings.detectorUrl});
      window.close();
    });
  });

  // Test with current tab button
  document.getElementById('testUrl').addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (tabs[0]) {
        chrome.storage.sync.get({detectorUrl: 'http://localhost:8501'}, function(settings) {
          const testUrl = `${settings.detectorUrl}?url=${encodeURIComponent(tabs[0].url)}`;
          chrome.tabs.create({url: testUrl});
          window.close();
        });
      }
    });
  });

  // Save settings button
  document.getElementById('saveSettings').addEventListener('click', function() {
    const settings = {
      detectorUrl: document.getElementById('detectorUrl').value,
      autoRedirect: document.getElementById('autoRedirect').checked,
      showWarnings: document.getElementById('showWarnings').checked
    };

    chrome.storage.sync.set(settings, function() {
      // Show success message
      const button = document.getElementById('saveSettings');
      const originalText = button.textContent;
      button.textContent = 'Saved!';
      button.style.background = '#4caf50';

      setTimeout(() => {
        button.textContent = originalText;
        button.style.background = '#1976d2';
      }, 2000);
    });
  });
}

// Utility function to increment stats
function incrementStat(statName) {
  chrome.storage.local.get({[statName]: 0}, function(stats) {
    stats[statName]++;
    chrome.storage.local.set(stats);
  });
}

// Export for use by other scripts
window.popupUtils = {
  incrementStat: incrementStat
};
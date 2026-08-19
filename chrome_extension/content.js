// Content script for Phishing URL Detector
// This script runs on all web pages and intercepts link clicks

let extensionEnabled = true;
const DETECTOR_HOSTNAMES = ['localhost', '127.0.0.1'];

// Load settings from storage
chrome.storage.sync.get(['enabled'], (result) => {
  extensionEnabled = result.enabled !== false;
});

// Listen for settings changes
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (changes.enabled) {
    extensionEnabled = changes.enabled.newValue;
  }
});

// Intercept all link clicks
document.addEventListener('click', function(event) {
  if (!extensionEnabled) return;

  // Find the clicked link element
  let linkElement = event.target;
  while (linkElement && linkElement.tagName !== 'A') {
    linkElement = linkElement.parentElement;
  }

  if (!linkElement || !linkElement.href) return;

  const url = linkElement.href;

  // Skip if it's not an HTTP/HTTPS URL
  if (!url.startsWith('http://') && !url.startsWith('https://')) return;

  // Skip if we are on the detector page itself
  const currentDomain = window.location.hostname;
  if (DETECTOR_HOSTNAMES.includes(currentDomain)) return;

  // Skip if it's the same domain (internal links)
  try {
    const linkDomain = new URL(url).hostname;
    if (linkDomain === currentDomain) return;
  } catch (e) {
    return; // Invalid URL
  }

  // Prevent default click behavior
  event.preventDefault();
  event.stopPropagation();

  // Check the URL
  checkUrl(url, linkElement);
});

// Check URL with background script
function checkUrl(url, linkElement) {
  chrome.runtime.sendMessage({
    action: 'checkUrl',
    url: url
  }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('Extension error:', chrome.runtime.lastError);
      // Fallback: allow the click
      window.location.href = url;
      return;
    }

    if (response.error) {
      console.error('Check error:', response.error);
      // Fallback: allow the click
      window.location.href = url;
      return;
    }

    // Show loading indicator on the link
    showLoadingIndicator(linkElement);

    // The background script opened the detector tab
    // We'll wait for the user to make a decision there
  });
}

// Show loading indicator on clicked link
function showLoadingIndicator(linkElement) {
  const originalText = linkElement.textContent;
  const originalColor = linkElement.style.color;

  linkElement.style.color = '#ffa500';
  linkElement.textContent = '🔍 Checking URL...';

  // Restore after 3 seconds if no response
  setTimeout(() => {
    if (linkElement.textContent === '🔍 Checking URL...') {
      linkElement.textContent = originalText;
      linkElement.style.color = originalColor;
    }
  }, 3000);
}

// Listen for messages from the detector page
window.addEventListener('message', function(event) {
  // Only accept messages from our detector
  if (event.origin !== 'http://localhost:8501' &&
      event.origin !== 'http://127.0.0.1:8501') return;

  if (event.data.type === 'phishingCheckResult') {
    handleCheckResult(event.data);
  }
});

// Handle check result from detector
function handleCheckResult(data) {
  if (data.result === 'safe') {
    // Allow navigation
    window.location.href = data.url;
  } else if (data.result === 'phishing') {
    // Show warning and don't navigate
    showPhishingWarning(data.url, data.details);
  }
}

// Show phishing warning
function showPhishingWarning(url, details) {
  // Create warning overlay
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
  `;

  const warningBox = document.createElement('div');
  warningBox.style.cssText = `
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
    max-width: 500px;
    text-align: center;
  `;

  warningBox.innerHTML = `
    <h2 style="color: #d32f2f; margin-top: 0;">⚠️ Phishing Warning!</h2>
    <p style="color: #333; font-size: 16px; line-height: 1.5;">
      Our phishing detector has identified this URL as potentially dangerous:
    </p>
    <p style="color: #666; font-family: monospace; background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all;">
      ${url}
    </p>
    <p style="color: #d32f2f; font-weight: bold;">
      Risk Level: ${details.risk_level.toUpperCase()}
    </p>
    <p style="color: #666; font-size: 14px;">
      Confidence: ${(details.confidence * 100).toFixed(1)}%
    </p>
    <div style="margin-top: 20px;">
      <button id="cancelBtn" style="background: #4CAF50; color: white; border: none; padding: 10px 20px; margin: 0 10px; border-radius: 5px; cursor: pointer;">
        Stay Safe (Recommended)
      </button>
      <button id="proceedBtn" style="background: #f44336; color: white; border: none; padding: 10px 20px; margin: 0 10px; border-radius: 5px; cursor: pointer;">
        Proceed Anyway
      </button>
    </div>
  `;

  overlay.appendChild(warningBox);
  document.body.appendChild(overlay);

  // Handle button clicks
  document.getElementById('cancelBtn').onclick = () => {
    document.body.removeChild(overlay);
  };

  document.getElementById('proceedBtn').onclick = () => {
    document.body.removeChild(overlay);
    window.location.href = url;
  };
}
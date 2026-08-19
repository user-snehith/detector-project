// Background script for Phishing URL Detector extension

// Configuration
const DETECTOR_URL = 'http://localhost:8501';
const CHECK_ENDPOINT = `${DETECTOR_URL}/check?url=`;

// Store for pending checks
let pendingChecks = new Map();

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkUrl') {
    checkUrl(request.url, sender.tab.id, sendResponse);
    return true; // Keep message channel open for async response
  }

  if (request.action === 'getPendingCheck') {
    const check = pendingChecks.get(request.checkId);
    sendResponse(check || null);
  }

  if (request.action === 'clearPendingCheck') {
    pendingChecks.delete(request.checkId);
    sendResponse({success: true});
  }
});

// Check URL with our phishing detector
async function checkUrl(url, tabId, sendResponse) {
  try {
    // Generate unique check ID
    const checkId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);

    // Store pending check
    pendingChecks.set(checkId, {
      id: checkId,
      url: url,
      tabId: tabId,
      status: 'checking',
      timestamp: Date.now()
    });

    // Open detector in new tab
    const detectorTab = await chrome.tabs.create({
      url: `${DETECTOR_URL}?check=${encodeURIComponent(url)}&checkId=${checkId}`,
      active: true
    });

    // Store detector tab ID
    const check = pendingChecks.get(checkId);
    if (check) {
      check.detectorTabId = detectorTab.id;
    }

    sendResponse({checkId: checkId, detectorTabId: detectorTab.id});

  } catch (error) {
    console.error('Error checking URL:', error);
    sendResponse({error: error.message});
  }
}

// Clean up old pending checks (older than 5 minutes)
setInterval(() => {
  const now = Date.now();
  const maxAge = 5 * 60 * 1000; // 5 minutes

  for (const [checkId, check] of pendingChecks.entries()) {
    if (now - check.timestamp > maxAge) {
      pendingChecks.delete(checkId);
    }
  }
}, 60000); // Clean up every minute

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // Set default settings
    chrome.storage.sync.set({
      enabled: true,
      autoRedirect: false,
      showWarnings: true,
      detectorUrl: DETECTOR_URL
    });

    // Show welcome message
    chrome.tabs.create({
      url: chrome.runtime.getURL('welcome.html')
    });
  }
});
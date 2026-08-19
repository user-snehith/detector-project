# Phishing URL Detector Chrome Extension

This Chrome extension automatically checks URLs for phishing before you click them, using our AI-powered phishing detector.

## Features

- **Automatic Link Monitoring**: Intercepts all link clicks on web pages
- **Real-time Analysis**: Uses machine learning to detect phishing URLs
- **Homograph Detection**: Identifies lookalike domains (g00gle, amaz0n, etc.)
- **Safe Browsing**: Shows warnings for suspicious links
- **Extension Integration**: Seamlessly works with our Streamlit web app

## Installation

1. **Load the Extension**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select the `chrome_extension` folder

2. **Start the Detector**:
   - Make sure our phishing detector is running: `streamlit run frontend/app.py`
   - The extension will connect to `http://localhost:8501`

3. **Configure**:
   - Click the extension icon in Chrome toolbar
   - Adjust settings as needed

## How It Works

1. **Link Click Detection**: Extension monitors all link clicks on web pages
2. **URL Interception**: When you click a link, it's sent to our detector
3. **Analysis**: Our AI analyzes the URL for phishing characteristics
4. **Decision**: You see the results and choose to proceed or cancel
5. **Safe Navigation**: Only safe links allow navigation

## Extension Files

- `manifest.json` - Extension configuration
- `background.js` - Background service worker
- `content.js` - Content script for web pages
- `popup.html/js` - Extension popup interface
- `icons/` - Extension icons

## Permissions

The extension requires these permissions:
- `activeTab` - Access current tab for analysis
- `storage` - Save settings and statistics
- `scripting` - Inject content scripts
- `tabs` - Create new tabs for detector
- `host_permissions` - Access local detector server

## Settings

- **Enable/Disable**: Turn monitoring on/off
- **Detector URL**: URL of your phishing detector (default: localhost:8501)
- **Auto-redirect**: Automatically open detector for suspicious links
- **Show Warnings**: Display phishing warnings

## Troubleshooting

**Extension not working?**
- Make sure the detector is running on localhost:8501
- Check that the extension is enabled in chrome://extensions
- Try refreshing the page

**False positives/negatives?**
- The detector uses machine learning and may occasionally misclassify
- You can always override decisions manually

**Performance issues?**
- The extension adds minimal overhead (~5ms per link check)
- Analysis happens locally when possible

## Development

To modify the extension:
1. Edit the source files
2. Reload the extension in chrome://extensions
3. Test on various websites

## Security Notes

- All analysis happens locally when possible
- URLs are only sent to your local detector server
- No external API calls or data collection
- Extension works offline for basic checks

## License

This extension is part of the Phishing URL Detector project.
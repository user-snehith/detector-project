"""
Browser Integration Examples for Phishing Detector
"""

# ============================================================================
# EXAMPLE 1: JavaScript (Browser Extension)
# ============================================================================

BROWSER_EXTENSION_JAVASCRIPT = """
// content.js - Analyze all links on page
function checkLink(url) {
    fetch('http://127.0.0.1:5000/predict?url=' + encodeURIComponent(url))
        .then(response => response.json())
        .then(data => {
            if (data.is_phishing) {
                addPhishingWarning(url, data.confidence);
            }
        })
        .catch(error => console.log('Detection failed:', error));
}

function addPhishingWarning(url, confidence) {
    // Highlight suspicious links in red
    const links = document.querySelectorAll('a');
    links.forEach(link => {
        if (link.href === url || link.textContent === url) {
            link.style.backgroundColor = '#ffcccc';
            link.title = `⚠️ PHISHING WARNING - Confidence: ${(confidence*100).toFixed(0)}%`;
            link.addEventListener('click', (e) => {
                e.preventDefault();
                alert(`🚨 PHISHING DETECTED!\\nURL: ${url}\\nConfidence: ${(confidence*100).toFixed(0)}%`);
            });
        }
    });
}

// Check all links on page load
document.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('a[href]');
    links.forEach(link => checkLink(link.href));
});
"""

# ============================================================================
# EXAMPLE 2: Python Desktop App Integration
# ============================================================================

PYTHON_DESKTOP_INTEGRATION = """
import requests
import webbrowser
from urllib.parse import urlparse
import tkinter as tk
from tkinter import simpledialog, messagebox

class PhishingDetectorApp:
    def __init__(self):
        self.api_url = "http://127.0.0.1:5000"
    
    def check_url(self, url):
        '''Check if URL is phishing'''
        try:
            response = requests.get(f"{self.api_url}/predict", params={"url": url})
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def safe_open_url(self, url):
        '''Opens URL only if safe'''
        result = self.check_url(url)
        
        if result.get("error"):
            messagebox.showerror("Error", f"Detection failed: {result['error']}")
            return
        
        if result["is_phishing"]:
            response = messagebox.askyesno(
                "⚠️ PHISHING WARNING",
                f"This URL appears to be phishing!\\n\\n"
                f"URL: {url}\\n"
                f"Confidence: {result['confidence']:.0%}\\n"
                f"Risk Level: {result['risk_level'].upper()}\\n\\n"
                f"Open anyway?"
            )
            if response:
                webbrowser.open(url)
        else:
            messagebox.showinfo("✅ Safe", f"This URL appears safe\\n\\nOpening...")
            webbrowser.open(url)
    
    def show_gui(self):
        root = tk.Tk()
        root.title("Phishing Detector")
        
        tk.Label(root, text="Enter URL:").pack(pady=5)
        url_entry = tk.Entry(root, width=50)
        url_entry.pack(pady=5)
        
        def check():
            url = url_entry.get()
            if not url:
                messagebox.showwarning("Input", "Please enter a URL")
                return
            self.safe_open_url(url)
        
        tk.Button(root, text="Check & Open", command=check).pack(pady=5)
        root.mainloop()

# Usage
if __name__ == "__main__":
    app = PhishingDetectorApp()
    app.show_gui()
"""

# ============================================================================
# EXAMPLE 3: PowerShell Integration
# ============================================================================

POWERSHELL_INTEGRATION = """
# Get-PhishingStatus.ps1 - PowerShell function to check URLs

function Test-PhishingURL {
    param(
        [Parameter(Mandatory=$true)]
        [string]$URL
    )
    
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/predict" `
            -Method GET `
            -Body @{ url = $URL } `
            -UseBasicParsing
        
        $status = if ($response.is_phishing) { "🚨 PHISHING" } else { "✅ SAFE" }
        
        Write-Host "URL: $URL"
        Write-Host "Status: $status"
        Write-Host "Confidence: $($response.confidence * 100)%"
        Write-Host "Risk Level: $($response.risk_level.ToUpper())"
        
        return $response
    }
    catch {
        Write-Error "Failed to check URL: $_"
    }
}

# Example usage
# Test-PhishingURL "https://google.com"
# Test-PhishingURL "http://paypal.com.verify.com"
"""

# ============================================================================
# EXAMPLE 4: Email Client Integration (VBA - Outlook)
# ============================================================================

OUTLOOK_VBA_INTEGRATION = """
' This code goes in Outlook VBA Editor (Alt+F11 while in Outlook)

Function CheckEmailLinks(mailItem As MailItem) As String
    Dim linkCount As Integer
    Dim httpRequest As Object
    Dim response As String
    Dim URL As String
    
    linkCount = 0
    
    ' Extract links from email body (simple regex)
    Dim regEx As Object
    Set regEx = CreateObject("VBScript.RegExp")
    regEx.Pattern = "https?://[^\\s]+"
    regEx.Global = True
    
    Dim matches As Object
    Set matches = regEx.Execute(mailItem.Body)
    
    For Each match In matches
        URL = match.Value
        
        Set httpRequest = CreateObject("MSXML2.XMLHTTP")
        With httpRequest
            .Open "GET", "http://127.0.0.1:5000/predict?url=" & URL, False
            .Send
            
            If .Status = 200 Then
                response = .responseText
                ' Check if phishing detected
                If InStr(response, "\\"is_phishing\\": true") > 0 Then
                    MsgBox "⚠️ PHISHING LINK DETECTED: " & URL
                End If
            End If
        End With
        
        linkCount = linkCount + 1
    Next
    
    CheckEmailLinks = "Checked " & linkCount & " links"
End Function

' Run this when email is received
' CheckEmailLinks ActiveInspector.CurrentItem
"""

# ============================================================================
# EXAMPLE 5: Slack Bot Integration
# ============================================================================

SLACK_BOT_INTEGRATION = """
# slack_bot.py - Slack bot to check URLs
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests

# Initialize
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
api_url = "http://127.0.0.1:5000"

@app.message("check")
def handle_check_request(message, say):
    '''Check URL when user says "check <url>"'''
    text = message["text"]
    
    # Extract URL from message
    import re
    urls = re.findall(r'https?://[^\\s]+', text)
    
    if not urls:
        say("Please provide a URL. Example: check https://example.com")
        return
    
    for url in urls:
        try:
            response = requests.get(f"{api_url}/predict", params={"url": url})
            result = response.json()
            
            status = "🚨 PHISHING" if result["is_phishing"] else "✅ SAFE"
            confidence = f"{result['confidence']:.0%}"
            risk = result["risk_level"].upper()
            
            say(f"{status}\\nURL: {url}\\nConfidence: {confidence}\\nRisk: {risk}")
        except Exception as e:
            say(f"Error checking URL: {e}")

@app.event("link_shared")
def handle_link_shared(ack, body):
    '''Auto-check links shared in Slack'''
    ack()
    
    links = body["links"]
    for link in links:
        url = link["url"]
        
        try:
            response = requests.get(f"{api_url}/predict", params={"url": url})
            result = response.json()
            
            if result["is_phishing"]:
                # Post warning
                app.client.chat_postMessage(
                    channel=body["channel"],
                    text=f"⚠️ WARNING: Potential phishing link detected!\\nURL: {url}\\nConfidence: {result['confidence']:.0%}"
                )
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
"""

# ============================================================================
# EXAMPLE 6: Mobile App Integration (React Native)
# ============================================================================

REACT_NATIVE_INTEGRATION = """
// PhishingDetector.js - React Native Integration

import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    Alert,
    StyleSheet,
    ActivityIndicator
} from 'react-native';

export default function PhishingDetector() {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    
    const checkURL = async () => {
        if (!url) {
            Alert.alert('Error', 'Please enter a URL');
            return;
        }
        
        setLoading(true);
        try {
            const response = await fetch(
                `http://127.0.0.1:5000/predict?url=${encodeURIComponent(url)}`
            );
            const data = await response.json();
            setResult(data);
            
            if (data.is_phishing) {
                Alert.alert(
                    '⚠️ WARNING',
                    `Phishing detected!\\nConfidence: ${(data.confidence * 100).toFixed(0)}%`
                );
            } else {
                Alert.alert('✅ Safe', 'This URL appears safe');
            }
        } catch (error) {
            Alert.alert('Error', 'Failed to check URL');
        }
        setLoading(false);
    };
    
    return (
        <View style={styles.container}>
            <Text style={styles.title}>🛡️ Phishing Detector</Text>
            
            <TextInput
                style={styles.input}
                placeholder="Enter URL"
                value={url}
                onChangeText={setUrl}
            />
            
            <TouchableOpacity
                style={styles.button}
                onPress={checkURL}
                disabled={loading}
            >
                {loading ? (
                    <ActivityIndicator color="#fff" />
                ) : (
                    <Text style={styles.buttonText}>Check URL</Text>
                )}
            </TouchableOpacity>
            
            {result && (
                <View style={styles.result}>
                    <Text style={{
                        color: result.is_phishing ? '#d32f2f' : '#2e7d32',
                        fontSize: 18,
                        fontWeight: 'bold'
                    }}>
                        {result.is_phishing ? 'PHISHING' : 'SAFE'}
                    </Text>
                    <Text>Confidence: {(result.confidence * 100).toFixed(0)}%</Text>
                    <Text>Risk: {result.risk_level.toUpperCase()}</Text>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#f5f5f5'
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
        textAlign: 'center'
    },
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        padding: 10,
        marginBottom: 10,
        borderRadius: 5,
        backgroundColor: '#fff'
    },
    button: {
        backgroundColor: '#667eea',
        padding: 12,
        borderRadius: 5,
        alignItems: 'center'
    },
    buttonText: {
        color: '#fff',
        fontWeight: 'bold',
        fontSize: 16
    },
    result: {
        marginTop: 20,
        padding: 15,
        backgroundColor: '#fff',
        borderRadius: 5
    }
});
"""

# ============================================================================
# MAIN: Print all examples
# ============================================================================

if __name__ == "__main__":
    examples = {
        "Browser Extension (JavaScript)": BROWSER_EXTENSION_JAVASCRIPT,
        "Desktop App (Python)": PYTHON_DESKTOP_INTEGRATION,
        "PowerShell": POWERSHELL_INTEGRATION,
        "Outlook VBA": OUTLOOK_VBA_INTEGRATION,
        "Slack Bot": SLACK_BOT_INTEGRATION,
        "React Native Mobile": REACT_NATIVE_INTEGRATION,
    }
    
    for name, code in examples.items():
        print(f"\n{'='*70}")
        print(f"{name}")
        print(f"{'='*70}")
        print(code)

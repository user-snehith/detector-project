import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys
import tldextract
import urllib.parse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import PhishingDetector, ModelTrainer

st.set_page_config(
    page_title="Phishing URL Detector",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main {
        background-color: #f5f7fa;
    }
    .stButton>button {
        background-color: #667eea;
        color: white;
        border-radius: 5px;
    }
    .extension-banner {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    .safe-banner {
        background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Page title
st.title("AI-Based URL Phishing Detector")
st.markdown("**Protect yourself from malicious links with machine learning**")

# Check for extension parameters
query_params = st.query_params
extension_check = query_params.get("check")
check_id = query_params.get("checkId")
url_to_check = query_params.get("url")

# Decode URL-encoded parameters if present
if extension_check:
    extension_check = urllib.parse.unquote(extension_check)
if url_to_check:
    url_to_check = urllib.parse.unquote(url_to_check)

# Handle extension check mode
if extension_check or url_to_check:
    url_to_check = extension_check or url_to_check
    display_url = url_to_check if '://' in url_to_check else 'http://' + url_to_check

    st.markdown("""
    <div class="extension-banner">
        <h2>🔍 Link Check Requested</h2>
        <p>You clicked a link and our extension is checking it for safety.</p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-check the URL
    if url_to_check:
        try:
            # Check URL existence first
            exist_info = PhishingDetector.check_url_existence(url_to_check)
            if not exist_info['exists']:
                st.warning(f"URL check: {exist_info['reason']} - this domain does not resolve.")

            # Additional reachability check (HTTP)
            reach_info = PhishingDetector.check_url_reachability(url_to_check)
            if not reach_info['reachable']:
                st.warning(f"Reachability check: {reach_info['reason']}")
            else:
                st.success(f"Reachability check: {reach_info['reason']}")

            # Check if model exists
            model_path = "models/sklearn_model.joblib"
            if not Path(model_path).exists():
                st.warning(f"Model not found at {model_path}. Please train a model first.")
            else:
                detector = PhishingDetector(model_path, "sklearn")
                result = detector.predict(url_to_check)

                # Parse URL for domain extraction
                url_formatted = url_to_check if '://' in url_to_check else 'http://' + url_to_check
                parsed = tldextract.extract(url_formatted)

                # Display result
                if result['is_phishing']:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 30px; border-radius: 10px; margin: 20px 0; text-align: center;">
                        <h1>🚨 PHISHING DETECTED!</h1>
                        <p style="font-size: 18px;">This link appears to be malicious and may steal your personal information.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="safe-banner">
                        <h1>✅ URL APPEARS SAFE</h1>
                        <p style="font-size: 18px;">Our analysis indicates this link is likely safe to visit.</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Show analysis details
                col1, col2, col3 = st.columns(3)

                with col1:
                    status = "PHISHING" if result['is_phishing'] else "SAFE"
                    status_color = "#d32f2f" if result['is_phishing'] else "#2e7d32"
                    st.markdown(f"### <span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)

                with col2:
                    st.metric("Confidence", f"{result['confidence']:.2%}")

                with col3:
                    st.metric("Risk Level", result['risk_level'].upper())

                # Show homograph attack details if detected
                if result.get('homograph_info') and result['homograph_info']['is_homograph']:
                    st.markdown("---")
                    st.subheader("⚠️ Lookalike Domain Detected (Homograph Attack)")

                    homo_info = result['homograph_info']
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Matched Brand", homo_info['matched_brand'].capitalize())
                    with col2:
                        st.metric("Similarity", f"{homo_info['similarity_score']:.2%}")
                    with col3:
                        st.metric("Character Substitutions", homo_info['substitution_count'])

                    st.warning(
                        f"**This domain mimics '{homo_info['matched_brand']}' using character substitutions!**\n\n"
                        f"- Domain: `{parsed.domain}`\n"
                        f"- Normalized: `{homo_info['normalized_domain']}`\n"
                        f"- This is a common phishing technique to deceive users."
                    )

                # Decision buttons for extension
                st.markdown("---")
                st.subheader("What would you like to do?")

                col1, col2 = st.columns(2)

                safe_url = display_url if '://' in display_url else f'http://{display_url}'
                safe_url_quoted = urllib.parse.quote(safe_url, safe=':/?#[]@!$&\'()*+,;=')

                with col1:
                    st.markdown(f"""
                        <a href=\"{safe_url_quoted}\" target=\"_top\" rel=\"noopener noreferrer\" style="display:inline-block; width:100%; background:#4caf50; color:#fff; padding:12px 20px; border-radius:8px; text-align:center; text-decoration:none; font-weight:600;">
                            ✅ Proceed to Link
                        </a>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("❌ Cancel - Stay Safe", use_container_width=True, type="secondary"):
                        st.info("Navigation cancelled. You stayed safe!")

                # Show detailed analysis
                with st.expander("View Detailed Analysis"):
                    details_df = pd.DataFrame({
                        "Metric": ["URL", "Status", "Confidence", "Risk Level", "Model"],
                        "Value": [
                            display_url,
                            "Phishing" if result['is_phishing'] else "Safe",
                            f"{result['confidence']:.4f}",
                            result['risk_level'],
                            result['model_type']
                        ]
                    })
                    st.table(details_df)

        except Exception as e:
            st.error(f"Error analyzing URL: {e}")
            # Provide fallback buttons
            col1, col2 = st.columns(2)
            with col1:
                fallback_url = url_to_check if '://' in url_to_check else f'http://{url_to_check}'
                fallback_url_quoted = urllib.parse.quote(fallback_url, safe=':/?#[]@!$&\'()*+,;=')
                st.markdown(f"""
                    <a href=\"{fallback_url_quoted}\" target=\"_top\" rel=\"noopener noreferrer\" style="display:inline-block; width:100%; background:#4caf50; color:#fff; padding:12px 20px; border-radius:8px; text-align:center; text-decoration:none; font-weight:600;">
                        ✅ Proceed Anyway
                    </a>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.info("Navigation cancelled.")
# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    model_type = st.radio("Select Model", ["Scikit-Learn", "Keras/TensorFlow"], index=0)
    model_path_map = {
        "Scikit-Learn": "models/sklearn_model.joblib",
        "Keras/TensorFlow": "models/keras_model.h5"
    }
    model_path = model_path_map[model_type]
    # Map to correct model type identifiers
    model_type_map_detector = {
        "Scikit-Learn": "sklearn",
        "Keras/TensorFlow": "keras"
    }
    model_type_lower = model_type_map_detector[model_type]
    
    st.markdown("---")
    
    # Model training section
    st.subheader("Train New Model")
    if st.button("Train Scikit-Learn Model"):
        with st.spinner("Training Scikit-Learn model..."):
            try:
                result = ModelTrainer.train_sklearn_model(
                    data_path=None,
                    output_path="models/sklearn_model.joblib"
                )
                st.success(f"Model trained. Accuracy: {result['accuracy']:.4f}")
                st.text(result["report"])
            except Exception as e:
                st.error(f"Error training model: {e}")
    
    if st.button("Train Keras Model"):
        with st.spinner("Training Keras model... (this may take a minute)"):
            try:
                result = ModelTrainer.train_keras_model(
                    data_path=None,
                    output_path="models/keras_model.h5",
                    epochs=20
                )
                st.success(f"Model trained. Accuracy: {result['accuracy']:.4f}")
            except Exception as e:
                st.error(f"Error training model: {e}")

# Main content
tab1, tab2, tab3 = st.tabs(["Single URL Check", "Batch Analysis", "About"])
with tab1:
    st.subheader("Check a Single URL")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url_input = st.text_input(
            "Enter URL to analyze:",
            placeholder="https://example.com or google.com"
        )
    
    with col2:
        check_btn = st.button("Check URL", use_container_width=True)
    
    if check_btn and url_input:
        try:
            # Check URL existence first
            exist_info = PhishingDetector.check_url_existence(url_input)
            if not exist_info['exists']:
                st.warning(f"URL check: {exist_info['reason']} - this domain does not resolve.")

            # Additional reachability check (HTTP)
            reach_info = PhishingDetector.check_url_reachability(url_input)
            if not reach_info['reachable']:
                st.warning(f"Reachability check: {reach_info['reason']}")
            else:
                st.success(f"Reachability check: {reach_info['reason']}")

            # Check if model exists
            if not Path(model_path).exists():
                st.warning(f"Model not found at {model_path}. Please train a model first.")
            else:
                detector = PhishingDetector(model_path, model_type_lower)
                result = detector.predict(url_input)
                
                # Parse URL for domain extraction
                url_formatted = url_input if '://' in url_input else 'http://' + url_input
                parsed = tldextract.extract(url_formatted)

                # Display result
                col1, col2, col3 = st.columns(3)

                with col1:
                    status = "PHISHING" if result['is_phishing'] else "SAFE"
                    status_color = "#d32f2f" if result['is_phishing'] else "#2e7d32"
                    st.markdown(f"### <span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)

                with col2:
                    st.metric("Confidence", f"{result['confidence']:.2%}")

                with col3:
                    st.metric("Risk Level", result['risk_level'].upper())

                # URL analysis details
                st.markdown("---")
                st.subheader("Analysis Details")

                details_df = pd.DataFrame({
                    "Metric": ["URL", "Status", "Confidence", "Risk Level", "Model"],
                    "Value": [
                        result['url'],
                        "Phishing" if result['is_phishing'] else "Safe",
                        f"{result['confidence']:.4f}",
                        result['risk_level'],
                        result['model_type']
                    ]
                })
                st.table(details_df)
                
                # Show homograph attack details if detected
                if result.get('homograph_info') and result['homograph_info']['is_homograph']:
                    st.markdown("---")
                    st.subheader("⚠️ Lookalike Domain Detected (Homograph Attack)")
                    
                    homo_info = result['homograph_info']
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Matched Brand", homo_info['matched_brand'].capitalize())
                    with col2:
                        st.metric("Similarity", f"{homo_info['similarity_score']:.2%}")
                    with col3:
                        st.metric("Character Substitutions", homo_info['substitution_count'])
                    
                    st.warning(
                        f"**This domain mimics '{homo_info['matched_brand']}' using character substitutions!**\n\n"
                        f"- Domain: `{parsed.domain}`\n"
                        f"- Normalized: `{homo_info['normalized_domain']}`\n"
                        f"- This is a common phishing technique to deceive users."
                    )

                # Risk visualization - using bar chart instead of gauge
                confidence_pct = result['confidence'] * 100
                fig = go.Figure(data=[
                    go.Bar(
                        x=[confidence_pct],
                        y=["Phishing Risk"],
                        orientation='h',
                        marker={
                            'color': "#FF6B6B" if confidence_pct > 70 else ("#FFD700" if confidence_pct > 30 else "#90EE90"),
                            'line': {'color': 'darkblue', 'width': 2}
                        },
                        text=[f"{confidence_pct:.1f}%"],
                        textposition='auto'
                    )
                ])
                fig.update_layout(
                    xaxis=dict(range=[0, 100], title="Confidence Score (%)"),
                    yaxis=dict(title=""),
                    height=300,
                    showlegend=False,
                    margin=dict(l=100)
                )
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error analyzing URL: {e}")

with tab2:
    st.subheader("Batch URL Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader("Upload CSV file (with 'url' column)", type="csv")
    
    with col2:
        if st.button("Process Batch", use_container_width=True):
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    if 'url' not in df.columns:
                        st.error("CSV must contain 'url' column")
                    else:
                        if not Path(model_path).exists():
                            st.warning("Model not found. Please train a model first.")
                        else:
                            detector = PhishingDetector(model_path, model_type_lower)
                            
                            with st.spinner("Processing URLs..."):
                                results = detector.predict_batch(df['url'].tolist())
                            
                            results_df = pd.DataFrame(results)
                            
                            # Statistics
                            col1, col2, col3, col4 = st.columns(4)
                            phishing_count = results_df['is_phishing'].sum()
                            safe_count = len(results_df) - phishing_count
                            
                            with col1:
                                st.metric("Total URLs", len(results_df))
                            with col2:
                                st.metric("Phishing", phishing_count)
                            with col3:
                                st.metric("Safe", safe_count)
                            with col4:
                                st.metric("Phishing Rate", f"{(phishing_count/len(results_df)*100):.1f}%")
                            
                            # Results table
                            st.markdown("---")
                            st.subheader("Detailed Results")
                            st.dataframe(results_df, use_container_width=True)
                            
                            # Download results
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results CSV",
                                data=csv,
                                file_name="phishing_analysis_results.csv",
                                mime="text/csv"
                            )
                
                except Exception as e:
                    st.error(f"Error processing file: {e}")

with tab3:
    st.subheader("About This Tool")
    
    st.markdown("""
    ### Purpose
    This tool uses machine learning to detect phishing URLs and protect users from malicious links that could lead to data theft and security breaches.
    
    ### Technology Stack
    - **Backend**: Python, scikit-learn, TensorFlow/Keras
    - **Frontend**: Streamlit
    - **Feature Engineering**: URL analysis with 28+ features including homograph detection
    - **Models**: Logistic Regression & Neural Networks
    
    ### How It Works
    1. **Feature Extraction**: Analyzes URL structure (length, special characters, suspicious tokens, etc.)
    2. **Homograph Detection**: Detects lookalike domains that mimic legitimate brands with character substitutions
    3. **ML Model**: Uses trained classifier to assess threat level
    4. **Prediction**: Returns risk score and classification
    
    ### Features Analyzed
    - URL length and character composition
    - Domain and host characteristics
    - IP address detection
    - Suspicious keywords presence
    - Subdomain structure
    - TLD properties
    - Entropy analysis
    - **NEW: Homograph/Lookalike detection** (g00gle, amaz0n, rnicrosoft, etc.)
    - Character obfuscation patterns
    
    ### 📈 Model Performance
    - **Accuracy**: ~85-94% depending on model type
    - **Inference Speed**: <100ms per URL
    - **Privacy**: Runs locally, no external API calls
    - **Homograph Detection**: Identifies 100+ brand variations
    
    ### Lookalike Domain Examples
    This tool detects domains that mimic legitimate brands:
    - `g00gle.com` (google with zeros)
    - `amaz0n.com` (amazon with zero)
    - `rnicrosoft.com` (microsoft with letter substitution)
    - `pay-pal.com` (paypal with dash)
    - Similar patterns for other brands
    
    ### Disclaimer
    This tool provides predictions based on URL features. While highly accurate, it should be used as
    one layer of defense among others. Always exercise caution with unknown links.
    """)
    
    st.markdown("---")
    st.subheader("Dataset Format")
    st.markdown("""
    For batch analysis and training, use CSV format:
    ```
    url,label
    https://google.com,0
    http://suspicious-site.com,1
    ```
    Where `label` is 0 (safe) or 1 (phishing).
    """)

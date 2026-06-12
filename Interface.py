import streamlit as st
from PIL import Image
import json
import pandas as pd
import base64
from File_Parser import PolicyProcessor

# ==============================================================================
# BUG FIX 1: Added a try-except block to prevent FileNotFoundError crashes
# if the local images (like VanpontRisk.png) are missing from the directory.
# ==============================================================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        # Returns a blank transparent 1x1 pixel if the image is missing
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="



def clean_and_format_value(val) -> str:
    if val is None: return "N/A"
    if isinstance(val, (int, float)): return f"${val:,.0f}"
    if isinstance(val, list): return " / ".join([clean_and_format_value(x) for x in val])
    if isinstance(val, dict): return " | ".join([f"{str(k).title()}: {clean_and_format_value(v)}" for k, v in val.items()])
    val_str = str(val).strip()
    try:
        clean_numeric_str = val_str.replace('$', '').replace(',', '').strip()
        numeric_value = float(clean_numeric_str)
        if numeric_value.is_integer(): return f"${int(numeric_value):,}"
        return f"${numeric_value:,.2f}"
    except ValueError:
        return val_str

def render_coverage_sections(json_data):

    if not json_data:
        st.warning("No policy data returned.")
        return

    if "coverage_parts" not in json_data:
        st.info("No coverage parts found in the extracted policy.")
        return

    coverage_parts = json_data["coverage_parts"]

    for part_name, coverages in coverage_parts.items():
        st.markdown(f"<h3 style='margin-top:20px;'>{part_name}</h3>", unsafe_allow_html=True)

        rows = []
        for cov in coverages:
            rows.append({
                "Coverage": cov.get("name", "N/A"),
                "Limit": clean_and_format_value(cov.get("limit")),
                "Deductible": clean_and_format_value(cov.get("deductible"))
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ==============================================================================
# 2. STREAMLIT APPLICATION CONFIGURATION & EXACT CSS OVERRIDES
# ==============================================================================
try:
    image_icon = Image.open("VanpontRisk.png")
    st.set_page_config(page_title="Insurance Policy Risk Auditor", page_icon=image_icon, layout="wide")
except FileNotFoundError:
    st.set_page_config(page_title="Insurance Policy Risk Auditor", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Canvas Architecture overrides */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #F8FAFC !important;
    }
    .main .block-container {
        padding: 2.5rem 4rem !important;
    }

    /* PERSISTENT CUSTOM DARK NAVIGATION SIDEBAR DESIGN */
    [data-testid="stSidebar"] {
        background-color: #0A1128 !important;
        color: #F1F5F9 !important;
        min-width: 280px !important;
    }
    [data-testid="stSidebar"] hr {
        border-top: 1px solid #1E293B !important;
        margin: 16px 0 !important;
    }
    .sidebar-logo-text {
        font-size: 26px; font-weight: 800; color: #FFFFFF; letter-spacing: -1px; margin: 0; text-align: center;
    }
    .sidebar-sub-logo {
        font-size: 10px; font-weight: 700; color: #38BDF8; letter-spacing: 2px; margin: -5px 0 20px 0; text-align: center;
    }
    .sidebar-section-title {
        font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;
    }
    .nav-item-active {
        background-color: #1E3A8A !important; color: #FFFFFF !important; padding: 10px 14px; border-radius: 8px; font-weight: 600; display: flex; align-items: center; gap: 10px; margin-bottom: 6px;
    }
    .nav-item-inactive {
        color: #94A3B8 !important; padding: 10px 14px; border-radius: 8px; font-weight: 500; display: flex; align-items: center; gap: 10px; margin-bottom: 6px; cursor: pointer;
    }

    /* CORE WORKSPACE PROCESS STEP RUNNING LOGIC DISPLAY */
    .pipeline-container {
        display: flex; justify-content: space-between; align-items: center; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 24px; margin-bottom: 24px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .step-item { display: flex; align-items: center; gap: 12px; }
    .step-icon { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 14px; }
    .step-icon.active { background-color: #2563EB; color: #FFFFFF; }
    .step-icon.pending { background-color: #F1F5F9; color: #64748B; border: 1px solid #E2E8F0; }
    .step-text b { font-size: 14px; color: #0F172A; display: block; }
    .step-text span { font-size: 12px; color: #64748B; }
    .step-line { flex-grow: 1; height: 1px; background-color: #E2E8F0; margin: 0 16px; }

    /* CORE METRIC STAT CARDS DESIGNS */
    .kpi-box {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .kpi-icon-frame { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
    .kpi-meta p { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; margin: 0; letter-spacing: 0.5px; }
    .kpi-meta h2 { font-size: 28px; font-weight: 700; color: #0F172A; margin: 2px 0; }
    .kpi-meta span { font-size: 12px; color: #64748B; }

    /* DASHBOARD CARD CONTAINERS AND PLACEHOLDERS */
    .dashboard-card {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; min-height: 380px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); margin-bottom: 24px;
    }
    .card-title { font-size: 18px; font-weight: 600; color: #0F172A; margin: 0 0 8px 0; display: flex; align-items: center; gap: 8px; }
    .card-subtitle { font-size: 13px; color: #64748B; margin-bottom: 24px; line-height: 1.5; }
    
    /* RIGHT CARD LIST STYLING */
    .feature-list { list-style: none; padding: 0; margin: 0; }
    .feature-list li { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; font-size: 14px; color: #334155; font-weight: 500; }
    .check-icon { background-color: #2563EB; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; justify-content: center; align-items: center; font-size: 10px; }
    .card-footer { display: flex; justify-content: space-between; font-size: 12px; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 16px; margin-top: 40px;}

    /* RECENT ANALYSES TABLE */
    .recent-table-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    .table-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid #E2E8F0; padding-bottom: 16px; }
    .table-headers { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr 1fr; font-size: 12px; font-weight: 600; color: #64748B; padding-bottom: 12px; }
    .empty-state { text-align: center; padding: 40px 0; }
    .empty-state p { margin: 4px 0; color: #64748B; font-size: 13px; }
    .empty-state h4 { margin: 0; color: #0F172A; font-size: 15px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. SIDEBAR COMPONENT TREE (Uploader Removed)
# ==============================================================================
dashboard = get_base64_image("dash.png")
policy_icon = get_base64_image("Policy.png")
analysis_icon = get_base64_image("Analysis.png")
report_icon = get_base64_image("Report.png")
alert_icon = get_base64_image("Alert.png")
setting_icon = get_base64_image("Settings.png")

with st.sidebar:

    try:
        st.image("VanpontRisk.png", use_container_width=True)
    except FileNotFoundError:
        st.markdown("<h2 class='sidebar-logo-text'>VanpontRisk</h2>", unsafe_allow_html=True)

    st.markdown('<p class="sidebar-section-title" style="margin-top: 20px;">Workspace</p>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="nav-item-inactive"><img src="data:image/png;base64,{dashboard}" width="40" style="vertical-align: middle; margin-right: 8px;"> Dashboard</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="nav-item-inactive"><img src="data:image/png;base64,{policy_icon}" width="40" style="vertical-align: middle; margin-right: 8px;"> Policies</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="nav-item-inactive"><img src="data:image/png;base64,{analysis_icon}" width="40" style="vertical-align: middle; margin-right: 8px;"> Analysis</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="nav-item-inactive"><img src="data:image/png;base64,{report_icon}" width="40" style="vertical-align: middle; margin-right: 8px;"> Report</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="nav-item-inactive"><img src="data:image/png;base64,{alert_icon}" width="40" style="vertical-align: middle; margin-right: 8px;"> Alerts</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="nav-item-inactive"><img src="data:image/png;base64,{setting_icon}" width="40" style="vertical-align: middle; margin-right: 8px;"> Settings</div>',
        unsafe_allow_html=True
    )


    st.markdown('<p class="sidebar-section-title">System Status</p>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px; color:#10B981; margin:0; font-weight:600;'>● Ready</p><span style='font-size:11px; color:#64748B;'>All systems operational</span>", unsafe_allow_html=True)
    st.caption("Beta Engine v1.6.0")

# ==============================================================================
# 4. MAIN DASHBOARD CONTENT GRID INTERFACE
# ==============================================================================
# HEADER
st.markdown("<h1 style='color: #0F172A; font-size: 28px; font-weight:700; letter-spacing: -0.5px; margin-bottom: 4px;'>Insurance Policy Risk Auditor</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 14px; margin-top: 0; margin-bottom:28px;'>Upload a policy package and receive a complete coverage analysis, gap assessment, and risk summary.</p>", unsafe_allow_html=True)

# Create an empty container at the top for the Pipeline & KPIs
# This allows us to render them visually at the top, but define them later in the script
# after we have grabbed the uploaded files!
top_metrics_container = st.container()

# MIDDLE ROW: Upload Card and Ready Card
col1, col2 = st.columns([1.1, 1])

with col1:
    selected_type= st.selectbox(
        label="Is the client a commercial or personal lines holder?",
        options=["Commercial", "Personal"],
        index=0  # Optional: Sets the default selected item (0 is the first item)
    )

    if selected_type == "Commercial":
        selected_Lease_Bool= st.selectbox(
            label="Does the client own the building for business operations",
            options=["Yes", "No"],
            index=0  # Optional: Sets the default selected item (0 is the first item)
        )
        st.markdown("""
        <div class="dashboard-card" style="padding-bottom: 10px; margin-bottom: 0px; min-height: auto;">
            <div class="card-title">📄 Upload Policy Package</div>
            <div class="card-subtitle">Upload your insurance policy packet (declarations, forms, endorsements, and schedules) as PDF files to begin the analysis.</div>
        </div>
        """, unsafe_allow_html=True)

        # The REAL uploader placed right below the text in the column
        uploaded_file = st.file_uploader("Upload PDF here", accept_multiple_files=False, type="pdf", key="main_upload", label_visibility="collapsed")
        st.spinner(text="In progress...", show_time=True, width="content")

        st.markdown("""
            <div style="text-align: center; font-size: 11px; color: #64748B; margin-top: 8px; margin-bottom: 24px;">
                🔒 Your files are secure and encrypted. They are only used for analysis.
            </div>
        """, unsafe_allow_html=True)
    else:
        print("We do not offer our services for personal lines due to domestic regulations")

@st.cache_resource
def get_processor():
    return PolicyProcessor(api_key='AQ.Ab8RN6Jx1Oeqrhmgf_0U5Y7njJ5AcOi4b6tpGYDH0iGIKR0xKw')

processor = get_processor()

json_data = None

if uploaded_file:
    with st.spinner("Extracting and analyzing policy..."):
        uploaded_file.seek(0)
        raw_text = processor.extract_text_from_pdf(uploaded_file)

        uploaded_file.seek(0)
        json_text = processor.parse_policy(raw_text)

        try:
            json_data = json.loads(json_text)
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON.")
            st.text(json_text)





with col2:
    my_custom_css = """
    <style>
        .feature-list { list-style: none; padding: 0; margin: 0; }
        .feature-list li { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; font-size: 14px; color: #334155; font-weight: 500; }
        .check-icon { background-color: #2563EB; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; justify-content: center; align-items: center; font-size: 10px; }
    </style>
    """

    # 2. Inject it into the Streamlit app
    st.markdown(my_custom_css, unsafe_allow_html=True)

    # 3. Use it in your layout
    st.markdown("""
        <ul class="feature-list">
            <li><div class="check-icon">✓</div> Multi-peril policy parsing</li>
        </ul>
    """, unsafe_allow_html=True)
    st.markdown("""
        <ul class="feature-list">
            <li><div class="check-icon">✓</div> Risk and Exposure Identification</li>
        </ul>
    """, unsafe_allow_html=True)
    st.markdown("""
        <ul class="feature-list">
            <li><div class="check-icon">✓</div> Actionable Recommendations</li>
        </ul>
    """, unsafe_allow_html=True)

# ==============================================================================
# CALCULATE METRICS AND POPULATE TOP CONTAINER
# ==============================================================================

if json_data:
    render_coverage_sections(json_data)
    gap = 0
    if selected_Lease_Bool =="Yes":
        if "Building Coverage Part" in json_data:
            gap = 0
        else:
            gap =1
    else:
        gap = 0

    col_kpi = st.columns(1)
    with col_kpi[0]:

    # Logic to calculate total gaps across the entire policy
        total_gaps = gap

        if total_gaps >0:
            dict = {"gap":gap,
                    "Gap Type":"No Building Coverage"}
        else:
            dict = {"gap":gap,
                    "Gap Type":"No Gaps"}

        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-icon-frame" style="background: #FEF2F2; color: #DC2626;">
                    ⚠️
                </div>
                <div class="kpi-meta">
                    <p>Total Gaps</p>
                    <h2>{total_gaps}</h2>
                    <span>{dict.get('Gap Type','None')}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)




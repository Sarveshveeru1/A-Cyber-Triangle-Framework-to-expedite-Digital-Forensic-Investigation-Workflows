# streamlit_app.py

import streamlit as st
import json
import os
from analyzer.system_info import save_system_info_to_file
from analyzer.log_parser import parse_evtx_file
from analyzer.malware_scanner import run_virus_scan
from analyzer.timeline_generator import generate_timeline
from analyzer.report_generator import generate_html_report, generate_pdf_report
from utils.s3_uploader import upload_to_s3
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS config
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

# Helper functions
def list_s3_files(prefix="triage_reports/"):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
    return [obj["Key"] for obj in response.get("Contents", []) if obj["Key"] != prefix]

def download_s3_file(file_key):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    download_path = os.path.join("output", os.path.basename(file_key))
    s3.download_file(S3_BUCKET, file_key, download_path)
    return download_path

# Streamlit UI
st.set_page_config(page_title="Cyber Triage Tool", layout="centered")
st.title("🛡️ Cyber Triage Tool")

tabs = st.tabs(["🏠 Home", "🛠️ Run Analysis", "📂 View Reports"])

# Tab 1: Home
with tabs[0]:
    st.subheader("Welcome to the Cyber Triage Tool")
    st.write("""
    This tool helps you collect and review key system forensic artifacts.  
    It performs:
    - System info collection (user, OS, memory, disk)
    - Parses Windows Event Logs (Application, Security, System)
    - Scans binaries in Downloads folder using VirusTotal
    - Generates a unified timeline
    - Generates a final triage report (HTML + PDF)
    - Uploads all results to AWS S3
    """)

# Tab 2: Run Analysis
with tabs[1]:
    st.subheader("🛠️ Run Forensic Analysis")

    # 1. System Info
    if st.button("Collect System Info"):
        sys_info_path = "output/system_info.json"
        save_system_info_to_file(sys_info_path)
        st.success("✅ System information collected.")
        with open(sys_info_path) as f:
            st.json(json.load(f))
        upload_to_s3(sys_info_path, "triage_reports/system_info.json")
        st.success("📤 System info uploaded to S3.")

    # 2A. Application Log Parser
    if st.button("Parse Application Logs"):
        st.info("📘 Parsing Application.evtx...")
        output_path = parse_evtx_file("data/Application.evtx", output_path="output/app_log_summary.json")
        with open(output_path) as f:
            st.json(json.load(f))
        upload_to_s3(output_path, "triage_reports/app_log_summary.json")
        st.success("📤 Application log uploaded to S3.")

    # 2B. Security Log Parser
    if st.button("Parse Security Logs"):
        st.info("🔐 Parsing Security.evtx...")
        output_path = parse_evtx_file("data/Security.evtx", output_path="output/security_log_summary.json")
        with open(output_path) as f:
            st.json(json.load(f))
        upload_to_s3(output_path, "triage_reports/security_log_summary.json")
        st.success("📤 Security log uploaded to S3.")

    # 2C. System Log Parser
    if st.button("Parse System Logs"):
        st.info("⚙️ Parsing System.evtx...")
        output_path = parse_evtx_file("data/System.evtx", output_path="output/system_log_summary.json")
        with open(output_path) as f:
            st.json(json.load(f))
        upload_to_s3(output_path, "triage_reports/system_log_summary.json")
        st.success("📤 System log uploaded to S3.")

    # 3. Malware Scan
    if st.button("Run Malware Scan (VirusTotal)"):
        st.info("🦠 Scanning Downloads folder using VirusTotal...")
        vt_report_path = run_virus_scan("C:\\Users\\pradeep\\Downloads")
        with open(vt_report_path) as f:
            st.json(json.load(f))
        upload_to_s3(vt_report_path, "triage_reports/virus_scan_report.json")
        st.success("📤 Virus scan report uploaded to S3.")

    # 4. Timeline Generator
    if st.button("Generate Timeline"):
        st.info("📅 Creating chronological forensic timeline...")
        timeline_path = generate_timeline()
        with open(timeline_path) as f:
            st.json(json.load(f))
        upload_to_s3(timeline_path, "triage_reports/timeline.json")
        st.success("📤 Timeline report uploaded to S3.")

    # 5. Generate Triage Report (HTML + PDF)
    if st.button("Generate PDF/HTML Triage Report"):
        st.info("📝 Generating Triage Report...")
        html_path = generate_html_report()
        pdf_path = generate_pdf_report(html_path)

        if pdf_path:
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download PDF Report", f, file_name="triage_report.pdf")

            upload_to_s3(pdf_path, "triage_reports/triage_report.pdf")
            st.success("📤 Triage PDF uploaded to S3.")
        else:
            st.error("❌ Failed to generate PDF report. Make sure wkhtmltopdf is installed.")

# Tab 3: View Reports
with tabs[2]:
    st.subheader("📂 Reports Available in S3")

    files = list_s3_files()
    if not files:
        st.info("No reports found in S3.")
    else:
        for file_key in files:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(file_key)
            with col2:
                if st.button("Download", key=file_key):
                    path = download_s3_file(file_key)
                    with open(path, "rb") as f:
                        st.download_button("Click to Download", f, file_name=os.path.basename(path))

import os
import json
import pdfkit
from jinja2 import Environment, FileSystemLoader

# Path to wkhtmltopdf executable
WKHTMLTOPDF_PATH = r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"

def load_json(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return json.load(f)

def generate_html_report(
    system_info_path="output/system_info.json",
    log_summary_path="output/security_log_summary.json",
    vt_report_path="output/virus_scan_report.json",
    timeline_path="output/timeline.json",
    output_html="output/triage_report.html"
):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("triage_report_template.html")

    context = {
        "system_info": load_json(system_info_path),
        "logs": load_json(log_summary_path),
        "vt_results": load_json(vt_report_path),
        "timeline": load_json(timeline_path)
    }

    html_out = template.render(context)

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"✅ HTML report generated at {output_html}")
    return output_html

def generate_pdf_report(input_html="output/triage_report.html", output_pdf="output/triage_report.pdf"):
    try:
        config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
        pdfkit.from_file(input_html, output_pdf, configuration=config)
        print(f"✅ PDF report generated at {output_pdf}")
        return output_pdf
    except Exception as e:
        print(f"❌ PDF generation failed: {str(e)}")
        return None

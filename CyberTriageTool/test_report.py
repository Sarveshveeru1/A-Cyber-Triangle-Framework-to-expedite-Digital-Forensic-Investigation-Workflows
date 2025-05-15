from analyzer.report_generator import generate_html_report, generate_pdf_report

html_path = generate_html_report()
generate_pdf_report(html_path)

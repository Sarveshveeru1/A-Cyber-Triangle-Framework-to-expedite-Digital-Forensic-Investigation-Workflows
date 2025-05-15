# test_upload.py

from utils.s3_uploader import upload_to_s3

upload_to_s3("output/system_info.json", "triage_reports/system_info.json")

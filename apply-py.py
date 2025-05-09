import os
import json
import gspread
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SHEETS_NAME = "apply-py"
SENDER_EMAIL = "magbanuaezra@gmail.com"
APP_PASSWORD = os.environ["APP_PASSWORD"]
FILE_NAME = "Resume_MagbanuaEzra.pdf"
FILE_PATH = "Resume_MagbanuaEzra.pdf"

SUBJECT_LINE = "Internship Inquiry – Software Engineering"
GENERIC_MESSAGE_TXT_PATH = "generic-message.txt"
GENERIC_BODY_MESSAGE = ""
with open(GENERIC_MESSAGE_TXT_PATH, "r") as file:
    line = file.readline()
    while line:
        GENERIC_BODY_MESSAGE += line
        line = file.readline()

SERVICE_CREDENTIALS = json.loads(os.environ["SERVICE_ACCOUNT"])
gc = gspread.service_account_from_dict(SERVICE_CREDENTIALS)
sh = gc.open(SHEETS_NAME)
worksheet = sh.sheet1
worksheet_data = worksheet.get_all_values()[1:]

with smtplib.SMTP("smtp.gmail.com", 587) as s:
    s.starttls()
    s.login("magbanuaezra@gmail.com", APP_PASSWORD)

    for idx in range(len(worksheet_data)):
        company = worksheet_data[idx][0]
        receiver = worksheet_data[idx][1]
        status = worksheet_data[idx][2]

        if status != "":
            continue

        body_header = f"Good day {company},\n\n"
        body_content = body_header + GENERIC_BODY_MESSAGE

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver
        msg["Subject"] = SUBJECT_LINE
        msg.attach(MIMEText(body_content, "plain"))

        attachment = open(FILE_PATH, "rb")
        p = MIMEBase("application", "octet-stream")
        p.set_payload((attachment).read())
        attachment.close()

        encoders.encode_base64(p)
        p.add_header("Content-Disposition", "attachment; filename= %s" % FILE_NAME)
        msg.attach(p)

        print(f"Sending email to {receiver}")
        s.sendmail(SENDER_EMAIL, receiver, msg.as_string())
        print(f"Sent email to {receiver} ✔")
        worksheet.update_cell(idx + 2, 3, "✔")

    print("Finished")

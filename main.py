import os
import smtplib
import json
import matplotlib.pyplot as plt
import numpy as np
import imghdr
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.message import EmailMessage
from credentials import EMAIL_ADDRESS, EMAIL_PASSWORD, MY_EMAIL_ADDRESS, DRIVER_PATH


def makeProperDate(date):
    return f"{date[8:10]}.{date[5:7]}.{date[2:4]}"


# EMAIL_ADDRESS = os.getenv("EMAIL_USER", "None")
# EMAIL_PASSWORD = os.getenv("EMAIL_PASS", "None")
# MY_EMAIL_ADDRESS = os.getenv("MY_EMAIL", "None")

chromeOptions = Options()
chromeOptions.add_argument("--headless")
# driver = webdriver.Chrome(DRIVER_PATH, options=chromeOptions)
driver = webdriver.Chrome(DRIVER_PATH)
driver.maximize_window()
driver.get("https://www.gov.pl/web/koronawirus/wykaz-zarazen-koronawirusem-sars-cov-2")

print("start timer")
time.sleep(60)
print("end timer")

driver.execute_script("window.scrollTo(0, 400)") 
s = driver.get_window_size()
w = driver.execute_script('return document.body.parentNode.scrollWidth')
h = driver.execute_script('return document.body.parentNode.scrollHeight')
driver.set_window_size(w, h)
driver.find_element_by_tag_name('body').screenshot("screenshot.png")
driver.set_window_size(s['width'], s['height'])
# driver.save_screenshot("screen.png")
driver.quit()

with open("./data.json") as file:
    data = json.load(file)

finalMessage = str(json.dumps(data["table"][-1], indent=2))
finalMessage = finalMessage + "\n\n~~~~~~~~~~~~\n\n"
for entry in reversed(data["table"]):
    finalMessage = finalMessage + f"{makeProperDate(entry['lastUpdatedAtSource'][0:10])} - "
    finalMessage = finalMessage + f"{entry['dailyInfected']} cases, {entry['dailyDeceased']} deaths, {entry['dailyTested']} tests\n"

plt.style.use("fivethirtyeight")
plt.rcParams.update({"font.size": 9})
dates = []
cases = []
for entry in data["table"]:
    dates.append(makeProperDate(entry["lastUpdatedAtSource"][0:10]))
    cases.append(entry["dailyInfected"])

dates = dates[-30:]
cases = cases[-30:]

yPos = np.arange(len(dates))
plt.xticks(yPos, dates)
plt.bar(yPos, cases)
for i in range(len(dates)):
    plt.text(i, cases[i] // 2, cases[i], ha="center")
plt.savefig("graph.png", dpi=200)

with open("./graph.png", "rb") as file:
    fileData = file.read()
    fileType = imghdr.what(file.name)

msg = EmailMessage()
msg["From"] = EMAIL_ADDRESS
msg["To"] = MY_EMAIL_ADDRESS
msg["Subject"] = "Covid Update You Lazy Bitch"
msg.set_content(finalMessage)
msg.add_attachment(fileData,
                   maintype="image",
                   subtype=fileType,
                   filename="graph")

# with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    # smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    # smtp.send_message(msg)


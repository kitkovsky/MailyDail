import smtplib
import json
import matplotlib.pyplot as plt
import numpy as np
import imghdr
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.message import EmailMessage
#from credentials import EMAIL_ADDRESS, EMAIL_PASSWORD, MY_EMAIL_ADDRESS 
import easyocr
from PIL import Image
from datetime import date
import json
from datetime import datetime


def makeProperDate(date):
    return f"{date[8:10]}.{date[5:7]}.{date[2:4]}"


def strToInt(string):
    result = 0
    base = 1
    for char in reversed(string):
        if char != ',':
            result = result + (int(char) * base)
            base = base * 10
    return result


def appendJSON(newData, filename="data.json"):
    with open(filename, "r+") as file:
        fileData = json.load(file)
        fileData["table"].append(newData)
        file.seek(0)
        json.dump(fileData, file, indent = 4)

def mainBoi():
    driver = webdriver.Chrome("/home/kitkovsky/Desktop/maily-dail/chromedriver")
    driver.get("https://www.gov.pl/web/koronawirus/wykaz-zarazen-koronawirusem-sars-cov-2")
    driver.maximize_window()

    print("start timer")
    time.sleep(60)
    print("end timer")

    driver.execute_script("window.scrollTo(0, 800)")
    driver.save_screenshot("screenshot.png")
    driver.quit()

    im = Image.open("/home/kitkovsky/Desktop/maily-dail/screenshot.png")
    casesCrop = im.crop((435, 200, 590, 252))
    casesCrop.save("/home/kitkovsky/Desktop/maily-dail/casesCrop.png")
    deathsCrop = im.crop((970, 200, 1150, 252))
    deathsCrop.save("/home/kitkovsky/Desktop/maily-dail/deathsCrop.png")
    testsCrop = im.crop((682, 430, 872, 482))
    testsCrop.save("/home/kitkovsky/Desktop/maily-dail/testsCrop.png")

    reader = easyocr.Reader(["en"])
    casesResult = strToInt(reader.readtext("/home/kitkovsky/Desktop/maily-dail/casesCrop.png", detail = 0)[0])
    deathsResult = strToInt(reader.readtext("/home/kitkovsky/Desktop/maily-dail/deathsCrop.png", detail = 0)[0])
    testsResult = strToInt(reader.readtext("/home/kitkovsky/Desktop/maily-dail/testsCrop.png", detail = 0)[0])

    today = date.today().strftime("%d/%m/%y")
    today = str(today).replace("/", "-")

    newEntry = {"dailyInfected": casesResult,
        "dailyTested": testsResult,
        "dailyDeceased": deathsResult,
        "lastUpdatedAtSource": today}

    appendJSON(newEntry)

    with open("/home/kitkovsky/Desktop/maily-dail/data.json") as file:
        data = json.load(file)

    finalMessage = str(json.dumps(data["table"][-1], indent=2))
    finalMessage = finalMessage + "\n\n~~~~~~~~~~~~\n\n"
    for entry in reversed(data["table"]):
        finalMessage = finalMessage + f"{entry['lastUpdatedAtSource']} - "
        finalMessage = finalMessage + f"{entry['dailyInfected']} cases, {entry['dailyDeceased']} deaths, {entry['dailyTested']} tests\n"

    plt.style.use("fivethirtyeight")
    plt.rcParams.update({"font.size": 3.5})
    plt.rcParams.update({"figure.figsize": [10, 5]})
    dates = []
    cases = []
    for entry in data["table"]:
        dates.append(entry["lastUpdatedAtSource"])
        cases.append(entry["dailyInfected"])

    dates = dates[-30:]
    cases = cases[-30:]

    yPos = np.arange(len(dates))
    plt.xticks(yPos, dates)
    plt.bar(yPos, cases)
    for i in range(len(dates)):
        plt.text(i, cases[i] // 2, cases[i], ha="center")
    plt.savefig("graph.png", dpi=500)

    with open("/home/kitkovsky/Desktop/maily-dail/graph.png", "rb") as file:
        fileData = file.read()
        fileType = imghdr.what(file.name)

    EMAIL_ADDRESS="uselesstrash19@gmail.com"
    EMAIL_PASSWORD="zbtg hrvk djev usah"
    MY_EMAIL_ADDRESS="okitkowski114@gmail.com"

    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = MY_EMAIL_ADDRESS
    msg["Subject"] = "Covid Update You Lazy Bitch"
    msg.set_content(finalMessage)
    msg.add_attachment(fileData,
                       maintype="image",
                       subtype=fileType,
                       filename="graph")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    plt.cla()
    plt.clf()

while True:
    now = datetime.now()
    currentTime = now.strftime("%H:%M:%S")
    print(currentTime)
    if currentTime[0] == "1" and currentTime[1] == "3":
        mainBoi()
    time.sleep(3600)


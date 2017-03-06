"""
ANAPHORA RESOLUTION

Change personal pronouns to their real entity

"""

import requests

text = "Why Did Attorney General Loretta Lynch Plead The Fifth? Barracuda Brigade 2016-10-28 Print The administration is blocking congressional probe into cash payments to Iran. Of course she needs to plead the 5th. She either can't recall, refuses to answer, or just plain deflects the question. Straight up corruption at its finest!\
100percentfedUp.com ; Talk about covering your ass! Loretta Lynch did just that when she plead the Fifth to avoid incriminating herself over payments to Iran'Corrupt to the core! Attorney General Loretta Lynch is declining to comply with an investigation by leading members of Congress about the Obama administration's secret efforts to send Iran $1.7 billion in cash earlier this year, prompting accusations that Lynch has 'pleaded the Fifth' Amendment to avoid incriminating herself over these payments, according to lawmakers and communications exclusively obtained by the Washington Free Beacon."

r = requests.post("http://localhost:8125/BARTDemo/ShowText/process/", data=text)
print(r.status_code, r.reason)
print(r.text)
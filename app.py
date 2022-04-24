import os
import re
import json
import requests
from sqlite_utils import Database
from slack import WebClient
from bs4 import BeautifulSoup
from slack.errors import SlackApiError
import csv
from pprint import pprint


db = Database("food_inspections.db")

#print(db.schema)

def get_max_row_id():
    for row in db.query("""select max(rowid) from inspections"""):
        max_id = list(row.values())
    return max_id

#print(get_max_row_id())

def get_ids_in_db():
    uid_list = []
    for id in db.query("""select uid from inspections"""):
        tmp_lst = list(id.values())
        uid_list.extend(tmp_lst)

    return uid_list


def get_inspections():
    infile = open("food_inspections.csv", newline='')
    reader = csv.DictReader(infile)
    uid_list = get_ids_in_db()
    db_list = []
    main_list = []
    max_id = get_max_row_id()
    for item in reader:
        item =  {k.lower(): v for k, v in item.items()}
        if 'COLLEGE PARK' in item['city']:
            if 'location' in item:
                item['coordinates'] = item['location']
                del item['location']
            else:
                item['coordinates'] = []

            item['uid'] = item['establishment_id']+'-'+item['inspection_date']
            #db_list.append(item)

            if item['uid'] in uid_list:
                print(f"{item['uid']} already in db")
            else:
                db_list.append(item)

    db["inspections"].insert_all(db_list, ignore = True)

    values = ['Critical Violations observed','Non-Compliant - Violations Observed']

    for row in db.query("select * from inspections where inspection_results in ('Critical Violations observed','Non-Compliant - Violations Observed') and rowid > ?", max_id):
            main_list.append(row)

    return main_list

#get_inspections()

def send_slack_msg():
    client = WebClient()
    slack_token = os.environ["SLACK_API_TOKEN"]
    client = WebClient(token=slack_token)
    for_message = get_inspections()
    for item in for_message:
        try:
            response = client.chat_postMessage(
            channel="slack-bots",
            blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": f":rotating_light: Food Inspection result: *{item['inspection_results']}* :rotating_light:\n An {item['inspection_type']} inspection took place at {item['name']} on {item['inspection_date']}, and the result was {item['inspection_results']} \n For more: <https://data.princegeorgescountymd.gov/Health/Food-Inspection/umjn-t2iz|Here's the link to the data>. \n Want to file an MPIA? <https://www.princegeorgescountymd.gov/DocumentCenter/View/4629/MPIA-Request-Form-PDF| Here's a form> for that."}}]
            #text=f"🚨 Food Inspection result: {item['inspection_type']} 🚨 Inspectiontook place at {item['name']} on {item['inspection_date']}, and the result was {item['inspection_results']}."
            )
        except SlackApiError as e:
    #You will get a SlackApiError if "ok" is False
            assert e.response["error"]

send_slack_msg()

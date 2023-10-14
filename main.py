import asyncio
import time
from datetime import datetime, timedelta
import os
import requests
import json
import g4f


async def gpt4(question):
    chat_completion = await g4f.ChatCompletion.create_async(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}],
        provider=g4f.Provider.GptGo,
        stream=False,
    )
    return chat_completion


profile_id = ""
Token = ""
UTC = 6


def send_message(phone, text):
    url = f"https://wappi.pro/api/sync/message/send?profile_id={profile_id}"
    headers = {
        'Authorization': Token,
        'Content-Type': 'application/json'
    }

    payload = {
        "recipient": str(phone),
        "body": text
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)


def write_id_to_file(id):
    with open("id_file.txt", "a") as file:
        file.write(str(id) + "\n")


def is_id_in_file(id):
    if os.path.exists("id_file.txt"):
        with open("id_file.txt", "r") as file:
            existing_ids = file.readlines()
            return str(id) + "\n" in existing_ids
    return False


def recieve_message(limit, messages_from_last_minutes):
    some_minutes_later = datetime.now() - timedelta(minutes=UTC * 60 + messages_from_last_minutes)
    formatted_date_time = some_minutes_later.strftime("%Y-%m-%dT%H:%M:%S")
    time_now = datetime.now()
    formatted_date_time_without_strafe = time_now.strftime("%Y-%m-%dT%H:%M:%S")
    date_obj = datetime.strptime(formatted_date_time_without_strafe, "%Y-%m-%dT%H:%M:%S")
    url = f"https://wappi.pro/api/sync/messages/all/get?profile_id={profile_id}&limit={limit}&date={formatted_date_time}"
    payload = {}
    headers = {
        'Authorization': Token
    }
    json_string = requests.request("GET", url, headers=headers, data=payload).text
    data = json.loads(json_string)
    try:
        for i, message in enumerate(data['messages']):
            body_value = data['messages'][i]['body']
            from_value = data['messages'][i]['from']
            to_value = data['messages'][i]['to']
            id_to_check = data['messages'][i]['id']
            dt_object = datetime.fromtimestamp(data['messages'][i]['time'])
            hours = dt_object.hour
            minutes = dt_object.minute
            first_five_letters = body_value[:5]
            other_letters = body_value[5:]
            if not is_id_in_file(id_to_check):
                if first_five_letters == "!help":
                    answer = asyncio.run(gpt4(other_letters))
                    send_message(from_value[:11], answer)
                    write_id_to_file(id_to_check)
            else:
                print(f"ID {id_to_check} уже существует в файле и не выполняем код.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        

 while True:
     recieve_message(0, 1)
     time.sleep(3)
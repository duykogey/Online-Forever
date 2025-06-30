import os
import sys
import json
import asyncio
import requests
import websockets
from colorama import init, Fore
from keep_alive import keep_alive

init(autoreset=True)

status = "online"
custom_status = "youtube.com/@SealedSaucer"

usertoken = os.getenv("TOKEN")
if not usertoken:
    print(Fore.LIGHTRED_EX + "[ERROR] Please add a token inside Secrets.")
    sys.exit()

headers = {"Authorization": usertoken}
validate = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
if validate.status_code != 200:
    print(Fore.LIGHTRED_EX + "[ERROR] Invalid token.")
    sys.exit()

userinfo = validate.json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

async def run_onliner():
    print(Fore.LIGHTGREEN_EX + f"Logged in as {username}#{discriminator} ({userid})")
    uri = "wss://gateway.discord.gg/?v=9&encoding=json"

    async with websockets.connect(uri) as ws:
        hello = json.loads(await ws.recv())
        heartbeat_interval = hello["d"]["heartbeat_interval"]

        asyncio.create_task(send_heartbeat(ws, heartbeat_interval))

        payload = {
            "op": 2,
            "d": {
                "token": usertoken,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                },
                "presence": {
                    "status": status,
                    "afk": False,
                    "since": 0,
                    "activities": [
                        {
                            "name": "Custom Status",
                            "type": 4,
                            "state": custom_status
                        }
                    ]
                }
            }
        }

        await ws.send(json.dumps(payload))

        while True:
            await asyncio.sleep(60)

async def send_heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        await ws.send(json.dumps({"op": 1, "d": None}))

keep_alive()
asyncio.run(run_onliner())

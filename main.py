import os
import sys
import json
import asyncio
import requests
import websockets
from colorama import init, Fore

init(autoreset=True)

status = "online"
custom_status = "Always online"

usertoken = os.getenv("TOKEN")
if not usertoken:
    print(Fore.RED + "[ERROR] No token found.")
    sys.exit()

headers = {"Authorization": usertoken}
user = requests.get("https://discord.com/api/v9/users/@me", headers=headers)

if user.status_code != 200:
    print(Fore.RED + "[ERROR] Invalid token.")
    sys.exit()

userinfo = user.json()
print(Fore.GREEN + f"Logged in as {userinfo['username']}#{userinfo['discriminator']}")

async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        await ws.send(json.dumps({"op": 1, "d": None}))

async def main():
    uri = "wss://gateway.discord.gg/?v=9&encoding=json"
    async with websockets.connect(uri, max_size=2**20) as ws:
        hello = json.loads(await ws.recv())
        interval = hello["d"]["heartbeat_interval"]
        asyncio.create_task(heartbeat(ws, interval))

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

asyncio.run(main())

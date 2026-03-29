import socket
import requests
import time
from datetime import datetime

WEBHOOK_URL = "PUT WEBHOOK URL HERE"

SERVER_IP = "PUT SERVER IP HERE"
SERVER_PORT = PORT-NUMBER-HERE
SERVER_NAME = "PUT SERVER NAME HERE"

CHECK_INTERVAL = 10

last_status = None
message_id = None


def ping_server(ip, port):
    start = time.time()
    try:
        sock = socket.create_connection((ip, port), timeout=5)
        sock.close()
        return True, int((time.time() - start) * 1000)
    except:
        return False, None


def get_beammp_data():
    try:
        res = requests.get("https://backend.beammp.com/servers-info", timeout=10)
        servers = res.json()

        for server in servers:
            if server.get("ip") == SERVER_IP and int(server.get("port")) == SERVER_PORT:
                players = server.get("players", [])
                return {
                    "player_count": len(players),
                    "players": players
                }
    except:
        pass

    return None


def send_or_update(status, ping, player_data):
    global message_id

    color = 0x00FF00 if status else 0xFF0000
    status_text = "🟢 Online" if status else "🔴 Offline"

    player_count = 0
    player_list = "None"

    if player_data:
        player_count = player_data["player_count"]
        if player_count > 0:
            player_list = "\n".join(player_data["players"])

    embed = {
        "title": SERVER_NAME,
        "color": color,
        "fields": [
            {"name": "Status", "value": status_text, "inline": True},
            {"name": "Ping", "value": f"{ping} ms" if ping else "N/A", "inline": True},
            {"name": "Players", "value": f"{player_count}", "inline": True},
            {"name": "Player List", "value": player_list[:1000] or "None", "inline": False}
        ],
        "footer": {
            "text": f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
        }
    }

    data = {"embeds": [embed]}

    if message_id is None:
        res = requests.post(WEBHOOK_URL + "?wait=true", json=data)
        if res.status_code == 200:
            message_id = res.json()["id"]
            print("Sent webhook message")
        else:
            print("Error sending:", res.text)
    else:
        res = requests.patch(f"{WEBHOOK_URL}/messages/{message_id}", json=data)
        if res.status_code != 200:
            print("Error updating:", res.text)


print("BeamMP monitor started")

while True:
    status, ping = ping_server(SERVER_IP, SERVER_PORT)

    player_data = get_beammp_data() if status else None

    if status != last_status or status:
        send_or_update(status, ping, player_data)
        last_status = status

    time.sleep(CHECK_INTERVAL)

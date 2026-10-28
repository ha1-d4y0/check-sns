import os
import sys
import discord
import requests
import textwrap
from dotenv import load_dotenv
from tabulate import tabulate
from datetime import datetime, timezone, timedelta

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
STEAM_API_KEY = os.getenv('STEAM_API_KEY')
XBOX_API_KEY = os.getenv('XBOX_API_KEY')

TARGET_DISCORD_ID = int(os.getenv('TARGET_DISCORD_ID')) if os.getenv('TARGET_DISCORD_ID') else None
TARGET_STEAM_ID = os.getenv('TARGET_STEAM_ID')
TARGET_XBOX_TAG = os.getenv('TARGET_XBOX_GAMERTAG')

JST = timezone(timedelta(hours=9))

class MonitorCLI(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True
        super().__init__(intents=intents)

    async def on_ready(self):
        mode = sys.argv[1] if len(sys.argv) > 1 else "status"
        print(f"\n🚀 [ 取得時刻: {datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')} ]")
        
        if mode == "all":
            await self.show_comprehensive_report()
        else:
            await self.show_live_status()
        await self.close()

    def wrap_text(self, text, width=45):
        if not text: return "-"
        return "\n".join(textwrap.wrap(str(text), width=width))

    def format_time(self, raw_str):
        try:
            dt = datetime.fromisoformat(raw_str.replace('Z', '+00:00')).astimezone(JST)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except: return raw_str

    def get_steam_data(self):
        if not STEAM_API_KEY or not TARGET_STEAM_ID: return None
        url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={TARGET_STEAM_ID}"
        try:
            res = requests.get(url, timeout=5).json()
            players = res.get('response', {}).get('players', [])
            return players[0] if players else None
        except: return None

    def get_xbox_data(self):
        if not XBOX_API_KEY or not TARGET_XBOX_TAG: return None
        headers = {"X-Authorization": XBOX_API_KEY, "Accept": "application/json"}
        try:
            res = requests.get(f"https://xbl.io/api/v2/friends/search?gt={TARGET_XBOX_TAG}", headers=headers, timeout=10)
            user_data = res.json().get('content', {}).get('profileUsers', [])[0]
            xuid = user_data.get('id')
            pres_res = requests.get(f"https://xbl.io/api/v2/presence/{xuid}", headers=headers, timeout=5)
            if pres_res.status_code == 200:
                p_content = pres_res.json().get('content', [])
                user_data['presence_detail'] = p_content[0] if isinstance(p_content, list) and p_content else p_content
            return user_data
        except: return None

    async def show_live_status(self):
        member = None
        for guild in self.guilds:
            if m := guild.get_member(TARGET_DISCORD_ID):
                member = m; break
        
        table = []
        # --- DISCORD ---
        if member:
            status_icons = {"online": "🟢 Online", "idle": "🌙 Idle", "dnd": "🔴 DnD", "offline": "⚪ Offline"}
            table.append(["Discord", "Status", status_icons.get(str(member.status), "⚪ Unknown")])
            games = [a.name for a in member.activities if not isinstance(a, discord.Spotify)]
            table.append(["Discord", "Playing", self.wrap_text(", ".join(games))])
            dev_info = []
            if member.desktop_status != discord.Status.offline: dev_info.append("Desktop")
            if member.mobile_status != discord.Status.offline: dev_info.append("Mobile")
            if member.web_status != discord.Status.offline: dev_info.append("Web")
            if not dev_info:
                table.append(["Discord", "Last Seen", "No active device"])
            else:
                table.append(["Discord", "Active On", ", ".join(dev_info)])

        # --- STEAM ---
        if s := self.get_steam_data():
            s_map = {0:"⚪ Offline", 1:"🔵 Online", 2:"🔴 Busy", 3:"🌙 Away", 4:"💤 Snooze"}
            table.append(["Steam", "Status", s_map.get(s.get('personastate'), "Unknown")])
            table.append(["Steam", "Playing", self.wrap_text(s.get('gameextrainfo', "-"))])
            if l_off := s.get('lastlogoff'):
                l_off_t = datetime.fromtimestamp(l_off, JST).strftime('%Y-%m-%d %H:%M:%S')
                table.append(["Steam", "Last Logoff", l_off_t])

        # --- XBOX ---
        if x := self.get_xbox_data():
            st = next((i.get('value') for i in x.get('settings', []) if i.get('id') == 'PresenceText'), "Unknown")
            table.append(["Xbox", "Status", self.wrap_text(st)])
            if pd := x.get('presence_detail'):
                if ls := pd.get('lastSeen'):
                    table.append(["Xbox", "Last Title", self.wrap_text(ls.get('titleName', "-"))])
                    table.append(["Xbox", "Last Seen", self.format_time(ls.get('timestamp'))])

        print(tabulate(table, headers=["Source", "Item", "Current Value"], tablefmt="fancy_grid"))

    async def show_comprehensive_report(self):
        try: user = await self.fetch_user(TARGET_DISCORD_ID)
        except: return
        s = self.get_steam_data()
        x = self.get_xbox_data()
        report = []
        report.append(["DISCORD", "Name", user.name])
        report.append(["DISCORD", "ID", user.id])
        report.append(["DISCORD", "Created", user.created_at.astimezone(JST).strftime('%Y-%m-%d %H:%M:%S')])
        if user.avatar:
            report.append(["DISCORD", "Avatar URL", self.wrap_text(user.avatar.url, width=70)])
        if s:
            report.append(["---", "---", "---"])
            for k, v in s.items():
                if k in ['timecreated', 'lastlogoff'] and v:
                    v = datetime.fromtimestamp(v, JST).strftime('%Y-%m-%d %H:%M:%S')
                report.append(["STEAM", k, self.wrap_text(v, width=70)])
        if x:
            report.append(["---", "---", "---"])
            report.append(["XBOX", "XUID", x.get('id')])
            for setting in x.get('settings', []):
                report.append(["XBOX_Set", setting.get('id'), self.wrap_text(setting.get('value'), width=70)])
            if pd := x.get('presence_detail'):
                report.append(["XBOX_Live", "State", pd.get('state', "Unknown")])
                if ls := pd.get('lastSeen'):
                    for lk, lv in ls.items():
                        if lk == 'timestamp': lv = self.format_time(lv)
                        report.append(["XBOX_Last", lk, self.wrap_text(lv, width=70)])
        print(tabulate(report, headers=["Category", "Key", "Information"], tablefmt="fancy_grid"))

if __name__ == "__main__":
    if DISCORD_TOKEN and TARGET_DISCORD_ID:
        MonitorCLI().run(DISCORD_TOKEN)

import os
import sys
import socket
import urllib.parse
import urllib.request
import urllib.error
import json
import random
import string
import threading
import time

# تعديل clear عشان يشتغل على A Shell
def clear_screen():
    try:
        os.system('clear')
    except:
        os.system('cls' if os.name == 'nt' else 'printf "\033c"')

WHITE = '\033[1;37m'
GREEN = '\033[1;32m'
BLUE = '\033[1;34m'
PINK = '\033[1;35m'
YELLOW = '\033[1;33m'
RED = '\033[1;31m'
CYAN = '\033[1;36m'
RESET = '\033[0m'

WEBHOOK_URL = ""
found_count = 0
checked_count = 0
lock = threading.Lock()
running = True
checked_set = set()
checked_set_lock = threading.Lock()

def show_logo():
    print(f"{WHITE}")
    print(" ▄▄▄▄▄▄▄           ")
    print(" ▀▀▀▀▀██              ")
    print("     ██   ▄▄          ")
    print("    ██   ▄██ ▀█▄▄▀███▀")
    print("  ▄▄██▄▄  ██ ▄█▀ ▄███▄")
    print("    ██    ████   ██ ██")
    print(f"{RESET}")

def translate_to_arabic(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res[0][0][0]
    except:
        return "حدث خطأ أثناء الترجمة"

def get_bot_servers(token):
    print(f"\n{YELLOW}[*] جاري الاتصال بديسكورد...{RESET}")
    guilds_url = "https://discord.com/api/v10/users/@me/guilds"
    req = urllib.request.Request(guilds_url, headers={'Authorization': f'Bot {token}', 'User-Agent': 'DiscordBot'})
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            guilds = json.loads(response.read().decode('utf-8'))
            if not guilds:
                print(f"\n{PINK}[!] البوت مو داخل في أي سيرفر.{RESET}")
                return
            print(f"\n{GREEN}✔ البوت داخل في ({len(guilds)}) سيرفرات:{RESET}\n")
            for index, g in enumerate(guilds, 1):
                guild_id = g['id']
                guild_name = g['name']
                print(f"{WHITE}[{index}] {YELLOW}{guild_name}{WHITE} (ID: {guild_id}){RESET}")
                try:
                    channels_url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
                    c_req = urllib.request.Request(channels_url, headers={'Authorization': f'Bot {token}', 'User-Agent': 'DiscordBot'})
                    with urllib.request.urlopen(c_req, timeout=5) as c_res:
                        channels = json.loads(c_res.read().decode('utf-8'))
                        text_channel = None
                        for ch in channels:
                            if ch['type'] == 0:
                                text_channel = ch['id']
                                break
                        if text_channel:
                            invite_url = f"https://discord.com/api/v10/channels/{text_channel}/invites"
                            data = json.dumps({"max_age": 86400, "max_uses": 0}).encode('utf-8')
                            i_req = urllib.request.Request(invite_url, data=data, headers={
                                'Authorization': f'Bot {token}', 'Content-Type': 'application/json', 'User-Agent': 'DiscordBot'
                            }, method='POST')
                            with urllib.request.urlopen(i_req, timeout=5) as i_res:
                                invite_data = json.loads(i_res.read().decode('utf-8'))
                                print(f"    🔗 https://discord.gg/{invite_data['code']}")
                        else:
                            print(f"    🔗 لا يوجد روم كتابي")
                except:
                    print(f"    🔗 صلاحيات البوت لا تسمح")
                print("-" * 40)
    except:
        print(f"\n{PINK}❌ التوكن غير صحيح.{RESET}")

def send_to_webhook(username, pattern_type):
    global WEBHOOK_URL
    if not WEBHOOK_URL:
        return
    icons = {"under_begin": "🔰", "under_mid": "💎", "under_end": "🔥", "under_x2": "👑"}
    icon = icons.get(pattern_type, "⭐")
    data = {
        "content": f"{icon} **تيكن توك - يوزر نادر!**\n📛 `{username}`\n🔗 https://www.tiktok.com/@{username}",
        "username": "TikTok Rare Checker"
    }
    try:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(WEBHOOK_URL, data=data_bytes,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

def generate_rare_username():
    """توليد يوزر نادر مع أندر سكور"""
    chars_letters = string.ascii_lowercase
    chars_digits = string.digits
    chars_all = chars_letters + chars_digits
    
    pattern = random.randint(1, 6)
    
    if pattern == 1:  # _xyz
        body = ''.join(random.choices(chars_all, k=3))
        return f"_{body}", "under_begin"
    elif pattern == 2:  # x_yz
        a = random.choice(chars_all)
        body = ''.join(random.choices(chars_all, k=2))
        return f"{a}_{body}", "under_mid"
    elif pattern == 3:  # xy_z
        body = ''.join(random.choices(chars_all, k=2))
        a = random.choice(chars_all)
        return f"{body}_{a}", "under_mid"
    elif pattern == 4:  # xyz_
        body = ''.join(random.choices(chars_all, k=3))
        return f"{body}_", "under_end"
    elif pattern == 5:  # _xy_
        body = ''.join(random.choices(chars_all, k=2))
        return f"_{body}_", "under_x2"
    else:  # x_9m مثلاً
        a = random.choice(chars_letters)
        b = random.choice(chars_digits)
        c = random.choice(chars_letters)
        d = random.choice(chars_digits)
        return f"{a}_{b}{c}{d}", "under_mid"

def check_username(username):
    try:
        req = urllib.request.Request(f"https://www.tiktok.com/@{username}",
            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'}, method='HEAD')
        urllib.request.urlopen(req, timeout=5)
        return False
    except urllib.error.HTTPError as e:
        return e.code in [404, 302, 301]
    except:
        return False

def tiktok_worker():
    global found_count, checked_count, running, checked_set
    while running:
        username, ptype = generate_rare_username()
        with checked_set_lock:
            if username in checked_set:
                continue
            checked_set.add(username)
        with lock:
            checked_count += 1
            current_checked = checked_count
        print(f"{WHITE}[{current_checked}] {BLUE}فحص: {CYAN}{username}{RESET}    ", end='\r')
        if check_username(username):
            with lock:
                found_count += 1
                current_found = found_count
            color = {"under_begin": CYAN, "under_end": YELLOW, "under_x2": RED}.get(ptype, GREEN)
            print(f"\n{color}✅ [{ptype}] {WHITE}{username} {color}https://www.tiktok.com/@{username}{RESET}")
            with open('tiktok_hits.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{ptype}] {username}\n")
            send_to_webhook(username, ptype)

def tiktok_menu():
    global WEBHOOK_URL, running, found_count, checked_count, checked_set
    found_count = 0; checked_count = 0; running = True; checked_set = set()
    clear_screen()
    print(f"\n{RED}══════════ TikTok Rare Username Checker ══════════{RESET}")
    print(f"\n{WHITE}أنماط اليوزرات النادرة مع أندر سكور _")
    print(f"  {CYAN}_xxx{RESET}  : أندر سكور بالبداية")
    print(f"  {GREEN}x_xx{RESET}  : أندر سكور بالوسط")
    print(f"  {YELLOW}xxx_{RESET}  : أندر سكور بالنهاية")
    print(f"  {RED}_xx_{RESET}  : أندر سكور بداية+نهاية{RESET}")
    
    WEBHOOK_URL = input(f"\n{WHITE}◀ رابط ويبهوك الديسكورد: {RESET}").strip()
    if not WEBHOOK_URL:
        print(f"{YELLOW}⚠ بدون ويبهوك{RESET}")
        WEBHOOK_URL = ""
    
    try:
        t = input(f"{WHITE}◀ عدد الثريدات (Enter=30): {RESET}").strip()
        threads_count = int(t) if t else 30
    except:
        threads_count = 30
    
    print(f"\n{GREEN}🚀 الشغل بـ {threads_count} ثريد | Ctrl+C للإيقاف{RESET}\n")
    time.sleep(1)
    
    threads = []
    try:
        for _ in range(threads_count):
            th = threading.Thread(target=tiktok_worker, daemon=True)
            th.start()
            threads.append(th)
        while running:
            time.sleep(3)
            with lock:
                print(f"{WHITE}[فحص {checked_count}] {GREEN}✅ {found_count} متاح{RESET}    ", end='\r')
    except KeyboardInterrupt:
        running = False
        print(f"\n\n{YELLOW}⏹ تم الإيقاف | {GREEN}{found_count} يوزر متاح{RESET}")
        print(f"{WHITE}📁 المحفوظ: tiktok_hits.txt{RESET}")
        input(f"\n{WHITE}Enter للرجوع...{RESET}")
        main_menu()

def main_menu():
    clear_screen()
    show_logo()
    print(f"{GREEN}~ [1] IP & Ports Tool{RESET}")
    print(f"       {BLUE}~ [2] Translation EN->AR{RESET}")
    print(f"                                    {PINK}~ [3] Discord Users{RESET}")
    print(f"                                    {YELLOW}~ [4] Discord Bot Tool{RESET}")
    print(f"{RED}~ [5] TikTok Rare Checker 🔥{RESET}")
    print(f"\n{YELLOW} [0] Exit{RESET}")
    choice = input(f"\n{WHITE}◀ اختار: {RESET}").strip()
    
    if choice == '1':
        domain = input(f"\n{WHITE}الموقع: {RESET}").strip()
        try:
            ip = socket.gethostbyname(domain)
            print(f"{GREEN}✔ IP: {YELLOW}{ip}{RESET}")
            print(f"   Port 80: {GREEN}HTTP{RESET}")
            print(f"   Port 443: {GREEN}HTTPS{RESET}")
        except:
            print(f"{PINK}❌ خطأ في الموقع{RESET}")
    elif choice == '2':
        word = input(f"{WHITE}الكلمة بالإنجليزي: {RESET}").strip()
        print(f"{BLUE}✔ {YELLOW}{translate_to_arabic(word)}{RESET}")
    elif choice == '3':
        print(f"\n{PINK}Discord 4-letter users:{RESET}")
        for u in ["6j5w", "8vgu", "8vgd"]:
            print(f"  • {PINK}{u}{RESET}")
    elif choice == '4':
        token = input(f"{WHITE}Bot Token: {RESET}").strip()
        if token: get_bot_servers(token)
    elif choice == '5':
        tiktok_menu()
        return
    elif choice == '0':
        print(f"\n{YELLOW}في أمان الله!{RESET}")
        sys.exit()
    else:
        print(f"{PINK}❌ رقم غلط{RESET}")
    
    input(f"\n{WHITE}Enter للرجوع...{RESET}")
    main_menu()

if __name__ == "__main__":
    main_menu()

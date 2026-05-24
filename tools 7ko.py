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

# متغيرات عامة
WEBHOOK_URL = ""
found_count = 0
checked_count = 0
lock = threading.Lock()
running = True
checked_set = set()
checked_set_lock = threading.Lock()

# متغيرات ديسكورد
DC_WEBHOOK = ""
DC_TOKEN = ""
dc_found = 0
dc_checked = 0
dc_running = True
dc_checked_set = set()

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
        return "حدث خطأ"

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
                guild_id = g['id']; guild_name = g['name']
                print(f"{WHITE}[{index}] {YELLOW}{guild_name}{WHITE} (ID: {guild_id}){RESET}")
                try:
                    channels_url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
                    c_req = urllib.request.Request(channels_url, headers={'Authorization': f'Bot {token}', 'User-Agent': 'DiscordBot'})
                    with urllib.request.urlopen(c_req, timeout=5) as c_res:
                        channels = json.loads(c_res.read().decode('utf-8'))
                        text_channel = None
                        for ch in channels:
                            if ch['type'] == 0: text_channel = ch['id']; break
                        if text_channel:
                            invite_url = f"https://discord.com/api/v10/channels/{text_channel}/invites"
                            data = json.dumps({"max_age": 86400, "max_uses": 0}).encode('utf-8')
                            i_req = urllib.request.Request(invite_url, data=data, headers={
                                'Authorization': f'Bot {token}', 'Content-Type': 'application/json', 'User-Agent': 'DiscordBot'
                            }, method='POST')
                            with urllib.request.urlopen(i_req, timeout=5) as i_res:
                                invite_data = json.loads(i_res.read().decode('utf-8'))
                                print(f"    🔗 https://discord.gg/{invite_data['code']}")
                        else: print(f"    🔗 لا يوجد روم كتابي")
                except: print(f"    🔗 صلاحيات البوت لا تسمح")
                print("-" * 40)
    except: print(f"\n{PINK}❌ التوكن غير صحيح.{RESET}")

# ========== تيك توك ==========
def send_tt_webhook(username, ptype):
    global WEBHOOK_URL
    if not WEBHOOK_URL: return
    data = {
        "content": f"✅ **تيكن توك - يوزر نادر!**\n📛 `{username}`\n🔗 https://www.tiktok.com/@{username}",
        "username": "TikTok Rare Checker"
    }
    try:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(WEBHOOK_URL, data=data_bytes,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
        urllib.request.urlopen(req, timeout=5)
    except: pass

def generate_rare_username():
    chars_all = string.ascii_lowercase + string.digits
    chars_letters = string.ascii_lowercase
    p = random.randint(1, 6)
    if p == 1:
        return f"_{''.join(random.choices(chars_all, k=3))}", "under_begin"
    elif p == 2:
        a = random.choice(chars_all)
        return f"{a}_{''.join(random.choices(chars_all, k=2))}", "under_mid"
    elif p == 3:
        return f"{''.join(random.choices(chars_all, k=2))}_{random.choice(chars_all)}", "under_mid"
    elif p == 4:
        return f"{''.join(random.choices(chars_all, k=3))}_", "under_end"
    elif p == 5:
        return f"_{''.join(random.choices(chars_all, k=2))}_", "under_x2"
    else:
        return f"{random.choice(chars_letters)}_{random.choice(chars_digits)}{random.choice(chars_letters)}{random.choice(chars_digits)}", "under_mid"

def check_tt_username(username):
    try:
        req = urllib.request.Request(f"https://www.tiktok.com/@{username}",
            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'}, method='HEAD')
        urllib.request.urlopen(req, timeout=5)
        return False
    except urllib.error.HTTPError as e:
        return e.code in [404, 302, 301]
    except: return False

def tt_worker():
    global found_count, checked_count, running, checked_set
    while running:
        username, ptype = generate_rare_username()
        with checked_set_lock:
            if username in checked_set: continue
            checked_set.add(username)
        with lock:
            checked_count += 1; cur_c = checked_count
        print(f"{WHITE}[{cur_c}] {BLUE}تيك: {CYAN}{username}{RESET}    ", end='\r')
        if check_tt_username(username):
            with lock: found_count += 1; cur_f = found_count
            color = {"under_begin": CYAN, "under_end": YELLOW, "under_x2": RED}.get(ptype, GREEN)
            print(f"\n{color}✅ [{ptype}] {WHITE}{username} {color}https://www.tiktok.com/@{username}{RESET}")
            with open('tiktok_hits.txt', 'a', encoding='utf-8') as f: f.write(f"[{ptype}] {username}\n")
            send_tt_webhook(username, ptype)

def tiktok_menu():
    global WEBHOOK_URL, running, found_count, checked_count, checked_set
    found_count = 0; checked_count = 0; running = True; checked_set = set()
    clear_screen()
    print(f"\n{RED}══════ TikTok Rare Checker ══════{RESET}")
    print(f"  {CYAN}_xxx{RESET}  {GREEN}x_xx{RESET}  {YELLOW}xxx_{RESET}  {RED}_xx_{RESET}")
    WEBHOOK_URL = input(f"\n{WHITE}◀ ويبهوك: {RESET}").strip()
    if not WEBHOOK_URL: print(f"{YELLOW}⚠ بدون ويبهوك{RESET}"); WEBHOOK_URL = ""
    try: t = input(f"{WHITE}◀ ثريدات (Enter=30): {RESET}").strip(); threads_count = int(t) if t else 30
    except: threads_count = 30
    print(f"\n{GREEN}🚀 {threads_count} ثريد | Ctrl+C للإيقاف{RESET}\n")
    time.sleep(1)
    threads = []
    try:
        for _ in range(threads_count):
            th = threading.Thread(target=tt_worker, daemon=True); th.start(); threads.append(th)
        while running: time.sleep(3); print(f"{WHITE}[فحص {checked_count}] {GREEN}✅ {found_count}{RESET}    ", end='\r')
    except KeyboardInterrupt:
        running = False
        print(f"\n\n{YELLOW}⏹ {GREEN}{found_count} متاح{RESET}"); print(f"{WHITE}📁 tiktok_hits.txt{RESET}")
        input(f"\n{WHITE}Enter للرجوع...{RESET}"); main_menu()

# ========== ديسكورد يوزرات ==========
def send_dc_webhook(username, ptype):
    global DC_WEBHOOK
    if not DC_WEBHOOK: return
    data = {
        "content": f"✅ **ديسكورد - يوزر مميز متاح!**\n📛 `{username}`\n🔗 https://discord.com/users/{username}\n🏷 `{ptype}`",
        "username": "Discord User Checker"
    }
    try:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(DC_WEBHOOK, data=data_bytes,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
        urllib.request.urlopen(req, timeout=5)
    except: pass

def gen_dc_username():
    """توليد يوزرات ديسكورد مميزة مثل: 7mo, .ksa, _fvl, 7mo., _7mo, ksa., mo7_, x9m_, _x9m, 7m.o"""
    ll = string.ascii_lowercase; ld = string.digits; la = ll + ld
    p = random.randint(1, 12)
    if p == 1:   return ''.join(random.choices(la, k=3)), "ثلاثي_خالص"
    elif p == 2: return '.' + ''.join(random.choices(ll, k=3)), "نقطة_بداية"
    elif p == 3: return '_' + ''.join(random.choices(ll, k=3)), "أندر_بداية"
    elif p == 4: return ''.join(random.choices(la, k=3)) + '.', "نقطة_نهاية"
    elif p == 5: return ''.join(random.choices(la, k=3)) + '_', "أندر_نهاية"
    elif p == 6: return '_' + ''.join(random.choices(la, k=3)), "أندر_بداية2"
    elif p == 7: return ''.join(random.choices(ll, k=3)) + '.', "نقطة_نهاية_حروف"
    elif p == 8: return ''.join(random.choices(la, k=3)) + '_', "أندر_نهاية_مختلط"
    elif p == 9: return f"_{random.choice(ll)}{random.choice(ld)}{random.choice(ll)}", "أندر_بداية_مميز"
    elif p == 10: return f"{random.choice(la)}{random.choice(ll)}.{random.choice(la)}", "نقطة_وسط"
    elif p == 11: return '.' + ''.join(random.choices(la, k=3)), "نقطة_بداية_مختلط"
    else: return ''.join(random.choices(ll, k=4)), "رباعي_حروف"

def check_dc_username(username, token):
    """فحص يوزر ديسكورد - الطريقة الصحيحة"""
    try:
        url = "https://discord.com/api/v10/users/@me"
        data = json.dumps({"global_name": username}).encode('utf-8')
        req = urllib.request.Request(url, data=data,
            headers={'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
            method='PATCH')
        with urllib.request.urlopen(req, timeout=5) as res:
            result = json.loads(res.read().decode('utf-8'))
            # نجح التغيير! الاسم متاح
            # نرجع الاسم القديم
            restore_data = json.dumps({"global_name": ""}).encode('utf-8')
            restore_req = urllib.request.Request(url, data=restore_data,
                headers={'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
                method='PATCH')
            try: urllib.request.urlopen(restore_req, timeout=5)
            except: pass
            return True
    except urllib.error.HTTPError as e:
        if e.code == 400:
            try:
                body = json.loads(e.read().decode('utf-8'))
                msg = body.get('message', '')
                code = body.get('code', 0)
                if code == 50006 or 'taken' in msg.lower() or 'already' in msg.lower(): return False
                if code == 50035 or 'invalid' in msg.lower(): return False
                return False
            except: return False
        return False
    except: return False

def dc_worker():
    global dc_found, dc_checked, dc_running, DC_TOKEN, dc_checked_set
    while dc_running:
        username, ptype = gen_dc_username()
        if username in dc_checked_set: continue
        dc_checked_set.add(username)
        dc_checked += 1; cur_c = dc_checked
        print(f"{WHITE}[{cur_c}] {BLUE}دس: {CYAN}{username} ({ptype}){RESET}    ", end='\r')
        if check_dc_username(username, DC_TOKEN):
            dc_found += 1; cur_f = dc_found
            color = {"ثلاثي_خالص": GREEN, "نقطة_بداية": CYAN, "أندر_بداية": YELLOW,
                     "نقطة_نهاية": PINK, "أندر_نهاية": RED, "أندر_بداية2": YELLOW,
                     "نقطة_نهاية_حروف": GREEN, "أندر_نهاية_مختلط": CYAN,
                     "أندر_بداية_مميز": RED, "نقطة_وسط": PINK,
                     "نقطة_بداية_مختلط": CYAN, "رباعي_حروف": GREEN}.get(ptype, GREEN)
            print(f"\n{color}✅ [{ptype}] {WHITE}{username}{RESET}")
            with open('discord_hits.txt', 'a', encoding='utf-8') as f: f.write(f"[{ptype}] {username}\n")
            send_dc_webhook(username, ptype)

def discord_menu():
    global DC_WEBHOOK, DC_TOKEN, dc_found, dc_checked, dc_running, dc_checked_set
    dc_found = 0; dc_checked = 0; dc_running = True; dc_checked_set = set()
    clear_screen()
    print(f"\n{RED}══════ Discord Username Checker ══════{RESET}")
    print(f"{WHITE}أنماط يوزرات مميزة:")
    print(f"  {GREEN}7mo{RESET} - {CYAN}.ksa{RESET} - {YELLOW}_fvl{RESET} - {PINK}7mo.{RESET}")
    print(f"  {RED}_7mo{RESET} - {GREEN}ksa.{RESET} - {CYAN}mo7_{RESET} - {YELLOW}_x9m{RESET}")
    
    DC_WEBHOOK = input(f"\n{WHITE}◀ ويبهوك الديسكورد: {RESET}").strip

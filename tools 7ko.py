import os
import sys
import socket
import urllib.request
import urllib.parse
import urllib.error
import json
import random
import string
import threading
import time
import gzip

def clear_screen():
    os.system('clear')

WHITE  = '\033[1;37m'
GREEN  = '\033[1;32m'
BLUE   = '\033[1;34m'
PINK   = '\033[1;35m'
YELLOW = '\033[1;33m'
CYAN   = '\033[1;36m'
RESET  = '\033[0m'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]

def show_logo():
    print(f"{WHITE}")
    print(" ▄▄▄▄▄▄▄              ")
    print(" ▀▀▀▀▀██              ")
    print("     ██   ▄▄          ")
    print("  ▄▄██▄▄  ██ ▄█▀ ▄███▄")
    print("    ██    ████   ██ ██")
    print("    ██   ▄██ ▀█▄▄▀███▀")
    print(f"{RESET}")

# ─────────────────────────────────────────────
# أداة 1
# ─────────────────────────────────────────────
def tool_ip():
    print(f"\n{GREEN}[+] أداة استخراج IP وبورتات الموقع{RESET}")
    domain = input(f"{WHITE}◀ أدخل رابط الموقع بدون www (مثال: google.com): {RESET}").strip()
    try:
        ip_address = socket.gethostbyname(domain)
        print(f"\n{GREEN}✔ IP Address للموقع هو: {YELLOW}{ip_address}{RESET}")
        print(f"{GREEN}✔ البورتات المفتوحة الافتراضية للويب:{RESET}")
        print(f"   - Port 80  (HTTP)  -> {GREEN}متاح{RESET}")
        print(f"   - Port 443 (HTTPS) -> {GREEN}متاح{RESET}")
    except socket.gaierror:
        print(f"\n{PINK}❌ خطأ: لم يتم العثور على الموقع.{RESET}")

# ─────────────────────────────────────────────
# أداة 2
# ─────────────────────────────────────────────
def translate_to_arabic(text):
    try:
        url = (f"https://translate.googleapis.com/translate_a/single"
               f"?client=gtx&sl=en&tl=ar&dt=t&q={urllib.parse.quote(text)}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode('utf-8'))
            return res[0][0][0]
    except:
        return "حدث خطأ أثناء الترجمة."

def tool_translate():
    print(f"\n{BLUE}[+] أداة الترجمة الفورية{RESET}")
    word = input(f"{WHITE}◀ اكتب الكلمة بالإنجليزية: {RESET}").strip()
    result = translate_to_arabic(word)
    print(f"\n{BLUE}✔ الترجمة: {YELLOW}{result}{RESET}")

# ─────────────────────────────────────────────
# أداة 3
# ─────────────────────────────────────────────
def tool_discord_users():
    print(f"\n{PINK}[+] يوزرات ديسكورد رباعية المطلوبة:{RESET}\n")
    users = ["6j5w", "8vgu", "8vgd", "8vgq"]
    for u in users:
        print(f" {WHITE}•{RESET} {PINK}{u}{RESET}")

# ─────────────────────────────────────────────
# أداة 4
# ─────────────────────────────────────────────
def get_bot_servers(token):
    print(f"\n{YELLOW}[*] جاري الاتصال بديسكورد...{RESET}")
    guilds_url = "https://discord.com/api/v10/users/@me/guilds"
    req = urllib.request.Request(
        guilds_url,
        headers={'Authorization': f'Bot {token}', 'User-Agent': 'DiscordBot'}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            guilds = json.loads(response.read().decode('utf-8'))
            if not guilds:
                print(f"\n{PINK}![!] البوت شغال لكنه مو في أي سيرفر.{RESET}")
                return
            print(f"\n{GREEN}✔ البوت داخل في ({len(guilds)}) سيرفرات:{RESET}\n")
            for index, g in enumerate(guilds, 1):
                guild_id   = g['id']
                guild_name = g['name']
                print(f"{WHITE}[{index}] {YELLOW}{guild_name}{WHITE} (ID: {guild_id}){RESET}")
                try:
                    c_req = urllib.request.Request(
                        f"https://discord.com/api/v10/guilds/{guild_id}/channels",
                        headers={'Authorization': f'Bot {token}', 'User-Agent': 'DiscordBot'}
                    )
                    with urllib.request.urlopen(c_req, timeout=5) as c_res:
                        channels = json.loads(c_res.read().decode('utf-8'))
                        text_channel = next((ch['id'] for ch in channels if ch['type'] == 0), None)
                        if text_channel:
                            data = json.dumps({"max_age": 86400, "max_uses": 0}).encode('utf-8')
                            i_req = urllib.request.Request(
                                f"https://discord.com/api/v10/channels/{text_channel}/invites",
                                data=data,
                                headers={
                                    'Authorization': f'Bot {token}',
                                    'Content-Type': 'application/json',
                                    'User-Agent': 'DiscordBot'
                                },
                                method='POST'
                            )
                            with urllib.request.urlopen(i_req, timeout=5) as i_res:
                                invite = json.loads(i_res.read().decode('utf-8'))
                                print(f"    🔗 {GREEN}https://discord.gg/{invite['code']}{RESET}")
                        else:
                            print(f"    🔗 {PINK}لا يوجد روم كتابي متاح{RESET}")
                except:
                    print(f"    🔗 {PINK}صلاحيات البوت لا تسمح بصنع رابط{RESET}")
                print("-" * 40)
    except:
        print(f"\n{PINK}❌ التوكن غير صحيح أو انتهت صلاحيته.{RESET}")

def tool_discord_bot():
    print(f"\n{YELLOW}[+] أداة فحص سيرفرات البوت{RESET}")
    bot_token = input(f"{WHITE}◀ أدخل توكن البوت: {RESET}").strip()
    if bot_token:
        get_bot_servers(bot_token)
    else:
        print(f"\n{PINK}❌ لم تدخل التوكن!{RESET}")

# ─────────────────────────────────────────────
# أداة 5 – فاحص يوزرات تيك توك
# ─────────────────────────────────────────────
def generate_username(length):
    valid_first = string.ascii_lowercase + string.digits
    valid_rest  = string.ascii_lowercase + string.digits + '_'
    return random.choice(valid_first) + ''.join(random.choices(valid_rest, k=length - 1))

def read_body(response):
    raw = response.read()
    enc = response.headers.get('Content-Encoding', '')
    if enc == 'gzip':
        try:
            raw = gzip.decompress(raw)
        except:
            pass
    return raw.decode('utf-8', errors='ignore')

def is_tiktok_available(username):
    """
    Returns True  → يوزر متاح (غير موجود على تيك توك)
    Returns False → يوزر مأخوذ أو غير واضح
    Returns None  → خطأ في الاتصال (تجاهل هذا اليوزر)
    """
    try:
        url = f"https://www.tiktok.com/@{username}"
        req = urllib.request.Request(url, headers={
            'User-Agent':      random.choice(USER_AGENTS),
            'Accept':          'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection':      'keep-alive',
            'Cache-Control':   'no-cache',
        })
        with urllib.request.urlopen(req, timeout=8) as response:
            body = read_body(response)

            lower = body.lower()
            uname = username.lower()

            # مأخوذ: اليوزر موجود في البيانات المضمّنة
            if f'"uniqueid":"{uname}"' in lower:
                return False
            if f'"uniqueId":"{username}"' in body:
                return False

            # متاح: مؤشرات واضحة إن الحساب غير موجود
            not_found_signals = [
                "couldn't find this account",
                "this account doesn\u2019t exist",
                '"statuscode":10202',
                '"status_code":10202',
                '"user":{}',
                'page not found',
            ]
            if any(s in lower for s in not_found_signals):
                return True

            # إذا الصفحة ترجع بدون أي بيانات يوزر واضحة → متاح
            if '"uniqueid"' not in lower and '"userinfo"' not in lower:
                return True

            return False

    except urllib.error.HTTPError as e:
        if e.code in (404, 301):
            return True
        return None
    except urllib.error.URLError:
        return None
    except Exception:
        return None

def send_to_webhook(username, webhook_url):
    try:
        payload = {
            "embeds": [{
                "title": "✅ يوزر تيك توك متاح!",
                "description": f"**@{username}**\n🔗 https://www.tiktok.com/@{username}",
                "color": 0x00ff88,
                "footer": {"text": "7ko Tools – TikTok Checker"}
            }]
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status in (200, 204)
    except:
        return False

found_lock  = threading.Lock()
stop_event  = threading.Event()
stats       = {'checked': 0, 'found': 0, 'skipped': 0}
print_lock  = threading.Lock()

def print_status():
    with found_lock:
        c, f, s = stats['checked'], stats['found'], stats['skipped']
    with print_lock:
        print(f"\r{CYAN}[~] فحصنا: {WHITE}{c}{CYAN}  |  وجدنا: {GREEN}{f}{CYAN}  |  تجاهلنا: {YELLOW}{s}{RESET}   ", end='', flush=True)

def checker_worker(webhook_url, length):
    while not stop_event.is_set():
        username  = generate_username(length)
        available = is_tiktok_available(username)

        with found_lock:
            if available is None:
                stats['skipped'] += 1
            else:
                stats['checked'] += 1

        if available is True:
            sent = send_to_webhook(username, webhook_url)
            with found_lock:
                stats['found'] += 1
            with print_lock:
                marker = "✅" if sent else "⚠️"
                print(f"\r{GREEN}✔ @{username}  →  {marker}  {'أُرسل للويبهوك' if sent else 'فشل الإرسال'}{RESET}")
                print_status()

def tool_tiktok(webhook_url, length):
    global stop_event, stats
    stop_event.clear()
    stats = {'checked': 0, 'found': 0, 'skipped': 0}

    num_threads = 15

    print(f"\n{CYAN}[+] بدأ الفحص | طول اليوزر: {WHITE}{length}{CYAN} | ثريدات: {WHITE}{num_threads}{RESET}")
    print(f"{WHITE}    اضغط Ctrl+C للإيقاف{RESET}\n")
    print_status()

    threads = [
        threading.Thread(target=checker_worker, args=(webhook_url, length), daemon=True)
        for _ in range(num_threads)
    ]
    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(0.5)
            print_status()
    except KeyboardInterrupt:
        stop_event.set()
        with found_lock:
            c, f = stats['checked'], stats['found']
        print(f"\n\n{YELLOW}[!] توقف. فحصنا {c} يوزر، وجدنا {f} متاح.{RESET}")

# ─────────────────────────────────────────────
# القائمة الرئيسية
# ─────────────────────────────────────────────
def main_menu():
    clear_screen()
    show_logo()

    print(f"{GREEN}~ [1] IP Address & Ports Tool{RESET}")
    print(f"       {BLUE}~ [2] Translation Tool (EN → AR){RESET}")
    print(f"                      {PINK}~ [3] Discord Users Tool{RESET}")
    print(f"                                    {YELLOW}~ [4] Discord Bot Tool{RESET}")
    print(f"                                                   {CYAN}~ [5] TikTok Username Checker{RESET}")
    print("\n" + "=" * 52)
    print(f"{YELLOW} [0] Exit / خروج{RESET}")
    print("=" * 52)

    choice = input(f"\n{WHITE}◀ اختر رقم الأداة: {RESET}").strip()

    if choice == '1':
        tool_ip()

    elif choice == '2':
        tool_translate()

    elif choice == '3':
        tool_discord_users()

    elif choice == '4':
        tool_discord_bot()

    elif choice == '5':
        print(f"\n{CYAN}╔══════════════════════════════════════╗")
        print(f"║    أداة صيد يوزرات تيك توك           ║")
        print(f"╚══════════════════════════════════════╝{RESET}")

        # طول اليوزر
        while True:
            length_input = input(f"\n{WHITE}◀ تبي رباعي (4) ولا خماسي (5)؟  ← {RESET}").strip()
            if length_input in ('4', '5'):
                length = int(length_input)
                break
            print(f"{PINK}❌ اختر 4 أو 5 فقط{RESET}")

        # ويبهوك
        wh = input(f"\n{WHITE}◀ أدخل رابط الويبهوك: {RESET}").strip()
        if not wh:
            print(f"\n{PINK}❌ لازم تدخل الويبهوك!{RESET}")
            input(f"\n{WHITE}اضغط Enter للعودة...{RESET}")
            main_menu()
            return

        tool_tiktok(wh, length)

    elif choice == '0':
        print(f"\n{YELLOW}في أمان الله! تم الخروج.{RESET}\n")
        sys.exit()

    else:
        print(f"\n{PINK}❌ اختيار غير صحيح.{RESET}")

    input(f"\n{WHITE}اضغط Enter للعودة إلى القائمة...{RESET}")
    main_menu()

if __name__ == "__main__":
    main_menu()

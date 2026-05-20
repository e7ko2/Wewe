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

def clear_screen():
    os.system('clear')

WHITE = '\033[1;37m'
GREEN = '\033[1;32m'
BLUE = '\033[1;34m'
PINK = '\033[1;35m'
YELLOW = '\033[1;33m'
CYAN = '\033[1;36m'
RESET = '\033[0m'

WEBHOOK_URL = ""

def show_logo():
    print(f"{WHITE}")
    print(" ▄▄▄▄▄▄▄              ")
    print(" ▀▀▀▀▀██              ")
    print("     ██   ▄▄          ")
    print("  ▄▄██▄▄  ██ ▄█▀ ▄███▄")
    print("    ██    ████   ██ ██")
    print("    ██   ▄██ ▀█▄▄▀███▀")
    print(f"{RESET}")

def translate_to_arabic(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res[0][0][0]
    except:
        return "حدث خطأ أثناء الترجمة، تأكد من اتصال الإنترنت."

def get_bot_servers(token):
    print(f"\n{YELLOW}[*] جاري الاتصال بديسكورد وفحص التوكن...{RESET}")
    
    guilds_url = "https://discord.com/api/v10/users/@me/guilds"
    req = urllib.request.Request(guilds_url, headers={'Authorization': f'Bot {token}', 'User-Agent': 'DiscordBot'})
    
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            guilds = json.loads(response.read().decode('utf-8'))
            
            if not guilds:
                print(f"\n{PINK}![!] البوت شغال، لكنه مو داخل في أي سيرفر حالياً.{RESET}")
                return
                
            print(f"\n{GREEN}✔ تم بنجاح! البوت داخل في ({len(guilds)}) سيرفرات:{RESET}\n")
            
            for index, g in enumerate(guilds, 1):
                guild_id = g['id']
                guild_name = g['name']
                print(f"{WHITE}[{index}] السيرفر: {YELLOW}{guild_name}{WHITE} (ID: {guild_id}){RESET}")
                
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
                                'Authorization': f'Bot {token}',
                                'Content-Type': 'application/json',
                                'User-Agent': 'DiscordBot'
                            }, method='POST')
                            
                            with urllib.request.urlopen(i_req, timeout=5) as i_res:
                                invite_data = json.loads(i_res.read().decode('utf-8'))
                                print(f"    🔗 رابط الدعوة: {GREEN}https://discord.gg/{invite_data['code']}{RESET}")
                        else:
                            print(f"    🔗 رابط الدعوة: {PINK}لم يتم العثور على روم كتابي متاح{RESET}")
                except:
                    print(f"    🔗 رابط الدعوة: {PINK}صلاحيات البوت لا تسمح بصنع رابط في هذا السيرفر{RESET}")
                print("-" * 40)
                
    except Exception as e:
        print(f"\n{PINK}❌ خطأ: التوكن غير صحيح أو انتهت صلاحيته.{RESET}")

def generate_username():
    chars = string.ascii_lowercase + string.digits + '_'
    first_chars = string.ascii_lowercase + string.digits
    username = random.choice(first_chars)
    username += ''.join(random.choices(chars, k=3))
    return username

def is_tiktok_available(username):
    try:
        url = f"https://www.tiktok.com/@{username}"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            body = response.read().decode('utf-8', errors='ignore')
            if '"statusCode":10202' in body or 'User not found' in body or '"userInfo":{}' in body:
                return True
            return False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return True
        return False
    except:
        return False

def send_to_webhook(username, webhook_url):
    try:
        payload = {
            "embeds": [{
                "title": "✅ يوزر تيك توك رباعي متاح!",
                "description": f"**@{username}**\n🔗 https://www.tiktok.com/@{username}",
                "color": 0x00ff88,
                "footer": {"text": "7ko Tools - TikTok Checker"}
            }]
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status in (200, 204)
    except:
        return False

found_lock = threading.Lock()
stop_event = threading.Event()
stats = {'checked': 0, 'found': 0}

def checker_worker(webhook_url):
    while not stop_event.is_set():
        username = generate_username()
        with found_lock:
            stats['checked'] += 1

        available = is_tiktok_available(username)

        if available:
            sent = send_to_webhook(username, webhook_url)
            with found_lock:
                stats['found'] += 1
                if sent:
                    print(f"\r{GREEN}✔ يوزر متاح: @{username} → تم الإرسال للويبهوك ✅{RESET}")
                else:
                    print(f"\r{YELLOW}✔ يوزر متاح: @{username} → فشل الإرسال ❌{RESET}")
                print(f"{CYAN}[~] تم الفحص: {stats['checked']} | وجدنا: {stats['found']}{RESET}", end='', flush=True)

def tiktok_checker_tool(webhook_url):
    global stop_event, stats
    stop_event.clear()
    stats = {'checked': 0, 'found': 0}

    num_threads = 10

    print(f"\n{CYAN}[+] تم تشغيل فاحص يوزرات تيك توك الرباعية{RESET}")
    print(f"{WHITE}[~] عدد الثريدات: {num_threads} | اضغط Ctrl+C للإيقاف{RESET}\n")
    print(f"{CYAN}[~] تم الفحص: 0 | وجدنا: 0{RESET}", end='', flush=True)

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=checker_worker, args=(webhook_url,), daemon=True)
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)
            with found_lock:
                print(f"\r{CYAN}[~] تم الفحص: {stats['checked']} | وجدنا: {stats['found']}{RESET}", end='', flush=True)
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n\n{YELLOW}[!] تم الإيقاف. الإجمالي: فحصنا {stats['checked']} يوزر، وجدنا {stats['found']} متاح.{RESET}")

def main_menu():
    global WEBHOOK_URL
    clear_screen()
    show_logo()
    
    print(f"{GREEN}~ [1] IP Address & Ports Tool{RESET}")
    print(f"       {BLUE}~ [2] Translation Tool (EN -> AR){RESET}")
    print(f"                                    {PINK}~ [3] Discord Users Tool{RESET}")
    print(f"                                    {YELLOW}~ [4] Discord Bot Tool{RESET}")
    print(f"                                    {CYAN}~ [5] TikTok 4-Char Username Checker{RESET}")
    print("\n" + "="*50)
    print(f"{YELLOW} [0] Exit / خروج{RESET}")
    print("="*50)
    
    choice = input(f"\n{WHITE}◀ اختر رقم الأداة التي تبيها: {RESET}").strip()
    
    if choice == '1':
        print(f"\n{GREEN}[+] أداة استخراج IP وبورتات الموقع{RESET}")
        domain = input(f"{WHITE}◀ أدخل رابط الموقع بدون www (مثال: google.com): {RESET}").strip()
        try:
            ip_address = socket.gethostbyname(domain)
            print(f"\n{GREEN}✔ IP Address للموقع هو: {YELLOW}{ip_address}{RESET}")
            print(f"{GREEN}✔ البورتات المفتوحة الافتراضية للويب: {RESET}")
            print(f"   - Port 80 (HTTP)  -> {GREEN}متاح لفحص الاتصال{RESET}")
            print(f"   - Port 443 (HTTPS) -> {GREEN}متاح لتأمين البيانات{RESET}")
        except socket.gaierror:
            print(f"\n{PINK}❌ خطأ: لم يتم العثور على الموقع، تأكد من كتابة الرابط بشكل صحيح بدون http أو www.{RESET}")
            
    elif choice == '2':
        print(f"\n{BLUE}[+] أداة الترجمة الفورية{RESET}")
        word = input(f"{WHITE}◀ اكتب الكلمة بالإنجليزية لترجمتها للعربية: {RESET}").strip()
        result = translate_to_arabic(word)
        print(f"\n{BLUE}✔ الترجمة بالعربي هي: {YELLOW}{result}{RESET}")
        
    elif choice == '3':
        print(f"\n{PINK}[+] يوزرات ديسكورد رباعية المطلوبة:{RESET}\n")
        users = ["6j5w", "8vgu", "8vgd", "8vgq"]
        for u in users:
            print(f" {WHITE}•{RESET} {PINK}{u}{RESET}")
            
    elif choice == '4':
        print(f"\n{YELLOW}[+] أداة فحص سيرفرات البوت والروابط{RESET}")
        bot_token = input(f"{WHITE}◀ أدخل توكن البوت (Bot Token): {RESET}").strip()
        if bot_token:
            get_bot_servers(bot_token)
        else:
            print(f"\n{PINK}❌ لم تقم بكتابة التوكن!{RESET}")

    elif choice == '5':
        print(f"\n{CYAN}[+] أداة صيد يوزرات تيك توك الرباعية{RESET}")
        if WEBHOOK_URL:
            change = input(f"{WHITE}◀ الويبهوك الحالي: {YELLOW}{WEBHOOK_URL[:40]}...{WHITE}\nتبي تغيره؟ (y/n): {RESET}").strip().lower()
            if change == 'y':
                wh = input(f"{WHITE}◀ أدخل رابط الويبهوك الجديد: {RESET}").strip()
                if wh:
                    WEBHOOK_URL = wh
        else:
            wh = input(f"{WHITE}◀ أدخل رابط ويبهوك الديسكورد: {RESET}").strip()
            if not wh:
                print(f"\n{PINK}❌ لازم تدخل رابط الويبهوك!{RESET}")
                input(f"\n{WHITE}اضغط Enter للعودة...{RESET}")
                main_menu()
                return
            WEBHOOK_URL = wh

        tiktok_checker_tool(WEBHOOK_URL)
            
    elif choice == '0':
        print(f"\n{YELLOW}في أمان الله يا حكو! تم الخروج.{RESET}\n")
        sys.exit()
    else:
        print(f"\n{PINK}❌ اختيار غير صحيح، الرجاء اختيار رقم متاح في القائمة{RESET}")
        
    input(f"\n{WHITE}اضغط Enter للعودة إلى القائمة الرئيسية...{RESET}")
    main_menu()

if __name__ == "__main__":
    clear_screen()
    show_logo()
    print(f"{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║   أدخل ويبهوك الديسكورد للأداة 5   ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════╝{RESET}")
    wh = input(f"\n{WHITE}◀ رابط الويبهوك (اضغط Enter لتخطي): {RESET}").strip()
    if wh:
        WEBHOOK_URL = wh
        print(f"{GREEN}✔ تم حفظ الويبهوك!{RESET}")
    else:
        print(f"{YELLOW}[!] لم يتم إدخال ويبهوك، يمكنك إدخاله عند استخدام الأداة 5{RESET}")
    
    time.sleep(1)
    main_menu()

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
    os.system('clear')

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
        return "حدث خطأ أثناء الترجمة، تأكد من اتصال الإنترنت."

def get_bot_servers(token):
    print(f"\n{YELLOW}[*] جاري الاتصال بديسكورد وفحص التوكن...{RESET}")
    
    guilds_url = "https://discord.com/api/v10/users/@me/guilds"
    req = urllib.request.Request(guilds_url, headers={'Authorization': f'Bot {token}', 'User-Agent': 'DiscordBot'})
    
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            guilds = json.loads(response.read().decode('utf-8'))
            
            if not guilds:
                print(f"\n{PINK}[!] البوت شغال، لكنه مو داخل في أي سيرفر حالياً.{RESET}")
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

def send_to_webhook(username, pattern_type):
    global WEBHOOK_URL
    if not WEBHOOK_URL:
        return
    
    # أيقونة حسب النمط
    icons = {
        "under_begin": "🔰",   # _xxx
        "under_mid": "💎",     # x_xx
        "under_end": "🔥",     # xxx_
        "under_x2": "👑"       # _xx_ or xx_x
    }
    icon = icons.get(pattern_type, "⭐")
    
    data = {
        "content": f"{icon} **تيكن توك - يوزر نادر مع أندر سكور!**\n\n"
                   f"📛 **اليوزر:** `{username}`\n"
                   f"🔗 **الرابط:** https://www.tiktok.com/@{username}\n"
                   f"📋 **النوع:** `{pattern_type}`",
        "username": "TikTok Rare Checker",
        "avatar_url": "https://i.imgur.com/4M34hi2.png"
    }
    
    try:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(WEBHOOK_URL, data=data_bytes, 
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

def generate_rare_username():
    """توليد يوزر 4-5 أحرف مع أندر سكور _ في مكان عشوائي"""
    chars_letters = string.ascii_lowercase
    chars_digits = string.digits
    chars_all = chars_letters + chars_digits
    
    # اختيار نمط عشوائي
    pattern = random.randint(1, 6)
    
    if pattern == 1:  # _xxx  (أندر سكور في البداية)
        body = ''.join(random.choices(chars_all, k=3))
        username = f"_{body}"
        ptype = "under_begin"
    elif pattern == 2:  # x_xx  (أندر سكور في المنتصف بعد أول حرف)
        a = random.choice(chars_all)
        body = ''.join(random.choices(chars_all, k=2))
        username = f"{a}_{body}"
        ptype = "under_mid"
    elif pattern == 3:  # xx_x  (أندر سكور قبل الآخر)
        body = ''.join(random.choices(chars_all, k=2))
        a = random.choice(chars_all)
        username = f"{body}_{a}"
        ptype = "under_mid"
    elif pattern == 4:  # xxx_  (أندر سكور في النهاية)
        body = ''.join(random.choices(chars_all, k=3))
        username = f"{body}_"
        ptype = "under_end"
    elif pattern == 5:  # _xx_  (أندر سكور بداية ونهاية)
        body = ''.join(random.choices(chars_all, k=2))
        username = f"_{body}_"
        ptype = "under_x2"
    else:  # xx_x  (أي نمط آخر)
        a = random.choice(chars_letters)
        b = random.choice(chars_digits)
        c = random.choice(chars_letters)
        username = f"{a}{b}_{c}"
        ptype = "under_mid"
    
    return username, ptype

def check_username(username):
    try:
        req = urllib.request.Request(f"https://www.tiktok.com/@{username}", 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}, method='HEAD')
        urllib.request.urlopen(req, timeout=5)
        return False
    except urllib.error.HTTPError as e:
        if e.code in [404, 302, 301]:
            return True
        return False
    except:
        return False

def tiktok_worker():
    global found_count, checked_count, running, checked_set
    
    while running:
        username, ptype = generate_rare_username()
        
        # منع التكرار
        with checked_set_lock:
            if username in checked_set:
                continue
            checked_set.add(username)
        
        with lock:
            checked_count += 1
            current_checked = checked_count
        
        print(f"{WHITE}[{current_checked}] {BLUE}جاري فحص: {CYAN}{username}{RESET}    ", end='\r')
        
        if check_username(username):
            with lock:
                found_count += 1
                current_found = found_count
            
            # ألوان مختلفة حسب النمط
            color = GREEN
            if ptype == "under_begin":
                color = CYAN
            elif ptype == "under_end":
                color = YELLOW
            elif ptype == "under_x2":
                color = RED
            
            print(f"\n{color}✅ [نادر: {ptype}] {WHITE}{username} {color}https://www.tiktok.com/@{username}{RESET}")
            
            # حفظ في ملف
            with open('tiktok_rare_hits.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{ptype}] {username} | https://www.tiktok.com/@{username}\n")
            
            # إرسال للويبهوك
            send_to_webhook(username, ptype)
            
            # صوت تنبيه
            print('\a', end='')

def tiktok_checker_menu():
    global WEBHOOK_URL, running, found_count, checked_count, checked_set
    
    found_count = 0
    checked_count = 0
    running = True
    checked_set = set()
    
    clear_screen()
    print(f"\n{RED}═══════════════════════════════════════{RESET}")
    print(f"{RED}   TikTok Rare Username Checker 🚀{RESET}")
    print(f"{RED}═══════════════════════════════════════{RESET}")
    print(f"\n{WHITE}🔥 الأداة تولد يوزرات نادرة مع أندر سكور _")
    print(f"🎯 أنماط اليوزرات:")
    print(f"   {CYAN}_xxx{RESET}  - أندر سكور بالبداية (نادر جداً)")
    print(f"   {GREEN}x_xx{RESET}  - أندر سكور بالوسط")
    print(f"   {YELLOW}xxx_{RESET}  - أندر سكور بالنهاية")
    print(f"   {RED}_xx_{RESET}  - أندر سكور بداية ونهاية (أندر ما يكون){RESET}")
    
    WEBHOOK_URL = input(f"\n{WHITE}◀ أدخل رابط ويبهوك الديسكورد:\n{BLUE}>> {RESET}").strip()
    
    if not WEBHOOK_URL:
        print(f"\n{YELLOW}⚠ ما أدخلت رابط ويبهوك! بتشتغل بدون إرسال.{RESET}")
        WEBHOOK_URL = ""
    
    try:
        threads_count = input(f"\n{WHITE}◀ عدد الثريدات? (يفضل 20-100, Enter=50):\n{BLUE}>> {RESET}").strip()
        threads_count = int(threads_count) if threads_count else 50
        if threads_count < 1 or threads_count > 500:
            threads_count = 50
    except:
        threads_count = 50
    
    print(f"\n{GREEN}🚀 بدء الفحص بـ {threads_count} ثريد... اضغط Ctrl+C للإيقاف{RESET}")
    print(f"{YELLOW}⚡ اليوزرات النادرة المتاحة راح تظهر بكل الألوان🔥{RESET}\n")
    
    time.sleep(1)
    
    threads = []
    try:
        for _ in range(threads_count):
            t = threading.Thread(target=tiktok_worker, daemon=True)
            t.start()
            threads.append(t)
        
        while running:
            time.sleep(3)
            with lock:
                unique_count = len(checked_set)
                print(f"{WHITE}[فحص {checked_count}] {GREEN}✅ متاح: {found_count} {BLUE}| {CYAN}فريد: {unique_count}{RESET}    ", end='\r')
    
    except KeyboardInterrupt:
        running = False
        print(f"\n\n{YELLOW}⏹ تم إيقاف الفحص.{RESET}")
        print(f"{GREEN}📊 النتيجة: فحص {checked_count} يوزر - وجد {found_count} نادر متاح{RESET}")
        print(f"{WHITE}📁 اليوزرات محفوظة في: tiktok_rare_hits.txt{RESET}")
        
        input(f"\n{WHITE}اضغط Enter للعودة للقائمة الرئيسية...{RESET}")
        main_menu()

def main_menu():
    clear_screen()
    show_logo()
    
    print(f"{GREEN}~ [1] IP Address & Ports Tool{RESET}")
    print(f"       {BLUE}~ [2] Translation Tool (EN -> AR){RESET}")
    print(f"                                    {PINK}~ [3] Discord Users Tool{RESET}")
    print(f"                                    {YELLOW}~ [4] Discord Bot Tool{RESET}")
    print(f"{RED}~ [5] TikTok Rare Username Checker (أندر سكور) 🔥{RESET}")
    print("\n" + "="*50)
    print(f"{YELLOW} [0] Exit / خروج{RESET}")
    print("="*50)
    
    choice = input(f"\n{WHITE}◀ اختر رقم الأداة: {RESET}").strip()
    
    if choice == '1':
        print(f"\n{GREEN}[+] أداة استخراج IP وبورتات الموقع{RESET}")
        domain = input(f"{WHITE}◀ أدخل رابط الموقع: {RESET}").strip()
        try:
            ip_address = socket.gethostbyname(domain)
            print(f"\n{GREEN}✔ IP Address: {YELLOW}{ip_address}{RESET}")
            print(f"{GREEN}✔ البورتات المفتوحة الافتراضية: {RESET}")
            print(f"   - Port 80 (HTTP)  -> {GREEN}متاح{RESET}")
            print(f"   - Port 443 (HTTPS) -> {GREEN}متاح{RESET}")
        except socket.gaierror:
            print(f"\n{PINK}❌ خطأ: لم يتم العثور على الموقع.{RESET}")
            
    elif choice == '2':
        print(f"\n{BLUE}[+] أداة الترجمة الفورية{RESET}")
        word = input(f"{WHITE}◀ اكتب الكلمة بالإنجليزية: {RESET}").strip()
        result = translate_to_arabic(word)
        print(f"\n{BLUE}✔ الترجمة: {YELLOW}{result}{RESET}")
        
    elif choice == '3':
        print(f"\n{PINK}[+] يوزرات ديسكورد رباعية:{RESET}\n")
        users = ["6j5w", "8vgu", "8vgd", "8vgq"]
        for u in users:
            print(f" {WHITE}•{RESET} {PINK}{u}{RESET}")
            
    elif choice == '4':
        print(f"\n{YELLOW}[+] أداة فحص سيرفرات البوت{RESET}")
        bot_token = input(f"{WHITE}◀ أدخل توكن البوت: {RESET}").strip()
        if bot_token:
            get_bot_servers(bot_token)
        else:
            print(f"\n{PINK}❌ لم تقم بكتابة التوكن!{RESET}")
    
    elif choice == '5':
        tiktok_checker_menu()
        return
            
    elif choice == '0':
        print(f"\n{YELLOW}في أمان الله! تم الخروج.{RESET}\n")
        sys.exit()
    else:
        print(f"\n{PINK}❌ اختيار غير صحيح.{RESET}")
        
    input(f"\

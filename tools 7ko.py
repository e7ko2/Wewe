import os
import sys
import socket
import urllib.request
import urllib.parse
import urllib.error
import json
import string
import random
import threading
import time
from queue import Queue

def clear_screen():
    os.system('clear')

WHITE = '\033[1;37m'
GREEN = '\033[1;32m'
BLUE = '\033[1;34m'
PINK = '\033[1;35m'
YELLOW = '\033[1;33m'
RED = '\033[1;31m'
RESET = '\033[0m'

# متغيرات عامة للخيار 5
FOUND_COUNT = 0
CHECKED_COUNT = 0
LOCK = threading.Lock()
STOP_FLAG = False
WEBHOOK_URL = ""
START_TIME = 0

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

# ========== خيار 5: فحص يوزرات تيك توك رباعية ==========

def send_to_discord(username):
    """إرسال اليوزر الصحيح للويبهوك فقط"""
    global WEBHOOK_URL
    data = {
        "content": f"@everyone ✅ **تم العثور على يوزر تيك توك رباعي صحيح!**\n**@{username}**\nhttps://www.tiktok.com/@{username}"
    }
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
        method='POST'
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        return True
    except:
        return False

def check_tiktok_user(username):
    """فحص إذا اليوزر موجود على تيك توك"""
    url = f"https://www.tiktok.com/@{username}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
    })
    try:
        resp = urllib.request.urlopen(req, timeout=4)
        if resp.getcode() == 200:
            html = resp.read().decode('utf-8', errors='ignore')
            if 'Page Not Found' in html or 'page not found' in html or 'could not be found' in html:
                return False
            return True
        return False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        elif e.code in (403, 302, 301):
            return True
        return False
    except:
        return False

def generate_username():
    """توليد يوزر رباعي عشوائي"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=4))

def worker(thread_id):
    """دالة الشغالة - كل ثريد"""
    global FOUND_COUNT, CHECKED_COUNT, STOP_FLAG
    
    while not STOP_FLAG:
        username = generate_username()
        
        with LOCK:
            CHECKED_COUNT += 1
            current_checked = CHECKED_COUNT
        
        # عرض تقدم كل 20 فحص
        if current_checked % 20 == 0:
            with LOCK:
                cf = FOUND_COUNT
            elapsed = max(int(time.time() - START_TIME), 1)
            print(f"\r{YELLOW}[*] فحص: {current_checked} | وجد: {GREEN}{cf}{RESET} | سرعة: {WHITE}{current_checked // elapsed}/ث{RESET}  ", end="", flush=True)
        
        # الفحص الفعلي
        exists = check_tiktok_user(username)
        
        if exists:
            with LOCK:
                FOUND_COUNT += 1
                current_found = FOUND_COUNT
            
            # إرسال للويبهوك فقط الصحيح
            success = send_to_discord(username)
            symbol = "✅" if success else "⚠️"
            print(f"\n{GREEN}{symbol} [موجود] @{username} -> تم الإرسال! (#{current_found}){RESET}")
        
        # وقفة خفيفة جداً
        time.sleep(0.03)

def tiktok_username_tool():
    """الخيار الخامس - الأداة الرئيسية"""
    global WEBHOOK_URL, FOUND_COUNT, CHECKED_COUNT, STOP_FLAG, START_TIME
    
    FOUND_COUNT = 0
    CHECKED_COUNT = 0
    STOP_FLAG = False
    START_TIME = time.time()
    
    clear_screen()
    show_logo()
    
    print(f"\n{PINK}══════════════════════════════════════════{RESET}")
    print(f"{PINK}   TikTok 4-Character Username Checker{RESET}")
    print(f"{PINK}══════════════════════════════════════════{RESET}\n")
    
    # طلب الويبهوك
    WEBHOOK_URL = input(f"{WHITE}◀ أدخل رابط Webhook الديسكورد: {RESET}").strip()
    
    if not WEBHOOK_URL.startswith("https://discord.com/api/webhooks/"):
        print(f"\n{RED}❌ رابط ويبهوك غير صحيح!{RESET}")
        input(f"\n{WHITE}اضغط Enter للعودة...{RESET}")
        return
    
    # اختبار الويبهوك
    print(f"\n{YELLOW}[*] جاري اختبار الويبهوك...{RESET}")
    test_data = {"content": "🚀 **تم تشغيل فحص يوزرات تيك توك الرباعية!** جاري البحث..."}
    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(test_data).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=5)
        print(f"{GREEN}✔ الويبهوك شغال 100%!{RESET}")
    except:
        print(f"{RED}❌ فشل الاتصال بالويبهوك!{RESET}")
        input(f"\n{WHITE}اضغط Enter للعودة...{RESET}")
        return
    
    # اختيار عدد الثريدات
    print(f"\n{WHITE}اختر السرعة:{RESET}")
    print(f"  {GREEN}[1]{RESET} هادئ - 5 ثريدات")
    print(f"  {GREEN}[2]{RESET} سريع - 15 ثريد")
    print(f"  {GREEN}[3]{RESET} سوبر - 30 ثريد {YELLOW}(ممتاز){RESET}")
    print(f"  {GREEN}[4]{RESET} أسطوري - 50 ثريد {RED}(قد يحظر){RESET}")
    
    speed = input(f"\n{WHITE}◀ اختر (1-4) [افتراضي 3]: {RESET}").strip()
    speed_map = {'1': 5, '2': 15, '3': 30, '4': 50}
    num_threads = speed_map.get(speed, 30)
    
    clear_screen()
    show_logo()
    
    print(f"\n{GREEN}══════════════════════════════════════════{RESET}")
    print(f"{GREEN}   🔍 الأداة شغالة! 🔍{RESET}")
    print(f"{GREEN}══════════════════════════════════════════{RESET}")
    print(f"{WHITE}  • ثريدات: {YELLOW}{num_threads}{RESET}")
    print(f"{WHITE}  • الصحيح → ويبهوك | الغلط → يتجاهل{RESET}")
    print(f"{WHITE}  • اوقف بـ {RED}Ctrl+C{RESET}")
    print(f"{GREEN}══════════════════════════════════════════\n{RESET}")
    
    # تشغيل الثريدات
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    # الحلقة الرئيسية
    try:
        while True:
            time.sleep(3)
    except KeyboardInterrupt:
        STOP_FLAG = True
        elapsed = int(time.time() - START_TIME)
        print(f"\n\n{YELLOW}⏹ تم الإيقاف!{RESET}")
        print(f"{GREEN}📊 الإحصائيات:{RESET}")
        print(f"  • إجمالي الفحص: {WHITE}{CHECKED_COUNT}{RESET}")
        print(f"  • يوزرات صحيحة: {GREEN}{FOUND_COUNT}{RESET}")
        print(f"  • الوقت: {WHITE}{elapsed} ثانية{RESET}")
        print(f"  • السرعة: {WHITE}{CHECKED_COUNT // max(elapsed, 1)} يوزر/ثانية{RESET}")
    
    input(f"\n{WHITE}اضغط Enter للعودة...{RESET}")

# ========== القائمة الرئيسية ==========

def main_menu():
    clear_screen()
    show_logo()
    
    print(f"{GREEN}~ [1] IP Address & Ports Tool{RESET}")
    print(f"       {BLUE}~ [2] Translation Tool (EN -> AR){RESET}")
    print(f"                                    {PINK}~ [3] Discord Users Tool{RESET}")
    print(f"                                    {YELLOW}~ [4] Discord Bot Tool{RESET}")
    print(f"                                    {RED}~ [5] TikTok 4-Char Username 🔥{RESET}")
    print("\n" + "="*50)
    print(f"{YELLOW} [0] Exit{RESET}")
    print("="*50)
    
    choice = input(f"\n{WHITE}◀ اختر رقم: {RESET}").strip()
    
    if choice == '1':
        print(f"\n{GREEN}[+] IP & Ports{RESET}")
        domain = input(f"{WHITE}◀ domain: {RESET}").strip()
        try:
            ip = socket.gethostbyname(domain)
            print(f"\n{GREEN}✔ IP: {YELLOW}{ip}{RESET}")
            print(f"{GREEN}✔ Ports: 80 (HTTP), 443 (HTTPS){RESET}")
        except socket.gaierror:
            print(f"\n{PINK}❌ خطأ في اسم النطاق{RESET}")
    elif choice == '2':
        print(f"\n{BLUE}[+] Translation{RESET}")
        word = input(f"{WHITE}◀ EN: {RESET}").strip()
        print(f"\n{GREEN}AR: {YELLOW}{translate_to_arabic(word)}{RESET}")
    elif choice == '3':
        print(f"\n{PINK}[+] Discord users:{RESET}\n")
        for u in ["6j5w", "8vgu", "8vgd", "8vgq"]:
            print(f"  {PINK}• {u}{RESET}")
    elif choice == '4':
        print(f"\n{YELLOW}[+] Bot Tool{RESET}")
        token = input(f"{WHITE}◀ Bot token: {RESET}").strip()
        if token: get_bot_servers(token)
        else: print(f"{PINK}❌ لا يوجد توكن{RESET}")
    elif choice == '5':
        tiktok_username_tool()
    elif choice == '0':
        print(f"\n{YELLOW}الله معاك!{RESET}\n"); sys.exit()
    else:
        print(f"\n{PINK}❌ رقم خطأ{RESET}")
    
    input(f"\n{WHITE}اضغط Enter...{RESET}")
    main_menu()

if __name__ == "__main__":
    main_menu()

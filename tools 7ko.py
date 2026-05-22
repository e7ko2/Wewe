import os
import sys
import socket
import urllib.request
import urllib.parse
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

# ====== متغيرات عامة للخيار الخامس ======
FOUND_COUNT = 0
CHECKED_COUNT = 0
LOCK = threading.Lock()
STOP_FLAG = False
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

# ===================== خيار 5: فحص يوزرات تيك توك رباعية =====================

def send_to_discord(username):
    """إرسال اليوزر الصحيح للويبهوك"""
    global WEBHOOK_URL
    data = {
        "content": f"@everyone ✅ تم العثور على يوزر تيك توك رباعي صحيح:\n**@{username}**\nhttps://www.tiktok.com/@{username}"
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
    """فحص إذا كان يوزر تيك توك موجود أو لا"""
    url = f"https://www.tiktok.com/@{username}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
    })
    try:
        resp = urllib.request.urlopen(req, timeout=4)
        # إذا جاب 200 معناه اليوزر موجود
        if resp.getcode() == 200:
            # نتأكد أكثر: نشوف إذا الصفحة تقول "Page not found" أو لا
            html = resp.read().decode('utf-8', errors='ignore')
            if 'Page Not Found' in html or 'page not found' in html or 'could not be found' in html:
                return False
            return True
        return False
    except urllib.error.HTTPError as e:
        # 404 = غير موجود ، 403 = موجود غالباً (ممنوع لكن الحساب موجود)
        if e.code == 404:
            return False
        elif e.code == 403 or e.code == 302 or e.code == 301:
            # 403 معناه الحساب موجود لكن محظور أو خاص
            # 302/301 إعادة توجيه = موجود
            return True
        return False
    except:
        return False

def generate_username():
    """توليد يوزر رباعي عشوائي"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=4))

def worker(thread_id):
    """دالة كل ثريد يعملها"""
    global FOUND_COUNT, CHECKED_COUNT, STOP_FLAG
    
    while not STOP_FLAG:
        username = generate_username()
        
        with LOCK:
            CHECKED_COUNT += 1
            current_checked = CHECKED_COUNT
            current_found = FOUND_COUNT
        
        # شاشة عرض سريعة
        if current_checked % 10 == 0:
            print(f"\r{YELLOW}[*] تم الفحص: {current_checked} | تم العثور: {GREEN}{current_found}{RESET}    ", end="", flush=True)
        
        # فحص اليوزر
        exists = check_tiktok_user(username)
        
        if exists:
            with LOCK:
                FOUND_COUNT += 1
                current_found = FOUND_COUNT
            
            # إرسال للويبهوك
            success = send_to_discord(username)
            
            symbol = "✅" if success else "⚠️"
            print(f"\n{GREEN}{symbol} [يوزر رباعي صحيح] @{username} -> تم الإرسال للويبهوك! (إجمالي: {current_found}){RESET}")
        
        # وقفة خفيفة عشان لا نثقل على السيرفر
        time.sleep(0.05)

def tiktok_username_tool():
    """الخيار الخامس - أداة فحص يوزرات تيك توك الرباعية"""
    global WEBHOOK_URL, FOUND_COUNT, CHECKED_COUNT, STOP_FLAG
    
    # تصفير المتغيرات
    FOUND_COUNT = 0
    CHECKED_COUNT = 0
    STOP_FLAG = False
    
    clear_screen()
    show_logo()
    
    print(f"\n{PINK}══════════════════════════════════════════{RESET}")
    print(f"{PINK}   TikTok 4-Character Username Checker{RESET}")
    print(f"{PINK}══════════════════════════════════════════{RESET}\n")
    
    # طلب الويبهوك
    WEBHOOK_URL = input(f"{WHITE}◀ أدخل رابط Webhook الديسكورد: {RESET}").strip()
    
    if not WEBHOOK_URL.startswith("https://discord.com/api/webhooks/"):
        print(f"\n{RED}❌ رابط ويبهوك غير صحيح! تأكد من الرابط.{RESET}")
        input(f"\n{WHITE}اضغط Enter للعودة...{RESET}")
        return
    
    # اختبار الويبهوك
    print(f"\n{YELLOW}[*] جاري اختبار الويبهوك...{RESET}")
    test_data = {
        "content": "🚀 **تم تشغيل أداة فحص يوزرات تيك توك الرباعية!**\n✅ جاري البحث عن يوزرات رباعية..."
    }
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
        print(f"{RED}❌ فشل الاتصال بالويبهوك، تحقق من الرابط.{RESET}")
        input(f"\n{WHITE}اضغط Enter للعودة...{RESET}")
        return
    
    # اختيار عدد الثريدات
    print(f"\n{WHITE}عدد الثريدات (السرعة):{RESET}")
    print(f"{GREEN}  [1] {RESET}هادئ - 5 ثريدات")
    print(f"{GREEN}  [2] {RESET}سريع - 15 ثريد")
    print(f"{GREEN}  [3] {RESET}سوبر - 30 ثريد {YELLOW}(يوصى به){RESET}")
    print(f"{GREEN}  [4] {RESET}أسطوري - 50 ثريد {RED}(قد يحظر){RESET}")
    
    speed = input(f"\n{WHITE}◀ اختر السرعة (1-4) [افتراضي 3]: {RESET}").strip()
    speed_map = {'1': 5, '2': 15, '3': 30, '4': 50}
    num_threads = speed_map.get(speed, 30)
    
    clear_screen()
    show_logo()
    
    print(f"\n{GREEN}══════════════════════════════════════════{RESET}")
    print(f"{GREEN}   🔍 الأداة شغالة! 🔍{RESET}")
    print(f"{GREEN}══════════════════════════════════════════{RESET}")
    print(f"{WHITE}  • عدد الثريدات: {YELLOW}{num_threads}{RESET}")
    print(f"{WHITE}  • اليوزرات الصحيحة تُرسل للويبهوك{RESET}")
    print(f"{WHITE}  • الغلط يتجاهل ولا يرسل شيء{RESET}")
    print(f"{WHITE}  • اضغط {RED}Ctrl+C{RESET} {WHITE}لإيقاف الأداة{RESET}")
    print(f"{GREEN}══════════════════════════════════════════\n{RESET}")
    
    # تشغيل الثريدات
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    # مراقبة لوحة الإحصائيات
    try:
        while True:
            time.sleep(2)
            with LOCK:
                print(f"\r{YELLOW}[*] تم الفحص: {CHECKED_COUNT} | تم العثور: {GREEN}{FOUND_COUNT}{RESET} | {WHITE}يوزر/ثانية: {YELLOW}{CHECKED_COUNT // max(int(time.time() - start_time), 1)}{RESET}    ", end="", flush=True)
    except KeyboardInterrupt:
        STOP_FLAG = True
        print(f"\n\n{YELLOW}⏹ تم إيقاف الأداة!{RESET}")
        print(f"{GREEN}📊 الإحصائيات النهائية:{RESET}")
        print(f"{WHITE}  • إجمالي الفحص: {YELLOW}{CHECKED_COUNT}{RESET}")
        print(f"{WHITE}  • يوزرات صحيحة: {GREEN}{FOUND_COUNT}{RESET}")
        print(f"{WHITE}  • تم إرسال الكل للويبهوك ✅{RESET}")
    
    input(f"\n{WHITE}اضغط Enter للعودة للقائمة...{RESET}")

# ===================== القائمة الرئيسية =====================

def main_menu():
    clear_screen()
    show_logo()
    
    print(f"{GREEN}~ [1] IP Address & Ports Tool{RESET}")
    print(f"       {BLUE}~ [2] Translation Tool (EN -> AR){RESET}")
    print(f"                                    {PINK}~ [3] Discord Users Tool{RESET}")
    print(f"                                    {YELLOW}~ [4] Discord Bot Tool{RESET}")
    print(f"                                    {RED}~ [5] TikTok 4-Char Username Checker 🔥{RESET}")
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
            get_bot_servers(b

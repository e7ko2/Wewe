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

WEBHOOK_URL = ""
found_count = 0
checked_count = 0
lock = threading.Lock()
running = True

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

def send_to_webhook(username):
    """إرسال اليوزر الرباعي المتاح إلى الويبهوك"""
    global WEBHOOK_URL
    if not WEBHOOK_URL:
        return
    
    data = {
        "content": f"✅ **تيكن توك - يوزر رباعي متاح!**\n\n📛 **اليوزر:** `{username}`\n🔗 **الرابط:** https://www.tiktok.com/@{username}",
        "username": "TikTok Checker",
        "avatar_url": "https://i.imgur.com/4M34hi2.png"
    }
    
    try:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(WEBHOOK_URL, data=data_bytes, 
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

def check_username(username):
    """فحص إذا كان يوزر تيك توك متاح (غير مستخدم)"""
    try:
        req = urllib.request.Request(f"https://www.tiktok.com/@{username}", 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}, method='HEAD')
        urllib.request.urlopen(req, timeout=5)
        return False  # status 200 = اليوزر موجود (غير متاح)
    except urllib.error.HTTPError as e:
        if e.code in [404, 302, 301]:
            return True  # اليوزر غير موجود = متاح!
        return False
    except:
        return False

def generate_4letter():
    """توليد يوزر عشوائي 4 أحرف (حروف + أرقام)"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=4))

def tiktok_worker():
    """وظيفة العامل - يفحص يوزرات رباعية"""
    global found_count, checked_count, running
    
    while running:
        username = generate_4letter()
        
        with lock:
            checked_count += 1
            current_checked = checked_count
        
        # عرض حالة الفحص
        print(f"{WHITE}[{current_checked}] {BLUE}جاري فحص: {YELLOW}{username}{RESET}    ", end='\r')
        
        if check_username(username):
            with lock:
                found_count += 1
                current_found = found_count
            
            print(f"\n{GREEN}✅ [متاح] {WHITE}{username} {GREEN}https://www.tiktok.com/@{username}{RESET}")
            
            # حفظ في ملف
            with open('tiktok_hits.txt', 'a', encoding='utf-8') as f:
                f.write(f"{username} | https://www.tiktok.com/@{username}\n")
            
            # إرسال للويبهوك
            send_to_webhook(username)
            
            # صوت تنبيه
            print('\a', end='')

def tiktok_checker_menu():
    """القائمة الرئيسية لخيار تيك توك"""
    global WEBHOOK_URL, running, found_count, checked_count
    
    found_count = 0
    checked_count = 0
    running = True
    
    clear_screen()
    print(f"\n{YELLOW}═══════════════════════════════════════{RESET}")
    print(f"{RED}   TikTok 4-Letter Username Checker 🚀{RESET}")
    print(f"{YELLOW}═══════════════════════════════════════{RESET}")
    print(f"\n{WHITE}الأداة بتولد يوزرات 4 أحرف عشوائية وتفحصها.")
    print(f"اليوزرات المتاحة (غير المستخدمة) ترسل للويبهوك وتنحفظ بملف.{RESET}")
    
    WEBHOOK_URL = input(f"\n{WHITE}◀ أدخل رابط ويبهوك الديسكورد (Discord Webhook URL):\n{BLUE}>> {RESET}").strip()
    
    if not WEBHOOK_URL:
        print(f"\n{YELLOW}⚠ ما أدخلت رابط ويبهوك! بتشتغل بدون إرسال للويبهوك.{RESET}")
        WEBHOOK_URL = ""
    
    try:
        threads_count = input(f"\n{WHITE}◀ عدد الثريدات للفحص السريع? (يفضل 10-50, Enter=20):\n{BLUE}>> {RESET}").strip()
        threads_count = int(threads_count) if threads_count else 20
        if threads_count < 1:
            threads_count = 20
    except:
        threads_count = 20
    
    print(f"\n{GREEN}🚀 بدء الفحص بـ {threads_count} ثريد... اضغط Ctrl+C للإيقاف{RESET}")
    print(f"{YELLOW}⚡ اليوزرات المتاحة راح تظهر باللون الأخضر وترسل للويبهوك{RESET}\n")
    
    time.sleep(1)
    
    # تشغيل عدة ثريدات
    threads = []
    try:
        for _ in range(threads_count):
            t = threading.Thread(target=tiktok_worker, daemon=True)
            t.start()
            threads.append(t)
        
        # مراقبة الاحصائيات كل 3 ثواني
        while running:
            time.sleep(3)
            with lock:
                print(f"{WHITE}[{checked_count}] {GREEN}تم الفحص ✅ | {BLUE}موجود: {found_count} {RESET}    ", end='\r')
    
    except KeyboardInterrupt:
        running = False
        print(f"\n\n{YELLOW}⏹ تم إيقاف الفحص.{RESET}")
        print(f"{GREEN}📊 النتيجة النهائية: فحص {checked_count} يوزر - وجد {found_count} يوزر متاح{RESET}")
        print(f"{WHITE}📁 اليوزرات المتاحة محفوظة في ملف: tiktok_hits.txt{RESET}")
        
        input(f"\n{WHITE}اضغط Enter للعودة للقائمة الرئيسية...{RESET}")
        main_menu()

def main_menu():
    clear_screen()
    show_logo()
    
    print(f"{GREEN}~ [1] IP Address & Ports Tool{RESET}")
    print(f"       {BLUE}~ [2] Translation Tool (EN -> AR){RESET}")
    print(f"                                    {PINK}~ [3] Discord Users Tool{RESET}")
    print(f"                                    {YELLOW}~ [4] Discord Bot Tool{RESET}")
    print(f"{RED}~ [5] TikTok 4-Letter Username Generator & Checker 🚀{RESET}")
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
        tiktok_checker_menu()
        return
            
    elif choice == '0':
        print(f"\n{YELLOW}في أمان الله يا حكو! تم الخروج.{RESET}\n")
        sys.exit()
    else:
        print(f"\n{PINK}❌ اختيار غير صحيح، الرجاء اختيار رقم متاح في القائمة{RESET}")
        
    input(f"\n{WHITE}اضغط Enter للعودة إلى القائمة الرئيسية...{RESET}")
    main_menu()

if __name__ == "__main__":
    main_menu()

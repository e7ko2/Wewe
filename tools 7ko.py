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

WEBHOOK_URL = ""
found_count = 0
checked_count = 0
lock = threading.Lock()
running = True
checked_set = set()
checked_set_lock = threading.Lock()

# ---- متغيرات ديسكورد يوزرات ----
DC_WEBHOOK = ""
DC_TOKEN = ""
dc_found = 0
dc_checked = 0
dc_running = True

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

# ==================== ديسكورد يوزرات ====================

def send_dc_webhook(username):
    """إرسال اليوزر المتاح للويبهوك"""
    global DC_WEBHOOK
    if not DC_WEBHOOK:
        return
    data = {
        "content": f"✅ **ديسكورد - يوزر مميز متاح!**\n📛 `{username}`\n🔗 https://discord.com/users/{username}",
        "username": "Discord User Checker"
    }
    try:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(DC_WEBHOOK, data=data_bytes,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

def generate_dc_username():
    """توليد يوزر ديسكورد مميز مثل: 7mo, .ksa, _fvl, 7mo., x9m_, _7mo, ksa., mo7_, _x9m"""
    chars_letters = string.ascii_lowercase
    chars_digits = string.digits
    chars_all = chars_letters + chars_digits
    
    pattern = random.randint(1, 10)
    
    if pattern == 1:  # 7mo (3 حروف/أرقام)
        a = random.choice(chars_all)
        b = random.choice(chars_letters)
        c = random.choice(chars_all)
        return f"{a}{b}{c}", "ثلاثي"
    elif pattern == 2:  # .ksa (نقطة + 3 أحرف)
        body = ''.join(random.choices(chars_letters, k=3))
        return f".{body}", "نقطة_بداية"
    elif pattern == 3:  # _fvl (أندر + 3 أحرف)
        body = ''.join(random.choices(chars_letters, k=3))
        return f"_{body}", "أندر_بداية"
    elif pattern == 4:  # 7mo. (3 أحرف + نقطة)
        body = ''.join(random.choices(chars_all, k=3))
        return f"{body}.", "نقطة_نهاية"
    elif pattern == 5:  # x9m_ (4 أحرف + أندر)
        body = ''.join(random.choices(chars_all, k=3))
        return f"{body}_", "أندر_نهاية"
    elif pattern == 6:  # _7mo (أندر + 3 أحرف مع رقم)
        body = ''.join(random.choices(chars_all, k=3))
        return f"_{body}", "أندر_بداية_مختلط"
    elif pattern == 7:  # ksa. (3 أحرف + نقطة)
        body = ''.join(random.choices(chars_letters, k=3))
        return f"{body}.", "نقطة_نهاية_حروف"
    elif pattern == 8:  # mo7_ (3 أحرف + أندر)
        body = ''.join(random.choices(chars_all, k=3))
        return f"{body}_", "أندر_نهاية_مختلط"
    elif pattern == 9:  # _x9m (أندر + حرف + رقم + حرف)
        a = random.choice(chars_letters)
        b = random.choice(chars_digits)
        c = random.choice(chars_letters)
        return f"_{a}{b}{c}", "أندر_بداية_مميز"
    elif pattern == 10:  # 7m.o (حرف + نقطة + حرفين)
        a = random.choice(chars_all)
        b = random.choice(chars_letters)
        c = random.choice(chars_all)
        return f"{a}{b}.{c}", "نقطة_وسط"
    else:  # 7mo
        body = ''.join(random.choices(chars_all, k=3))
        return body, "ثلاثي"

def check_dc_username(username, token):
    """فحص يوزر ديسكورد عن طريق API"""
    try:
        url = f"https://discord.com/api/v10/users/@me"
        req = urllib.request.Request(url, headers={'Authorization': token, 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
        
        # الآن نفحص availability عن طريق lookup
        lookup_url = f"https://discord.com/api/v10/users/@me/relationships"
        l_req = urllib.request.Request(lookup_url, headers={'Authorization': token, 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(l_req, timeout=5) as l_res:
            pass
        
        # نستخدم طريقة الـ lookup غير المباشرة: نجرب نغير اليوزر ونشوف لو موجود
        # هذه الطريقة أسهل: نحاول نبعت ريكويست لبروفايل اليوزر
        check_url = f"https://discord.com/api/v10/users/{random.randint(100000000000000000, 999999999999999999)}"
        # بدلاً من ذلك نستخدم طريقة البحث باليوزر
        
        # الطريقة المضمونة: نفحص عن طريق الـ guilds members
        # لكن بساطة: نستخدم service lookup
        test_url = f"https://discord.com/api/v10/users/@me/profiles"
        test_req = urllib.request.Request(test_url, headers={'Authorization': token, 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(test_req, timeout=5) as test_res:
            pass
        
        # الآن نجرب نغير display name أو نشوف لو اليوزر متاح
        # أسهل طريقة: نستخدم lookup للـ username
        # ديسكورد ما عنده API عام لفحص username availability
        # لكن نقدر نستخدم experimental endpoint
        
        # أقرب طريقة: نحاول نغير username حقنا لهذا الاسم
        # لو نجح = متاح، لو فشل = غير متاح
        return False  # نستخدم طريقة مختلفة بالأسفل
        
    except Exception as e:
        return False

def check_dc_username_simple(username):
    """فحص سريع عبر صفحة الـ vanity URL"""
    try:
        # ديسكورد ما عنده صفحة عامة لـ username
        # نستخدم طريقة head request
        req = urllib.request.Request(f"https://discord.com/users/{username}",
            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'}, method='HEAD')
        urllib.request.urlopen(req, timeout=5)
        return False  # الصفحة موجودة значит userName غير متاح
    except urllib.error.HTTPError as e:
        return e.code in [404, 302, 301]  # الصفحة مو موجودة значит userName متاح
    except:
        return False

def check_dc_username_api(username, token):
    """فحص عبر API ديسكورد - الطريقة الصحيحة"""
    try:
        # ديسكورد يوفر endpoint لـ lookup username (global name)
        # نستخدم method بسيطة: نغير الـ global name حقنا
        url = "https://discord.com/api/v10/users/@me"
        data = json.dumps({"global_name": username}).encode('utf-8')
        req = urllib.request.Request(url, data=data,
            headers={'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
            method='PATCH')
        with urllib.request.urlopen(req, timeout=5) as res:
            result = json.loads(res.read().decode('utf-8'))
            # لو نجح التغيير معناه الاسم متاح
        
        # نرجع الاسم القديم
        old_name = result.get('global_name', '')
        return True
        
    except urllib.error.HTTPError as e:
        if e.code == 400:
            body = e.read().decode('utf-8')
            if '"global_name"' in body or 'already' in body.lower() or 'taken' in body.lower():
                return False  # الاسم مستخدم
            return True  # خطأ ثاني لكن ممكن الاسم متاح
        return False
    except:
        return False

def check_dc_username_final(username, token):
    """الطريقة النهائية لفحص ديسكورد يوزر"""
    try:
        # طريقة 1: نحاول نغير global_name
        url = "https://discord.com/api/v10/users/@me"
        data = json.dumps({"global_name": username}).encode('utf-8')
        req = urllib.request.Request(url, data=data,
            headers={'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
            method='PATCH')
        
        with urllib.request.urlopen(req, timeout=5) as res:
            # نجح التغيير! الاسم متاح
            result = json.loads(res.read().decode('utf-8'))
            old_name = result.get('global_name', username)
            
            # نرجع الاسم القديم عشان ما يضرب الحساب
            restore_data = json.dumps({"global_name": ""}).encode('utf-8')
            restore_req = urllib.request.Request(url, data=restore_data,
                headers={'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
                method='PATCH')
            urllib.request.urlopen(restore_req, timeout=5)
            
            return True
            
    except urllib.error.HTTPError as e:
        if e.code == 400:
            try:
                body = json.loads(e.read().decode('utf-8'))
                err_msg = body.get('message', '')
                err_code = body.get('code', 0)
                
                # كود الخطأ 50006 = username already taken
                if err_code == 50006 or 'taken' in err_msg.lower() or 'already' in err_msg.lower():
                    return False  # الاسم مستخدم
                if err_code == 50035 or 'invalid' in err_msg.lower():
                    return False  # اسم غير صالح
                return False
            except:
                return False
        return False
    except:
        return False

def dc_worker():
    global dc_found, dc_checked, dc_running, DC_TOKEN
    
    while dc_running:
        username, ptype = generate_dc_username()
        
        # منع التكرار
        with checked_set_lock:
            if username in checked_set:
                continue
            checked_set.add(username)
        
        with lock:
            dc_checked += 1
            current_checked = dc_checked
        
        print(f"{WHITE}[{current_checked}] {BLUE}فحص دس: {CYAN}{username} ({ptype}){RESET}    ", end='\r')
        
        if check_dc_username_final(username, DC_TOKEN):
            with lock:
                dc_found += 1
                current_found = dc_found
            
            colors = {"ثلاثي": GREEN, "نقطة_بداية": CYAN, "أندر_بداية": YELLOW, 
                     "نقطة_نهاية": PINK, "أندر_نهاية": RED, "أندر_بداية_مختلط": CYAN,
                     "نقطة_نهاية_حروف": GREEN, "أندر_نهاية_مختلط": YELLOW,
                     "أندر_بداية_مميز": RED, "نقطة_وسط": PINK}
            color = colors.get(ptype, GREEN)
            
            print(f"\n{color}✅ [{ptype}] {WHITE}{username} {color}متاح!{RESET}")
            
            # حفظ
            with open('discord_hits.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{ptype}] {username}\n")
            
            # إرسال ويبهوك
            send_dc_webhook(username)

def discord_users_menu():
    global DC_WEBHO

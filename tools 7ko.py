import os
import sys
import socket
import urllib.request
import urllib.parse
import json

def clear_screen():
    os.system('clear')

WHITE = '\033[1;37m'
GREEN = '\033[1;32m'
BLUE = '\033[1;34m'
PINK = '\033[1;35m'
YELLOW = '\033[1;33m'
RESET = '\033[0m'

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

def main_menu():
    clear_screen()
    show_logo()
    
    print(f"{GREEN}~ [1] IP Address & Ports Tool{RESET}")
    print("\n")
    print(f"       {BLUE}~ [2] Translation Tool (EN -> AR){RESET}")
    print("\n")
    print(f"                                    {PINK}~ [3] Discord Users Tool{RESET}")
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
            
    elif choice == '0':
        print(f"\n{YELLOW}في أمان الله يا حكو! تم الخروج.{RESET}\n")
        sys.exit()
    else:
        print(f"\n{PINK}❌ اختيار غير صحيح، الرجاء اختيار 1 أو 2 أو 3{RESET}")
        
    input(f"\n{WHITE}اضغط Enter للعودة إلى القائمة الرئيسية...{RESET}")
    main_menu()

if __name__ == "__main__":
    main_menu()

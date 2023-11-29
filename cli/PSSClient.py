import requests
import json

class PSSClient():
    def __init__(self, host: str, port: int = None):
        self._host = host
        self._port = port
        self._address = host if port == None else f"{host}:{str(port)}"
    
    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port
    
    @property
    def address(self):
        return self._address
    
    def download(self, endpoint, args):
        result = requests.get(f"{self.address}/{endpoint}/" + "/".join(f"{arg}" for arg in args))
        if result.ok:
            return result.content, True
        else:
            return {"error": "Request failed"}, False


    def get(self, endpoint, args):
        result = requests.get(f"{self.address}/{endpoint}/" + "/".join(f"{arg}" for arg in args))
        if result.ok:
            return json.loads(result.content), True
        else:
            return {"error": "Request failed"}, False
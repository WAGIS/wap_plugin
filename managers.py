import time
import requests
import os

# self.api_manag = WaporAPIManager()
# self.canv_manag = CanvasManager()
# self.file_manag = FileManager()

class WaporAPIManager:
    def __init__(self, plugin_cwd, APIToken='1ba703cd638a4a473a62472d744fc3d3079e888494f9ca1ed492418a79e3f090eb1756e8284ef483'):
        self.plugin_cwd = plugin_cwd
        self.APIToken = APIToken
        self.connected =  False
        self.sign_in_url = r'https://io.apps.fao.org/gismgr/api/v1/iam/sign-in/'
        self.query_url = r'https://io.apps.fao.org/gismgr/api/v1/query/'

    def connectWapor(self):
        request_headers = {'X-GISMGR-API-KEY': self.APIToken}

        resp = requests.post(
                        self.sign_in_url,
                        headers=request_headers)

        print('Connecting to WaPOR Database . . .')

        resp_json = resp.json()
        if resp_json['message']=='OK':
            self.AccessToken=resp_json['response']['accessToken']
            print('SUCCESS: Access granted')
            print('Access expires in 3600s')

            self.lastConnection_time = time.time()
            return True

        else:
            print('Fail to coonect to Wapor Database . . .')
            return False

    def isConnected(self):
        if not self.connected:
            return False
        elif time.time() - self.lastConnection_time > 3600:
            self.connected = False

        return self.connected

    def disconnectWapor(self):
        pass

    def login(self):
        pass

    def query(self):
        pass

class FileManager:
    def __init__(self, plugin_dir):
        self.plugin_dir = plugin_dir

    def check_path(self, path):
        return os.path.exists(path)

    def create_path(self, path):
        path = os.path.join(self.plugin_dir,path)
        if not self.check_path(path):
            os.mkdir(path)

    def readLayer():
        pass

class CanvasManager:
    def __init__(self, ):
        pass

    def disp_rast(self, raster):
        pass
    
    def rm_rast(self, raster):
        pass


import time
import requests
import os

# self.api_manag = WaporAPIManager()
# self.canv_manag = CanvasManager()
# self.file_manag = FileManager()

class WaporAPIManager:
    def __init__(self, APIToken='1ba703cd638a4a473a62472d744fc3d3079e888494f9ca1ed492418a79e3f090eb1756e8284ef483'):
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
            print('Fail to connect to Wapor Database . . .')
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
        dir = os.path.join(self.plugin_dir,path)
        return os.path.exists(dir)

    def create_path(self, path):
        dir = os.path.join(self.plugin_dir,path)
        if not os.path.exists(dir):
            os.mkdir(dir)
        else:
            print('The path [{}] is already in the workspace'.format(path))

    def list_rasters(self, rasters_path):
        rasters_dir = os.path.join(self.plugin_dir,rasters_path)
        tif_files_dir = []
        tif_names = []
        if os.path.exists(rasters_dir):
            for dirpath, _, fnames in os.walk(rasters_dir):
                for f in fnames:
                    if f.endswith(".tif"):
                        tif_names.append(f)
                        tif_files_dir.append(os.path.join(dirpath, f))
            
            print('Found {} layers in the workspace [{}]'.format(len(tif_names),rasters_path))
        else:
            self.create_path(rasters_path)
        return tif_files_dir, tif_names

    def read_layer():
        pass

class CanvasManager:
    def __init__(self, interface, plugin_dir, rasters_path):
        self.iface = interface
        self.plugin_dir = plugin_dir
        self.rasters_dir = os.path.join(self.plugin_dir,rasters_path)

    def add_rast(self, raster_name):
        raster_dir = os.path.join(self.rasters_dir,raster_name)
        return bool(self.iface.addRasterLayer(raster_dir,raster_name))
    
    def rm_rast(self, raster):
        pass


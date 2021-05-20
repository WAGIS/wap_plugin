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
        self.catalog_url = r'https://io.apps.fao.org/gismgr/api/v1/catalog/'

        self.payload = {'overview':False,'paged':False}
        self.time_out = 5

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
    
    def query_listing(self, url):
        try:
            resp = requests.get(url,self.payload,timeout=self.time_out).json()

            listing = dict()
            for elem in resp['response']:
                listing[elem['caption']] = elem['code']
            return listing
        except (requests.ConnectionError, requests.Timeout) as exception:
            return None
        except (KeyError) as exception:
            return {'---':None}

    def query_info(self, url):
        try:
            resp = requests.get(url,timeout=self.time_out).json()
            return resp['response']
        except (requests.ConnectionError, requests.Timeout) as exception:
            return None

    def pull_workspaces(self):
        workspaces_url = self.catalog_url+'workspaces'
        workspaces_dict = self.query_listing(workspaces_url)
        if workspaces_dict is None:
            raise Exception("Query [pull_workspaces] error, no internet conection or timeout")
        else:
            return workspaces_dict
        
    def get_info_workspace(self, workspace):
        workspace_url = self.catalog_url+'workspaces/{}'.format(workspace)
        workspace_resp = self.query_info(workspace_url)
        if workspace_resp is None:
            raise Exception("Query [info_workspaces] error, no internet conection or timeout")
        else:
            return workspace_resp['caption'], workspace_resp['description']

    def pull_cubes(self, workspace):
        cubes_url = self.catalog_url+'workspaces/{}/cubes'.format(workspace)
        cubes_dict = self.query_listing(cubes_url)
        if cubes_dict is None:
            raise Exception("Query [pull_cubes] error, no internet conection or timeout")
        else:
            return cubes_dict
    
    def get_info_cube(self, workspace, cube):
        cube_url = self.catalog_url+'workspaces/{}/cubes/{}'.format(workspace,cube)
        cube_resp = self.query_info(cube_url)
        if cube_resp is None:
            raise Exception("Query [info_cube] error, no internet conection or timeout")
        else:
            return cube_resp['caption'], cube_resp['description']

    def pull_cube_dims(self, workspace, cube):
        cube_dims_url = self.catalog_url+'workspaces/{}/cubes/{}/dimensions'.format(workspace,cube)
        cube_dims_dict = self.query_listing(cube_dims_url)
        if cube_dims_dict is None:
            raise Exception("Query [pull_cube_dims] error, no internet conection or timeout")
        else:
            return cube_dims_dict

    def get_info_cube_dim(self, workspace, cube, dimension):
        cube_dim_url = self.catalog_url+'workspaces/{}/cubes/{}/dimensions/{}'.format(workspace,cube,dimension)
        cube_dim_resp = self.query_info(cube_dim_url)
        if cube_dim_resp is None:
            raise Exception("Query [info_cube_dim] error, no internet conection or timeout")
        else:
            return cube_dim_resp['caption'], cube_dim_resp['description']

    def pull_cube_dim_membs(self, workspace, cube, dimension):
        cube_dim_membs_url = self.catalog_url+'workspaces/{}/cubes/{}/dimensions/{}/members'.format(workspace,cube,dimension)
        cube_dim_membs_dict = self.query_listing(cube_dim_membs_url)
        if cube_dim_membs_dict is None:
            raise Exception("Query [pull_cube_dim_membs] error, no internet conection or timeout")
        else:
            return cube_dim_membs_dict

    def get_info_cube_dim_memb(self, workspace, cube, dimension, member):
        cube_dim_memb_url = self.catalog_url+'workspaces/{}/cubes/{}/dimensions/{}/members/{}'.format(workspace,cube,dimension,member)
        cube_dim_memb_resp = self.query_info(cube_dim_memb_url)
        if cube_dim_memb_resp is None:
            raise Exception("Query [info_cube_dim_memb] error, no internet conection or timeout")
        else:
            return cube_dim_memb_resp['caption'], cube_dim_memb_resp['description']

    def pull_cube_meas(self, workspace, cube):
        cube_meas_url = self.catalog_url+'workspaces/{}/cubes/{}/measures'.format(workspace,cube)
        cube_meas_dict = self.query_listing(cube_meas_url)
        if cube_meas_dict is None:
            raise Exception("Query [pull_cube_meas] error, no internet conection or timeout")
        else:
            return cube_meas_dict

    def get_info_cube_mea(self, workspace, cube, measure):
        cube_meas_url = self.catalog_url+'workspaces/{}/cubes/{}/measures/{}'.format(workspace,cube,measure)
        cube_meas_resp = self.query_info(cube_meas_url)
        if cube_meas_resp is None:
            raise Exception("Query [info_cube_meas] error, no internet conection or timeout")
        else:
            return cube_meas_resp['caption'], cube_meas_resp['description']


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
        if not self.iface.addRasterLayer(raster_dir,raster_name):
            print("Layer failed to load raster [{}]".format(raster_name))
            return False
        return True
    
    def rm_rast(self, raster):
        pass


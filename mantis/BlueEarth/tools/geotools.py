#coding:utf-8

"""
geotools.py
坐标转换
逆地址转换
基站lbs坐标转换
"""
import traceback
import requests

def geocoding_address( lon, lat):
    """
    逆地理编码服务
    refer:
    http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding

    http://api.map.baidu.com/geocoder/v2/?location=39.983424,116.322987&output=json&pois=1&ak=XDFk8RGryIrg3Hd7cr2101Yx
    http://api.map.baidu.com/geocoder/v2/?location=39.983424,116.322987&output=json&pois=0&ak=XDFk8RGryIrg3Hd7cr2101Yx

    :param lon:
    :param lat:
    :return:

    ak ='2lGY892LYZokThGF0Ie1FoXjIxaBFNi4'
    """
    ak ='XDFk8RGryIrg3Hd7cr2101Yx'
    # ak = self.cfgs.get('ak')
    url = "http://api.map.baidu.com/geocoder/v2/"
    params = {
        'location': "%s,%s" % (lat, lon),
        'output': 'json',
        'pois': 0,
        'ak': ak
    }
    address = ''
    try:
        resp = requests.get(url, params)
        data = resp.json().get('result', {})
        address = data.get('formatted_address', '')
    except:
        traceback.print_exc()
        # instance.getLogger().error("<%s> geocoding failed!" % (self.name,))
    return address


if __name__ == '__main__':
    print geocoding_address(121,31.1)

import os, requests, base64
import enc
from proto import QueryCurrRegionHttpRsp_pb2

if __name__ == '__main__':

    parseList = [
        "00/25539185",
        "01/26692920",
        "09/22299426"
    ]

    output = base64.b64decode(enc.decrypt(requests.get(os.environ.get('URL')).text))
    curr = QueryCurrRegionHttpRsp_pb2.QueryCurrRegionHttpRsp.FromString(output)

    for i in parseList:
        url = f"https://autopatchhk.yuanshen.com/client_design_data/{curr.region_info.resource_url_bak}/output_{curr.region_info.client_data_version}_{curr.region_info.client_version_suffix}/client/General/AssetBundles/blocks/{i}.blk"
    
        print(url)

        os.makedirs("./blk/", exist_ok=True)
        with open("./blk/" + i.split("/")[1] + ".blk", "wb") as file:
            file.write(requests.get(url).content)

import os, requests, base64
import enc
from proto import QueryCurrRegionHttpRsp_pb2

if __name__ == '__main__':

    parseList = [
        "00/24230448",
        "00/25539185",
        "01/26692920",
        "02/27251172",
        "03/25181351",
        "04/25776943",
        "05/20618174",
        "06/25555476",
        "07/30460104",
        "08/32244380",
        "09/22299426",
        "10/23331191",
        "11/21030516",
        "12/32056053",
        "13/34382464",
        "14/27270675",
        "15/21419401"
    ]

    output = base64.b64decode(enc.decrypt(requests.get(os.environ.get('URL')).text))
    curr = QueryCurrRegionHttpRsp_pb2.QueryCurrRegionHttpRsp.FromString(output)
    target = curr.region_info.next_res_version_config
    target = target if str(target) != '' else curr.region_info.res_version_config

    for i in parseList:
        url = f"{curr.region_info.data_url}/output_{curr.region_info.client_data_version}_{curr.region_info.client_version_suffix}/client/General/AssetBundles/blocks/{i}.blk"
    
        print(url)

        os.makedirs("./blk/", exist_ok=True)
        with open("./blk/" + i.split("/")[1] + ".blk", "wb") as file:
            file.write(requests.get(url).content)
    
    url = f"{curr.region_info.resource_url}/output_{target.version}_{target.version_suffix}/client/StandaloneWindows64/AssetBundles/blocks/00/31049740.blk"
    
    print(url)  

    os.makedirs("./blk/", exist_ok=True)
    with open("./blk/" + i.split("/")[1] + ".blk", "wb") as file:
        file.write(requests.get(url).content)
    

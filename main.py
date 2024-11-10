import os, requests, base64
import enc
from proto import QueryCurrRegionHttpRsp_pb2
from threading import Thread, Lock
from dotenv import load_dotenv
import json

load_dotenv()

# Function to download a part of the file
def download_chunk(url, start_byte, end_byte, chunk_num, output_file, lock):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)
    with lock:
        with open(output_file, 'r+b') as f:
            f.seek(start_byte)
            f.write(response.content)
    print(f"Chunk {chunk_num} downloaded")

# Function to get the file size
def get_file_size(url):
    response = requests.head(url)
    return int(response.headers['Content-Length'])

# Function to download file with multiple threads
def multi_thread_download(url, output_file, num_threads=4):
    file_size = get_file_size(url)
    chunk_size = file_size // num_threads

    # Initialize the output file
    with open(output_file, 'wb') as f:
        f.truncate(file_size)

    threads = []
    lock = Lock()

    for i in range(num_threads):
        start_byte = i * chunk_size
        # Ensure the last chunk goes to the end of the file
        end_byte = start_byte + chunk_size - 1 if i < num_threads - 1 else file_size - 1
        thread = Thread(target=download_chunk, args=(url, start_byte, end_byte, i + 1, output_file, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Download completed")


def zzz_link_create(url, file_type, output_name, base_revision=False):
    
    file_list = requests.get(url)
    file_list = json.loads(file_list.text)

    if base_revision:
        url = url.replace("res_version", "base_revision")
        base_file = requests.get(url)
        base_file = base_file.text
        base_url = f"https://autopatchcn.juequling.com/game_res/beta_live/output_{base_file}/client/"
        
        with open(output_name, 'w') as f:
            for i in file_list["files"]:
                f.write(base_url + "StandaloneWindows64/cn/" + i["remoteName"] + "\n")
                f.write("  out=" + file_type + "/" + i["remoteName"] + "\n")

    else:
        with open(output_name, 'w') as f:
            for i in file_list["files"]:
                f.write(result[file_type]["base_url"] + "StandaloneWindows64/cn/" + i["remoteName"] + "\n")
                f.write("  out=" + file_type + "/" + i["remoteName"] + "\n")


if __name__ == '__main__':

    """
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

    output = base64.b64decode(enc.decrypt(requests.get("https://cnbeta02dispatch.yuanshen.com/query_cur_region?version=CNCBAndroid5.0.50&lang=1&platform=2&binary=1&time=91&channel_id=1&sub_channel_id=1&account_type=1&dispatchSeed=c12ddc85b0940cf3&key_id=4&aid=114514").text))
    curr = QueryCurrRegionHttpRsp_pb2.QueryCurrRegionHttpRsp.FromString(output)
"""

    result = requests.get("https://beta-beta01-cn.juequling.com/query_gateway?version=CNBetaWin1.4.1&rsa_ver=3&language=1&platform=3&seed=3e1cd96bf8f15f60&channel_id=1&sub_channel_id=0")
    result = enc.decrypt(result.text)
    result = base64.b64decode(result)
    result = json.loads(result)
    result = result["cdn_conf_ext"]

    print(result)

    design_url = result["design_data"]["base_url"] + "StandaloneWindows64/cn/data_version"
    res_url = result["game_res"]["base_url"] + "StandaloneWindows64/cn/res_version"
    silence_url = result["silence_data"]["base_url"] + "StandaloneWindows64/cn/silence_version"

    zzz_link_create(design_url, "design_data", "data.txt")
    zzz_link_create(res_url, "game_res", "res.txt", base_revision=True)
    zzz_link_create(silence_url, "silence_data", "silence.txt")


    # print(curr)

    #for i in parseList:
        #url = f"{curr.region_info.data_url}/output_{curr.region_info.client_data_version}_{curr.region_info.client_version_suffix}/client/General/AssetBundles/blocks/{i}.blk"


        #url = f"https://autopatchhkbeta.yuanshen.com/client_design_data/4.8_live/output_23861316_d5bfeb0907/client/General/AssetBundles/blocks/{i}.blk"

        #print(url)

        #os.makedirs("./blk/", exist_ok=True)
        # multi_thread_download(url, "./blk/" + i.split("/")[1] + ".blk", 16)
        #with open("./blk/" + i.split("/")[1] + ".blk", "wb") as file:
        #    file.write(requests.get(url).content)


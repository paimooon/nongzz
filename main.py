import os, requests, base64
import enc
from proto import QueryCurrRegionHttpRsp_pb2
from threading import Thread, Lock

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

    for i in parseList:
        url = f"{curr.region_info.data_url}/output_{curr.region_info.client_data_version}_{curr.region_info.client_version_suffix}/client/General/AssetBundles/blocks/{i}.blk"
    
        print(url)

        os.makedirs("./blk/", exist_ok=True)
        multi_thread_download(url, "./blk/" + i.split("/")[1] + ".blk", 16)

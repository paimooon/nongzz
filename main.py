import os
import enc
import requests

if __name__ == '__main__':
    req = requests.get(os.environ.get('URL'))
    
    output = enc.decrypt(req.text)

    print(output)
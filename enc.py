#!/usr/bin/env python3
# script from https://github.com/lilmayofuksu/sus-scripts/blob/main/enc_dispatch_decryptor.py

import sys, os
import base64

import json
import traceback
from xml.etree import ElementTree as etree

import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def conv_num(num):
    num = base64.b64decode(num)
    num = ''.join(['{:02x}'.format(x) for x in num])
    num = int(num, 16)
    return num

def get_params_from_xml(xml, params):
    return tuple([conv_num(xml.find(p).text) for p in params])

def get_key_from_xml(s, params):
    xml = etree.fromstring(s)
    params = get_params_from_xml(xml, params)
    return RSA.construct( params )

def get_pub_key_from_xml(s):
    return get_key_from_xml(s, ['Modulus', 'Exponent'])

def get_priv_key_from_xml(s):
    return get_key_from_xml(s, ['Modulus', 'Exponent', 'D', 'P', 'Q'])

def verify(message, sign, key):
    signer = pkcs1_15.new(key)
    digest = SHA256.new(message)
    signer.verify(digest, sign) # Throws an exception in the case of invalid signature

def do_sign(message, key):
    signer = pkcs1_15.new(key)
    digest = SHA256.new(message)
    return signer.sign(digest)

def decrypt(req):

    server_response = json.loads(req)

    content = None
    sign = None

    keys = {
        "5": {
            "publicRSAKey": "<RSAKeyValue><Modulus>15RBm/vARY0axYksImhsTicpv09OYfS4+wCvmE7psOvZhW2URZ2Rlf5DsEtuRG/7v5W/2obqqVkf+1dorPcR2iqrYZ4VVPf7KU3Cgqh0kzLGxWOpGxzwJULEyFVaiMDWbk7gr8rik/jYyhLiLc52zz3E3whTUPleKhOhXnxx1iOKY+TPVI8jJfDNiQoh0UvgjnkigJ/saPzjogeig/4McBc4l5cDkvttkKQKq7oXe9OCBClgKlYjcc1CNalwMlTz7NvLEko+ZLTgpA+kElZumyBXT67mmW7t7IDXorscAI7auwusKWmq797alFkQ/6sUqs8KKGnqQ2fwHfa/RYDhEw==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>",
            "privateRSAKey": "<RSAKeyValue><Modulus>sJbFp3WcsiojjdQtVnTuvtawL2m4XxK93F6lCnFwcZqUP39txFGGlrogHMqreyawIUN7E5shtwGzigzjW8Ly5CryBJpXP3ehNTqJS7emb+9LlC19Oxa1eQuUQnatgcsd16DPH7kJ5JzN3vXnhvUyk4Qficdmm0uk7FRaNYFi7EJs4xyqFTrp3rDZ0dzBHumlIeK1om7FNt6Nyivgp+UybO7kl0NLFEeSlV4S+7ofitWQsO5xYqKAzSzz+KIRQcxJidGBlZ1JN/g5DPDpx/ztvOWYUlM7TYk6xN3focZpU0kBzAw/rn94yW9z8jpXfzk+MvWzVL/HAcPy4ySwkay0Nw==</Modulus><Exponent>AQAB</Exponent><P>19wQUISXtpnmCrEZfbyZ6IwOy8ZCVaVUtbTjVa8UyfNglzzJG3yzcXU3X35v5/HNCHaXbG2qcbQLThnHBA+obW3RDo+Q49V84Zh1fUNH0ONHHuC09kB//gHqzn/4nLf1aJ2O0NrMyrZNsZ0ZKUKQuVCqWjBOmTNUitcc8RpXZ8s=</P><Q>0W09POM/It7RoVGI+cfbbgSRmzFo9kzSp5lP7iZ81bnvUMabu2nv3OeGc3Pmdh1ZJFRw6iDM6VVbG0uz8g+f8+JT32XdqM7MJAmgfcYfTVBMiVnh330WNkeRrGWqQzB2f2Wr+0vJjU8CAAcOWDh0oNguJ1l1TSyKxqdL8FsA38U=</Q><DP>udt1AJ7psgOYmqQZ+rUlH6FYLAQsoWmVIk75XpE9KRUwmYdw8QXRy2LNpp9K4z7C9wKFJorWMsh+42Q2gzyoHHBtjEf4zPLIb8XBg3UmpKjMV73Kkiy/B4nHDr4I5YdO+iCPEy0RH4kQJFnLjEcQLT9TLgxh4G7d4B2PgdjYYTk=</DP><DQ>rdgiV2LETCvulBzcuYufqOn9/He9i4cl7p4jbathQQFBmSnkqGQ+Cn/eagQxsKaYEsJNoOxtbNu/7x6eVzeFLawYt38Vy0UuzFN5eC54WXNotTN5fk2VnKU4VYVnGrMmCobZhpbYzoZhQKiazby/g60wUtW9u7xXzqOdM/428Yk=</DQ><InverseQ>cGxDsdUW6B/B/nz9QgIhfnKrauCa8/SEVjzoHA6bdlLJNaw8Hlq2cW00ZcCGlXOXLCBBNl9Nn7rf00169TKFx2urNnEK52WKuOOPPDbDuEwAtuoarP8fx21TnF9d4E9ukmJ4ABx3oe8Y1ia/yoCCML3L4L6FbOpbu2vGi1L6zmo=</InverseQ><D>PMpalrBtVgQdoziUtvugKMA9fMT3PHt2MsO+Kx8sJ1+gg0952Sh7na3LWj4G1GlYHstdNj2kWJzUUsTnC/LLrPJ/yEfdmzKyo2FYXGGHgWcubH9QaiQCKv5qdormZhUnW9C3HOOVXUcBtCyRHKuSUqgcN1EWqIVc7CKJv3ugM1aEP5HF/IbDAmfKdllJd0tstKLP9AdA2v/5R+QpEFrG3QJ9TuY4tnGjLp80DEd0FwEk8cLKH5oO8RuLHudKdxJTwm7/jxgnwOuCVtmxcJigDlTPw0wO5oQyCg1YIVBWgRxGQRShofsGVZ3dRQVE+cNnUHgGaStWhETxrnzc6pLBqQ==</D></RSAKeyValue>",
        },
        "sign": {
            "publicRSAKey": "<RSAKeyValue><Modulus>xbbx2m1feHyrQ7jP+8mtDF/pyYLrJWKWAdEv3wZrOtjOZzeLGPzsmkcgncgoRhX4dT+1itSMR9j9m0/OwsH2UoF6U32LxCOQWQD1AMgIZjAkJeJvFTrtn8fMQ1701CkbaLTVIjRMlTw8kNXvNA/A9UatoiDmi4TFG6mrxTKZpIcTInvPEpkK2A7Qsp1E4skFK8jmysy7uRhMaYHtPTsBvxP0zn3lhKB3W+HTqpneewXWHjCDfL7Nbby91jbz5EKPZXWLuhXIvR1Cu4tiruorwXJxmXaP1HQZonytECNU/UOzP6GNLdq0eFDE4b04Wjp396551G99YiFP2nqHVJ5OMQ==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>",
            "privateRSAKey": "<RSAKeyValue><Modulus>xbbx2m1feHyrQ7jP+8mtDF/pyYLrJWKWAdEv3wZrOtjOZzeLGPzsmkcgncgoRhX4dT+1itSMR9j9m0/OwsH2UoF6U32LxCOQWQD1AMgIZjAkJeJvFTrtn8fMQ1701CkbaLTVIjRMlTw8kNXvNA/A9UatoiDmi4TFG6mrxTKZpIcTInvPEpkK2A7Qsp1E4skFK8jmysy7uRhMaYHtPTsBvxP0zn3lhKB3W+HTqpneewXWHjCDfL7Nbby91jbz5EKPZXWLuhXIvR1Cu4tiruorwXJxmXaP1HQZonytECNU/UOzP6GNLdq0eFDE4b04Wjp396551G99YiFP2nqHVJ5OMQ==</Modulus><Exponent>AQAB</Exponent><P>8tHjikSSZN18ggXxm3MGJV8Nnb1tP3onQJZcZXOnzHptK7knmOWzuw/wMRyMZnq8ewsY6+Rw3HNydHeX/kc7PpMi69W5SbfpvWMeW2rXFlK2MZ4pmzWKGElK7aUgD5OsrwUJGcoBEnS6CFcY1kUi2B4zbfRKCOnZEvghJcnvbhc=</P><Q>0HJLZHA2lRi+QJJkdIWdAz+OrWOV3HD7SniMAalYuKURoD/zFZSdmucKs8UX+32WWlt1NH90Ijye0gwDLZ0fghQfJgpRqHIdLMIBQ0qlLSzjfeSfmHL20a+fuPK44nh2T0WjU8hkzup/OaR0IFtfc0XZManM69tgYkccLeyxWvc=</Q><DP>0ckOik32INjOklNqS0BURgNaczbOZTI3KXD+wNPsXBhFq6nbERkbb/k0LmoYzw0pPDD5Rgxmib/gWcldct29zLE4UYKkA5G2it5QwvCKhYnOSQ35qlPWTGc+KhUonuyaG9gA5dwFkxlwBHajSbQPh6KIEm4lbJAE8IOZt9lAV98=</DP><DQ>qlyvh7A6vBLT87xyA9XsJOp+NvIMWnWwvAXYD8eTrp2i0UFS8FFdmmu4kILGfhH/n2veWADPLugyueN9eXtQdCTz7EhEwxI5DAqns5K/ezOT3qHLWnKjjW8ncKZYOyhPMazttx0yXvbC8p6ZFpT3ZyQwRmnMBPxwQwJxYotvzLM=</DQ><InverseQ>MibG8IyHSo7CJz82+7UHm98jNOlg6s73CEjp0W/+FL45Ka7MF/lpxtR3eSmxltvwvjQoti3V4Qboqtc2IPCt+EtapTM7Wo41wlLCWCNx4u25pZPH/c8g1yQ+OvH+xOYG+SeO98Phw/8d3IRfR83aqisQHv5upo2Rozzo0Kh3OsE=</InverseQ><D>xHmGYY8qvmr1LnkrhYTmiFOP2YZV8nLDqs6cCb8xM+tbQUr62TwOS0m/acwL6YnPu4Qx/eI1/PfvHTXzu6pQA7FTRECQcbr9qNTAo6QkZJgWc+dOiARlOtCrdY+ZMHQhHq4E1tat++c+MJfH+y5ki9lOlrynHaI01caIQZCFCe7IbZprpA4tmJzH3uk/9iblwwy/K7yHJ36+RDAoD0LPsS3ixBqyCXaVMtYiGGWK8766ScH/RCS9w9Hu45KW7wEGfBBfWIRIsyYTpnc06luD4FtslGh2Hd6uUI4iC8uwAvqDmKE2ZZ90X4zzsZfm2I3jDlpapILaT0JABOCOuMPEWQ==</D></RSAKeyValue>"
        }
    }

    public_key_xml = keys["5"]['publicRSAKey']
    private_key_xml = keys["5"]['privateRSAKey']
    
    pub_rsa_key = get_pub_key_from_xml(public_key_xml)
    priv_rsa_key = get_priv_key_from_xml(private_key_xml)

    try:
        content = base64.b64decode(server_response['content'])
        sign = base64.b64decode(server_response['sign'])

    except Exception:
        print(f'\nAn error occured while parsing the input data: \n\n{traceback.format_exc()}')

    if content:
        dec = PKCS1_v1_5.new(priv_rsa_key)

        chunk_size = 256

        out = b''

        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            out += dec.decrypt(chunk, None)

        return base64.b64encode(out).decode()

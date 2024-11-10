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

def get_priv_key_from_xml(s):
    return get_key_from_xml(s, ['Modulus', 'Exponent']) # , 'D', 'P', 'Q'

def decrypt(req):
    server_response = json.loads(req)

    content = None

    keys = {
        "5": {
            "privateRSAKey": "<RSAKeyValue><Modulus>sJbFp3WcsiojjdQtVnTuvtawL2m4XxK93F6lCnFwcZqUP39txFGGlrogHMqreyawIUN7E5shtwGzigzjW8Ly5CryBJpXP3ehNTqJS7emb+9LlC19Oxa1eQuUQnatgcsd16DPH7kJ5JzN3vXnhvUyk4Qficdmm0uk7FRaNYFi7EJs4xyqFTrp3rDZ0dzBHumlIeK1om7FNt6Nyivgp+UybO7kl0NLFEeSlV4S+7ofitWQsO5xYqKAzSzz+KIRQcxJidGBlZ1JN/g5DPDpx/ztvOWYUlM7TYk6xN3focZpU0kBzAw/rn94yW9z8jpXfzk+MvWzVL/HAcPy4ySwkay0Nw==</Modulus><Exponent>AQAB</Exponent><P>19wQUISXtpnmCrEZfbyZ6IwOy8ZCVaVUtbTjVa8UyfNglzzJG3yzcXU3X35v5/HNCHaXbG2qcbQLThnHBA+obW3RDo+Q49V84Zh1fUNH0ONHHuC09kB//gHqzn/4nLf1aJ2O0NrMyrZNsZ0ZKUKQuVCqWjBOmTNUitcc8RpXZ8s=</P><Q>0W09POM/It7RoVGI+cfbbgSRmzFo9kzSp5lP7iZ81bnvUMabu2nv3OeGc3Pmdh1ZJFRw6iDM6VVbG0uz8g+f8+JT32XdqM7MJAmgfcYfTVBMiVnh330WNkeRrGWqQzB2f2Wr+0vJjU8CAAcOWDh0oNguJ1l1TSyKxqdL8FsA38U=</Q><DP>udt1AJ7psgOYmqQZ+rUlH6FYLAQsoWmVIk75XpE9KRUwmYdw8QXRy2LNpp9K4z7C9wKFJorWMsh+42Q2gzyoHHBtjEf4zPLIb8XBg3UmpKjMV73Kkiy/B4nHDr4I5YdO+iCPEy0RH4kQJFnLjEcQLT9TLgxh4G7d4B2PgdjYYTk=</DP><DQ>rdgiV2LETCvulBzcuYufqOn9/He9i4cl7p4jbathQQFBmSnkqGQ+Cn/eagQxsKaYEsJNoOxtbNu/7x6eVzeFLawYt38Vy0UuzFN5eC54WXNotTN5fk2VnKU4VYVnGrMmCobZhpbYzoZhQKiazby/g60wUtW9u7xXzqOdM/428Yk=</DQ><InverseQ>cGxDsdUW6B/B/nz9QgIhfnKrauCa8/SEVjzoHA6bdlLJNaw8Hlq2cW00ZcCGlXOXLCBBNl9Nn7rf00169TKFx2urNnEK52WKuOOPPDbDuEwAtuoarP8fx21TnF9d4E9ukmJ4ABx3oe8Y1ia/yoCCML3L4L6FbOpbu2vGi1L6zmo=</InverseQ><D>PMpalrBtVgQdoziUtvugKMA9fMT3PHt2MsO+Kx8sJ1+gg0952Sh7na3LWj4G1GlYHstdNj2kWJzUUsTnC/LLrPJ/yEfdmzKyo2FYXGGHgWcubH9QaiQCKv5qdormZhUnW9C3HOOVXUcBtCyRHKuSUqgcN1EWqIVc7CKJv3ugM1aEP5HF/IbDAmfKdllJd0tstKLP9AdA2v/5R+QpEFrG3QJ9TuY4tnGjLp80DEd0FwEk8cLKH5oO8RuLHudKdxJTwm7/jxgnwOuCVtmxcJigDlTPw0wO5oQyCg1YIVBWgRxGQRShofsGVZ3dRQVE+cNnUHgGaStWhETxrnzc6pLBqQ==</D></RSAKeyValue>",
        },
        "4": {
            "privateRSAKey": "<RSAKeyValue><Modulus>yaxqjPJP5+Innfv5IdfQqY/ftS++lnDRe3EczNkIjESWXhHSOljEw9b9C+/BtF+fO9QZL7Z742y06eIdvsMPQKdGflB26+9OZ8AF4SpXDn3aVWGr8+9qpB7BELRZI/Ph2FlFL4cobCzMHunncW8zTfMId48+fgHkAzCjRl5rC6XT0Yge6+eKpXmF+hr0vGYWiTzqPzTABl44WZo3rw0yurZTzkrmRE4kR2VzkjY/rBnQAbFKKFUKsUozjCXvSag4l461wDkhmmyivpNkK5cAxuDbsmC39iqagMt9438fajLVvYOvpVs9ci5tiLcbBtfB4Rf/QVAkqtTm86Z0O3e7Dw==</Modulus><Exponent>AQAB</Exponent><P>/auFx84D7UlrfuFQcp5t+n2sex7Hj6kbK3cp27tZ2o6fix7GbJoG6IdBxRyE8NWVr+u5BnbT7wseDMEOjSbyxjuCl/vXlRX01JUhEPTC7bpIpGSU4XMngcE7BT2EEYtKdFQnPK9WW3k7sT2EC/rVIKu9YERyjDZico1AvC+MxUk=</P><Q>y4ahJvcD+6Wq2nbOnFUByVh79tIi1llM5RY/pVviE6IfEgnSfUf1qnqCs5iQn9ifiCDJjMqb+egXXBc/tGP/E5qGe8yTOEZ2Y5pu8T0sfkfBBNbEEFZORnOAFti1uD4nkxNwqolrJyFJGMmP7Ff533Su2VK79zbtyGVJEoAddZc=</Q><DP>FTcIHDq9l1XBmL3tRXi8h+uExlM/q2MgM5VmucrEbAPrke4D+Ec1drMBLCQDdkTWnPzg34qGlQJgA/8NYX61ZSDK/j0AvaY1cKX8OvfNaaZftuf2j5ha4H4xmnGXnwQAORRkp62eUk4kUOFtLrdOpcnXL7rpvZI6z4vCszpi0ok=</DP><DQ>p3lZEl8g/+oK9UneKfYpSi1tlGTGFevVwozUQpWhKta1CnraogycsnOtKWvZVi9C1xljwF7YioPY9QaMfTvroY3+K9DjM+OHd96UfB4Chsc0pW60V10te/t+403f+oPqvLO6ehop+kEBjUwPCkQ6cQ3q8xmJYpvofoYZ4wdZNnE=</DQ><InverseQ>cBvFa7+2fpF/WbodRb3EaGOe22C1NHFlvdkgNzb4vKWTiBGix60Mmab72iyInEdZvfirDgJoou67tMy+yrKxlvuZooELGg4uIM2oSkKWnf0ezCyovy+d62JqNGmSgESx1vNhm6JkNM8XUaKPb2qnxjaV5Mcsrd5Nxhg7p5q7JGM=</InverseQ><D>spmttur01t+SxDec11rgIPoYXMZOm76H1jFDFyrxhf9Lxz0zF5b7kpA3gzWuLwYr53kbYQTTzIG96g7k1sa6IEDDjiPGXYWNwxXsXw73EA9mpwybkqkpoPTXd+qvssZN8SKFweSJaNt3Xb05yVx4bATaL7+80Sztd+HABxag6Cs7eRBB63tLJFHJ+h4xznpOnOd476Sq+S0q64sMeYDLmP+2UiFA6PVhmO9Km0BRmOmzpV/cfLjY3BRfu0s7RFUPr4Sf/uxL8Kmia8rMHqNJfdUyjPVmjLsKLnCnnHlVrspxMOhhk8PFEy7ZbXpCxnum0vGMWPH1cJypE0cCWMACUQ==</D></RSAKeyValue>"
        },
        "zzz": {
            "privateRSAKey": "<RSAKeyValue><Exponent>AQAB</Exponent><Modulus>rkQoCtGS5YSrzxm89Wq3GSR/uw5AJDwGqu+tkXViZwOF8H6xgL7KPi2OVATHCoaNFLTAD5nlLSjg0pHEAqHafvXtzj4Gh8tvF2A6/8yB5ceT3Oszo9UR5d7hsI55sxb37QUpQLHYoxKs79FohJ74Z5V2LgSY+0XvbGxMHxhxHTc=</Modulus></RSAKeyValue>"
        }
    }

    f = open('zzz.pem', 'rb')
    zzz_key = RSA.importKey(f.read())

    private_key_xml = keys['4']['privateRSAKey']
    priv_rsa_key = zzz_key  #get_priv_key_from_xml(private_key_xml)

    try:
        content = base64.b64decode(server_response['content'])

    except Exception:
        print(f'\nAn error occured while parsing the input data: \n\n{traceback.format_exc()}')

    if content:
        dec = PKCS1_v1_5.new(priv_rsa_key)

        chunk_size = 128

        out = b''

        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            out += dec.decrypt(chunk, None)

        return base64.b64encode(out).decode()

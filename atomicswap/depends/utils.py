#!/usr/bin/env python3

import os, sysconfig, time, pickle, base64, json

from atomicswap.depends.config import tannhauser
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def save_wallet(filename, btc_address, ltc_address):
    try:
        _get_path = sysconfig.get_paths()
        _curr_path = _get_path['purelib']
        _sw = open(f'{_curr_path}/atomicswap/wallets/{filename}', 'wb')
        pickle.dump(btc_address, _sw)
        pickle.dump(ltc_address, _sw)
        _sw.close()
        return True
    except Exception as ex:
        print(ex)
        return False

def load_wallet(filename):
    try:
        _lw = open(f'{filename}', 'rb')
        _btc_address = pickle.load(_lw)
        _ltc_address = pickle.load(_lw)
        _lw.close()

        res = {
            'btc_address': _btc_address,
            'ltc_address': _ltc_address
        }

        return res
    except Exception as ex:
        print(ex)
        return False

def save_user_swap(filename, sender_funding_address, server_claim_address, htlc_address, send_fund_txid, amount, refund_blockheight, secret_hash_hex):
    try:
        _get_path = sysconfig.get_paths()
        _curr_path = _get_path['purelib']
        _sw = open(f'{_curr_path}/atomicswap/user_swaps/{filename}', 'wb')
        pickle.dump(sender_funding_address, _sw)
        pickle.dump(server_claim_address, _sw)
        pickle.dump(htlc_address, _sw)
        pickle.dump(send_fund_txid, _sw)
        pickle.dump(amount, _sw)
        pickle.dump(refund_blockheight, _sw)
        pickle.dump(secret_hash_hex, _sw)
        _sw.close()

        return True
    except Exception as ex:
        print(ex)
        return False

def load_user_swap(filename):
    try:
        _get_path = sysconfig.get_paths()
        _curr_path = _get_path['purelib']
        _lswp = open(f'{_curr_path}/atomicswap/user_swaps/{filename}', 'rb')
        sender_funding_address = pickle.load(_lswp)
        server_claim_address = pickle.load(_lswp)
        htlc_address = pickle.load(_lswp)
        send_fund_txid = pickle.load(_lswp)
        amount = pickle.load(_lswp)
        refund_blockheight = pickle.load(_lswp)
        secret_hash_hex = pickle.load(_lswp)
        _lswp.close()

        res = {
            'sender_funding_address':sender_funding_address,
            'server_claim_address':server_claim_address,
            'htlc_address':htlc_address,
            'send_fund_txid':send_fund_txid,
            'amount':amount,
            'refund_blockheight':refund_blockheight,
            'secret_hash_hex':secret_hash_hex,
        }
    except Exception as ex:
        print(ex)
        res = False

    return res

def save_bond(filename, swap_token, sender_address, server_address, htlc_address, refund_blockheight, btc_amount, btc_send_fund, secret_hash_hex, redeem_script, conter_address, swap_amount, server_amount, finalized = False):
    try:
        _get_path = sysconfig.get_paths()
        _curr_path = _get_path['purelib']
        _sw = open(f'{_curr_path}/atomicswap/bonds/{filename}', 'wb')
        pickle.dump(filename, _sw)
        pickle.dump(swap_token, _sw)
        pickle.dump(sender_address, _sw)
        pickle.dump(server_address, _sw)
        pickle.dump(htlc_address, _sw)
        pickle.dump(refund_blockheight, _sw)
        pickle.dump(btc_amount, _sw)
        pickle.dump(btc_send_fund, _sw)
        pickle.dump(secret_hash_hex, _sw)
        pickle.dump(redeem_script, _sw)
        pickle.dump(conter_address, _sw)
        pickle.dump(swap_amount, _sw)
        pickle.dump(server_amount, _sw)
        pickle.dump(finalized, _sw)
        _sw.close()

        return True
    except Exception as ex:
        print(ex)
        return False

def load_bond(filename, path = False):
    try:
        _get_path = sysconfig.get_paths()
        _curr_path = _get_path['purelib']

        if path:
            _lswp = open(f'{filename}', 'rb')
        else:
            _lswp = open(f'{_curr_path}/atomicswap/bonds/{filename}', 'rb')

        _filename = pickle.load(_lswp)
        _swap_token = pickle.load(_lswp)
        _sender_address = pickle.load(_lswp)
        _server_address = pickle.load(_lswp)
        _htlc_address = pickle.load(_lswp)
        _refund_blockheight = pickle.load(_lswp)
        _amount = pickle.load(_lswp)
        _send_fund = pickle.load(_lswp)
        _secret_hash_hex = pickle.load(_lswp)
        _redeem_script = pickle.load(_lswp)
        _conter_address = pickle.load(_lswp)
        _swap_amount = pickle.load(_lswp)
        _server_amount = pickle.load(_lswp)
        _finalized = pickle.load(_lswp)
        _lswp.close()

        result = {
            'filename': _filename,
            'swap_token': _swap_token,
            'sender_address': _sender_address,
            'server_address': _server_address,
            'htlc_address': _htlc_address,
            'refund_blockheight': _refund_blockheight,
            'amount': _amount,
            'txid': _send_fund,
            'secret_hash_hex': _secret_hash_hex,
            'redeem_script': _redeem_script,
            'conter_address': _conter_address,
            'swap_amount': _swap_amount,
            'server_amount': _server_amount,
            'finalized': _finalized
        }
    except Exception as ex:
        print(ex)
        result = False

    return result

def save_user_data(data):
    try:
        _password = data['_user_password'].encode('utf-8')
        _data = json.dumps(data).encode('utf-8')

        _kdf = PBKDF2HMAC(algorithm = hashes.SHA256(), length = 32, salt = _password, iterations = 400000)
        _key = base64.urlsafe_b64encode(_kdf.derive(_password))
        _f = Fernet(_key)
        _encrypted = _f.encrypt(_data)

        # write encrypted
        _get_path = sysconfig.get_paths()
        _curr_path = _get_path['purelib']
        _filename = "saved_user_data"

        with open(f'{_curr_path}/atomicswap/depends/{_filename}', 'wb') as _file:
            _file.write(_encrypted)

        return True
    except Exception as ex:
        print(ex)
        return False

def load_user_data(passphrase):
    try:
        _password = passphrase.encode('utf-8')
        _get_path = sysconfig.get_paths()
        _curr_path = _get_path['purelib']
        _filename = "saved_user_data"

        with open(f'{_curr_path}/atomicswap/depends/{_filename}', 'rb') as _file:
            _encrypted = _file.read()

            if _encrypted:
                res = decrypt_user_file(_password, _encrypted)
                
                if res:
                    pass
                else:
                    res = 'wrong password!'
            else:
                res = False

        return res
    except Exception as ex:
        print(ex)
        return False

def decrypt_user_file(passphrase, encrypted_data):
    try:
        # decrypt file
        _kdf = PBKDF2HMAC(algorithm = hashes.SHA256(), length = 32, salt = passphrase, iterations = 400000)
        _key = base64.urlsafe_b64encode(_kdf.derive(passphrase))
        _f = Fernet(_key)
        _decrypted = _f.decrypt(encrypted_data)
        res = json.loads(_decrypted.decode('utf-8'))

        return res
    except Exception as ex:
        print(ex)
        return False

def check_user_file():
    try:
        _get_path = sysconfig.get_paths()
        _curr_path = _get_path['purelib']
        _filename = "saved_user_data"
        _path = f'{_curr_path}/atomicswap/depends/{_filename}'
        _file_exists = os.path.isfile(_path)

        return _file_exists
    except Exception as ex:
        print(ex)
        return False


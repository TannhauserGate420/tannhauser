#!/usr/bin/env python3

import sys, hashlib, binascii, time
from bitcoinrpc.authproxy import AuthServiceProxy , JSONRPCException

import litecoin
from litecoin import SelectParams
from litecoin.core import b2x, lx, b2lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160, CTxIn, CTxOut, CTransaction
from litecoin.core.script import CScript, OP_DUP, OP_IF, OP_ELSE, OP_ENDIF, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL, OP_FALSE, OP_DROP, OP_CHECKLOCKTIMEVERIFY, OP_SHA256, OP_TRUE
from litecoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from litecoin.wallet import CBitcoinAddress, CBitcoinSecret

from atomicswap.depends.config import tannhauser

class LTCScript():
    @classmethod
    def get_fee(cls, conn_data, blocks = tannhauser['fee_blocks'], fee_mode = tannhauser['fee_estimate_mode']):
        try:
            rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            fee = rpc_connection.estimatesmartfee(blocks, fee_mode)
            fee_per_byte = float(fee["feerate"] / 1000) * tannhauser['fee_factor']
            fee_per_byte = round(fee_per_byte,8)
            fee["fee_per_byte"] = fee_per_byte
        except Exception as ex:
            print(ex)
            fee["fee_per_byte"] = round(float(0.0012 / 1000), 8)

        return fee

    @classmethod
    def getnewaddress(cls, label, conn_data, addr_type = 'legacy'):
        try:
            rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            _new_address = rpc_connection.getnewaddress(label, addr_type)
            return _new_address
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def import_address(cls, address, conn_data):
        try:
            address = str(address)
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            import_address = _rpc_connection.importaddress(address, 'htlc_address', False)
        except Exception as ex:
            print(ex)

    @classmethod
    def get_addressinfo(cls, address, conn_data):
        try:
            address = str(address)
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            addr_info = _rpc_connection.validateaddress(address)
        except Exception as ex:
            print(ex)

        return addr_info

    @classmethod
    def list_lock(cls, conn_data):
        try:
            rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            _lilo = rpc_connection.listlockunspent()
            return _lilo
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def lock_utxo(cls, txid, vout, lock, conn_data):
        try:
            rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            _lock = rpc_connection.lockunspent(lock, [{'txid':txid, 'vout':vout}])
            return _lock
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def unspent(cls, address, conn_data, confirmations = 1):
        try:
            _address = str(address)
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            r = _rpc_connection.listunspent(confirmations, 9999999, [_address])

            r2 = []
            for unspent in r:
                unspent['outpoint'] = COutPoint(lx(unspent['txid']), unspent['vout'])
                del unspent['txid']
                del unspent['vout']

                try:
                    unspent['address'] = CBitcoinAddress(unspent['address'])
                except Exception as ex:
                    print(ex)

                unspent['scriptPubKey'] = CScript(binascii.unhexlify(unspent['scriptPubKey'].encode('ascii')))
                unspent['amount'] = int(unspent['amount'] * COIN)
                r2.append(unspent)

            # compute total balance
            _balance = 0
            for _txout in r2:
                _balance += _txout['amount']
        except Exception as ex:
            print(ex)

        return [r, r2, _balance]

    @classmethod
    def get_privkey(cls, address, conn_data):
        try:
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            wif = _rpc_connection.dumpprivkey(address)
        except Exception as ex:
            print(ex)

        return wif

    @classmethod
    def unlock_wallet(cls, conn_data, gap = 10):
        try:
            _passphrase = conn_data['ltc_walletpassphrase']
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            _unlock = _rpc_connection.walletpassphrase(_passphrase, gap)
        except Exception as ex:
            print(ex)

    @classmethod
    def blockcount(cls, conn_data):
        try:
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            blockheight = _rpc_connection.getblockcount()
        except Exception as ex:
            print(ex)

        return blockheight

    @classmethod
    def get_transaction(cls, txid, conn_data, index = 0):
        try:
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            tx_info = _rpc_connection.gettransaction(txid)
            fund_details = tx_info['details']
            output_address = fund_details[index]['address']
            fund_vout = fund_details[index]['vout']
        except Exception as ex:
            print(ex)

        return [output_address, fund_vout, tx_info['confirmations']]

    @classmethod
    def send_transaction(cls, tx_hex, conn_data):
        try:
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            broadcast = _rpc_connection.sendrawtransaction(tx_hex)
        except Exception as ex:
            print(ex)

        return broadcast

    @classmethod
    def sign_transaction(cls, tx, conn_data):
        _hex_tx = binascii.hexlify(tx.serialize()).decode('ascii')

        try:
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            sign = _rpc_connection.signrawtransactionwithwallet(_hex_tx)
            sign['tx'] = CTransaction.deserialize(binascii.unhexlify(sign['hex'].encode('ascii')))
            del sign['hex']
        except Exception as ex:
            print(ex)

        return sign

    @classmethod
    def decode_rawtransaction(cls, tx_hex, conn_data):
        try:
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            decode_tx_hex = _rpc_connection.decoderawtransaction(tx_hex)
        except Exception as ex:
            print(ex)

        return decode_tx_hex

    @classmethod
    def get_rawtransaction(cls, txid, conn_data, debug = False):
        try:
            _rpc_connection = AuthServiceProxy(f"http://{conn_data['ltc_rpc_user']}:{conn_data['ltc_rpc_password']}@{conn_data['ltc_rpc_url']}:{conn_data['ltc_rpc_port']}")
            tx_raw = _rpc_connection.getrawtransaction(txid, debug)
        except Exception as ex:
            print(ex)
            tx_raw = False

        return tx_raw

    def __init__(self, net, localhost):
        self.params = SelectParams(net)
        self.localhost = localhost

    def get_clean_address(self, address):
        return CBitcoinAddress(address)

    def gen_preimage(self, secret):
        self.preimage = secret.encode('UTF-8')
        self.hashed_preimage = hashlib.sha256(self.preimage).digest()
        self.hashed_preimage_hex = hashlib.sha256(self.preimage).hexdigest()

        return [self.preimage, self.hashed_preimage, self.hashed_preimage_hex]

    def get_redeem_script(self, blocks, hashed_preimage, sender_address, receiver_address, conn_data, validate = False):
        if validate:
            self.redeem_blockheight = blocks
        else:
            self.current_blockheight = LTCScript.blockcount(conn_data)
            self.redeem_blockheight = self.current_blockheight + blocks

        self.redeem_script = CScript([OP_IF,
                                        OP_SHA256, hashed_preimage, OP_EQUALVERIFY,
                                        OP_DUP, OP_HASH160, receiver_address,
                                    OP_ELSE,
                                        self.redeem_blockheight, OP_CHECKLOCKTIMEVERIFY, OP_DROP,
                                        OP_DUP, OP_HASH160, sender_address,
                                    OP_ENDIF,
                                    OP_EQUALVERIFY,
                                    OP_CHECKSIG]
        )

        self.script_pubkey = self.redeem_script.to_p2sh_scriptPubKey()
        self.p2sh_address = CBitcoinAddress.from_scriptPubKey(self.script_pubkey)

        return [self.redeem_blockheight, b2x(self.redeem_script), self.p2sh_address, self.redeem_script]

    def gen_fund_tx(self, network, sender_address, htlc_address, amount, conn_data, fee_per_byte = 1, wif = None):
        self.sender_address = sender_address
        self.htlc_address = htlc_address
        self.amount = amount
        self.fee_per_byte = fee_per_byte

        _unspent = LTCScript.unspent(self.sender_address, conn_data)
        _txouts = _unspent[1]

        # set fee
        _balance_total = 0
        for _txout in _txouts:
            _balance_total += max(_txout['amount'], 0)

        # compose vin
        _txins = [CTxIn(_txout['outpoint'], nSequence=0) for _txout in _txouts]

        # compose vout receiver
        _txout_receiver = CTxOut(self.amount, CBitcoinAddress(str(self.htlc_address)).to_scriptPubKey())

        # compose vout change
        _amount_change = _balance_total - self.amount - self.fee_per_byte
        _txout_change = CTxOut(_amount_change, CBitcoinAddress(str(self.sender_address)).to_scriptPubKey())

        # compose unsigned transaction
        _tx = CTransaction(_txins, [_txout_receiver, _txout_change])

        # sign transaction
        _sign_raw = LTCScript.sign_transaction(_tx, conn_data)

        # get signed tx
        _signed_tx = _sign_raw['tx']

        # signed tx hex
        _signed_tx_hex = b2x(_signed_tx.serialize())

        # decode tx
        _decode_tx_hex = LTCScript.decode_rawtransaction(_signed_tx_hex, conn_data)

        # TODO change this later to a smarter solution

        # compose final tx include correct fees
        _vsize = int(_decode_tx_hex['vsize'])
        _final_fee = int(_vsize * self.fee_per_byte + 10)
        _final_amount_change = _balance_total - self.amount - _final_fee
        _final_txout_change = CTxOut(_final_amount_change, CBitcoinAddress(str(self.sender_address)).to_scriptPubKey())
        _final_tx = CTransaction(_txins, [_txout_receiver, _final_txout_change])
        _final_tx_hex = b2x(_final_tx.serialize())
        _final_sign_raw = LTCScript.sign_transaction(_final_tx, conn_data)
        _final_signed_tx = _final_sign_raw['tx']
        _final_signed_tx_hex = b2x(_final_signed_tx.serialize())

        return [_final_signed_tx, _final_signed_tx_hex, _final_fee]

    def refund(self, txid, vout, amount, fee_per_byte, address, redeem_blockheight, redeem_script, privkey, conn_data):
        privkey = CBitcoinSecret(privkey)
        self.txid = lx(txid)
        self.txin = CMutableTxIn(COutPoint(self.txid, vout))
        self.txin.nSequence = 0
        self.txout = CMutableTxOut(amount - fee_per_byte, address.to_scriptPubKey())
        self.tx = CMutableTransaction([self.txin], [self.txout])
        self.tx.nLockTime = redeem_blockheight
        self.sighash = SignatureHash(redeem_script, self.tx, 0, SIGHASH_ALL)
        self.sig = privkey.sign(self.sighash) + bytes([SIGHASH_ALL])
        self.txin.scriptSig = CScript([self.sig, privkey.pub, OP_FALSE, redeem_script])
        self.refund_hex = b2x(self.tx.serialize())

        ## todo: insert smarter solution to get current fees

        # decode tx
        _decode_tx_hex = LTCScript.decode_rawtransaction(self.refund_hex, conn_data)

        _vsize = _decode_tx_hex['vsize']
        _final_fee = int(_vsize * fee_per_byte + 10)
        self.txout = CMutableTxOut(amount - _final_fee, address.to_scriptPubKey())
        self.tx = CMutableTransaction([self.txin], [self.txout])
        self.tx.nLockTime = redeem_blockheight
        self.sighash = SignatureHash(redeem_script, self.tx, 0, SIGHASH_ALL)
        self.sig = privkey.sign(self.sighash) + bytes([SIGHASH_ALL])
        self.txin.scriptSig = CScript([self.sig, privkey.pub, OP_FALSE, redeem_script])
        self.refund_hex = b2x(self.tx.serialize())

        return [self.refund_hex, self.tx, _final_fee]

    def claim(self, txid, vout, amount, fee_per_byte, address, redeem_blockheight, redeem_script, privkey, preimage, conn_data):
        privkey = CBitcoinSecret(privkey)
        self.txid = lx(txid)
        self.txin = CMutableTxIn(COutPoint(self.txid, vout))
        self.txout = CMutableTxOut(amount - fee_per_byte, address.to_scriptPubKey())
        self.tx = CMutableTransaction([self.txin], [self.txout])
        self.tx.nLockTime = redeem_blockheight
        self.sighash = SignatureHash(redeem_script, self.tx, 0, SIGHASH_ALL)
        self.sig = privkey.sign(self.sighash) + bytes([SIGHASH_ALL])
        self.txin.scriptSig = CScript([self.sig, privkey.pub, preimage, OP_TRUE, redeem_script])
        self.claim_hex = b2x(self.tx.serialize())

        ## todo: insert smarter solution to get current fees

        # decode tx
        _decode_tx_hex = LTCScript.decode_rawtransaction(self.claim_hex, conn_data)

        _vsize = _decode_tx_hex['vsize']
        _final_fee = int(_vsize * fee_per_byte + 10)
        self.txout = CMutableTxOut(amount - _final_fee, address.to_scriptPubKey())
        self.tx = CMutableTransaction([self.txin], [self.txout])
        self.tx.nLockTime = redeem_blockheight
        self.sighash = SignatureHash(redeem_script, self.tx, 0, SIGHASH_ALL)
        self.sig = privkey.sign(self.sighash) + bytes([SIGHASH_ALL])
        self.txin.scriptSig = CScript([self.sig, privkey.pub, preimage, OP_TRUE, redeem_script])
        self.claim_hex = b2x(self.tx.serialize())

        return [self.claim_hex, self.tx, _final_fee]

    def get_secret(self, txid, conn_data):
        try:
            self.txid = lx(txid)
            self.tx_raw = LTCScript.get_rawtransaction(txid, conn_data, True)

            _asm = self.tx_raw['vin'][0]['scriptSig']['asm'].split(" ")
            _secret_hex = _asm[2]
            secret = binascii.unhexlify(_secret_hex).decode('utf-8')
        except Exception as ex:
            print(ex)

        return secret

    def get_lock_utxos(self, address, conn_data, lock = False):
        try:
            # get utxos
            _ltc_unspent = self._handle_ltc.unspent(address, confirmations = 0)

            if _ltc_unspent[0]:
                for _data in _ltc_unspent[0]:
                    _utxo = {'txid': _data['txid'], 'vout': _data['vout'], 'balance': _data['amount'], 'confirmations': _data['confirmations']}

                    # lock utxo
                    _lock_utxo = LTCScript.lock_utxo(_utxo['txid'], _utxo['vout'], lock, conn_data)

                    # cool down
                    time.sleep(0.2)

                _locked = True
            else:
                _locked = False
        except Exception as ex:
            print(ex)
            _locked = False

        return _locked

    def unlock_utxos(self, address, conn_data, lock = True):
        try:
            # list locked utxos
            _list_lock = LTCScript.list_lock(conn_data)

            if _list_lock:
                for _data in _list_lock:
                    _txid = _data['txid']
                    _vout = _data['vout']
                    _addr_raw = LTCScript.get_transaction(_txid, conn_data, _vout)

                    if _addr_raw[0] == address:
                        _unlock_utxo = LTCScript.lock_utxo(_txid, _vout, lock, conn_data)

                        # cool down
                        time.sleep(0.2)

                        _unlock = True
                    else:
                        _unlock = False
            else:
                _unlock = False
        except Exception as ex:
            print(ex)
            _unlock = False

        return _unlock

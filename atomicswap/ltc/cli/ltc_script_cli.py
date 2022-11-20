#!/usr/bin/env python3

import sys, hashlib, binascii, time

import litecoin
from litecoin import SelectParams
from litecoin.core import b2x, lx, b2lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160, CTxIn, CTxOut, CTransaction
from litecoin.core.script import CScript, OP_DUP, OP_IF, OP_ELSE, OP_ENDIF, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL, OP_FALSE, OP_DROP, OP_CHECKLOCKTIMEVERIFY, OP_SHA256, OP_TRUE
from litecoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from litecoin.wallet import CBitcoinAddress, CBitcoinSecret

from depends.config import tannhauser

class LTCScript():
    def __init__(self, net, localhost, path):
        self.params = SelectParams(net)
        self.localhost = localhost

        if self.localhost:
            import litecoin.rpc
            self.litecoind = litecoin.rpc.Proxy(path)
        else:
            pass

    def get_fee(self, blocks = tannhauser['fee_blocks'], fee_mode = tannhauser['fee_estimate_mode']):
        try:
            fee = self.litecoind.estimatesmartfee(blocks, fee_mode)
            fee_per_byte = float(fee["feerate"] / 1000)
            fee_per_byte = round(fee_per_byte,8)
            fee["fee_per_byte"] = fee_per_byte
        except Exception as ex:
            fee["fee_per_byte"] = round(float(0.0012 / 1000), 8)

        return fee

    def getnewaddress(self, label, addr_type = 'legacy'):
        try:
            _new_address = self.litecoind.getnewaddress(label, addr_type)
            return _new_address
        except Exception as ex:
            print(ex)
            return False

    def import_address(self, address):
        try:
            address = str(address)
            import_address = self.litecoind.importaddress(address, 'htlc_address', False)
        except Exception as ex:
            print(ex)

    def get_addressinfo(self, address):
        try:
            address = str(address)
            addr_info = self.litecoind.validateaddress(address)
        except Exception as ex:
            print(ex)

        return addr_info

    def list_lock(self):
        try:
            _lilo = self.litecoind.listlockunspent()
            return _lilo
        except Exception as ex:
            print(ex)
            return False

    def lock_utxo(self, txid, vout, lock):
        try:
            _lock = self.litecoind.lockunspent(lock, [{'txid':txid, 'vout':vout}])
            return _lock
        except Exception as ex:
            print(ex)
            return False

    def unspent(self, address, confirmations = 1):
        try:
            _address = str(address)
            r = self.litecoind.listunspent(confirmations, 9999999, [_address])

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

    def get_privkey(self, address):
        try:
            wif = self.litecoind.dumpprivkey(address)
        except Exception as ex:
            print(ex)

        return wif

    def unlock_wallet(self, passphrase, gap = 10):
        try:
            _unlock = self.litecoind.walletpassphrase(_passphrase, gap)
        except Exception as ex:
            print(ex)

    def blockcount(self):
        try:
            blockheight = self.litecoind.getblockcount()
        except Exception as ex:
            print(ex)

        return blockheight

    def get_transaction(self, txid, index = 0):
        try:
            txid = lx(txid)
            tx_info = self.litecoind.gettransaction(txid)
            fund_details = tx_info['details']
            output_address = fund_details[index]['address']
            fund_vout = fund_details[index]['vout']
        except Exception as ex:
            print(ex)

        return [output_address, fund_vout, tx_info['confirmations']]

    def send_transaction(self, tx_hex):
        try:
            broadcast = self.litecoind.sendrawtransaction(tx_hex)
        except Exception as ex:
            print(ex)

        return broadcast

    def sign_transaction(self, tx):
        try:
            _hex_tx = binascii.hexlify(tx.serialize()).decode('ascii')
            sign = self.litecoind.signrawtransactionwithwallet(_hex_tx)
            sign['tx'] = CTransaction.deserialize(binascii.unhexlify(sign['hex'].encode('ascii')))
            del sign['hex']
        except Exception as ex:
            print(ex)

        return sign

    def decode_rawtransaction(self, tx_hex):
        try:
            decode_tx_hex = self.litecoind.decoderawtransaction(tx_hex)
        except Exception as ex:
            print(ex)

        return decode_tx_hex

    def get_rawtransaction(self, txid, debug = False):
        try:
            tx_raw = self.litecoind.getrawtransaction(txid, debug)
        except Exception as ex:
            print(ex)
            tx_raw = False

        return tx_raw

    def get_clean_address(self, address):
        return CBitcoinAddress(address)

    def gen_preimage(self, secret):
        self.preimage = secret.encode('UTF-8')
        self.hashed_preimage = hashlib.sha256(self.preimage).digest()
        self.hashed_preimage_hex = hashlib.sha256(self.preimage).hexdigest()

        return [self.preimage, self.hashed_preimage, self.hashed_preimage_hex]

    def get_redeem_script(self, blocks, hashed_preimage, sender_address, receiver_address, validate = False):
        if validate:
            self.redeem_blockheight = blocks
        else:
            self.current_blockheight = self.blockcount()
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

    def gen_fund_tx(self, network, sender_address, htlc_address, amount, fee_per_byte = 1, wif = None):
        self.sender_address = sender_address
        self.htlc_address = htlc_address
        self.amount = amount
        self.fee_per_byte = fee_per_byte

        _unspent = self.unspent(self.sender_address)
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
        _sign_raw = self.sign_transaction(_tx)

        # get signed tx
        _signed_tx = _sign_raw['tx']

        # signed tx hex
        _signed_tx_hex = b2x(_signed_tx.serialize())

        # decode tx
        _decode_tx_hex = self.decode_rawtransaction(_signed_tx_hex)

        # TODO change this later to a smarter solution

        # compose final tx include correct fees
        _vsize = int(_decode_tx_hex['vsize'])
        _final_fee = int(_vsize * self.fee_per_byte + 10)
        _final_amount_change = _balance_total - self.amount - _final_fee
        _final_txout_change = CTxOut(_final_amount_change, CBitcoinAddress(str(self.sender_address)).to_scriptPubKey())
        _final_tx = CTransaction(_txins, [_txout_receiver, _final_txout_change])
        _final_tx_hex = b2x(_final_tx.serialize())
        _final_sign_raw = self.sign_transaction(_final_tx)
        _final_signed_tx = _final_sign_raw['tx']
        _final_signed_tx_hex = b2x(_final_signed_tx.serialize())

        return [_final_signed_tx, _final_signed_tx_hex, _final_fee]

    def refund(self, txid, vout, amount, fee_per_byte, address, redeem_blockheight, redeem_script, privkey):
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
        _decode_tx_hex = self.decode_rawtransaction(self.refund_hex)

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

    def claim(self, txid, vout, amount, fee_per_byte, address, redeem_blockheight, redeem_script, privkey, preimage):
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
        _decode_tx_hex = self.decode_rawtransaction(self.claim_hex)

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

    def get_secret(self, txid):
        try:
            self.txid = lx(txid)
            self.tx_raw = self.get_rawtransaction(txid, True)

            _asm = self.tx_raw['vin'][0]['scriptSig']['asm'].split(" ")
            _secret_hex = _asm[2]
            secret = binascii.unhexlify(_secret_hex).decode('utf-8')
        except Exception as ex:
            print(ex)

        return secret

    def get_lock_utxos(self, address, lock = False):
        try:
            # get utxos
            _ltc_unspent = self._handle_ltc.unspent(address, confirmations = 0)

            if _ltc_unspent[0]:
                for _data in _ltc_unspent[0]:
                    _utxo = {'txid': _data['txid'], 'vout': _data['vout'], 'balance': _data['amount'], 'confirmations': _data['confirmations']}

                    # lock utxo
                    _lock_utxo = self.lock_utxo(_utxo['txid'], _utxo['vout'], lock)

                    # cool down
                    time.sleep(0.2)

                _locked = True
            else:
                _locked = False
        except Exception as ex:
            print(ex)
            _locked = False

        return _locked

    def unlock_utxos(self, address, lock = True):
        try:
            # list locked utxos
            _list_lock = self.list_lock()

            if _list_lock:
                for _data in _list_lock:
                    _txid = _data['txid']
                    _vout = _data['vout']
                    _addr_raw = self.get_transaction(_txid, _vout)

                    if _addr_raw[0] == address:
                        _unlock_utxo = self.lock_utxo(_txid, _vout, lock)

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

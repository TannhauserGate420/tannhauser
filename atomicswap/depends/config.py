#!/usr/bin/env python3

tannhauser = {
    "name" : "TannhauserGate",
    "version" : "0.2.6 dev",
    "authors" : ("iizegrim"),
    "server" : ['http://h6icwooluklzmvonhagxrf5aqo6jybooqv35x42fw6eeovyvsihnq2yd.onion'],
    "server_clear" : ['https://btcswap.net:30443'],
    "request_timeout" : 20,
    "btc_network":"BTC",
    "ltc_network":"LTC",
    "net":"mainnet",
    "localhost":bool(True),
    "blocks_btc_user":int(6), # ~1h
    "blocks_ltc_user":int(24), # ~1h
    "blocks_btc_bond_user": int(12), # ~2h
    "blocks_ltc_bond_user": int(48), # ~2h
    "blocks_btc_server":int(12), # ~2h
    "blocks_ltc_server":int(48), # ~2h
    "confirmations_htlc":int(1),
    "confirmations_btc":int(1),
    "confirmations_ltc":int(1),
    "fee_blocks": int(1),
    "fee_estimate_mode": str('ECONOMICAL'),
    "gap_factor": 200,
    "fee_factor": float(1.5),
    "unit": int(100000000)
}

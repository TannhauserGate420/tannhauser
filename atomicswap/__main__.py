#!/usr/bin/env python3

import os, sys, sysconfig, time, binascii, requests, emoji, json
import atomicswap.depends.utils as utils

from atomicswap.depends.config import tannhauser
from atomicswap.depends.spinner import QtWaitingSpinner

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from atomicswap.btc.gui.btc_script import BTCScript
from atomicswap.ltc.gui.ltc_script import LTCScript

from random import choice
from stem import Signal
from stem.control import Controller
#from fake_http_header import FakeHttpHeader

class RequestRunnable(QRunnable):
    def __init__(self, dialog, path, tor_url, tor_port, tor_control_port, tor = True, rotate = False):
        QRunnable.__init__(self)
        self._dialog = dialog
        self._path = path
        self._tor = tor
        self._tor_url = tor_url
        self._tor_port = tor_port
        self._tor_control_port = tor_control_port
        self._rotate = rotate

    def run(self):
        #_headers = FakeHttpHeader().as_header_dict()
        # there is a small bug at the fake_http_header lib. until solving we use this temp header
        _headers = {"user-agent": "TannhauserGate v0.2.1 dev",
                "content-type": "application/json; charset=utf-8",
                "accept": "application/json"
        }

        if self._tor:
            if self._rotate:
                with Controller.from_port(port = self._tor_control_port) as controller:
                    controller.authenticate()
                    controller.signal(Signal.NEWNYM)
            else:
                pass

            _base_url = choice(tannhauser['server'])
            _url = f'{_base_url}{self._path}'

            # set loop
            _tries, _max_tries = 0, 5

            while _tries <= _max_tries:
                try:
                    _session = requests.session()
                    _session.proxies = {}
                    _session.proxies['http'] = f"socks5h://{self._tor_url}:{self._tor_port}"
                    _res = _session.post(url = _url, headers = _headers, timeout = tannhauser['request_timeout'])
                    _res.close()
                    _res = _res.json()
                    break
                except Exception as ex:
                    print(ex)

                    _tries += 1
                    if _tries >= 2:
                        with Controller.from_port(port = self._tor_control_port) as controller:
                            controller.authenticate()
                            controller.signal(Signal.NEWNYM)
                        time.sleep(2)
                    else:
                        pass

                    _res = {
                        'type': 'server_online',
                        'status': False
                    }
        else:
            _base_url = choice(tannhauser['server'])
            _url = f'{_base_url}/{data}'
            _res = requests.get(url = _url, headers = _headers, timeout = tannhauser['request_timeout'])

        QThread.msleep(1000)
        QMetaObject.invokeMethod(self._dialog, "setData",
                                 Qt.QueuedConnection,
                                 Q_ARG(dict, _res))

class Output(QWidget):
    def __init__(self, **kwargs):
        super(Output, self).__init__()

        _get_path = sysconfig.get_paths()
        self._curr_path = _get_path['purelib']

        self._output_connecting = True if 'connecting' in kwargs  and kwargs['connecting'] else False
        self._output_start = True if 'start' in kwargs  and kwargs['start'] else False
        self._output_stats = True if 'output_stats' in kwargs and kwargs['output_stats'] else False
        self._output_offline = True if 'server_offline' in kwargs and kwargs['server_offline'] else False
        self._output_swap_data = True if 'new_swap_data' in kwargs and kwargs['new_swap_data'] else False
        self._output_faq = True if 'faq' in kwargs and kwargs['faq'] else False
        self._output_wallet = True if 'output_wallet' in kwargs and kwargs['output_wallet'] else False
        self._output_conn_get_swap_data = True if 'get_swap_data' in kwargs and kwargs['get_swap_data'] else False
        self._output_conn_send_swap_data = True if 'send_swap_data' in kwargs and kwargs['send_swap_data'] else False
        self._output_check_swap_data = True if 'check_swap_data' in kwargs and kwargs['check_swap_data'] else False
        self._output_upd_swap_status = True if 'upd_swap_status' in kwargs and kwargs['upd_swap_status'] else False

        self.btc_logo = QLabel('BTC')
        self.btc_logo.setStyleSheet("color: blue; font: bold")
        self.btc_logo.setAlignment(Qt.AlignCenter)
        self.btc_logo.setPixmap(QPixmap(f"{self._curr_path}/atomicswap/contrib/images/btc.png").scaled(300,300))

        self.ltc_logo = QLabel('LTC')
        self.ltc_logo.setStyleSheet("color: blue; font: bold")
        self.ltc_logo.setAlignment(Qt.AlignCenter)
        self.ltc_logo.setPixmap(QPixmap(f"{self._curr_path}/atomicswap/contrib/images/ltc.png").scaled(300,300))

        if self._output_connecting:
            self.header = QLabel('\nCONNECTING TO TANNHAUSER GATE ...')
            self.output_connecting()

        if self._output_start:
            self.output_start()

        if self._output_stats:
            self.server_status = kwargs['server_status']
            self.output_stats()

        if self._output_offline:
            self.server_status = kwargs['server_status']
            self.output_stats()

        if self._output_swap_data:
            self.swap_data = kwargs['swap_data']
            self.output_swap_data()

        if self._output_faq:
            self.output_faq()

        if self._output_wallet:
            self._btc_wallet = kwargs['btc_wallet']
            self._ltc_wallet = kwargs['ltc_wallet']
            self._balances = kwargs['balances']
            self.output_wallet()

        if self._output_conn_get_swap_data:
            self.header = QLabel('\nGETTING FRESH SWAP DATA ...')
            self.output_connecting()

        if self._output_conn_send_swap_data:
            self.header = QLabel('\nSENDING SWAP DATA ...')
            self.output_connecting()

        if self._output_check_swap_data:
            self._check_swap_data = kwargs['swap_data']
            self.output_check_swap_data()

        if self._output_upd_swap_status:
            self.header = QLabel('\nCHECKING YOUR SWAP STATUS ...')
            self.output_connecting()

    def output_start(self):
        self.header = QLabel('WELCOME TO TANNHAUSER GATE - YOUR FRIENDLY ATOMIC SWAP PARTNER!')
        font = self.header.font()
        font.setPointSize(13)
        self.header.setFont(font)
        self.header.setStyleSheet("color: lightgreen; font: bold")
        self.header.setAlignment(Qt.AlignCenter)

        self.footer = QLabel(f'NO SHADY TOKEN {emoji.emojize(":check_mark:")} NO REGISTRATION {emoji.emojize(":check_mark:")} OPEN SOURCE {emoji.emojize(":check_mark:")} TOR BY DEFAULT {emoji.emojize(":check_mark:")}')
        font = self.footer.font()
        font.setPointSize(13)
        self.footer.setFont(font)
        self.footer.setStyleSheet("color: lightgreen")
        self.footer.setAlignment(Qt.AlignCenter)

        layout = QGridLayout()
        layout.addWidget(self.header, 0, 0, 1, 0)
        layout.addWidget(self.btc_logo, 1, 0)
        layout.addWidget(self.ltc_logo, 1, 1)
        layout.addWidget(self.footer, 2, 0, 1, 0)
        self.setLayout(layout)

    def output_connecting(self):
        font = self.header.font()
        font.setPointSize(13)
        self.header.setFont(font)
        self.header.setStyleSheet("color: lightgreen")
        self.header.setAlignment(Qt.AlignCenter)

        layout = QGridLayout()
        layout.addWidget(self.header, 1, 0, 1, 0)
        layout.addWidget(self.btc_logo, 0, 0)
        layout.addWidget(self.ltc_logo, 0, 1)
        self.setLayout(layout)

    def output_swap_data(self):
        self.header = QLabel('\nPLEASE CHECK YOUR DATA CAREFULLY!\nIF YOU HIT THE \"SEND\" BUTTON THE COINS WILL BE SEND!\n')
        font = self.header.font()
        font.setPointSize(13)
        self.header.setFont(font)
        self.header.setStyleSheet("color: lightgreen; font: bold")
        self.header.setAlignment(Qt.AlignCenter)

        if self.swap_data[0] == 'btc':
            self.swp_data1 = QLabel('YOU WILL SEND (BTC): \n YOUR BOND (BTC): \n YOU WILL RECEIVE (LTC): \n YOUR BOND HTLC ADDRESS: \n CURRENT BLOCKHEIGHT: \n YOUR REFUND BLOCKHEIGHT (~2h): \n NETWORK FEE (SATS):')
            font = self.swp_data1.font()
            font.setPointSize(12)
            self.swp_data1.setFont(font)
            self.swp_data1.setStyleSheet("color: #E5E5E5")
            self.swp_data1.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

            _data = f" {self.swap_data[9]:,}\n {self.swap_data[11]:,}\n {self.swap_data[12]:,}\n {self.swap_data[6]}\n {self.swap_data[8]:,}\n {self.swap_data[7]:,}\n {self.swap_data[5]}"
            self.swp_data2 = QLabel(_data)
            font = self.swp_data2.font()
            font.setPointSize(12)
            self.swp_data2.setFont(font)
            self.swp_data2.setStyleSheet("color: lightgreen;")
            self.swp_data2.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.swp_data2.setTextInteractionFlags(Qt.TextSelectableByMouse)

            layout = QGridLayout()
            layout.addWidget(self.header, 0, 0, 1, 0)
            layout.addWidget(self.btc_logo, 1, 0)
            layout.addWidget(self.ltc_logo, 1, 1)
            layout.addWidget(self.swp_data1, 2, 0)
            layout.addWidget(self.swp_data2, 2, 1)
            self.setLayout(layout)
        else:
            self.swp_data1 = QLabel('YOU WILL SEND (LTC): \n YOUR BOND (LTC): \n YOU WILL RECEIVE (BTC): \n YOUR BOND HTLC ADDRESS: \n CURRENT BLOCKHEIGHT: \n YOUR REFUND BLOCKHEIGHT (~2h): \n NETWORK FEE (SATS):')
            font = self.swp_data1.font()
            font.setPointSize(12)
            self.swp_data1.setFont(font)
            self.swp_data1.setStyleSheet("color: #E5E5E5")
            self.swp_data1.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

            _data = f" {self.swap_data[9]:,}\n {self.swap_data[11]:,}\n {self.swap_data[12]:,}\n {self.swap_data[6]}\n {self.swap_data[8]:,}\n {self.swap_data[7]:,}\n {self.swap_data[5]}"
            self.swp_data2 = QLabel(_data)
            font = self.swp_data2.font()
            font.setPointSize(12)
            self.swp_data2.setFont(font)
            self.swp_data2.setStyleSheet("color: lightgreen;")
            self.swp_data2.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.swp_data2.setTextInteractionFlags(Qt.TextSelectableByMouse)

            layout = QGridLayout()
            layout.addWidget(self.header, 0, 0, 1, 0)
            layout.addWidget(self.ltc_logo, 1, 0)
            layout.addWidget(self.btc_logo, 1, 1)
            layout.addWidget(self.swp_data1, 2, 0)
            layout.addWidget(self.swp_data2, 2, 1)
            self.setLayout(layout)

    def output_stats(self):
        self.header = QLabel('WELCOME TO TANNHAUSER GATE - YOUR FRIENDLY ATOMIC SWAP PARTNER!\n')
        font = self.header.font()
        font.setPointSize(13)
        self.header.setFont(font)
        self.header.setStyleSheet("color: lightgreen; font: bold")
        self.header.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        if self._output_offline:
            self.srvr1 = QLabel('\nTANNHAUSER STATUS: \n SWAP POSSIBLE:')
            font = self.srvr1.font()
            font.setPointSize(12)
            self.srvr1.setFont(font)
            self.srvr1.setStyleSheet("color: #E5E5E5")
            self.srvr1.setAlignment(Qt.AlignRight)

            _stat = f"\n OFFLINE {emoji.emojize(':frowning_face:')}\n NOPE {emoji.emojize(':frowning_face:')}"
            self.srvr2 = QLabel(_stat)
            font = self.srvr2.font()
            font.setPointSize(12)
            self.srvr2.setFont(font)
            self.srvr2.setStyleSheet("color: lightgreen;")
            self.srvr2.setAlignment(Qt.AlignLeft)
        else:
            self.srvr1 = QLabel('\nTANNHAUSER STATUS: \n SWAP POSSIBLE: \n SUCCESSFUL SWAPS: \n REFUNDED: \n BTC/LTC: \n LTC/BTC: \n BTC (MIN/MAX): \n LTC (MIN/MAX): \n CURRENT BOND (MIN):')
            font = self.srvr1.font()
            font.setPointSize(12)
            self.srvr1.setFont(font)
            self.srvr1.setStyleSheet("color: #E5E5E5")
            self.srvr1.setAlignment(Qt.AlignRight)

            _stat = f"\n ONLINE {emoji.emojize(':grinning_face:')}\n YEP {emoji.emojize(':grinning_face:')}\n {self.server_status['success_count']}\n {self.server_status['refund_count']}\n {self.server_status['btc_ltc']}\n {self.server_status['ltc_btc']}\n {self.server_status['btc_min_btc']:,} / {self.server_status['btc_max_btc']:,}\n {self.server_status['ltc_min_ltc']:,} / {self.server_status['ltc_max_ltc']:,}\n BTC {self.server_status['btc_bond_btc']:,} / LTC {self.server_status['ltc_bond_ltc']:,}"
            self.srvr2 = QLabel(_stat)
            font = self.srvr2.font()
            font.setPointSize(12)
            self.srvr2.setFont(font)
            self.srvr2.setStyleSheet("color: lightgreen;")
            self.srvr2.setAlignment(Qt.AlignLeft)

        layout = QGridLayout()
        layout.addWidget(self.header, 0, 0, 1, 0)
        layout.addWidget(self.btc_logo, 1, 0)
        layout.addWidget(self.ltc_logo, 1, 1)
        layout.addWidget(self.srvr1, 2, 0)
        layout.addWidget(self.srvr2, 2, 1)
        self.setLayout(layout)

    def output_faq(self):
        self.faq_head = QLabel('TANNHAUSER GATE FAQ\n')
        font = self.faq_head.font()
        font.setPointSize(12)
        self.faq_head.setFont(font)
        self.faq_head.setStyleSheet("color: lightgreen; font: bold")
        self.faq_head.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.q1 = QLabel('Q: What the heck is an atomic swap?\nA: In computer science the term \"atomic\" refers to a process that is either executed as planned - or not at all. This means your swap will be executed as planned or you will get an automatic refund. There is no partial solution.\n')
        font = self.q1.font()
        font.setPointSize(11)
        self.q1.setFont(font)
        self.q1.setStyleSheet("color: lightgreen")
        self.q1.setAlignment(Qt.AlignLeft)
        self.q1.setWordWrap(True)

        self.q2 = QLabel('Q: Can I lose my coins if something went wrong?\nA: No. All transactions take place at the blockchain. No shady token is needed. All what you can lose are some fees for funding/refunding.\n')
        font = self.q2.font()
        font.setPointSize(11)
        self.q2.setFont(font)
        self.q2.setStyleSheet("color: lightgreen")
        self.q2.setAlignment(Qt.AlignLeft)
        self.q2.setWordWrap(True)

        self.q3 = QLabel('Q: Do I have to register or do I have to provide personal informations?\nA: No. Additionally Tannhauser Gate use Tor by default for your privacy.\n')
        font = self.q3.font()
        font.setPointSize(11)
        self.q3.setFont(font)
        self.q3.setStyleSheet("color: lightgreen")
        self.q3.setAlignment(Qt.AlignLeft)
        self.q3.setWordWrap(True)

        self.q4 = QLabel('Q: Is it possible that I get \"tainted\" coins?\nA: No. You will never receive \"tainted\" coins from Tannhauser Gate.\n')
        font = self.q4.font()
        font.setPointSize(11)
        self.q4.setFont(font)
        self.q4.setStyleSheet("color: lightgreen")
        self.q4.setAlignment(Qt.AlignLeft)
        self.q4.setWordWrap(True)

        self.q5 = QLabel('Q: Why Bitcoin and Litecoin?\nA: Beside obvious reasons like rank/marketcap - we have somewhere to start. More coins (and tokens at the ETH blockchain) will follow soon (ETH, DASH, DOGE, ZCASH).\n')
        font = self.q5.font()
        font.setPointSize(11)
        self.q5.setFont(font)
        self.q5.setStyleSheet("color: lightgreen")
        self.q5.setAlignment(Qt.AlignLeft)
        self.q5.setWordWrap(True)

        self.q6 = QLabel('Q: Why a bond and in which cases I lose the bond?\nA: For DDOS reasons. Tannhauser Gate will claim the bond if you dont send the swap transaction at all or the amount is less than agreed.')
        font = self.q6.font()
        font.setPointSize(11)
        self.q6.setFont(font)
        self.q6.setStyleSheet("color: lightgreen")
        self.q6.setAlignment(Qt.AlignLeft)
        self.q6.setWordWrap(True)

        self.q7 = QLabel("Tannhauser Gate is copyleft by GPL3. Everyone is invited to join us at <a href=https://github.com/TannhauserGate420><font color=lightgreen>GitHub</font></a>!")
        font = self.q7.font()
        font.setPointSize(12)
        self.q7.setFont(font)
        self.q7.setStyleSheet("color: lightgreen; font: bold")
        self.q7.setAlignment(Qt.AlignHCenter)
        self.q7.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.q7.setOpenExternalLinks(True)
        self.q7.setWordWrap(True)

        layout = QGridLayout()
        layout.addWidget(self.q7, 1, 0)
        layout.addWidget(self.q1, 2, 0)
        layout.addWidget(self.q2, 3, 0)
        layout.addWidget(self.q3, 4, 0)
        layout.addWidget(self.q4, 5, 0)
        layout.addWidget(self.q5, 6, 0)
        layout.addWidget(self.q6, 7, 0)
        self.setLayout(layout)

    def output_wallet(self):
        self.btc_logo.setPixmap(QPixmap(f"{self._curr_path}/atomicswap/contrib/images/btc.png").scaled(180,180))
        self.ltc_logo.setPixmap(QPixmap(f"{self._curr_path}/atomicswap/contrib/images/ltc.png").scaled(180,180))

        self.btc1 = QLabel('BTC ADDRESS: \n BALANCE: \n UNCONFIRMED:')
        font = self.btc1.font()
        font.setPointSize(12)
        self.btc1.setFont(font)
        self.btc1.setStyleSheet("color: #E5E5E5")
        self.btc1.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        _stat = f" {self._btc_wallet}\n {self._balances[4]:,}\n {self._balances[5]:,}"
        self.btc2 = QLabel(_stat)
        font = self.btc2.font()
        font.setPointSize(12)
        self.btc2.setFont(font)
        self.btc2.setStyleSheet("color: lightgreen;")
        self.btc2.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.btc2.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.ltc1 = QLabel('LTC ADDRESS: \n BALANCE: \n UNCONFIRMED:')
        font = self.ltc1.font()
        font.setPointSize(12)
        self.ltc1.setFont(font)
        self.ltc1.setStyleSheet("color: #E5E5E5")
        self.ltc1.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        _stat = f" {self._ltc_wallet}\n {self._balances[6]:,}\n {self._balances[7]:,}"
        self.ltc2 = QLabel(_stat)
        font = self.ltc2.font()
        font.setPointSize(12)
        self.ltc2.setFont(font)
        self.ltc2.setStyleSheet("color: lightgreen;")
        self.ltc2.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.ltc2.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout = QGridLayout()
        layout.addWidget(self.btc_logo, 1, 0)
        layout.addWidget(self.btc1, 1, 1)
        layout.addWidget(self.btc2, 1, 2)
        layout.addWidget(self.ltc_logo, 2, 0)
        layout.addWidget(self.ltc1, 2, 1)
        layout.addWidget(self.ltc2, 2, 2)
        self.setLayout(layout)

    def output_check_swap_data(self):
        # collect time data
        self._now = time.time()
        self._next = self._now + 60
        self._now_readable = time.ctime(self._now)
        self._next_readable = time.ctime(self._next)

        # shorting val
        _loaded_data = self._check_swap_data['load_bond_transaction']
        _server_data = self._check_swap_data['check_server_data']
        _bond_amount_btc = round(float(_loaded_data['amount'] / tannhauser['unit']), 8)

        # temp trick - todo: set direction at main
        if tannhauser['net'] == 'testnet':
            _direction = 'btc' if _loaded_data['htlc_address'].startswith('2') else 'ltc'
        else:
            _direction = 'btc' if _loaded_data['htlc_address'].startswith('3') else 'ltc'

        try:
            _loaded_swap_data = self._check_swap_data['load_swap_transaction']
        except Exception as ex:
            print(ex)
            _loaded_swap_data = False

        # temp trick
        if not _server_data:
            del(_server_data)
            _server_data = {}
            _server_data['status'] = False
        else:
            pass

        self._headline = QLabel(f'WE CHECK YOUR SWAP EVERY 60 SECONDS! YOU CAN PAUSE THE CHECK AT ANY TIME!')
        font = self._headline.font()
        font.setPointSize(12)
        self._headline.setFont(font)
        self._headline.setStyleSheet("color: lightgreen")
        self._headline.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._headline.setWordWrap(True)

        if not _server_data['status'] or _server_data['status'] in [1]:
            self._chk_swp_data1 = QLabel("\nSWAP TOKEN:\nBOND HTLC ADDRESS:\n BOND AMOUNT:\nBOND REFUND BLOCKHEIGHT:\nLAST CHECK:\nNEXT CHECK:")
            font = self._chk_swp_data1.font()
            font.setPointSize(11)
            self._chk_swp_data1.setFont(font)
            self._chk_swp_data1.setStyleSheet("color: white")
            self._chk_swp_data1.setAlignment(Qt.AlignRight)
            self._chk_swp_data1.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self._chk_swp_data2 = QLabel(f"\n{_loaded_data['swap_token']}\n{_loaded_data['htlc_address']}\n{_bond_amount_btc:,}\n{_loaded_data['refund_blockheight']:,}\n{self._now_readable}\n{self._next_readable}")
            font = self._chk_swp_data2.font()
            font.setPointSize(11)
            self._chk_swp_data2.setFont(font)
            self._chk_swp_data2.setStyleSheet("color: lightgreen;")
            self._chk_swp_data2.setAlignment(Qt.AlignLeft)
            self._chk_swp_data2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        elif _server_data['status'] == 2:
            _server_data_amount_unit = round(float(_server_data['amount'] / tannhauser['unit']), 8)

            self._chk_swp_data1 = QLabel("\nSWAP TOKEN:\nBOND HTLC ADDRESS:\n BOND AMOUNT:\nBOND REFUND BLOCKHEIGHT:\nTANNHAUSER HTLC ADDRESS:\nTANNHAUSER AMOUNT:\nTANNHAUSER REFUND BLOCKHEIGHT:\nLAST CHECK:\nNEXT CHECK:")
            font = self._chk_swp_data1.font()
            font.setPointSize(11)
            self._chk_swp_data1.setFont(font)
            self._chk_swp_data1.setStyleSheet("color: #E5E5E5")
            self._chk_swp_data1.setAlignment(Qt.AlignRight)
            self._chk_swp_data1.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self._chk_swp_data2 = QLabel(f"\n{_loaded_data['swap_token']}\n{_loaded_data['htlc_address']}\n{_bond_amount_btc:,}\n{_loaded_data['refund_blockheight']:,}\n{_server_data['htlc_address']}\n{_server_data_amount_unit:,}\n{_server_data['refund_blockheight']:,}\n{self._now_readable}\n{self._next_readable}")
            font = self._chk_swp_data2.font()
            font.setPointSize(11)
            self._chk_swp_data2.setFont(font)
            self._chk_swp_data2.setStyleSheet("color: lightgreen;")
            self._chk_swp_data2.setAlignment(Qt.AlignLeft)
            self._chk_swp_data2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        elif _server_data['status'] in [3, 5]:
            # define swap amount total
            _total_swap_amount = int(_loaded_data['amount'] + _loaded_swap_data['amount'])
            _total_swap_amount_unit = round(float(_total_swap_amount / tannhauser['unit']), 8)
            _server_data_amount_unit = round(float(_server_data['amount'] / tannhauser['unit']), 8)

            self._chk_swp_data1 = QLabel("\nSWAP TOKEN:\nTANNHAUSER HTLC ADDRESS:\nTANNHAUSER AMOUNT:\nTANNHAUSER REFUND BLOCKHEIGHT:\nYOUR SWAP HTLC ADDRESS:\nYOUR SWAP AMOUNT:\nYOUR SWAP REFUND BLOCKHEIGHT:\nLAST CHECK:\nNEXT CHECK:")
            font = self._chk_swp_data1.font()
            font.setPointSize(11)
            self._chk_swp_data1.setFont(font)
            self._chk_swp_data1.setStyleSheet("color: #E5E5E5")
            self._chk_swp_data1.setAlignment(Qt.AlignRight)
            self._chk_swp_data1.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self._chk_swp_data2 = QLabel()
            self._chk_swp_data2.setText(f"\n{_loaded_data['swap_token']}\n{_server_data['htlc_address']}\n{_server_data_amount_unit:,}\n{_server_data['refund_blockheight']:,}\n{_loaded_swap_data['htlc_address']}\n{_total_swap_amount_unit:,}\n{_loaded_swap_data['refund_blockheight']:,}\n{self._now_readable}\n{self._next_readable}")
            font = self._chk_swp_data2.font()
            font.setPointSize(11)
            self._chk_swp_data2.setFont(font)
            self._chk_swp_data2.setStyleSheet("color: lightgreen;")
            self._chk_swp_data2.setAlignment(Qt.AlignLeft)
            self._chk_swp_data2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        elif _server_data['status'] in [4, 6]:
            self._headline = QLabel(f'SWAP FAILED!')
            font = self._headline.font()
            font.setPointSize(13)
            self._headline.setFont(font)
            self._headline.setStyleSheet("color: lightgreen")
            self._headline.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

            if _loaded_swap_data:
                _total_swap_amount = int(_loaded_data['amount'] + _loaded_swap_data['amount'])
                _total_swap_amount_unit = round(float(_total_swap_amount / tannhauser['unit']), 8)
                _server_data_amount_unit = round(float(_server_data['amount'] / tannhauser['unit']), 8)

                self._chk_swp_data1 = QLabel("\nSWAP TOKEN:\nTANNHAUSER HTLC ADDRESS:\nTANNHAUSER SWAP AMOUNT:\nYOUR SWAP HTLC ADDRESS:\nYOUR SWAP AMOUNT:")
                font = self._chk_swp_data1.font()
                font.setPointSize(11)
                self._chk_swp_data1.setFont(font)
                self._chk_swp_data1.setStyleSheet("color: #E5E5E5")
                self._chk_swp_data1.setAlignment(Qt.AlignRight)
                self._chk_swp_data1.setTextInteractionFlags(Qt.TextSelectableByMouse)

                self._chk_swp_data2 = QLabel(f"\n{_loaded_data['swap_token']}\n{_server_data['htlc_address']}\n{_server_data_amount_unit:,}\n{_loaded_swap_data['htlc_address']}\n{_total_swap_amount_unit:,}")
                font = self._chk_swp_data2.font()
                font.setPointSize(11)
                self._chk_swp_data2.setFont(font)
                self._chk_swp_data2.setStyleSheet("color: lightgreen;")
                self._chk_swp_data2.setAlignment(Qt.AlignLeft)
                self._chk_swp_data2.setTextInteractionFlags(Qt.TextSelectableByMouse)
            else:
                _server_data_amount_unit = round(float(_server_data['amount'] / tannhauser['unit']), 8)

                self._chk_swp_data1 = QLabel("\nSWAP TOKEN:\nTANNHAUSER HTLC ADDRESS:\nTANNHAUSER SWAP AMOUNT:")
                font = self._chk_swp_data1.font()
                font.setPointSize(11)
                self._chk_swp_data1.setFont(font)
                self._chk_swp_data1.setStyleSheet("color: #E5E5E5")
                self._chk_swp_data1.setAlignment(Qt.AlignRight)
                self._chk_swp_data1.setTextInteractionFlags(Qt.TextSelectableByMouse)

                self._chk_swp_data2 = QLabel(f"\n{_loaded_data['swap_token']}\n{_server_data['htlc_address']}\n{_server_data_amount_unit:,}")
                font = self._chk_swp_data2.font()
                font.setPointSize(11)
                self._chk_swp_data2.setFont(font)
                self._chk_swp_data2.setStyleSheet("color: lightgreen;")
                self._chk_swp_data2.setAlignment(Qt.AlignLeft)
                self._chk_swp_data2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        elif _server_data['status'] == 7:
            # define swap amount total
            _total_swap_amount = int(_loaded_data['amount'] + _loaded_swap_data['amount'])
            _total_swap_amount_unit = round(float(_total_swap_amount / tannhauser['unit']), 8)
            _server_data_amount_unit = round(float(_server_data['amount'] / tannhauser['unit']), 8)

            self._headline = QLabel(f'SWAP SUCCESSFUL!')
            font = self._headline.font()
            font.setPointSize(11)
            self._headline.setFont(font)
            self._headline.setStyleSheet("color: lightgreen")
            self._headline.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

            self._chk_swp_data1 = QLabel("\nSWAP TOKEN:\nTANNHAUSER HTLC ADDRESS:\nTANNHAUSER SWAP AMOUNT:\nYOUR SWAP HTLC ADDRESS:\nYOUR SWAP AMOUNT:")
            font = self._chk_swp_data1.font()
            font.setPointSize(11)
            self._chk_swp_data1.setFont(font)
            self._chk_swp_data1.setStyleSheet("color: #E5E5E5")
            self._chk_swp_data1.setAlignment(Qt.AlignRight)
            self._chk_swp_data1.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self._chk_swp_data2 = QLabel()
            self._chk_swp_data2.setText(f"\n{_loaded_data['swap_token']}\n{_server_data['htlc_address']}\n{_server_data_amount_unit:,}\n{_loaded_swap_data['htlc_address']}\n{_total_swap_amount_unit:,}")
            font = self._chk_swp_data2.font()
            font.setPointSize(11)
            self._chk_swp_data2.setFont(font)
            self._chk_swp_data2.setStyleSheet("color: lightgreen;")
            self._chk_swp_data2.setAlignment(Qt.AlignLeft)
            self._chk_swp_data2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        elif _server_data['status'] ==  99:
            try:
                if _loaded_data['finalized']:
                    self._headline = QLabel(f'SWAP FAILED!')
                    self._chk_swp_data1 = QLabel("\nSWAP TOKEN:\nBOND HTLC ADDRESS:\n BOND AMOUNT:\nBOND REFUND BLOCKHEIGHT:")
                    self._chk_swp_data2 = QLabel(f"\n{_loaded_data['swap_token']}\n{_loaded_data['htlc_address']}\n{_bond_amount_btc:,}\n{_loaded_data['refund_blockheight']:,}")
                else:
                    self._headline = QLabel(f'SWAP FAILED! WE CHECK YOUR SWAP EVERY 60 SECONDS!')
                    self._chk_swp_data1 = QLabel("\nSWAP TOKEN:\nBOND HTLC ADDRESS:\n BOND AMOUNT:\nBOND REFUND BLOCKHEIGHT:\nLAST CHECK:\nNEXT CHECK:")
                    self._chk_swp_data2 = QLabel(f"\n{_loaded_data['swap_token']}\n{_loaded_data['htlc_address']}\n{_bond_amount_btc:,}\n{_loaded_data['refund_blockheight']:,}\n{self._now_readable}\n{self._next_readable}")
            except Exception as ex:
                print(ex)
                self._headline = QLabel(f'SWAP FAILED! WE CHECK YOUR SWAP EVERY 60 SECONDS!')
                self._chk_swp_data1 = QLabel("\nSWAP TOKEN:\nBOND HTLC ADDRESS:\n BOND AMOUNT:\nBOND REFUND BLOCKHEIGHT:\nLAST CHECK:\nNEXT CHECK:")
                self._chk_swp_data2 = QLabel(f"\n{_loaded_data['swap_token']}\n{_loaded_data['htlc_address']}\n{_bond_amount_btc:,}\n{_loaded_data['refund_blockheight']:,}\n{self._now_readable}\n{self._next_readable}")

            font = self._headline.font()
            font.setPointSize(12)
            self._headline.setFont(font)
            self._headline.setStyleSheet("color: lightgreen")
            self._headline.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

            font = self._chk_swp_data1.font()
            font.setPointSize(11)
            self._chk_swp_data1.setFont(font)
            self._chk_swp_data1.setStyleSheet("color: white")
            self._chk_swp_data1.setAlignment(Qt.AlignRight)
            self._chk_swp_data1.setTextInteractionFlags(Qt.TextSelectableByMouse)

            font = self._chk_swp_data2.font()
            font.setPointSize(11)
            self._chk_swp_data2.setFont(font)
            self._chk_swp_data2.setStyleSheet("color: lightgreen;")
            self._chk_swp_data2.setAlignment(Qt.AlignLeft)
            self._chk_swp_data2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        else:
            pass

        layout = QGridLayout()
        layout.addWidget(self._headline, 0, 0, 1, 0)

        if _direction == 'btc':
            layout.addWidget(self.btc_logo, 1, 0)
            layout.addWidget(self.ltc_logo, 1, 1)
        else:
            layout.addWidget(self.btc_logo, 1, 1)
            layout.addWidget(self.ltc_logo, 1, 0)

        layout.addWidget(self._chk_swp_data1, 2, 0)
        layout.addWidget(self._chk_swp_data2, 2, 1)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(f"Tannhauser Gate {tannhauser['version']}")
        self.setFixedWidth(800)
        self.setFixedHeight(500)
        self.setStyleSheet('color: white; background-color: #535353')
        self.center()

        _get_path = sysconfig.get_paths()
        self._curr_path = _get_path['purelib']

        self._handle_btc = BTCScript(tannhauser['net'], tannhauser['localhost'])
        self._handle_ltc = LTCScript(tannhauser['net'], tannhauser['localhost'])

        self.button1 = QPushButton("CONNECT")
        self.button1.setStyleSheet('color: white; background-color: darkred; font: bold; padding: 0.3em')
        self.button1.clicked.connect(self.get_user_data)

        self.button2 = QPushButton("CONFIG")
        self.button2.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
        self.button2.clicked.connect(self.save_user_data)

        self.button4 = QPushButton("EXIT")
        self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
        self.button4.clicked.connect(lambda: self.close())

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(start = True), 0, 0, 1, 0)
        layout.addWidget(self.button1, 1, 0)
        layout.addWidget(self.button2, 1, 1)
        layout.addWidget(self.button4, 1, 2)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    @pyqtSlot(dict)
    def setData(self, data):
        # stop spinner
        try:
            self.spinner.stop()
            del(self.spinner)
        except Exception as ex:
            print(ex)

        # collect data
        if data['type'] == 'ping_server':
            self._ping_server = data
            self.load_server()
        elif data['type'] == 'new_swap':
            self._swap_data = data
            self.load_bond_data()
        elif data['type'] == 'new_bond':
            self.finalize_swap()
        elif data['type'] == 'check_swap_status':
            self._csd = data
            self.check_swap()
        elif data['type'] == 'swap_data':
            self.check_swap_status()
        elif data['type'] == 'server_online':
            self._ping_server = data
            self.load_server_offline()
        else:
            pass

    def get_user_data(self):
        # load user data
        self._user_data = self.load_user_data()

        if self._user_data:
            self._user_tor_data = {
                "tor_url": self._user_data['_tor_url'],
                "tor_port": self._user_data['_tor_port'],
                "tor_control_port": self._user_data['_tor_control_port']
            }

            self._user_btc_data = {
                "btc_rpc_user": self._user_data['_btc_rpc_user'],
                "btc_rpc_password": self._user_data['_btc_rpc_password'],
                "btc_rpc_url": self._user_data['_btc_rpc_url'],
                "btc_rpc_port": self._user_data['_btc_rpc_port'],
                "btc_walletpassphrase": self._user_data['_btc_walletpassphrase'],
            }

            self._user_ltc_data = {
                "ltc_rpc_user": self._user_data['_ltc_rpc_user'],
                "ltc_rpc_password": self._user_data['_ltc_rpc_password'],
                "ltc_rpc_url": self._user_data['_ltc_rpc_url'],
                "ltc_rpc_port": self._user_data['_ltc_rpc_port'],
                "ltc_walletpassphrase": self._user_data['_ltc_walletpassphrase'],
            }
        else:
            self._user_data = self.save_user_data(True)

        # get server data
        self.get_server_data()

    def get_server_data(self):
        try:
            self.spinner.stop()
        except Exception as ex:
            print(ex)

        # set path
        _path = '/'

        # init spinner
        self.spinner = QtWaitingSpinner(self)

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(connecting = True), 0, 0, 1, 0)
        layout.addWidget(self.spinner, 0, 0, 1, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # start spinner
        self.spinner.start()

        # call request
        runnable = RequestRunnable(self, _path, self._user_tor_data['tor_url'], self._user_tor_data['tor_port'], self._user_tor_data['tor_control_port'])
        QThreadPool.globalInstance().start(runnable)

    def load_server(self):
        # output buttons
        self.output_main_buttons()

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(output_stats = True, server_status = self._ping_server), 0, 0, 1, 0)
        layout.addWidget(self.button1, 1, 0)
        layout.addWidget(self.button2, 1, 1)
        layout.addWidget(self.button3, 1, 2)
        layout.addWidget(self.button4, 1, 3)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def load_server_offline(self):
        # output buttons
        self.output_main_buttons()

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(server_offline = True, server_status = self._ping_server), 0, 0, 1, 0)
        layout.addWidget(self.button1, 1, 0)
        layout.addWidget(self.button2, 1, 1)
        layout.addWidget(self.button3, 1, 2)
        layout.addWidget(self.button4, 1, 3)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def output_main_buttons(self, faq = True):
        self.button1 = QPushButton("NEW WALLET")
        self.button1.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
        self.button1.clicked.connect(self.new_wallet)

        self.button2 = QPushButton("LOAD WALLET")
        self.button2.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
        self.button2.clicked.connect(self.load_wallet)

        if faq:
            self.button3 = QPushButton("FAQ")
            self.button3.clicked.connect(self.faq)
        else:
            self.button3 = QPushButton("MAIN")
            self.button3.clicked.connect(self.main)

        self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')

        self.button4 = QPushButton("EXIT")
        self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
        self.button4.clicked.connect(lambda: self.close())

    def new_wallet(self):
        # get wallet data
        self._btc_address = BTCScript.getnewaddress('swapClient', self._user_btc_data)
        self._ltc_address = LTCScript.getnewaddress('swapClient', self._user_ltc_data)

        # set balance value = 0
        self._btc_balance_confirmed, self._btc_balance_unconfirmed, self._ltc_balance_confirmed, self._ltc_balance_unconfirmed, self._btc_balance_confirmed_btc, self._btc_balance_unconfirmed_btc, self._ltc_balance_confirmed_ltc, self._ltc_balance_unconfirmed_ltc = 0, 0, 0, 0, 0, 0, 0, 0
        _balances = [self._btc_balance_confirmed, self._btc_balance_unconfirmed, self._ltc_balance_confirmed, self._ltc_balance_unconfirmed, self._btc_balance_confirmed_btc, self._btc_balance_unconfirmed_btc, self._ltc_balance_confirmed_ltc, self._ltc_balance_unconfirmed_ltc]

        # save wallet
        self._wallet_name = self.get_wallet_name()

        if self._wallet_name:
            _sv_wallet = utils.save_wallet(self._wallet_name, self._btc_address, self._ltc_address)

            # output
            self.button1 = QPushButton("INITIATE SWAP")
            self.button1.setStyleSheet('color: #E5E5E5; background-color: darkgreen; font: bold; padding: 0.3em')
            self.button1.clicked.connect(self.init_swap)

            self.button2 = QPushButton("CHECK SWAP")
            self.button2.setStyleSheet('color: #E5E5E5; background-color: darkcyan; font: bold; padding: 0.3em')
            self.button2.clicked.connect(self.recheck_swap)

            self.button3 = QPushButton("MAIN")
            self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
            self.button3.clicked.connect(self.main)

            self.button4 = QPushButton("EXIT")
            self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
            self.button4.clicked.connect(lambda: self.close())

            layout = QGridLayout()
            layout.addWidget(Output(output_wallet = True, btc_wallet = self._btc_address, ltc_wallet = self._ltc_address, balances = _balances), 0, 0, 1, 0)
            layout.addWidget(self.button1, 1, 0)
            layout.addWidget(self.button2, 1, 1)
            layout.addWidget(self.button3, 1, 2)
            layout.addWidget(self.button4, 1, 3)

            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
        else:
            pass

    def load_wallet(self, wallet = False):
        # select wallet
        if wallet:
            _wallet_data = utils.load_wallet(self._wallet_name)
            _load_success = True
        else:
            self._wallet_name = self.load_wallet_dialog()

            if self._wallet_name:
                _wallet_data = utils.load_wallet(self._wallet_name)
                _load_success = True
            else:
                _load_success = False

        if _load_success:
            # get wallet data
            self._btc_address = _wallet_data['btc_address']
            self._ltc_address = _wallet_data['ltc_address']

            try:
                _btc_balance_confirmed = BTCScript.unspent(self._btc_address, self._user_btc_data)
                _ltc_balance_confirmed = LTCScript.unspent(self._ltc_address, self._user_ltc_data)
                _btc_balance_unconfirmed = BTCScript.unspent(self._btc_address, self._user_btc_data, confirmations = 0)
                _ltc_balance_unconfirmed = LTCScript.unspent(self._ltc_address, self._user_ltc_data, confirmations = 0)

                self._btc_balance_confirmed = int(_btc_balance_confirmed[2])
                self._ltc_balance_confirmed = int(_ltc_balance_confirmed[2])
                self._btc_balance_unconfirmed = int(_btc_balance_unconfirmed[2] - _btc_balance_confirmed[2])
                self._ltc_balance_unconfirmed = int(_ltc_balance_unconfirmed[2] - _ltc_balance_confirmed[2])

                # get utxos
                self._btc_utxos = _btc_balance_confirmed[0]
                self._ltc_utxos = _ltc_balance_confirmed[0]

                # add units and sumup
                if self._btc_balance_confirmed > 0:
                    self._btc_balance_confirmed_btc = round(float(self._btc_balance_confirmed / tannhauser['unit']), 8)
                else:
                    self._btc_balance_confirmed_btc = 0

                if self._btc_balance_unconfirmed > 0:
                    self._btc_balance_unconfirmed_btc = round(float(self._btc_balance_unconfirmed / tannhauser['unit']), 8)
                else:
                    self._btc_balance_unconfirmed_btc = 0

                if self._ltc_balance_confirmed > 0:
                    self._ltc_balance_confirmed_ltc = round(float(self._ltc_balance_confirmed / tannhauser['unit']), 8)
                else:
                    self._ltc_balance_confirmed_ltc = 0

                if self._ltc_balance_unconfirmed > 0:
                    self._ltc_balance_unconfirmed_ltc = round(float(self._ltc_balance_unconfirmed / tannhauser['unit']), 8)
                else:
                    self._ltc_balance_unconfirmed_ltc = 0

                _balances = [self._btc_balance_confirmed,
                                self._btc_balance_unconfirmed,
                                self._ltc_balance_confirmed,
                                self._ltc_balance_unconfirmed,
                                self._btc_balance_confirmed_btc,
                                self._btc_balance_unconfirmed_btc,
                                self._ltc_balance_confirmed_ltc,
                                self._ltc_balance_unconfirmed_ltc
                ]

                self.button1 = QPushButton("INITIATE SWAP")
                self.button1.setStyleSheet('color: #E5E5E5; background-color: darkgreen; font: bold; padding: 0.3em')
                self.button1.clicked.connect(self.init_swap)

                try:
                    if self._ping_server['type'] == 'server_online' and not self._ping_server['status']:
                        self.button1.setEnabled(False)
                    else:
                        pass
                except Exception as ex:
                    print(ex)

                self.button2 = QPushButton("CHECK SWAP")
                self.button2.setStyleSheet('color: #E5E5E5; background-color: darkcyan; font: bold; padding: 0.3em')
                self.button2.clicked.connect(self.recheck_swap)

                try:
                    if self._ping_server['type'] == 'server_online' and not self._ping_server['status']:
                        self.button2.setEnabled(False)
                    else:
                        pass
                except Exception as ex:
                    print(ex)

                self.button3 = QPushButton("MAIN")
                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button3.clicked.connect(self.main)

                self.button4 = QPushButton("EXIT")
                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button4.clicked.connect(lambda: self.close())

                layout = QGridLayout()
                layout.addWidget(Output(output_wallet = True, btc_wallet = self._btc_address, ltc_wallet = self._ltc_address, balances = _balances), 0, 0, 1, 0)
                layout.addWidget(self.button1, 1, 0)
                layout.addWidget(self.button2, 1, 1)
                layout.addWidget(self.button3, 1, 2)
                layout.addWidget(self.button4, 1, 3)

                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
            except Exception as ex:
                print(ex)
                self.ok_cancel()
        else:
            pass

    def load_wallet_dialog(self):
        _options = QFileDialog.Options()
        _options |= QFileDialog.DontUseNativeDialog
        wallet_name, _ = QFileDialog.getOpenFileName(self,"SELECT WALLET", f"{self._curr_path}/atomicswap/wallets","All Files (*);;Python Files (*.py)", options = _options)

        if wallet_name:
            return wallet_name
        else:
            return False

    def get_wallet_name(self):
        _wallet_filename, ok_pressed = QInputDialog.getText(self, "WALLET FILE","PLEASE ENTER THE NAME OF YOUR NEW WALLET:", QLineEdit.Normal, "")

        if ok_pressed:
            return _wallet_filename
        else:
            return False

    def faq(self):
        # output buttons
        self.output_main_buttons(False)

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(faq = True), 0, 0, 1, 0)
        layout.addWidget(self.button1, 1, 0)
        layout.addWidget(self.button2, 1, 1)
        layout.addWidget(self.button3, 1, 2)
        layout.addWidget(self.button4, 1, 3)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def init_swap(self):
        # collect user data
        self._direction = self.get_direction()

        if self._direction:
            if self._direction.startswith('B'):
                self._direction = 'btc'
            else:
                self._direction = 'ltc'

            self._amount_unit = self.get_amount()

            if self._amount_unit:
                # convert to sats
                self._amount = int(self._amount_unit * tannhauser['unit'])

                # init bond
                if self._direction == 'btc':
                    _amount_valid = True if self._btc_balance_confirmed >= self._amount else False
                else:
                    _amount_valid = True if self._ltc_balance_confirmed >= self._amount else False

                if _amount_valid:
                    #self.send_bond()
                    self.new_swap_data()
                else:
                    _fail_info = QMessageBox(self)
                    _fail_info.setWindowTitle("FAILED!")

                    if self._direction == 'btc':
                        _fail_info.setText(f"NOT ENOUGH AVAILABLE FUNDS ({self._btc_balance_confirmed:,} < {self._ping_server['btc_min']:,})")
                    else:
                        _fail_info.setText(f"NOT ENOUGH AVAILABLE FUNDS ({self._ltc_balance_confirmed:,} < {self._ping_server['ltc_min']:,})")

                    _fail_info.setStyleSheet('color: white; background-color: red; font: bold')
                    _button = _fail_info.exec()
            else:
                pass
        else:
            pass

    def get_direction(self):
        _options = ("BTC -> LTC", "LTC -> BTC")
        _direction , ok_pressed = QInputDialog.getItem(self, "Path","PLEASE ENTER THE DIRECTION OF YOUR SWAP:", _options, 0, False)

        if ok_pressed:
            return _direction
        else:
            return False

    def recheck_swap(self):
        try:
            self.check_swap(False)
            self.check_swap_status()
            self.start_loop()
        except Exception as ex:
            print(ex)

    def load_bond_data(self):
        # get swap token
        self._swap_token = self._swap_data['swap_token']

        # unhexlify hex
        _secret_hash = binascii.unhexlify(self._swap_data['secret_hex_bond'])

        if self._direction == 'btc':
            try:
                # compose redeem script
                _sender_address = self._handle_btc.get_clean_address(self._btc_address)
                _recipient_address = self._handle_btc.get_clean_address(self._swap_data['btc_bond_address'])
                self._btc_redeem_script = self._handle_btc.get_redeem_script(tannhauser['blocks_btc_bond_user'], _secret_hash, _sender_address, _recipient_address, self._user_btc_data)

                # import htlc address
                self._htlc_address = self._btc_redeem_script[2]
                BTCScript.import_address(self._htlc_address, self._user_btc_data)

                # get addressinfo
                _htlc_addr_info = BTCScript.get_addressinfo(self._htlc_address, self._user_btc_data)

                # get current fee per byte
                _fee_per_byte = BTCScript.get_fee(self._user_btc_data)
                _fee_per_byte = round(_fee_per_byte['fee_per_byte'], 8)
                _fee_per_byte = int(_fee_per_byte * 1e8)

                # get amounts
                self._swap_amount = int(self._amount - self._swap_data['btc_bond_amount'])
                self._bond_amount = int(self._swap_data['btc_bond_amount'])
                self._conter_amount = self._swap_data['ltc_server_amount']

                # get current blockheight
                _current_blockheight = BTCScript.blockcount(self._user_btc_data)

                # unlock wallet
                BTCScript.unlock_wallet(self._user_btc_data)

                # compose tx
                self._fund_tx = self._handle_btc.gen_fund_tx(tannhauser['btc_network'], _sender_address, self._htlc_address, self._bond_amount, self._user_btc_data, _fee_per_byte)
            except Exception as ex:
                print(ex)

            # output swap data
            self._refund_blockheight = self._btc_redeem_script[0]
            _fee = self._fund_tx[2]
            self._swap_amount_btc = round(float(self._swap_amount / tannhauser['unit']), 8)
            self._bond_amount_btc = round(float(self._bond_amount / tannhauser['unit']), 8)
            self._conter_amount_ltc = round(float(self._conter_amount / tannhauser['unit']), 8)

            _output_swap_data = [self._direction,
                            self._amount,
                            self._swap_amount,
                            self._bond_amount,
                            self._conter_amount,
                            _fee,
                            self._htlc_address,
                            self._refund_blockheight,
                            _current_blockheight,
                            self._amount_unit,
                            self._swap_amount_btc,
                            self._bond_amount_btc,
                            self._conter_amount_ltc
            ]

            # store the output
            self._output_swap_data = _output_swap_data

            # add missing buttons
            self.output_main_buttons(False)

            # output
            self.button1 = QPushButton("BACK")
            self.button1.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em;')
            self.button1.clicked.connect(self.init_swap)

            self.button2 = QPushButton("SEND")
            self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
            self.button2.clicked.connect(self.brdcst_transaction)

            layout = QGridLayout()
            layout.addWidget(Output(new_swap_data = True, swap_data = _output_swap_data), 0, 0, 1, 0)
            layout.addWidget(self.button1, 1, 0)
            layout.addWidget(self.button2, 1, 1)
            layout.addWidget(self.button3, 1, 2)
            layout.addWidget(self.button4, 1, 3)

            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
        else:
            try:
                # compose redeem script
                _sender_address = self._handle_ltc.get_clean_address(self._ltc_address)
                _recipient_address = self._handle_ltc.get_clean_address(self._swap_data['ltc_bond_address'])
                self._ltc_redeem_script = self._handle_ltc.get_redeem_script(tannhauser['blocks_ltc_bond_user'], _secret_hash, _sender_address, _recipient_address, self._user_ltc_data)

                # import htlc address
                self._htlc_address = self._ltc_redeem_script[2]
                LTCScript.import_address(self._htlc_address, self._user_ltc_data)

                # get addressinfo
                _htlc_addr_info = LTCScript.get_addressinfo(self._htlc_address, self._user_ltc_data)

                # get current fee per byte
                _fee_per_byte = LTCScript.get_fee(self._user_ltc_data)
                _fee_per_byte = round(_fee_per_byte['fee_per_byte'], 8)
                _fee_per_byte = int(_fee_per_byte * 1e8)

                # get amounts
                self._swap_amount = int(self._amount - self._swap_data['ltc_bond_amount'])
                self._bond_amount = int(self._swap_data['ltc_bond_amount'])
                self._conter_amount = self._swap_data['btc_server_amount']

                # get current blockheight
                _current_blockheight = LTCScript.blockcount(self._user_ltc_data)

                # unlock wallet
                LTCScript.unlock_wallet(self._user_ltc_data)

                # compose tx
                self._fund_tx = self._handle_ltc.gen_fund_tx(tannhauser['ltc_network'], _sender_address, self._htlc_address, self._bond_amount, self._user_ltc_data, _fee_per_byte)
            except Exception as ex:
                print(ex)

            # output swap data
            self._refund_blockheight = self._ltc_redeem_script[0]
            _fee = self._fund_tx[2]
            self._swap_amount_ltc = round(float(self._swap_amount / tannhauser['unit']), 8)
            self._bond_amount_ltc = round(float(self._bond_amount / tannhauser['unit']), 8)
            self._conter_amount_btc = round(float(self._conter_amount / tannhauser['unit']), 8)

            _output_swap_data = [self._direction,
                            self._amount,
                            self._swap_amount,
                            self._bond_amount,
                            self._conter_amount,
                            _fee,
                            self._htlc_address,
                            self._refund_blockheight,
                            _current_blockheight,
                            self._amount_unit,
                            self._swap_amount_ltc,
                            self._bond_amount_ltc,
                            self._conter_amount_btc
            ]

            # store the output
            self._output_swap_data = _output_swap_data

            # add missing buttons
            self.output_main_buttons(False)

            # output
            self.button1 = QPushButton("BACK")
            self.button1.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em;')
            self.button1.clicked.connect(self.init_swap)

            self.button2 = QPushButton("SEND")
            self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
            self.button2.clicked.connect(self.brdcst_transaction)

            layout = QGridLayout()
            layout.addWidget(Output(new_swap_data = True, swap_data = _output_swap_data), 0, 0, 1, 0)
            layout.addWidget(self.button1, 1, 0)
            layout.addWidget(self.button2, 1, 1)
            layout.addWidget(self.button3, 1, 2)
            layout.addWidget(self.button4, 1, 3)

            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)

    def brdcst_transaction(self):
        if self._direction == 'btc':
            try:
                if tannhauser['localhost']:
                    self._fund_txid = BTCScript.send_transaction(self._fund_tx[1], self._user_btc_data)
                else:
                    pass

                _success = True
            except Exception as ex:
                print(ex)
                _success = False

            # short cooldown
            time.sleep(0.2)

            # lock funds for swap
            if _success:
                #_lock_funds = utils.lock_utxos(self._direction, self._btc_address)
                _sbd = self.send_bond_data()
            else:
                pass
        else:
            try:
                if tannhauser['localhost']:
                    self._fund_txid = LTCScript.send_transaction(self._fund_tx[1], self._user_ltc_data)
                else:
                    pass

                _success = True
            except Exception as ex:
                print(ex)
                _success = False

            # short cooldown
            time.sleep(0.2)

            # lock funds for swap
            if _success:
                #_lock_funds = utils.lock_utxos(self._direction, self._ltc_address)
                _sbd = self.send_bond_data()
            else:
                pass

    def finalize_swap(self):
        # final output
        self.final_data_output()

        # save swap data
        _ssd = self.save_swap_data()

        if _ssd:
            # save transaction
            _htlc_address = str(self._htlc_address)

            if self._direction == 'btc':
                _save_bond_transaction = utils.save_bond(_ssd,
                                                                self._swap_token,
                                                                self._btc_address,
                                                                self._swap_data['btc_bond_address'],
                                                                _htlc_address,
                                                                self._refund_blockheight,
                                                                self._bond_amount,
                                                                self._fund_txid,
                                                                self._swap_data['secret_hex_bond'],
                                                                self._btc_redeem_script[1],
                                                                self._ltc_address,
                                                                self._swap_amount,
                                                                self._swap_data['ltc_server_amount']
                )
            else:
                _save_bond_transaction = utils.save_bond(_ssd,
                                                                self._swap_token,
                                                                self._ltc_address,
                                                                self._swap_data['ltc_bond_address'],
                                                                _htlc_address,
                                                                self._refund_blockheight,
                                                                self._bond_amount,
                                                                self._fund_txid,
                                                                self._swap_data['secret_hex_bond'],
                                                                self._ltc_redeem_script[1],
                                                                self._btc_address,
                                                                self._swap_amount,
                                                                self._swap_data['btc_server_amount']
                )

            # cooldown
            time.sleep(0.2)

            # load transaction
            self._load_bond_transaction = utils.load_bond(_ssd)

            # start loop
            self.check_swap()
            self.start_loop()
        else:
            pass

    def check_swap(self, load_data = True):
        if load_data:
            try:
                if self._csd:
                    pass
                else:
                    self._csd = False
            except Exception as ex:
                print(ex)
                self._csd = False
        else:
            # load swap
            _filename = self.load_swap_dialog()
            self._load_bond_transaction = utils.load_bond(_filename, True)
            self._swap_token = self._load_bond_transaction['swap_token']

            if tannhauser['net'] == 'testnet':
                self._direction = 'btc' if self._load_bond_transaction['htlc_address'].startswith('2') else 'ltc'
            else:
                self._direction = 'btc' if self._load_bond_transaction['htlc_address'].startswith('3') else 'ltc'

            self._csd = False

        # set counter
        try:
            self._loop_counter += 5
            if self._loop_counter >= 100:
                self._loop_counter = 5
        except Exception as ex:
            print(ex)
            self._loop_counter = 5

        # progress bar
        self.pbar = QProgressBar(self)

        if self._csd:
            if self._csd['status'] == 0:
                self.pbar.setFormat('WAITING FOR CONFIRMATION ...')
                self.pbar.setValue(self._loop_counter)
                self._show_buttons = False

                self.button2 = QPushButton("PAUSE")
                self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                self.button2.clicked.connect(self.pause_hint)

                self.button3 = QPushButton("MAIN")
                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button3.clicked.connect(self.main)

                self.button4 = QPushButton("EXIT")
                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button4.clicked.connect(lambda: self.close())

                _res = {
                    'load_bond_transaction': self._load_bond_transaction,
                    'check_server_data': self._csd,
                }

                layout = QGridLayout()
                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                layout.addWidget(self.pbar, 1, 0, 1, 0)
                layout.addWidget(self.button2, 2, 0)

                if self._show_buttons:
                    layout.addWidget(self.button3, 2, 1)
                    layout.addWidget(self.button4, 2, 2)
                else:
                    pass

                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
            elif self._csd['status'] == 1:
                self.pbar.setFormat('TANNHAUSER PREPARING FUNDING TRANSACTION ...')
                self.pbar.setValue(self._loop_counter)
                self._show_buttons = False

                self.button2 = QPushButton("PAUSE")
                self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                self.button2.clicked.connect(self.pause_hint)

                self.button3 = QPushButton("MAIN")
                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button3.clicked.connect(self.main)

                self.button4 = QPushButton("EXIT")
                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button4.clicked.connect(lambda: self.close())

                _res = {
                    'load_bond_transaction': self._load_bond_transaction,
                    'check_server_data': self._csd,
                }

                layout = QGridLayout()
                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                layout.addWidget(self.pbar, 1, 0, 1, 0)
                layout.addWidget(self.button2, 2, 0)

                if self._show_buttons:
                    layout.addWidget(self.button3, 2, 1)
                    layout.addWidget(self.button4, 2, 2)
                else:
                    pass

                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
            elif self._csd['status'] == 2:
                try:
                    # get transaction info
                    if self._direction == 'btc':
                        _transaction_info = LTCScript.get_rawtransaction(self._csd['funding_txid'], self._user_ltc_data, True)
                    else:
                        _transaction_info = BTCScript.get_rawtransaction(self._csd['funding_txid'], self._user_btc_data, True)

                    _valid_tx = True
                except Exception as ex:
                    print(ex)
                    _valid_tx = False
                    _transaction_info = False

                if _transaction_info:
                    try:
                        if self._direction == 'btc':
                            # import htlc address
                            LTCScript.import_address(self._csd['htlc_address'], self._user_ltc_data)

                            # get addressinfo
                            _addr_info = LTCScript.get_addressinfo(self._csd['htlc_address'], self._user_ltc_data)

                            # get balance
                            for _i in _transaction_info['vout']:
                                if self._csd['htlc_address'] in _i['scriptPubKey']['addresses']:
                                    try:
                                        if _transaction_info['confirmations'] >= 1:
                                            _htlc_balance_server = int(float(_i['value']) * 1e8)
                                            _confirmations = _transaction_info['confirmations']
                                            _confirmed = True
                                        else:
                                            _htlc_balance_server = 0
                                            _confirmations = 0
                                            _confirmed = False
                                    except Exception as ex:
                                        print(ex)
                                        _htlc_balance_server = 0
                                        _confirmations = 0
                                        _confirmed = False

                                    break
                                else:
                                    _htlc_balance_server = 0
                                    _confirmations = 0
                                    _confirmed = False

                            # get real diff
                            _real_balance_diff = _htlc_balance_server - self._load_bond_transaction['server_amount']

                            # get amount gap
                            if _htlc_balance_server > 0:
                                _balance_gap = int(self._load_bond_transaction['server_amount'] / tannhauser['gap_factor'])
                                _balance_min = int(self._load_bond_transaction['server_amount'] - _balance_gap)
                                _balance_max = int(self._load_bond_transaction['server_amount'] + _balance_gap)

                                if _htlc_balance_server in range(_balance_min, _balance_max) and _confirmed:
                                    _valid_htlc_balance = True
                                    _refund = False
                                elif _htlc_balance_server not in range(_balance_min, _balance_max) and _confirmed:
                                    _valid_htlc_balance = False
                                    _refund = True
                                else:
                                    _valid_htlc_balance = False
                                    _refund = False
                            else:
                                _valid_htlc_balance = False
                                _refund = False

                            if _valid_htlc_balance and not _refund:
                                # get current fee per byte
                                _fee_per_byte = BTCScript.get_fee(self._user_btc_data)
                                _fee_per_byte = round(_fee_per_byte['fee_per_byte'], 8)
                                _fee_per_byte = int(_fee_per_byte * 1e8)

                                # get swap data
                                _secret_hash_hex = self._csd['secret_hash_hex']
                                _btc_amount = self._csd['conter_amount']

                                # unlock funds 4 swap
                                #_unlock_funds = utils.unlock_utxos('btc', self._csd['user_send_address'])

                                # check balance of btc funding addresses
                                _bal = BTCScript.unspent(self._csd['user_send_address'], self._user_btc_data)
                                _balance_user = _bal[2]

                                if (_balance_user - (_fee_per_byte + 1000)) > _btc_amount:
                                    _valid_amount = True
                                else:
                                    _valid_amount = False

                                if _valid_amount:
                                    # unhexlify hex
                                    _secret_hash = binascii.unhexlify(_secret_hash_hex)

                                    # compose redeem script
                                    _sender_address = self._handle_btc.get_clean_address(self._csd['user_send_address'])
                                    _recipient_address = self._handle_btc.get_clean_address(self._csd['server_claim_address'])
                                    self._btc_redeem_script = self._handle_btc.get_redeem_script(tannhauser['blocks_btc_user'], _secret_hash, _sender_address, _recipient_address, self._user_btc_data)

                                    # import htlc address
                                    BTCScript.import_address(self._btc_redeem_script[2], self._user_btc_data)

                                    # get addressinfo
                                    _btc_addr_info = BTCScript.get_addressinfo(self._btc_redeem_script[2], self._user_btc_data)

                                    # unlock wallet
                                    BTCScript.unlock_wallet(self._user_btc_data)

                                    # compose tx
                                    _btc_fund_tx = self._handle_btc.gen_fund_tx(tannhauser['btc_network'], _sender_address, self._btc_redeem_script[2], _btc_amount, self._user_btc_data, _fee_per_byte)

                                    # send funds
                                    self._btc_send_fund = BTCScript.send_transaction(_btc_fund_tx[1], self._user_btc_data)

                                    # save transaction
                                    _filename = f"User_{self._load_bond_transaction['swap_token']}"
                                    _htlc_address = str(self._btc_redeem_script[2])
                                    _sender_funding_address = self._csd['user_send_address']
                                    _server_claim_address = self._csd['server_claim_address']
                                    _refund_blockheight = self._btc_redeem_script[0]

                                    _btc_save_swap_transaction = utils.save_user_swap(_filename,
                                                                                    _sender_funding_address,
                                                                                    _server_claim_address,
                                                                                    _htlc_address,
                                                                                    self._btc_send_fund,
                                                                                    _btc_amount,
                                                                                    _refund_blockheight,
                                                                                    _secret_hash_hex
                                    )

                                    # short cooldown
                                    time.sleep(0.2)

                                    # send swap data to server
                                    _ssd = self.send_swap_data()
                                else:
                                    pass
                            elif not _valid_htlc_balance and _refund:
                                if self._load_bond_transaction['finalized']:
                                    # stop loop
                                    self.stop_loop()

                                    # set progress bar
                                    self.pbar.setFormat(f"BOND REFUND DONE!")
                                    self.pbar.setValue(100)
                                    self._show_buttons = True
                                else:
                                    # get current blockheight
                                    if self._direction == 'btc':
                                        _curr_blockheight = BTCScript.blockcount(self._user_btc_data)
                                    else:
                                        _curr_blockheight = LTCScript.blockcount(self._user_ltc_data)

                                    # get block diff
                                    _diff = self._load_bond_transaction['refund_blockheight'] - _curr_blockheight

                                    if _diff <= 0:
                                        # stop loop
                                        self.stop_loop()

                                        # make refund
                                        _refund_swap = self.refund(True)

                                        # set progress bar
                                        self.pbar.setFormat(f"BOND REFUND DONE!")
                                        self.pbar.setValue(100)
                                        self._show_buttons = True
                                    else:
                                        # set progress bar
                                        self.pbar.setFormat(f"BOND REFUND POSSIBLE IN {_diff} BLOCKS!")
                                        self.pbar.setValue(self._loop_counter)
                                        self._show_buttons = False

                                        self.button2 = QPushButton("PAUSE")
                                        self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                                        self.button2.clicked.connect(self.main)

                                # set progress bar
                                self.button3 = QPushButton("MAIN")
                                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                                self.button3.clicked.connect(self.main)

                                self.button4 = QPushButton("EXIT")
                                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                                self.button4.clicked.connect(lambda: self.close())

                                _res = {
                                    'load_bond_transaction': self._load_bond_transaction,
                                    'check_server_data': self._csd,
                                }

                                layout = QGridLayout()
                                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                                layout.addWidget(self.pbar, 1, 0, 1, 0)

                                if self._show_buttons:
                                    layout.addWidget(self.button3, 2, 0)
                                    layout.addWidget(self.button4, 2, 1)
                                else:
                                    layout.addWidget(self.button2, 2, 0)

                                widget = QWidget()
                                widget.setLayout(layout)
                                self.setCentralWidget(widget)
                            else:
                                #status
                                self.pbar.setFormat('FUNDING TRANSACTION DONE! WAITING FOR CONFIRMATION ...')

                                self.pbar.setValue(self._loop_counter)
                                self._show_buttons = False

                                self.button2 = QPushButton("PAUSE")
                                self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                                self.button2.clicked.connect(self.pause_hint)

                                self.button3 = QPushButton("MAIN")
                                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                                self.button3.clicked.connect(self.main)

                                self.button4 = QPushButton("EXIT")
                                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                                self.button4.clicked.connect(lambda: self.close())

                                _res = {
                                    'load_bond_transaction': self._load_bond_transaction,
                                    'check_server_data': self._csd,
                                }

                                layout = QGridLayout()
                                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                                layout.addWidget(self.pbar, 1, 0, 1, 0)
                                layout.addWidget(self.button2, 2, 0)

                                if self._show_buttons:
                                    layout.addWidget(self.button3, 2, 1)
                                    layout.addWidget(self.button4, 2, 2)
                                else:
                                    pass

                                widget = QWidget()
                                widget.setLayout(layout)
                                self.setCentralWidget(widget)

                        else:
                            # import htlc address
                            BTCScript.import_address(self._csd['htlc_address'], self._user_btc_data)

                            # get addressinfo
                            _addr_info = BTCScript.get_addressinfo(self._csd['htlc_address'], self._user_btc_data)

                            # get balance
                            for _i in _transaction_info['vout']:
                                if self._csd['htlc_address'] in _i['scriptPubKey']['address']:
                                    try:
                                        if _transaction_info['confirmations'] >= 1:
                                            _htlc_balance_server = int(float(_i['value']) * 1e8)
                                            _confirmations = _transaction_info['confirmations']
                                            _confirmed = True
                                        else:
                                            _htlc_balance_server = 0
                                            _confirmations = 0
                                            _confirmed = False
                                    except Exception as ex:
                                        print(ex)
                                        _htlc_balance_server = 0
                                        _confirmations = 0
                                        _confirmed = False

                                    break
                                else:
                                    _htlc_balance_server = 0
                                    _confirmations = 0
                                    _confirmed = False

                            # get real diff
                            _real_balance_diff = _htlc_balance_server - self._load_bond_transaction['server_amount']

                            # get amount gap
                            if _htlc_balance_server > 0:
                                _balance_gap = int(self._load_bond_transaction['server_amount'] / tannhauser['gap_factor'])
                                _balance_min = int(self._load_bond_transaction['server_amount'] - _balance_gap)
                                _balance_max = int(self._load_bond_transaction['server_amount'] + _balance_gap)

                                if _htlc_balance_server in range(_balance_min, _balance_max) and _confirmed:
                                    _valid_htlc_balance = True
                                    _refund = False
                                elif _htlc_balance_server not in range(_balance_min, _balance_max) and _confirmed:
                                    _valid_htlc_balance = False
                                    _refund = True
                                else:
                                    _valid_htlc_balance = False
                                    _refund = False
                            else:
                                _valid_htlc_balance = False
                                _refund = False

                            if _valid_htlc_balance and not _refund:
                                # get current fee per byte
                                _fee_per_byte = LTCScript.get_fee(self._user_ltc_data)
                                _fee_per_byte = round(_fee_per_byte['fee_per_byte'], 8)
                                _fee_per_byte = int(_fee_per_byte * 1e8)

                                # get swap data
                                _secret_hash_hex = self._csd['secret_hash_hex']
                                _ltc_amount = self._csd['conter_amount']

                                # unlock funds 4 swap
                                #_unlock_funds = utils.unlock_utxos('ltc', self._csd['user_send_address'])

                                # check balance of ltc funding addresses
                                _bal = LTCScript.unspent(self._csd['user_send_address'], self._user_ltc_data)
                                _balance_user = _bal[2]

                                if (_balance_user - (_fee_per_byte + 1000)) > _ltc_amount:
                                    _valid_amount = True
                                else:
                                    _valid_amount = False

                                if _valid_amount:
                                    # unhexlify hex
                                    _secret_hash = binascii.unhexlify(_secret_hash_hex)

                                    # compose redeem script
                                    _sender_address = self._handle_ltc.get_clean_address(self._csd['user_send_address'])
                                    _recipient_address = self._handle_ltc.get_clean_address(self._csd['server_claim_address'])
                                    self._ltc_redeem_script = self._handle_ltc.get_redeem_script(tannhauser['blocks_ltc_user'], _secret_hash, _sender_address, _recipient_address, self._user_ltc_data)

                                    # import htlc address
                                    LTCScript.import_address(self._ltc_redeem_script[2], self._user_ltc_data)

                                    # get addressinfo
                                    _ltc_addr_info = LTCScript.get_addressinfo(self._ltc_redeem_script[2], self._user_ltc_data)

                                    # unlock wallet
                                    LTCScript.unlock_wallet(self._user_ltc_data)

                                    # compose tx
                                    _ltc_fund_tx = self._handle_ltc.gen_fund_tx(tannhauser['ltc_network'], _sender_address, self._ltc_redeem_script[2], _ltc_amount, self._user_ltc_data, _fee_per_byte)

                                    # send funds
                                    self._ltc_send_fund = LTCScript.send_transaction(_ltc_fund_tx[1], self._user_ltc_data)

                                    # save transaction
                                    _filename = f"User_{self._load_bond_transaction['swap_token']}"
                                    _htlc_address = str(self._ltc_redeem_script[2])
                                    _sender_funding_address = self._csd['user_send_address']
                                    _server_claim_address = self._csd['server_claim_address']
                                    _refund_blockheight = self._ltc_redeem_script[0]

                                    _ltc_save_swap_transaction = utils.save_user_swap(_filename,
                                                                                    _sender_funding_address,
                                                                                    _server_claim_address,
                                                                                    _htlc_address,
                                                                                    self._ltc_send_fund,
                                                                                    _ltc_amount,
                                                                                    _refund_blockheight,
                                                                                    _secret_hash_hex
                                    )

                                    # short cooldown
                                    time.sleep(0.2)

                                    # send swap data to server
                                    _ssd = self.send_swap_data()
                                else:
                                    pass
                            elif not _valid_htlc_balance and _refund:
                                if self._load_bond_transaction['finalized']:
                                    # stop loop
                                    self.stop_loop()

                                    # set progress bar
                                    self.pbar.setFormat(f"BOND REFUND DONE!")
                                    self.pbar.setValue(100)
                                    self._show_buttons = True
                                else:
                                    # get current blockheight
                                    if self._direction == 'btc':
                                        _curr_blockheight = BTCScript.blockcount(self._user_btc_data)
                                    else:
                                        _curr_blockheight = LTCScript.blockcount(self._user_ltc_data)

                                    # get block diff
                                    _diff = self._load_bond_transaction['refund_blockheight'] - _curr_blockheight

                                    if _diff <= 0:
                                        # stop loop
                                        self.stop_loop()

                                        # make refund
                                        _refund_swap = self.refund(True)

                                        # set progress bar
                                        self.pbar.setFormat(f"BOND REFUND DONE!")
                                        self.pbar.setValue(100)
                                        self._show_buttons = True
                                    else:
                                        # set progress bar
                                        self.pbar.setFormat(f"BOND REFUND POSSIBLE IN {_diff} BLOCKS!")
                                        self.pbar.setValue(self._loop_counter)
                                        self._show_buttons = False

                                        self.button2 = QPushButton("PAUSE")
                                        self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                                        self.button2.clicked.connect(self.main)

                                # set progress bar
                                self.button3 = QPushButton("MAIN")
                                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                                self.button3.clicked.connect(self.main)

                                self.button4 = QPushButton("EXIT")
                                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                                self.button4.clicked.connect(lambda: self.close())

                                _res = {
                                    'load_bond_transaction': self._load_bond_transaction,
                                    'check_server_data': self._csd,
                                }

                                layout = QGridLayout()
                                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                                layout.addWidget(self.pbar, 1, 0, 1, 0)

                                if self._show_buttons:
                                    layout.addWidget(self.button3, 2, 0)
                                    layout.addWidget(self.button4, 2, 1)
                                else:
                                    layout.addWidget(self.button2, 2, 0)

                                widget = QWidget()
                                widget.setLayout(layout)
                                self.setCentralWidget(widget)
                            else:
                                #status
                                self.pbar.setFormat('FUNDING TRANSACTION DONE! WAITING FOR CONFIRMATION ...')

                                self.pbar.setValue(self._loop_counter)
                                self._show_buttons = False

                                self.button2 = QPushButton("PAUSE")
                                self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                                self.button2.clicked.connect(self.pause_hint)

                                self.button3 = QPushButton("MAIN")
                                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                                self.button3.clicked.connect(self.main)

                                self.button4 = QPushButton("EXIT")
                                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                                self.button4.clicked.connect(lambda: self.close())

                                _res = {
                                    'load_bond_transaction': self._load_bond_transaction,
                                    'check_server_data': self._csd,
                                }

                                layout = QGridLayout()
                                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                                layout.addWidget(self.pbar, 1, 0, 1, 0)
                                layout.addWidget(self.button2, 2, 0)

                                if self._show_buttons:
                                    layout.addWidget(self.button3, 2, 1)
                                    layout.addWidget(self.button4, 2, 2)
                                else:
                                    pass

                                widget = QWidget()
                                widget.setLayout(layout)
                                self.setCentralWidget(widget)

                    except Exception as ex:
                        print(ex)
                else:
                    pass
            elif self._csd['status'] == 3:
                try:
                    # load transaction
                    _filename = f"User_{self._load_bond_transaction['swap_token']}"
                    self._load_swap_transaction = utils.load_user_swap(_filename)
                except Exception as ex:
                    print(ex)

                self.pbar.setFormat('TANNHAUSER WAITING FOR USER FUNDING TX CONFIRMATION ...')
                self.pbar.setValue(self._loop_counter)
                self._show_buttons = False

                self.button2 = QPushButton("PAUSE")
                self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                self.button2.clicked.connect(self.main)

                self.button3 = QPushButton("MAIN")
                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button3.clicked.connect(self.main)

                self.button4 = QPushButton("EXIT")
                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button4.clicked.connect(lambda: self.close())

                _res = {
                    'load_bond_transaction': self._load_bond_transaction,
                    'check_server_data': self._csd,
                    'load_swap_transaction': self._load_swap_transaction
                }

                layout = QGridLayout()
                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                layout.addWidget(self.pbar, 1, 0, 1, 0)
                layout.addWidget(self.button2, 2, 0)

                if self._show_buttons:
                    layout.addWidget(self.button3, 2, 1)
                    layout.addWidget(self.button4, 2, 2)
                else:
                    pass

                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
            elif self._csd['status'] in [4, 6]:
                try:
                    # load transaction
                    _filename = f"User_{self._load_bond_transaction['swap_token']}"
                    self._load_swap_transaction = utils.load_user_swap(_filename)
                except Exception as ex:
                    print(ex)

                if self._load_bond_transaction['finalized']:
                    # stop loop
                    self.stop_loop()

                    ## set progress bar
                    self.pbar.setFormat(f"YOU LOST YOUR BOND! SWAP REFUND DONE!")
                    self.pbar.setValue(100)
                    self._show_buttons = True

                    try:
                        _res = {
                            'load_bond_transaction': self._load_bond_transaction,
                            'check_server_data': self._csd,
                            'load_swap_transaction': self._load_swap_transaction
                        }

                    except Exception as ex:
                        print(ex)

                        _res = {
                            'load_bond_transaction': self._load_bond_transaction,
                            'check_server_data': self._csd,
                        }
                else:
                    try:
                        if self._direction == 'btc':
                            _curr_blockheight = BTCScript.blockcount(self._user_btc_data)

                            # get block diff
                            _diff = self._load_swap_transaction['refund_blockheight'] - _curr_blockheight

                            if _diff <= 0:
                                # stop loop
                                self.stop_loop()

                                # make refund
                                _refund_swap = self.refund()

                                # set progress bar
                                self.pbar.setFormat(f"YOU LOST YOUR BOND! SWAP REFUND DONE!")
                                self.pbar.setValue(100)
                                self._show_buttons = True
                            else:
                                # set progress bar
                                self.pbar.setFormat(f"YOU LOST YOUR BOND! SWAP REFUND POSSIBLE IN {_diff} BLOCKS!")
                                self.pbar.setValue(self._loop_counter)
                                self._show_buttons = False

                            _res = {
                                'load_bond_transaction': self._load_bond_transaction,
                                'check_server_data': self._csd,
                                'load_swap_transaction': self._load_swap_transaction
                            }
                        else:
                            _curr_blockheight = LTCScript.blockcount(self._user_ltc_data)

                            # get block diff
                            _diff = self._load_swap_transaction['refund_blockheight'] - _curr_blockheight

                            if _diff <= 0:
                                # stop loop
                                self.stop_loop()

                                # make refund
                                _refund_swap = self.refund()

                                # set progress bar
                                self.pbar.setFormat(f"YOU LOST YOUR BOND! SWAP REFUND DONE!")
                                self.pbar.setValue(100)
                                self._show_buttons = True
                            else:
                                # set progress bar
                                self.pbar.setFormat(f"YOU LOST YOUR BOND! SWAP REFUND POSSIBLE IN {_diff} BLOCKS!")
                                self.pbar.setValue(self._loop_counter)
                                self._show_buttons = False

                            _res = {
                                'load_bond_transaction': self._load_bond_transaction,
                                'check_server_data': self._csd,
                                'load_swap_transaction': self._load_swap_transaction
                            }
                    except Exception as ex:
                        print(ex)

                        # stop loop
                        self.stop_loop()

                        self.pbar.setFormat(f"YOU LOST YOUR BOND! NO SWAP REFUND POSSIBLE!")
                        self.pbar.setValue(100)
                        self._show_buttons = True

                        _res = {
                            'load_bond_transaction': self._load_bond_transaction,
                            'check_server_data': self._csd,
                        }

                self.button2 = QPushButton("PAUSE")
                self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                self.button2.clicked.connect(self.main)

                self.button3 = QPushButton("MAIN")
                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button3.clicked.connect(self.main)

                self.button4 = QPushButton("EXIT")
                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button4.clicked.connect(lambda: self.close())

                layout = QGridLayout()
                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                layout.addWidget(self.pbar, 1, 0, 1, 0)

                if self._show_buttons:
                    layout.addWidget(self.button3, 2, 0)
                    layout.addWidget(self.button4, 2, 1)
                else:
                    layout.addWidget(self.button2, 2, 0)


                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
            elif self._csd['status'] == 5:
                try:
                    # load transaction
                    _filename = f"User_{self._load_bond_transaction['swap_token']}"
                    self._load_swap_transaction = utils.load_user_swap(_filename)
                except Exception as ex:
                    print(ex)

                self.pbar.setFormat('TANNHAUSER PREPARING WITHDRAW ...')
                self.pbar.setValue(self._loop_counter)
                self._show_buttons = False

                self.button2 = QPushButton("PAUSE")
                self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                self.button2.clicked.connect(self.main)

                self.button3 = QPushButton("MAIN")
                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button3.clicked.connect(self.main)

                self.button4 = QPushButton("EXIT")
                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button4.clicked.connect(lambda: self.close())

                _res = {
                    'load_bond_transaction': self._load_bond_transaction,
                    'check_server_data': self._csd,
                    'load_swap_transaction': self._load_swap_transaction
                }

                layout = QGridLayout()
                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                layout.addWidget(self.pbar, 1, 0, 1, 0)
                layout.addWidget(self.button2, 2, 0)

                if self._show_buttons:
                    layout.addWidget(self.button3, 2, 1)
                    layout.addWidget(self.button4, 2, 2)
                else:
                    pass

                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
            elif self._csd['status'] == 7:
                if self._load_bond_transaction['finalized']:
                    pass
                else:
                    try:
                        # get transaction info
                        if self._direction == 'btc':
                            _transaction_info = LTCScript.get_rawtransaction(self._csd['funding_txid'], self._user_ltc_data, True)
                        else:
                            _transaction_info = BTCScript.get_rawtransaction(self._csd['funding_txid'], self._user_btc_data, True)

                        _valid_tx = True
                    except Exception as ex:
                        print(ex)
                        _valid_tx = False
                        _transaction_info = False

                    if _transaction_info:
                        try:
                            if self._direction == 'btc':
                                # get secret from tx
                                _secret = self._handle_btc.get_secret(self._csd['server_claim_txid'], self._user_btc_data)
                                _secret_bool = True if _secret != False else False

                                # get current fee per byte
                                _fee_per_byte = LTCScript.get_fee(self._user_ltc_data)
                                _fee_per_byte = round(_fee_per_byte['fee_per_byte'], 8)
                                _fee_per_byte = int(_fee_per_byte * 1e8)

                                # unlock wallets
                                LTCScript.unlock_wallet(self._user_ltc_data)

                                # get address data
                                _sender_address = self._handle_ltc.get_clean_address(self._csd['server_address'])
                                _recipient_address = self._handle_ltc.get_clean_address(self._csd['user_address'])
                                _recipient_privkey = LTCScript.get_privkey(self._csd['user_address'], self._user_ltc_data)

                                # get tx data
                                for _i in _transaction_info['vout']:
                                    if self._csd['htlc_address'] in _i['scriptPubKey']['addresses']:
                                        _htlc_balance = int(float(_i['value']) * 1e8)
                                        _vout = _i['n']
                                        break
                                    else:
                                        _htlc_balance = 0
                                        _vout = 0

                                # import htlc address
                                LTCScript.import_address(self._csd['htlc_address'], self._user_ltc_data)

                                # get addressinfo
                                _addr_info = LTCScript.get_addressinfo(self._csd['htlc_address'], self._user_ltc_data)

                                # get amount gap
                                _balance_gap = int(_htlc_balance / tannhauser['gap_factor'])
                                _balance_min = int(_htlc_balance - _balance_gap)
                                _balance_max = int(_htlc_balance + _balance_gap)
                                _valid_htlc_balance = True if _htlc_balance in range(_balance_min, _balance_max) else False

                                if _valid_htlc_balance:
                                    # generate preimage from secret
                                    _h_preimage = self._handle_ltc.gen_preimage(_secret)

                                    # validate redeem script
                                    _ltc_redeem_script = self._handle_ltc.get_redeem_script(self._csd['refund_blockheight'], _h_preimage[1], _sender_address, _recipient_address, self._user_ltc_data, True)

                                    # generate claim tx
                                    _ltc_claim = self._handle_ltc.claim(self._csd['funding_txid'], _vout, _htlc_balance, _fee_per_byte, _recipient_address, _ltc_redeem_script[0], _ltc_redeem_script[3], _recipient_privkey, _h_preimage[0], self._user_ltc_data)

                                    # send funds
                                    _send_claim = LTCScript.send_transaction(_ltc_claim[0], self._user_ltc_data)

                                    # save transaction
                                    self._load_bond_transaction['finalized'] = True
                                    _save_bond_transaction = utils.save_bond(self._load_bond_transaction['filename'],
                                                                                    self._load_bond_transaction['swap_token'],
                                                                                    self._load_bond_transaction['sender_address'],
                                                                                    self._load_bond_transaction['server_address'],
                                                                                    self._load_bond_transaction['htlc_address'],
                                                                                    self._load_bond_transaction['refund_blockheight'],
                                                                                    self._load_bond_transaction['amount'],
                                                                                    self._load_bond_transaction['txid'],
                                                                                    self._load_bond_transaction['secret_hash_hex'],
                                                                                    self._load_bond_transaction['redeem_script'],
                                                                                    self._load_bond_transaction['conter_address'],
                                                                                    self._load_bond_transaction['swap_amount'],
                                                                                    self._load_bond_transaction['server_amount'],
                                                                                    self._load_bond_transaction['finalized'],
                                    )
                                else:
                                    pass
                            else:
                                # get secret from tx
                                _secret = self._handle_ltc.get_secret(self._csd['server_claim_txid'], self._user_ltc_data)
                                _secret_bool = True if _secret != False else False

                                # get current fee per byte
                                _fee_per_byte = BTCScript.get_fee(self._user_btc_data)
                                _fee_per_byte = round(_fee_per_byte['fee_per_byte'], 8)
                                _fee_per_byte = int(_fee_per_byte * 1e8)

                                # unlock wallets
                                BTCScript.unlock_wallet(self._user_btc_data)

                                # get address data
                                _sender_address = self._handle_btc.get_clean_address(self._csd['server_address'])
                                _recipient_address = self._handle_btc.get_clean_address(self._csd['user_address'])
                                _recipient_privkey = BTCScript.get_privkey(self._csd['user_address'], self._user_btc_data)

                                # get tx data
                                for _i in _transaction_info['vout']:
                                    if self._csd['htlc_address'] in _i['scriptPubKey']['address']:
                                        _htlc_balance = int(float(_i['value']) * 1e8)
                                        _vout = _i['n']
                                        break
                                    else:
                                        _htlc_balance = 0
                                        _vout = 0

                                # import htlc address
                                BTCScript.import_address(self._csd['htlc_address'], self._user_btc_data)

                                # get addressinfo
                                _addr_info = BTCScript.get_addressinfo(self._csd['htlc_address'], self._user_btc_data)

                                # get amount gap
                                _balance_gap = int(_htlc_balance / tannhauser['gap_factor'])
                                _balance_min = int(_htlc_balance - _balance_gap)
                                _balance_max = int(_htlc_balance + _balance_gap)
                                _valid_htlc_balance = True if _htlc_balance in range(_balance_min, _balance_max) else False

                                if _valid_htlc_balance:
                                    # generate preimage from secret
                                    _h_preimage = self._handle_btc.gen_preimage(_secret)

                                    # validate redeem script
                                    _btc_redeem_script = self._handle_btc.get_redeem_script(self._csd['refund_blockheight'], _h_preimage[1], _sender_address, _recipient_address, self._user_btc_data, True)

                                    # generate claim tx
                                    _btc_claim = self._handle_btc.claim(self._csd['funding_txid'], _vout, _htlc_balance, _fee_per_byte, _recipient_address, _btc_redeem_script[0], _btc_redeem_script[3], _recipient_privkey, _h_preimage[0], self._user_btc_data)

                                    # send funds
                                    _send_claim = BTCScript.send_transaction(_btc_claim[0], self._user_btc_data)

                                    # save transaction
                                    self._load_bond_transaction['finalized'] = True
                                    _save_bond_transaction = utils.save_bond(self._load_bond_transaction['filename'],
                                                                                    self._load_bond_transaction['swap_token'],
                                                                                    self._load_bond_transaction['sender_address'],
                                                                                    self._load_bond_transaction['server_address'],
                                                                                    self._load_bond_transaction['htlc_address'],
                                                                                    self._load_bond_transaction['refund_blockheight'],
                                                                                    self._load_bond_transaction['amount'],
                                                                                    self._load_bond_transaction['txid'],
                                                                                    self._load_bond_transaction['secret_hash_hex'],
                                                                                    self._load_bond_transaction['redeem_script'],
                                                                                    self._load_bond_transaction['conter_address'],
                                                                                    self._load_bond_transaction['swap_amount'],
                                                                                    self._load_bond_transaction['server_amount'],
                                                                                    self._load_bond_transaction['finalized'],
                                    )
                                else:
                                    pass
                        except Exception as ex:
                            print(ex)
                    else:
                        pass

                # stop loop
                self.stop_loop()

                try:
                    # load transaction
                    _filename = f"User_{self._load_bond_transaction['swap_token']}"
                    self._load_swap_transaction = utils.load_user_swap(_filename)
                except Exception as ex:
                    print(ex)

                self.pbar.setFormat('SWAP SUCCESSFUL!')
                self.pbar.setValue(100)
                self._show_buttons = True

                self.button3 = QPushButton("MAIN")
                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button3.clicked.connect(self.main)

                self.button4 = QPushButton("EXIT")
                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button4.clicked.connect(lambda: self.close())

                _res = {
                    'load_bond_transaction': self._load_bond_transaction,
                    'check_server_data': self._csd,
                    'load_swap_transaction': self._load_swap_transaction
                }

                layout = QGridLayout()
                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                layout.addWidget(self.pbar, 1, 0, 1, 0)

                if self._show_buttons:
                    layout.addWidget(self.button3, 2, 0)
                    layout.addWidget(self.button4, 2, 1)
                else:
                    pass

                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
            elif self._csd['status'] == 99:
                if self._load_bond_transaction['finalized']:
                    # stop loop
                    self.stop_loop()

                    # set progress bar
                    self.pbar.setFormat(f"BOND REFUND DONE!")
                    self.pbar.setValue(100)
                    self._show_buttons = True
                else:
                    # get current blockheight
                    if self._direction == 'btc':
                        _curr_blockheight = BTCScript.blockcount(self._user_btc_data)
                    else:
                        _curr_blockheight = LTCScript.blockcount(self._user_ltc_data)

                    # get block diff
                    _diff = self._load_bond_transaction['refund_blockheight'] - _curr_blockheight

                    if _diff <= 0:
                        # stop loop
                        self.stop_loop()

                        # make refund
                        _refund_swap = self.refund(True)

                        # set progress bar
                        self.pbar.setFormat(f"BOND REFUND DONE!")
                        self.pbar.setValue(100)
                        self._show_buttons = True
                    else:
                        # set progress bar
                        self.pbar.setFormat(f"BOND REFUND POSSIBLE IN {_diff} BLOCKS!")
                        self.pbar.setValue(self._loop_counter)
                        self._show_buttons = False

                        self.button2 = QPushButton("PAUSE")
                        self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
                        self.button2.clicked.connect(self.main)

                # set progress bar
                self.button3 = QPushButton("MAIN")
                self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button3.clicked.connect(self.main)

                self.button4 = QPushButton("EXIT")
                self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
                self.button4.clicked.connect(lambda: self.close())

                _res = {
                    'load_bond_transaction': self._load_bond_transaction,
                    'check_server_data': self._csd,
                }

                layout = QGridLayout()
                layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
                layout.addWidget(self.pbar, 1, 0, 1, 0)

                if self._show_buttons:
                    layout.addWidget(self.button3, 2, 0)
                    layout.addWidget(self.button4, 2, 1)
                else:
                    layout.addWidget(self.button2, 2, 0)

                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
        else:
            self.pbar.setFormat('WAITING FOR UPDATE ...')
            self.pbar.setValue(self._loop_counter)
            self._show_buttons = False

            self.button2 = QPushButton("PAUSE")
            self.button2.setStyleSheet('color: #E5E5E5; background-color: darkred; font: bold; padding: 0.3em')
            self.button2.clicked.connect(self.pause_hint)

            self.button3 = QPushButton("MAIN")
            self.button3.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
            self.button3.clicked.connect(self.main)

            self.button4 = QPushButton("EXIT")
            self.button4.setStyleSheet('color: #E5E5E5; background-color: #636363; font: bold; padding: 0.3em')
            self.button4.clicked.connect(lambda: self.close())

            _res = {
                'load_bond_transaction': self._load_bond_transaction,
                'check_server_data': self._csd,
            }

            layout = QGridLayout()
            layout.addWidget(Output(check_swap_data = True, swap_data = _res), 0, 0, 1, 0)
            layout.addWidget(self.pbar, 1, 0, 1, 0)
            layout.addWidget(self.button2, 2, 0)

            if self._show_buttons:
                layout.addWidget(self.button3, 2, 1)
                layout.addWidget(self.button4, 2, 2)
            else:
                pass

            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)

    def refund(self, bond = False):
        try:
            if self._direction == 'btc':
                # get current fee per byte
                _fee_per_byte = BTCScript.get_fee(self._user_btc_data)
                _fee_per_byte = round(_fee_per_byte['fee_per_byte'], 8)
                _fee_per_byte = int(_fee_per_byte * 1e8)

                # simple up vars
                if bond:
                    _sender_address = self._load_bond_transaction['sender_address']
                    _recipient_address = self._load_bond_transaction['server_address']
                    _htlc_address = self._load_bond_transaction['htlc_address']
                    _funding_txid = self._load_bond_transaction['txid']
                    _refund_blockheight = self._load_bond_transaction['refund_blockheight']
                    _amount = self._load_bond_transaction['amount']
                    _secret_hash_hex = self._load_bond_transaction['secret_hash_hex']
                else:
                    _sender_address = self._load_swap_transaction['sender_funding_address']
                    _recipient_address = self._load_swap_transaction['server_claim_address']
                    _htlc_address = self._load_swap_transaction['htlc_address']
                    _funding_txid = self._load_swap_transaction['send_fund_txid']
                    _refund_blockheight = self._load_swap_transaction['refund_blockheight']
                    _amount = self._load_swap_transaction['amount']
                    _secret_hash_hex = self._load_swap_transaction['secret_hash_hex']

                # get transaction info
                _transaction_info = BTCScript.get_rawtransaction(_funding_txid, self._user_btc_data, True)

                _htlc_balance_raw = BTCScript.unspent(_htlc_address, self._user_btc_data)
                _htlc_balance = _htlc_balance_raw[2]

                # unlock wallets
                BTCScript.unlock_wallet(self._user_btc_data)

                # get address data
                _sender_privkey = BTCScript.get_privkey(_sender_address, self._user_btc_data)
                _sender_address = self._handle_btc.get_clean_address(_sender_address)
                _recipient_address = self._handle_btc.get_clean_address(_recipient_address)

                # prepare secret hash
                _secret_hash = binascii.unhexlify(_secret_hash_hex)

                # validate redeem script
                _btc_redeem_script = self._handle_btc.get_redeem_script(_refund_blockheight, _secret_hash, _sender_address, _recipient_address, self._user_btc_data, True)

                # get vout index
                for _i in _transaction_info['vout']:
                    if _htlc_address == _i['scriptPubKey']['address']:
                        _vout = _i['n']
                        break
                    else:
                        pass

                # generate refund tx
                _btc_refund = self._handle_btc.refund(_funding_txid, _vout, _htlc_balance, _fee_per_byte, _sender_address, _refund_blockheight, _btc_redeem_script[3], _sender_privkey, self._user_btc_data)

                # send funds
                _send_refund = BTCScript.send_transaction(_btc_refund[0], self._user_btc_data)

                # save transaction
                self._load_bond_transaction['finalized'] = True
                _save_bond_transaction = utils.save_bond(self._load_bond_transaction['filename'],
                                                                self._load_bond_transaction['swap_token'],
                                                                self._load_bond_transaction['sender_address'],
                                                                self._load_bond_transaction['server_address'],
                                                                self._load_bond_transaction['htlc_address'],
                                                                self._load_bond_transaction['refund_blockheight'],
                                                                self._load_bond_transaction['amount'],
                                                                self._load_bond_transaction['txid'],
                                                                self._load_bond_transaction['secret_hash_hex'],
                                                                self._load_bond_transaction['redeem_script'],
                                                                self._load_bond_transaction['conter_address'],
                                                                self._load_bond_transaction['swap_amount'],
                                                                self._load_bond_transaction['server_amount'],
                                                                self._load_bond_transaction['finalized'],
                )
            else:
                # get current fee per byte
                _fee_per_byte = LTCScript.get_fee(self._user_ltc_data)
                _fee_per_byte = round(_fee_per_byte['fee_per_byte'], 8)
                _fee_per_byte = int(_fee_per_byte * 1e8)

                # simple up vars
                if bond:
                    _sender_address = self._load_bond_transaction['sender_address']
                    _recipient_address = self._load_bond_transaction['server_address']
                    _htlc_address = self._load_bond_transaction['htlc_address']
                    _funding_txid = self._load_bond_transaction['txid']
                    _refund_blockheight = self._load_bond_transaction['refund_blockheight']
                    _amount = self._load_bond_transaction['amount']
                    _secret_hash_hex = self._load_bond_transaction['secret_hash_hex']
                else:
                    _sender_address = self._load_swap_transaction['sender_funding_address']
                    _recipient_address = self._load_swap_transaction['server_claim_address']
                    _htlc_address = self._load_swap_transaction['htlc_address']
                    _funding_txid = self._load_swap_transaction['send_fund_txid']
                    _refund_blockheight = self._load_swap_transaction['refund_blockheight']
                    _amount = self._load_swap_transaction['amount']
                    _secret_hash_hex = self._load_swap_transaction['secret_hash_hex']

                # get transaction info
                _transaction_info = LTCScript.get_rawtransaction(_funding_txid, self._user_ltc_data, True)

                _htlc_balance_raw = LTCScript.unspent(_htlc_address, self._user_ltc_data)
                _htlc_balance = _htlc_balance_raw[2]

                # unlock wallets
                LTCScript.unlock_wallet(self._user_ltc_data)

                # get address data
                _sender_privkey = LTCScript.get_privkey(_sender_address, self._user_ltc_data)
                _sender_address = self._handle_ltc.get_clean_address(_sender_address)
                _recipient_address = self._handle_ltc.get_clean_address(_recipient_address)

                # prepare secret hash
                _secret_hash = binascii.unhexlify(_secret_hash_hex)

                # validate redeem script
                _ltc_redeem_script = self._handle_ltc.get_redeem_script(_refund_blockheight, _secret_hash, _sender_address, _recipient_address, self._user_ltc_data, True)

                # get vout index
                for _i in _transaction_info['vout']:
                    if _htlc_address in _i['scriptPubKey']['addresses']:
                        _vout = _i['n']
                        break
                    else:
                        pass

                # generate refund tx
                _ltc_refund = self._handle_ltc.refund(_funding_txid, _vout, _htlc_balance, _fee_per_byte, _sender_address, _refund_blockheight, _ltc_redeem_script[3], _sender_privkey, self._user_ltc_data)

                # send funds
                _send_refund = LTCScript.send_transaction(_ltc_refund[0], self._user_ltc_data)

                # save transaction
                self._load_bond_transaction['finalized'] = True
                _save_bond_transaction = utils.save_bond(self._load_bond_transaction['filename'],
                                                                self._load_bond_transaction['swap_token'],
                                                                self._load_bond_transaction['sender_address'],
                                                                self._load_bond_transaction['server_address'],
                                                                self._load_bond_transaction['htlc_address'],
                                                                self._load_bond_transaction['refund_blockheight'],
                                                                self._load_bond_transaction['amount'],
                                                                self._load_bond_transaction['txid'],
                                                                self._load_bond_transaction['secret_hash_hex'],
                                                                self._load_bond_transaction['redeem_script'],
                                                                self._load_bond_transaction['conter_address'],
                                                                self._load_bond_transaction['swap_amount'],
                                                                self._load_bond_transaction['server_amount'],
                                                                self._load_bond_transaction['finalized'],
                )
        except Exception as ex:
            print(ex)

    def load_swap_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        swap_filename, _ = QFileDialog.getOpenFileName(self,"SELECT SWAP", f"{self._curr_path}/atomicswap/bonds","All Files (*);;Python Files (*.py)", options=options)
        return swap_filename

    def check_swap_status(self):
        try:
            self.spinner.stop()
        except Exception as ex:
            print(ex)

        # set path
        _path = f'/checkSwap/{self._swap_token}'

        # init spinner
        self.spinner = QtWaitingSpinner(self)

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(upd_swap_status = True), 0, 0, 1, 0)
        layout.addWidget(self.spinner, 0, 0, 1, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # start spinner
        self.spinner.start()

        # call request
        runnable = RequestRunnable(self, _path, self._user_tor_data['tor_url'], self._user_tor_data['tor_port'], self._user_tor_data['tor_control_port'])
        QThreadPool.globalInstance().start(runnable)

    def start_loop(self):
        self.timer=QTimer()
        self.timer.timeout.connect(self.check_swap_status)
        self.timer.start(60000)

    def stop_loop(self):
        self.timer.stop()

    def save_swap_data(self):
        _filename, ok_pressed = QInputDialog.getText(self, "Save Swap Data","PLEASE ENTER THE FILENAME TO SAVE THE SWAP:", QLineEdit.Normal, "")
        if ok_pressed and _filename != '':
            return _filename
        else:
            _okBox = QMessageBox()
            _okBox.setIcon(QMessageBox.Information)
            _okBox.setWindowTitle("INFO")
            _okBox.setStandardButtons(QMessageBox.Ok)
            _okBox.setStyleSheet('color: white; background-color: red; font: bold')
            _okBox.setText("< p align = 'center'>PLEASE ENTER A FILENAME!</p>")
            _res = _okBox.exec()

            self.finalize_swap()

    def final_data_output(self):
        if self._direction == 'btc':
            _bond_amount = self._bond_amount_btc
        else:
            _bond_amount = self._bond_amount_ltc

        _info = QMessageBox(self)
        _info.setWindowTitle("SUCCESS!")
        _info.setStyleSheet('color: white; background-color: green; font: bold')
        _info.setText(f"<p align = 'center'>AMOUNT: {_bond_amount:,}<br><br>TxId: {self._fund_txid}</p>")
        _button = _info.exec()

    def send_bond_data(self):
        try:
            self.spinner.stop()
        except Exception as ex:
            print(ex)

        # collect data
        _htlc_address = str(self._htlc_address)

        # set path
        if self._direction == 'btc':
            _path = f"/newBond/{self._swap_token}/{self._direction}/{self._btc_address}/{self._swap_data['btc_bond_address']}/{_htlc_address}/{self._refund_blockheight}/{self._fund_txid}/{self._bond_amount}/{self._ltc_address}/{self._swap_amount}"
        else:
            _path = f"/newBond/{self._swap_token}/{self._direction}/{self._ltc_address}/{self._swap_data['ltc_bond_address']}/{_htlc_address}/{self._refund_blockheight}/{self._fund_txid}/{self._bond_amount}/{self._btc_address}/{self._swap_amount}"

        # init spinner
        self.spinner = QtWaitingSpinner(self)

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(send_swap_data = True), 0, 0, 1, 0)
        layout.addWidget(self.spinner, 0, 0, 1, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # start spinner
        self.spinner.start()

        # call request
        runnable = RequestRunnable(self, _path, self._user_tor_data['tor_url'], self._user_tor_data['tor_port'], self._user_tor_data['tor_control_port'])
        QThreadPool.globalInstance().start(runnable)

    def send_swap_data(self):
        try:
            self.spinner.stop()
        except Exception as ex:
            print(ex)

        if self._direction == 'btc':
            # collect data
            _swap_token = self._load_bond_transaction['swap_token']
            _sender_funding_address = self._csd['user_send_address']
            _server_claim_address = self._csd['server_claim_address']
            _htlc_address = str(self._btc_redeem_script[2])
            _fund_txid = self._btc_send_fund
            _btc_amount = self._csd['conter_amount']
            _refund_blockheight = self._btc_redeem_script[0]

            # set path
            _path = f"/swapData/{_swap_token}/{_sender_funding_address}/{_server_claim_address}/{_htlc_address}/{_fund_txid}/{_btc_amount}/{_refund_blockheight}"
        else:
            # collect data
            _swap_token = self._load_bond_transaction['swap_token']
            _sender_funding_address = self._csd['user_send_address']
            _server_claim_address = self._csd['server_claim_address']
            _htlc_address = str(self._ltc_redeem_script[2])
            _fund_txid = self._ltc_send_fund
            _ltc_amount = self._csd['conter_amount']
            _refund_blockheight = self._ltc_redeem_script[0]

            # set path
            _path = f"/swapData/{_swap_token}/{_sender_funding_address}/{_server_claim_address}/{_htlc_address}/{_fund_txid}/{_ltc_amount}/{_refund_blockheight}"

        # init spinner
        self.spinner = QtWaitingSpinner(self)

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(send_swap_data = True), 0, 0, 1, 0)
        layout.addWidget(self.spinner, 0, 0, 1, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # start spinner
        self.spinner.start()

        # call request
        runnable = RequestRunnable(self, _path, self._user_tor_data['tor_url'], self._user_tor_data['tor_port'], self._user_tor_data['tor_control_port'])
        QThreadPool.globalInstance().start(runnable)

    def new_swap_data(self):
        try:
            self.spinner.stop()
        except Exception as ex:
            print(ex)

        # set path
        _path = f'/newSwap/{self._direction}/{self._amount}'

        # init spinner
        self.spinner = QtWaitingSpinner(self)

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(get_swap_data = True), 0, 0, 1, 0)
        layout.addWidget(self.spinner, 0, 0, 1, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # start spinner
        self.spinner.start()

        # call request
        runnable = RequestRunnable(self, _path, self._user_tor_data['tor_url'], self._user_tor_data['tor_port'], self._user_tor_data['tor_control_port'])
        QThreadPool.globalInstance().start(runnable)

    def get_amount(self):
        if self._direction == 'btc':
            # get max
            if self._ping_server['btc_max'] > self._btc_balance_confirmed:
                _amount_max = self._btc_balance_confirmed_btc
            else:
                _amount_max = self._ping_server['btc_max_btc']

            # def amount
            _amount, ok_pressed = QInputDialog.getDouble(self, "Amount","PLEASE ENTER THE AMOUNT (BTC) YOU WANT TO SEND:", self._ping_server['btc_min_btc'], self._ping_server['btc_min_btc'], self._ping_server['btc_max_btc'], 8)
        else:
            # get max
            if self._ping_server['ltc_max'] > self._ltc_balance_confirmed:
                _amount_max = self._ltc_balance_confirmed_ltc
            else:
                _amount_max = self._ping_server['ltc_max_ltc']

            # def amount
            _amount, ok_pressed = QInputDialog.getDouble(self, "Amount","PLEASE ENTER THE AMOUNT (LTC) YOU WANT TO SEND:", self._ping_server['ltc_min_ltc'], self._ping_server['ltc_min_ltc'], self._ping_server['ltc_max_ltc'], 8)

        if ok_pressed:
            return _amount
        else:
            return False

    def ok_cancel(self, core: bool = True):
        _okBox = QMessageBox()
        _okBox.setIcon(QMessageBox.Information)
        _okBox.setWindowTitle("INFO")
        _okBox.setStandardButtons(QMessageBox.Ok)
        _okBox.setStyleSheet('color: white; background-color: red; font: bold')

        if core:
            _okBox.setText("YOUR BITCOIN/LITECOIN CORE IS NOT RUNNING!")
        else:
            _okBox.setText("< p align = 'center'>DONT FORGET TO COME BACK IN TIME OR YOU PUT YOUR BOND AT RISK!</p>")

        _res = _okBox.exec()

    def pause_hint(self):
        self._pause = True
        self.main()

    def load_user_data(self):
        try:
            _load = utils.load_user_data()
            return _load
        except Exception as ex:
            print(ex)
            return False

    def save_user_data(self, first_time_user = False):
        try:
            if first_time_user:
                _okBox = QMessageBox()
                _okBox.setIcon(QMessageBox.Information)
                _okBox.setWindowTitle("INFO")
                _okBox.setStandardButtons(QMessageBox.Ok)
                _okBox.setStyleSheet('color: white; background-color: green; font: bold')
                _okBox.setText("< p align = 'center'>HELLO FIRST TIME USER! THIS CLIENT USE BITCOIN/LITECOIN-CORE AND TOR FOR ANONYMOUS COMMUNICATION. PLEASE ENTER YOUR DATA AT THE NEXT WINDOWS. YOU WILL NEED YOUR RPCUSER/RPCPASSWORD/WALLETPASSPHRASE FOR YOUR BITCOIN AND LITECOIN INSTANCES. IF YOU DONT KNOW YOUR DATA (URL/PORTS), USE THE DEFAULT VALUES. THANKS!</p>")
                _res = _okBox.exec()
            else:
                pass

            _btc_rpc_username, _input1 = QInputDialog.getText(self, "BITCOIN RPC USER","PLEASE ENTER THE BITCOIN RPC USER:", QLineEdit.Normal, "YOUR BITCOIN RPC USERNAME")
            _btc_rpc_password, _input2 = QInputDialog.getText(self, "BITCOIN RPC PASSWORD","PLEASE ENTER THE BITCOIN RPC PASSWORD:", QLineEdit.Normal, "YOUR BITCOIN RPC PASSWORD")
            _btc_rpc_url, _input3 = QInputDialog.getText(self, "BITCOIN RPC URL","PLEASE ENTER THE BITCOIN RPC URL:", QLineEdit.Normal, "127.0.0.1")
            _btc_rpc_port, _input4 = QInputDialog.getInt(self, "BITCOIN CORE PORT","PLEASE ENTER THE BITCOIN PORT:", 2, 8332, 65000, 1)
            _btc_walletpassphrase, _input5 = QInputDialog.getText(self, "BITCOIN WALLET PASSPHRASE","PLEASE ENTER YOUR BITCOIN WALLET PASSPHRASE:", QLineEdit.Normal, "YOUR BITCOIN WALLET PASSPHRASE")

            _ltc_rpc_username, _input6 = QInputDialog.getText(self, "LITECOIN RPC USER","PLEASE ENTER THE LITECOIN RPC USER:", QLineEdit.Normal, "YOUR LITECOIN RPC USERNAME")
            _ltc_rpc_password, _input7 = QInputDialog.getText(self, "LITECOIN RPC PASSWORD","PLEASE ENTER THE LITECOIN RPC PASSWORD:", QLineEdit.Normal, "YOUR LITECOIN RPC PASSWORD")
            _ltc_rpc_url, _input8 = QInputDialog.getText(self, "LITECOIN RPC URL","PLEASE ENTER THE LITECOIN RPC URL:", QLineEdit.Normal, "127.0.0.1")
            _ltc_rpc_port, _input9 = QInputDialog.getInt(self, "LITECOIN CORE PORT","PLEASE ENTER THE LITECOIN RPC PORT:", 2, 9332, 65000, 1)
            _ltc_walletpassphrase, _input10 = QInputDialog.getText(self, "LITECOIN WALLET PASSPHRASE","PLEASE ENTER THE LITECOIN WALLET PASSPHRASE:", QLineEdit.Normal, "YOUR LITECOIN WALLET PASSPHRASE")

            _tor_url, _input11 = QInputDialog.getText(self, "TOR URL","PLEASE ENTER THE TOR URL:", QLineEdit.Normal, "127.0.0.1")
            _tor_port, _input12 = QInputDialog.getInt(self, "TOR PORT","PLEASE ENTER THE TOR PORT:", 2, 9050, 65000, 1)
            _tor_control_port, _input13 = QInputDialog.getInt(self, "TOR CONTROL PORT","PLEASE ENTER THE TOR CONTROL PORT:", 2, 9051, 65000, 1)

            # collect it
            self._user_data = {
                "_btc_rpc_user": _btc_rpc_username,
                "_btc_rpc_password": _btc_rpc_password,
                "_btc_rpc_url": _btc_rpc_url,
                "_btc_rpc_port": _btc_rpc_port,
                "_btc_walletpassphrase": _btc_walletpassphrase,
                "_ltc_rpc_user": _ltc_rpc_username,
                "_ltc_rpc_password": _ltc_rpc_password,
                "_ltc_rpc_url": _ltc_rpc_url,
                "_ltc_rpc_port": _ltc_rpc_port,
                "_ltc_walletpassphrase": _ltc_walletpassphrase,
                "_tor_url": _tor_url,
                "_tor_port": _tor_port,
                "_tor_control_port": _tor_control_port
            }

            # save it
            _save = utils.save_user_data(self._user_data)

            if _save:
                self._user_tor_data = {
                    "tor_url": self._user_data['_tor_url'],
                    "tor_port": self._user_data['_tor_port'],
                    "tor_control_port": self._user_data['_tor_control_port']
                }

                self._user_btc_data = {
                    "btc_rpc_user": self._user_data['_btc_rpc_user'],
                    "btc_rpc_password": self._user_data['_btc_rpc_password'],
                    "btc_rpc_url": self._user_data['_btc_rpc_url'],
                    "btc_rpc_port": self._user_data['_btc_rpc_port'],
                    "btc_walletpassphrase": self._user_data['_btc_walletpassphrase'],
                }

                self._user_ltc_data = {
                    "ltc_rpc_user": self._user_data['_ltc_rpc_user'],
                    "ltc_rpc_password": self._user_data['_ltc_rpc_password'],
                    "ltc_rpc_url": self._user_data['_ltc_rpc_url'],
                    "ltc_rpc_port": self._user_data['_ltc_rpc_port'],
                    "ltc_walletpassphrase": self._user_data['_ltc_walletpassphrase'],
                }
            else:
                pass

        except Exception as ex:
            print(ex)

    def main(self):
        # pause hint
        try:
            if self._pause:
                # stop loop
                try:
                    if self.timer.isActive():
                        self.stop_loop()
                        self._loop_counter = 0
                        self.ok_cancel(False)
                        self._pause = False
                    else:
                        pass
                except Exception as ex:
                    print(ex)
            else:
                pass
        except Exception as ex:
            print(ex)

        # stop loop
        try:
            if self.timer.isActive():
                self.stop_loop()
                self._loop_counter = 0
            else:
                pass
        except Exception as ex:
            print(ex)

        # output buttons
        self.output_main_buttons()

        # check server
        try:
            if self._ping_server['valid']:
                # layout
                layout = QGridLayout()
                layout.addWidget(Output(output_stats = True, server_status = self._ping_server), 0, 0, 1, 0)
                layout.addWidget(self.button1, 1, 0)
                layout.addWidget(self.button2, 1, 1)
                layout.addWidget(self.button3, 1, 2)
                layout.addWidget(self.button4, 1, 3)

                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
            elif self._ping_server['type'] == 'server_online':
                self.load_server_offline()
            else:
                self.get_server_data()
        except Exception as ex:
            print(ex)
            self.get_server_data()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

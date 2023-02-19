# Tannhauser Gate Atomic Swap

## Video Showcase (YouTube)

[![Video](https://img.youtube.com/vi/qfZ3Hac58Pw/0.jpg)](https://youtu.be/watch?v=qfZ3Hac58Pw "TannhauserGate")

## Installation

```
python3 -m venv venv
. venv/bin/activate
pip install TannhauserGate
tannhauser
```

## Depends

**Tannhauser Gate depends at [Tor](https://github.com/torproject/tor), [BitcoinCore](https://github.com/bitcoin/bitcoin) and [LitecoinCore](https://github.com/litecoin-project/litecoin). Please install it first. You will find sample config files [here](https://github.com/TannhauserGate420/tannhauser/tree/main/atomicswap/contrib).**

## Showcase

1. **Start the client and connect to Tannhauser Gate:**

   ![swap1](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap1.png)


2. **Take a look at the current conditions like rates, minimum/maximum and the minimum bond:**

   ![swap2](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap2.png)


3. **Load your wallet. First time users have to initiate a new wallet and fund it:**

   ![swap3](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap3.png)


4. **Initiate your atomic swap and choose your direction. In this showcase we swap Bitcoin for Litecoin:**

   ![swap4](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap4.png)


5. **Enter the amount you want to swap:**

   ![swap5](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap5.png)


6. **After hitting OK you will get an updated summary of your atomic swap with all relevant data:**

   ![swap6](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap6.png)


7. **If you feel fine hit "Send". After this you get a success message and the transaction ID:**

   ![swap7](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap7.png)


8. **Save your swap:**

   ![swap8](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap8.png)


9. **Now you can lean back, grab a coffee and enjoy an automatic atomic swap. The client will check your swap every minute. You have nothing to do - at this point all runs automatically. You can "PAUSE" the check at any time but its not recommended. First we have to wait for the bond confirmation:**

   ![swap9](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap9.png)


10. **If confirmed Tannhauser Gate will send the Litecoin amount:**

    ![swap10](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap10.png)


11. **Your client check this Litecoin transaction and send the leftover amount to your swap HTLC address after one confirmation:**

    ![swap11](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap11.png)


12. **At this point you have send the complete amount you want to swap. Tannhauser Gate will wait for one confirmation:**

    ![swap12](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap12.png)


13. **After one confirmation Tannhauser Gate will withdraw the bond and swap amount and the secret will be revealed to the blockchain:**

    ![swap13](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap13.png)


14. **The client extract the secret from the transaction and withdraw the Litecoin funds from the HTLC address:**

    ![swap14](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap14.png)


15. **A quick balance check shows the newly arrived Litecoin funds:**

    ![swap15](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap15.png)

## Transactions:

|           Action | TXID                                                         |
| ---------------: | ------------------------------------------------------------ |
|      Client Bond | https://chain.so/tx/BTC/1242b63342d6222a55cfb7c339142acb3e23937b255aeb108a6783ddad56b07c |
|       TG Funding | https://chain.so/tx/LTC/b9bf6e608636560084f0abdb2a552feaaa18452439c90c0c38abc77c0976fddc |
|   Client Funding | https://chain.so/tx/BTC/756c491c236a1ff87feb10f72001fc2450f1815333b38995f23daf034e17fdb0 |
| TG Bond withdraw | https://chain.so/tx/BTC/503ba2a313de754ee850340dd8aac601df11c3586d115abd8c647ce34bf3e46c |
| TG Swap withdraw | https://chain.so/tx/BTC/24872849fef2f7ee6a284b675eb28c9d2a16bf8b550f586cd185004588dcdf14 |
|  Client withdraw | https://chain.so/tx/LTC/9349b37068f8cffb04d7327c2d92930f3d7771999e31d2e8362c8bb03d7a23f0 |

## FAQ:

![swap0](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap0.png)

## How to get the secret:

![swap16](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap16.png)

![swap17](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap17.png)

## The different results:

**All went fine:**

![swap19](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap19.png)

**Case: The amount is less than agreed or not in time. Result: Swap failed. You lost your Bond. Swap refund is possible:**

![swap20](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap20.png)
![swap21](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap21.png)

**Case: You dont send the swap amount at all. Result: Swap failed. You lost your Bond. No refund possible:**

![swap22](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap22.png)

**Case: For any reason Tannhauser dont accept the swap. Result: Swap failed. Bond refund possible:**

![swap23](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap23.png)
![swap24](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/swap24.png)

## Configuration

![config](https://github.com/TannhauserGate420/tannhauser/blob/main/atomicswap/contrib/images/config.png)

## Notes

**Tannhauser Gate  is a simple POC for an automatic atomic swap service. Tannhauser  is still in development mode - so use it at your own risk. For the Litecoin connection Tannhauser uses a customized version of python-bitcoinlib. There is a simple GUI as wrapper for easy handling. The GUI is a little bit guerrilla - but it does the job. So if you are a QT wizard - feel free to make a PR. The GUI uses a different (additional) library for RPC in contrast to the CLI. For some reason the GUI produces a broken pipe error at irregular intervals and I don't have time to look into it at the moment. The main goal of the development is a simple p2p client, where the user can be both maker and taker. Until then you can swap smaller amounts with Tannhauser. For Tannhauser there is a general refund window of 2 hours. Refunds for the user are possible after 1 hour or after 2 hours (Bond).**

## Donations

**I do not accept donations. If you have some sats left donate them to the [Torproject](https://donate.torproject.org/cryptocurrency/) or to the [EFF](https://supporters.eff.org/donate/join-eff-4).**

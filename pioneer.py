from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import threading
import time
import random
from colorama import init, Fore

# Enable unaudited HD Wallet features (optional, depends on your use case)
Account.enable_unaudited_hdwallet_features()

# Function to read API key from file
def read_api_key():
    with open("apikey.txt", "r") as file:
        return file.read().strip()

# Function to read private key from file
def read_private_key():
    with open("privatekey.txt", "r") as file:
        return file.read().strip()

# Function to check sender balance
def check_balance(address):
    balance = web3.eth.get_balance(address)
    return balance

# Initialize Web3 and other components
rpc_url = read_api_key()
web3 = Web3(Web3.HTTPProvider(rpc_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Read private key from file
private_key = read_private_key()

try:
    # Create account object from private key
    sender_account = Account.from_key(private_key)
    sender_address = sender_account.address

    # Initialize transaction count
    transaction_count = 0

    # Display credits and donation message with color
    print(Fore.GREEN + "===================================================")
    print(Fore.GREEN + "                BOT Pioneer Particle")
    print(Fore.GREEN + "===================================================")
    print(Fore.YELLOW + " Developed by: JerryM")
    print(Fore.YELLOW + " Supported by: WIMIX")
    print(Fore.GREEN + "===================================================")
    print(Fore.CYAN + f" DONATE:{Fore.WHITE}0x6Fc6Ea113f38b7c90FF735A9e70AE24674E75D54")
    print(Fore.GREEN + "===================================================")
    print()

    # Check sender balance before starting transactions
    sender_balance = check_balance(sender_address)

    # If balance is zero or less than transaction cost, notify and exit
    if sender_balance <= 0:
        print(Fore.RED + "BOT berhenti. Saldo Kurang atau Tidak Mencukupi untuk Bertransaksi.")
    else:
        # Start a thread to print balance in real-time
        def print_sender_balance():
            while True:
                sender_balance = check_balance(sender_address)
                if sender_balance <= 0:
                    print(Fore.RED + "Saldo Kurang atau Tidak Mencukupi Untuk Bertransaksi.")
                    break
                time.sleep(5)  # Update every 5 seconds

        balance_thread = threading.Thread(target=print_sender_balance, daemon=True)
        balance_thread.start()

        # Loop to send 100 transactions
        for i in range(1, 101):
            # Get the latest nonce for sender address
            nonce = web3.eth.get_transaction_count(sender_address)

            # Generate a new random receiver account
            receiver_account = Account.create()
            receiver_address = receiver_account.address
            print(Fore.WHITE + f'Generated address {i}:', Fore.WHITE + receiver_address)

            # Amount to send in Ether (random between 0.00001 and 0.0001 ETH)
            amount_to_send = random.uniform(0.00001, 0.0001)

            # Convert amount to wei with proper precision
            amount_to_send_wei = int(web3.to_wei(amount_to_send, 'ether'))

            # Gas Price in gwei (random between 9 and 15 gwei)
            gas_price_gwei = random.uniform(9, 15)
            gas_price_wei = web3.to_wei(gas_price_gwei, 'gwei')

            # Prepare transaction
            transaction = {
                'nonce': nonce,
                'to': receiver_address,
                'value': amount_to_send_wei,
                'gas': 21000,  # Gas limit for a regular transaction
                'gasPrice': gas_price_wei,
                'chainId': 11155111  # Mainnet chain ID
            }

            # Sign the transaction with sender's private key
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

            # Send the transaction
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Print transaction details immediately after sending
            print(Fore.WHITE + "Transaction Hash:", Fore.WHITE + web3.to_hex(tx_hash))
            print(Fore.WHITE + "Sender Address:", Fore.GREEN + sender_address)
            print(Fore.WHITE + "Receiver Address:", receiver_address)

            # Increment transaction count
            transaction_count += 1

            # Wait for 15 seconds before checking transaction status
            time.sleep(15)

            # Retry 5 times with 10-second interval if transaction receipt not found
            retry_count = 0
            while retry_count < 5:
                try:
                    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
                    if tx_receipt is not None:
                        if tx_receipt['status'] == 1:
                            print(Fore.GREEN + "Transaksi SUKSES")
                            break
                        else:
                            print(Fore.RED + "Transaksi GAGAL")
                            break
                    else:
                        print(Fore.YELLOW + "Transaction is still pending. Retrying...")
                        retry_count += 1
                        time.sleep(10)
                except Exception as e:
                    print(Fore.RED + f"Error checking transaction status: {str(e)}")
                    retry_count += 1
                    time.sleep(10)

            print()  # Print a blank line for separation

            # Check if we have sent 101 transactions and exit the loop
            if transaction_count >= 101:
                break

    # Finished sending transactions or stopped due to empty balance
    print(Fore.GREEN + "Selesai.")
    print(Fore.WHITE + "Sender Address:", Fore.GREEN + sender_address)

except ValueError:
    print(Fore.RED + "Private key yang dimasukkan tidak valid 0x.......")

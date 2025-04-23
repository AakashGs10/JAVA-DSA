from flask import Flask, request, jsonify
from web3 import Web3
import json
import os
from dotenv import load_dotenv
from web3.exceptions import InvalidAddress
from eth_utils import is_address
from typing import Optional

load_dotenv()

app = Flask(__name__)

INFURA_ID = os.getenv("INFURA_ID")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

if not INFURA_ID or not CONTRACT_ADDRESS:
    raise ValueError("""
    ❌ Missing environment variables!
    Check your .env file contains:
    INFURA_ID=your_infura_id_here
    CONTRACT_ADDRESS=your_contract_address_here
    """)

try:
    CONTRACT_ADDRESS = Web3.to_checksum_address(CONTRACT_ADDRESS.strip())
except InvalidAddress:
    raise ValueError("❌ Invalid CONTRACT_ADDRESS in .env file")

w3 = Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/{INFURA_ID}"))
if not w3.is_connected():
    raise ConnectionError("❌ Failed to connect to Ethereum network")

with open("BlockchainLedgerABI.json", "r") as f:
    abi = json.load(f)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

class TransactionNode:
    def __init__(self, data: dict):
        self.data = data
        self.next: Optional[TransactionNode] = None

class TransactionLinkedList:
    def __init__(self):
        self.head: Optional[TransactionNode] = None
        self.size = 0

    def add(self, sender: str, receiver: str, amount: int, tx_hash: str):
        new_node = TransactionNode({
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "tx_hash": tx_hash,
            "validated": False
        })
        
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def get_all(self):
        transactions = []
        current = self.head
        index = 0
        while current:
            transactions.append({
                "id": index,
                "sender": current.data["sender"],
                "receiver": current.data["receiver"],
                "amount": current.data["amount"],
                "tx_hash": current.data["tx_hash"],
                "validated": current.data["validated"]
            })
            current = current.next
            index += 1
        return transactions

ledger = TransactionLinkedList()

def validate_eth_address(address: str) -> bool:
    return is_address(address) and address == Web3.to_checksum_address(address)

@app.route("/")
def home():
    return "✅ Flask server is running."

@app.route("/contract/submit_transaction", methods=["POST"])
def submit_transaction():
    try:
        data = request.json
        
        if not all(key in data for key in ["sender", "receiver", "amount", "private_key"]):
            return jsonify({"error": "Missing required fields"}), 400
            
        sender = data["sender"]
        receiver = data["receiver"]
        
        if not validate_eth_address(sender) or not validate_eth_address(receiver):
            return jsonify({"error": "Invalid Ethereum address"}), 400
            
        sender = Web3.to_checksum_address(sender)
        receiver = Web3.to_checksum_address(receiver)
        
        amount = int(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400

        total_value = amount + (amount * 5 // 100)
        
        txn = {
            'chainId': 11155111,
            'to': receiver,
            'value': total_value,
            'gas': 300000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': w3.eth.get_transaction_count(sender),
        }

        signed_txn = w3.eth.account.sign_transaction(txn, data["private_key"])
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        ledger.add(sender, receiver, amount, tx_hash.hex())
        return jsonify({"tx_hash": tx_hash.hex()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/contract/register_validator", methods=["POST"])
def register_validator():
    try:
        data = request.json
        address = Web3.to_checksum_address(data["address"])
        stake = int(data["amount"])
        
        if stake <= 0:
            return jsonify({"error": "Stake amount must be positive"}), 400

        txn = contract.functions.registerValidator().build_transaction({
            "from": address,
            "value": stake,
            "nonce": w3.eth.get_transaction_count(address),
            "gas": 300000,
            "gasPrice": w3.to_wei("20", "gwei")
        })
        
        signed_txn = w3.eth.account.sign_transaction(txn, data["private_key"])
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return jsonify({"tx_hash": tx_hash.hex()})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/contract/claim_rewards", methods=["POST"])
def claim_rewards():
    try:
        data = request.json
        address = Web3.to_checksum_address(data["address"])
        
        txn = contract.functions.claimRewards().build_transaction({
            "from": address,
            "nonce": w3.eth.get_transaction_count(address),
            "gas": 300000,
            "gasPrice": w3.to_wei("20", "gwei")
        })
        
        signed_txn = w3.eth.account.sign_transaction(txn, data["private_key"])
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return jsonify({"tx_hash": tx_hash.hex()})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/contract/redeem_stake", methods=["POST"])
def redeem_stake():
    try:
        data = request.json
        address = Web3.to_checksum_address(data["address"])
        
        txn = contract.functions.redeemStake().build_transaction({
            "from": address,
            "nonce": w3.eth.get_transaction_count(address),
            "gas": 300000,
            "gasPrice": w3.to_wei("20", "gwei")
        })
        
        signed_txn = w3.eth.account.sign_transaction(txn, data["private_key"])
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return jsonify({"tx_hash": tx_hash.hex()})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ledger", methods=["GET"])
def get_ledger():
    return jsonify({"ledger": ledger.get_all()})

@app.route("/contract/status/<address>", methods=["GET"])
def get_wallet_status(address):
    try:
        validated_address = Web3.to_checksum_address(address)
        validator_data = contract.functions.validators(validated_address).call()
        
        if validator_data[0] == 0 and validator_data[3] == False:
            is_validator = False
        else:
            is_validator = validator_data[3]

        return jsonify({
            "balance": w3.eth.get_balance(validated_address),
            "transaction_count": w3.eth.get_transaction_count(validated_address),
            "is_validator": is_validator,
            "is_contract": len(w3.eth.get_code(validated_address)) > 0
        })
    except Exception as e:
        return jsonify({"error": f"Address validation failed: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(port=5000)

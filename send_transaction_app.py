import streamlit as st
from web3 import Web3
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

INFURA_ID = os.getenv("INFURA_ID")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
FLASK_BASE_URL = "http://127.0.0.1:5000"

with open("BlockchainLedgerABI.json") as f:
    ABI = json.load(f)

w3 = Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/{INFURA_ID}"))
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

st.set_page_config(page_title="Ethereum Dashboard", layout="centered")
st.title("Ethereum Smart Contract Dashboard")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Send Transaction", "View Ledger", "Tx Status",
    "Register Validator", "Claim Rewards", "Redeem Stake", "Wallet Info"
])

with tab1:
    st.subheader("Send ETH Transaction")
    sender = st.text_input("Sender Address", key="sender_addr")
    receiver = st.text_input("Receiver Address", key="receiver_addr")
    amount_eth = st.number_input("Amount (ETH)", min_value=0.0, step=0.01, key="amount_eth")
    private_key = st.text_input("Sender Private Key", type="password", key="sender_pk")

    if st.button("Send Transaction", key="send_tx_btn"):
        try:
            if not sender or not receiver or not amount_eth or not private_key:
                st.error("All fields are required!")
                raise Exception("Missing form data")
                
            sender = Web3.to_checksum_address(sender)
            receiver = Web3.to_checksum_address(receiver)
            amount = int(amount_eth * 1e18)

            payload = {
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "private_key": private_key
            }
            
            response = requests.post(
                f"{FLASK_BASE_URL}/contract/submit_transaction",
                json=payload
            )

            if response.status_code == 200:
                tx_hash = response.json().get("tx_hash")
                st.success(f"Transaction Sent! Hash: {tx_hash}")
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")

        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("Transaction Ledger")
    try:
        response = requests.get(f"{FLASK_BASE_URL}/ledger")
        if response.status_code == 200:
            ledger_data = response.json().get("ledger", [])
            if ledger_data:
                formatted_data = []
                for tx in ledger_data:
                    formatted_data.append({
                        "ID": tx["id"],
                        "Sender": tx["sender"],
                        "Receiver": tx["receiver"],
                        "Amount (ETH)": tx["amount"] / 1e18,
                        "Tx Hash": tx["tx_hash"],
                        "Validated": tx["validated"]
                    })
                st.dataframe(formatted_data)
            else:
                st.warning("No transactions found. Send one first!")
        else:
            st.error(f"Failed to fetch ledger: HTTP {response.status_code}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

with tab3:
    st.subheader("Transaction Status")
    tx_hash = st.text_input("Enter Transaction Hash", key="tx_hash_input")
    if st.button("Check Status", key="check_status_btn"):
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            status = "Success" if receipt.status == 1 else "Failed"
            st.write(f"Status: {status}")
            st.json(dict(receipt))
        except Exception as e:
            st.warning("Transaction not found or pending.")

with tab4:
    st.subheader("Register as Validator")
    address = st.text_input("Your Address", key="reg_val_addr")
    stake_eth = st.number_input("Stake Amount (ETH)", min_value=0.0, step=0.01, key="stake_eth")
    private_key = st.text_input("Your Private Key", type="password", key="reg_val_pk")

    if st.button("Register", key="reg_val_btn"):
        try:
            payload = {
                "address": address,
                "amount": int(stake_eth * 1e18),
                "private_key": private_key
            }
            res = requests.post(f"{FLASK_BASE_URL}/contract/register_validator", json=payload)
            st.success(f"Registered! Tx Hash: {res.json()['tx_hash']}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab5:
    st.subheader("Claim Rewards")
    val_address = st.text_input("Validator Address", key="claim_val_addr")
    val_key = st.text_input("Private Key", type="password", key="claim_val_pk")

    if st.button("Claim Rewards", key="claim_btn"):
        try:
            payload = {"address": val_address, "private_key": val_key}
            res = requests.post(f"{FLASK_BASE_URL}/contract/claim_rewards", json=payload)
            st.success(f"Rewards Claimed: {res.json()['tx_hash']}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab6:
    st.subheader("Redeem Stake")
    red_address = st.text_input("Validator Address", key="redeem_val_addr")
    red_key = st.text_input("Private Key", type="password", key="redeem_val_pk")

    if st.button("Redeem Stake", key="redeem_btn"):
        try:
            payload = {"address": red_address, "private_key": red_key}
            res = requests.post(f"{FLASK_BASE_URL}/contract/redeem_stake", json=payload)
            st.success(f"Stake Redeemed: {res.json()['tx_hash']}")
        except Exception as e:
            st.error(f"Error: {str(e)}")


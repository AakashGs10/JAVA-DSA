
from flask import Flask, request, jsonify

app = Flask(__name__)

users = {
    "Puneeth": 1000,
    "Neeraj": 750,
    "Nithin": 500
}

validators = {}

class Person:
    def __init__(self, name, contribution):
        self.name = name
        self.contribution = contribution
        self.trust_score = 10

    def gain_trust(self):
        self.trust_score += 1

    def lose_trust(self):
        self.trust_score -= 1

    def details(self):
        return {"name": self.name, "contribution": self.contribution, "trust_score": self.trust_score}

class TransactionNode:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.next = None

class TransactionList:
    def __init__(self):
        self.head = None

    def add_transaction(self, sender, receiver, amount):
        new_node = TransactionNode(sender, receiver, amount)
        if not self.head:
            self.head = new_node
        else:
            temp = self.head
            while temp.next:
                temp = temp.next
            temp.next = new_node


    def get_transactions(self):
        transactions = []
        temp = self.head
        while temp:
            transactions.append({
                "sender": temp.sender,
                "receiver": temp.receiver,
                "amount": temp.amount
            })
            temp = temp.next
        return transactions

tx_list = TransactionList()

@app.route("/check/<user>", methods=["GET"])
def check_funds(user):
    if user in users:
        return jsonify({"message": f"{user} has ₹{users[user]}", "funds": users[user]})
    return jsonify({"error": f"{user} is not recognized."}), 404

@app.route("/send", methods=["POST"])
def send_money():
    data = request.json
    sender = data.get("sender")
    receiver = data.get("receiver")
    amount = data.get("amount")

    if sender not in users or receiver not in users:
        return jsonify({"error": "Invalid sender or receiver."}), 400

    if users[sender] < amount:
        return jsonify({"error": f"{sender} lacks enough funds."}), 400

    users[sender] -= amount
    users[receiver] += amount
    tx_list.add_transaction(sender, receiver, amount)

    return jsonify({"message": f"{sender} gave ₹{amount} to {receiver}.", "updated_funds": users})

@app.route("/transactions", methods=["GET"])
def get_transactions():
    return jsonify({"transactions": tx_list.get_transactions()})

@app.route("/contribute", methods=["POST"])
def contribute():
    data = request.json
    user = data.get("user")
    amount = data.get("contribution")

    if user not in users or users[user] < amount:
        return jsonify({"error": f"{user} has insufficient funds."}), 400

    users[user] -= amount
    validators[user] = Person(user, amount)

    return jsonify({"message": f"{user} contributed ₹{amount} and is now an active participant.", "participant": validators[user].details()})

@app.route("/participants", methods=["GET"])
def show_participants():
    return jsonify({"people": [v.details() for v in validators.values()]})

if __name__ == "__main__":
    app.run(port=5000, debug=True)

package blockchain;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;

class Transaction {
    String sender, receiver;
    double amount;

    public Transaction(String sender, String receiver, double amount) {
        this.sender = sender;
        this.receiver = receiver;
        this.amount = amount;
    }

    
    @Override
    public String toString() {
        return sender + " -> " + receiver + ": $" + String.format("%.2f", amount);
    }
}

class HashUtil {
    public static String sha256(String input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes("UTF-8"));
            StringBuilder hex = new StringBuilder();
            for (byte b : hash) hex.append(String.format("%02x", b));
            return hex.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}

class Block {
    String previousHash, hash;
    List<Transaction> transactions;
    long timestamp;

    public Block(String previousHash) {
        this.previousHash = previousHash;
        this.transactions = new ArrayList<>();
        this.timestamp = System.currentTimeMillis();
        this.hash = calculateHash();
    }

    public void addTransaction(String sender, String receiver, double amount) {
        transactions.add(new Transaction(sender, receiver, amount));
        this.hash = calculateHash();
    }

    public String calculateHash() {
        return HashUtil.sha256(previousHash + transactions.toString() + timestamp);
    }

    @Override
    public String toString() {
        return "Prev Hash: " + previousHash + "\n" +
               "Transactions: " + transactions + "\n" +
               "Hash: " + hash + "\n";
    }
}

class Blockchain {
    List<Block> chain;

    public Blockchain() {
        chain = new ArrayList<>();
        chain.add(new Block("0")); 
    }

    public void addBlock(Block block) {
        chain.add(block);
    }

    public String getLastHash() {
        return chain.get(chain.size() - 1).hash;
    }

    public String getChainString() {
        StringBuilder sb = new StringBuilder();
        for (Block block : chain) {
            sb.append(block.toString()).append("\n------\n");
        }
        return sb.toString();
    }
}

public class BlockchainGUI extends JFrame {
    private final JTextField senderField = new JTextField(20);
    private final JTextField receiverField = new JTextField(20);
    private final JTextField amountField = new JTextField(20);
    private final JTextArea blockchainArea = new JTextArea(20, 50);

    private final Blockchain blockchain = new Blockchain();

    public BlockchainGUI() {
        setTitle("Blockchain Transaction GUI");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));

        blockchainArea.setEditable(false);
        blockchainArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        JScrollPane scrollPane = new JScrollPane(blockchainArea);
        JPanel inputPanel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(8, 8, 8, 8);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        gbc.gridx = 0; gbc.gridy = 0;
        inputPanel.add(new JLabel("Sender Name:"), gbc);
        gbc.gridx = 1;
        inputPanel.add(senderField, gbc);

        gbc.gridx = 0; gbc.gridy = 1;
        inputPanel.add(new JLabel("Receiver Name:"), gbc);
        gbc.gridx = 1;
        inputPanel.add(receiverField, gbc);

        gbc.gridx = 0; gbc.gridy = 2;
        inputPanel.add(new JLabel("Amount ($):"), gbc);
        gbc.gridx = 1;
        inputPanel.add(amountField, gbc);

        JButton addBtn = new JButton("➕ Add Transaction");
        JButton showBtn = new JButton("📜 Show Blockchain");

        addBtn.setFont(new Font("SansSerif", Font.BOLD, 13));
        showBtn.setFont(new Font("SansSerif", Font.BOLD, 13));

        JPanel buttonPanel = new JPanel();
        buttonPanel.add(addBtn);
        buttonPanel.add(showBtn);

       
        addBtn.addActionListener(e -> addTransaction());
        showBtn.addActionListener(e -> blockchainArea.setText(blockchain.getChainString()));

        add(inputPanel, BorderLayout.NORTH);
        add(buttonPanel, BorderLayout.CENTER);
        add(scrollPane, BorderLayout.SOUTH);

        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    private void addTransaction() {
        try {
            String sender = senderField.getText().trim();
            String receiver = receiverField.getText().trim();
            double amount = Double.parseDouble(amountField.getText().trim());

            if (sender.isEmpty() || receiver.isEmpty()) {
                JOptionPane.showMessageDialog(this, "Sender and Receiver names cannot be empty.");
                return;
            }

            Block block = new Block(blockchain.getLastHash());
            block.addTransaction(sender, receiver, amount);
            blockchain.addBlock(block);

            senderField.setText("");
            receiverField.setText("");
            amountField.setText("");

            JOptionPane.showMessageDialog(this, "✅ Transaction successfully added!");

        } catch (NumberFormatException e) {
            JOptionPane.showMessageDialog(this, "❌ Invalid amount. Please enter a valid number.");
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(BlockchainGUI::new);
    }
}

import java.io.*;
import java.net.*;
import java.util.*;

class HttpRequestHandler {
    public static String sendGetRequest(String url) throws Exception {
        URL requestUrl = new URL(url);
        HttpURLConnection connection = (HttpURLConnection) requestUrl.openConnection();
        connection.setRequestMethod("GET");

        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;

        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        return response.toString();
    }

    public static String sendPostRequest(String url, String jsonData) throws Exception {
        URL requestUrl = new URL(url);
        HttpURLConnection connection = (HttpURLConnection) requestUrl.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);

        try (OutputStream outputStream = connection.getOutputStream()) {
            byte[] inputData = jsonData.getBytes("utf-8");
            outputStream.write(inputData, 0, inputData.length);
        }

        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;

        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        return response.toString();
    }
}

class Transaction {
    private final String sender;
    private final String receiver;
    private final double amount;

    public Transaction(String sender, String receiver, double amount) {
        this.sender = sender;
        this.receiver = receiver;
        this.amount = amount;
    }

    public String toJson() {
        return String.format("{\"sender\":\"%s\",\"receiver\":\"%s\",\"amount\":%.2f}", sender, receiver, amount);
    }
}

class TransactionManager {
    private final List<Transaction> pendingTransactions = new ArrayList<>();

    public void addTransaction(Transaction transaction) {
        pendingTransactions.add(transaction);
    }

    public void processTransactions() throws Exception {
        if (pendingTransactions.isEmpty()) {
            System.out.println("No pending transactions to process.");
            return;
        }

        for (Transaction transaction : pendingTransactions) {
            String response = HttpRequestHandler.sendPostRequest("http://localhost:5000/send", transaction.toJson());
            System.out.println("Transaction Processed: " + response);
        }
        pendingTransactions.clear();
    }
}

public class FinancialLedger {
    public static void main(String[] args) throws Exception {
        Scanner scanner = new Scanner(System.in);
        TransactionManager transactionManager = new TransactionManager();

        while (true) {
            System.out.println("\nSelect an option:");
            System.out.println("1️⃣ Initiate a Transaction");
            System.out.println("2️⃣ Process Pending Transactions");
            System.out.println("3️⃣ Exit");
            System.out.print("Enter your choice: ");

            if (!scanner.hasNextInt()) {
                System.out.println("Invalid input. Please enter a number.");
                scanner.next();
                continue;
            }

            int choice = scanner.nextInt();
            scanner.nextLine();

            switch (choice) {
                case 1:
                    System.out.print("Enter sender name: ");
                    String sender = scanner.nextLine();
                    System.out.print("Enter receiver name: ");
                    String receiver = scanner.nextLine();
                    System.out.print("Enter amount: ");

                    if (!scanner.hasNextDouble()) {
                        System.out.println("Invalid amount. Please enter a valid number.");
                        scanner.next();
                        continue;
                    }

                    double amount = scanner.nextDouble();
                    scanner.nextLine();

                    transactionManager.addTransaction(new Transaction(sender, receiver, amount));
                    System.out.println("Transaction recorded. Pending processing.");
                    break;

                case 2:
                    System.out.println("Processing all pending transactions...");
                    transactionManager.processTransactions();
                    break;

                case 3:
                    System.out.println("Exiting program. Have a great day!");
                    scanner.close();
                    return;

                default:
                    System.out.println("Invalid selection. Please choose a valid option.");
            }
        }
    }
}

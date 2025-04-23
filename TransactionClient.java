import java.io.*;
import java.net.*;
import java.util.*;

class HttpRequestHandler {
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
    private final double amountEth;
    private final String privateKey;

    public Transaction(String sender, String receiver, double amountEth, String privateKey) {
        this.sender = sender;
        this.receiver = receiver;
        this.amountEth = amountEth;
        this.privateKey = privateKey;
    }

    public String toJson() {
        long amountWei = (long) (this.amountEth * 1e18);
        return String.format(
            "{\"sender\":\"%s\", \"receiver\":\"%s\", \"amount\":%d, \"private_key\":\"%s\"}",
            sender, receiver, amountWei, privateKey
        );
    }
}

public class TransactionClient {
    public static void main(String[] args) throws Exception {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter sender Ethereum address: ");
        String sender = scanner.nextLine();

        System.out.print("Enter receiver Ethereum address: ");
        String receiver = scanner.nextLine();

        System.out.print("Enter amount in ETH: ");
        double amount = scanner.nextDouble();
        scanner.nextLine();

        System.out.print("Enter sender's private key: ");
        String privateKey = scanner.nextLine();

        Transaction tx = new Transaction(sender, receiver, amount, privateKey);

        try {
            String response = HttpRequestHandler.sendPostRequest(
                "http://127.0.0.1:5000/contract/submit_transaction",
                tx.toJson()
            );
            System.out.println("✅ Transaction Response: " + response);
        } catch (Exception e) {
            System.out.println("❌ Error: " + e.getMessage());
        }
    }
}
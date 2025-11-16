/**
 * BankAccount class - Your first Java class!
 *
 * This demonstrates:
 * - Encapsulation (private fields, public methods)
 * - Constructors
 * - Method implementation
 * - Input validation
 */
public class BankAccount {
    // TODO: Declare private fields
    // private int accountNumber;
    // private String accountHolder;
    // private double balance;

    /**
     * Constructor - initializes a new bank account
     * @param accountNumber Unique account identifier
     * @param accountHolder Name of account owner
     * @param initialBalance Starting balance (must be >= 0)
     */
    public BankAccount(int accountNumber, String accountHolder, double initialBalance) {
        // TODO: Initialize the fields
        // Remember to use 'this' keyword to distinguish fields from parameters
        // Validate that initialBalance is not negative
    }

    /**
     * Deposits money into the account
     * @param amount Amount to deposit (must be > 0)
     */
    public void deposit(double amount) {
        // TODO: Implement deposit logic
        // 1. Validate amount is positive
        // 2. Add to balance
        // 3. Print confirmation: "Deposited $X. New balance: $Y"
    }

    /**
     * Withdraws money from the account
     * @param amount Amount to withdraw (must be > 0 and <= balance)
     * @return true if successful, false otherwise
     */
    public boolean withdraw(double amount) {
        // TODO: Implement withdrawal logic
        // 1. Validate amount is positive
        // 2. Check if sufficient balance exists
        // 3. If yes: deduct from balance, print confirmation, return true
        // 4. If no: print error message, return false
        return false;  // Placeholder
    }

    /**
     * Gets the current balance
     * @return Current account balance
     */
    public double getBalance() {
        // TODO: Return the balance
        return 0.0;  // Placeholder
    }

    /**
     * Gets the account number
     * @return Account number
     */
    public int getAccountNumber() {
        // TODO: Return account number
        return 0;  // Placeholder
    }

    /**
     * Gets the account holder name
     * @return Account holder name
     */
    public String getAccountHolder() {
        // TODO: Return account holder
        return "";  // Placeholder
    }

    /**
     * Displays account information
     */
    public void displayAccountInfo() {
        // TODO: Print account details
        // Format: "Account #XXXX - Name - Balance: $XXX.XX"
        // Use System.out.printf for formatting: printf("Balance: $%.2f%n", balance);
    }
}

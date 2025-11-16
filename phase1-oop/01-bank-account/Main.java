/**
 * Main class - Entry point for the Bank Account System
 *
 * This demonstrates:
 * - Creating objects
 * - Calling methods
 * - Polymorphism (treating SavingsAccount as BankAccount)
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("=== Bank Account System ===\n");

        // TODO: Create a regular checking account
        // BankAccount checking = new BankAccount(1001, "John Doe", 1000.0);
        // System.out.println("Created checking account:");
        // checking.displayAccountInfo();
        // System.out.println();

        // TODO: Create a savings account
        // SavingsAccount savings = new SavingsAccount(1002, "Jane Smith", 5000.0, 0.05);
        // System.out.println("Created savings account:");
        // savings.displayAccountInfo();
        // System.out.println();

        System.out.println("=== Performing Transactions ===\n");

        // TODO: Test deposits on checking account
        // checking.deposit(500.0);
        // checking.deposit(-50.0);  // Should fail validation

        // TODO: Test withdrawals on checking account
        // checking.withdraw(200.0);
        // checking.withdraw(2000.0);  // Should fail - insufficient funds

        // TODO: Test savings account transactions
        // savings.deposit(1000.0);
        // savings.applyInterest();

        // TODO: Test minimum balance restriction
        // savings.withdraw(6250.0);  // Should fail - minimum balance
        // savings.withdraw(500.0);   // Should succeed

        System.out.println("\n=== Final Account Status ===\n");

        // TODO: Display final account information
        // checking.displayAccountInfo();
        // System.out.println();
        // savings.displayAccountInfo();

        // BONUS: Try polymorphism
        // BankAccount[] accounts = {checking, savings};
        // for (BankAccount account : accounts) {
        //     account.displayAccountInfo();
        //     System.out.println();
        // }
    }
}

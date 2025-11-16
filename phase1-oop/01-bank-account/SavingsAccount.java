/**
 * SavingsAccount - extends BankAccount
 *
 * This demonstrates:
 * - Inheritance (extends keyword)
 * - Calling parent constructor (super)
 * - Method overriding
 * - Adding new functionality to subclass
 */
public class SavingsAccount extends BankAccount {
    // TODO: Declare private field for interest rate
    // private double interestRate;

    private static final double MIN_BALANCE = 100.0;

    /**
     * Constructor for SavingsAccount
     * @param accountNumber Account ID
     * @param accountHolder Owner name
     * @param initialBalance Starting balance
     * @param interestRate Annual interest rate (e.g., 0.05 for 5%)
     */
    public SavingsAccount(int accountNumber, String accountHolder,
                          double initialBalance, double interestRate) {
        // TODO: Call parent class constructor using super()
        // super(accountNumber, accountHolder, initialBalance);

        // TODO: Initialize interestRate field
    }

    /**
     * Applies interest to the current balance
     * Interest is calculated as: balance * interestRate
     */
    public void applyInterest() {
        // TODO: Calculate interest
        // double interest = getBalance() * interestRate;

        // TODO: Add interest to account using deposit()
        // deposit(interest);

        // TODO: Print message
        // System.out.printf("Applied %.1f%% interest: $%.2f%n", interestRate * 100, interest);
    }

    /**
     * Overrides withdraw to enforce minimum balance
     * Savings accounts must maintain at least $100
     * @param amount Amount to withdraw
     * @return true if successful, false if would violate minimum balance
     */
    @Override
    public boolean withdraw(double amount) {
        // TODO: Check if withdrawal would leave balance below minimum
        // if (getBalance() - amount >= MIN_BALANCE) {
        //     return super.withdraw(amount);  // Call parent's withdraw
        // } else {
        //     System.out.println("Cannot withdraw: must maintain minimum balance of $" + MIN_BALANCE);
        //     return false;
        // }
        return false;  // Placeholder
    }

    /**
     * Displays savings account information including interest rate
     */
    @Override
    public void displayAccountInfo() {
        // TODO: Call parent's displayAccountInfo
        // super.displayAccountInfo();

        // TODO: Print additional info about interest rate
        // System.out.printf("Type: Savings (%.1f%% interest)%n", interestRate * 100);
    }

    /**
     * Gets the interest rate
     * @return Annual interest rate
     */
    public double getInterestRate() {
        // TODO: Return interest rate
        return 0.0;  // Placeholder
    }
}

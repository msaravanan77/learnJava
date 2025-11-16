# Module 1: Bank Account System

## Learning Objectives
- Understand Java classes vs C structs
- Master encapsulation (private fields, public methods)
- Learn constructors and method overloading
- Practice proper naming conventions
- Understand `this` keyword

## The Challenge

Build a simple banking system with the following features:

### Requirements

1. **BankAccount Class**
   - Private fields: `accountNumber`, `accountHolder`, `balance`
   - Constructor to initialize account
   - Methods:
     - `deposit(double amount)` - Add money
     - `withdraw(double amount)` - Remove money (check sufficient balance)
     - `getBalance()` - Return current balance
     - `getAccountInfo()` - Return account details
   - Validation: No negative deposits/withdrawals

2. **SavingsAccount Class** (extends BankAccount)
   - Additional field: `interestRate`
   - Method: `applyInterest()` - Add interest to balance
   - Override `withdraw()` to maintain minimum balance of $100

3. **Main Class**
   - Create multiple accounts
   - Perform transactions
   - Display account information

### Expected Output
```
=== Bank Account System ===

Creating accounts...
Account created: #1001 - John Doe - Balance: $1000.00
Account created: #1002 - Jane Smith (Savings) - Balance: $5000.00

Performing transactions...
John deposited $500.00. New balance: $1500.00
John withdrew $200.00. New balance: $1300.00
John tried to withdraw $2000.00. Insufficient funds!

Jane deposited $1000.00. New balance: $6000.00
Jane applied 5% interest. New balance: $6300.00
Jane tried to withdraw $6250.00. Must maintain minimum balance of $100!

=== Final Account Status ===
Account #1001 - John Doe
Type: Checking
Balance: $1300.00

Account #1002 - Jane Smith
Type: Savings (5.0% interest)
Balance: $6300.00
```

## Starter Code

Create three files:

### File 1: `BankAccount.java`
```java
public class BankAccount {
    // TODO: Add private fields
    // - accountNumber (int)
    // - accountHolder (String)
    // - balance (double)

    // TODO: Add constructor
    public BankAccount(int accountNumber, String accountHolder, double initialBalance) {
        // Initialize fields
        // Validate initialBalance is not negative
    }

    // TODO: Implement deposit method
    public void deposit(double amount) {
        // Validate amount > 0
        // Add to balance
        // Print confirmation message
    }

    // TODO: Implement withdraw method
    public boolean withdraw(double amount) {
        // Validate amount > 0
        // Check sufficient balance
        // Deduct from balance
        // Print confirmation or error message
        // Return true if successful, false otherwise
    }

    // TODO: Add getter for balance
    public double getBalance() {
        // Return balance
    }

    // TODO: Implement getAccountInfo method
    public void getAccountInfo() {
        // Print account number, holder name, balance
    }
}
```

### File 2: `SavingsAccount.java`
```java
public class SavingsAccount extends BankAccount {
    // TODO: Add private field for interestRate (double)
    private static final double MIN_BALANCE = 100.0;

    // TODO: Add constructor
    public SavingsAccount(int accountNumber, String accountHolder,
                          double initialBalance, double interestRate) {
        // Call parent constructor using super()
        // Initialize interestRate
    }

    // TODO: Implement applyInterest method
    public void applyInterest() {
        // Calculate interest: balance * interestRate
        // Use deposit() to add interest
        // Print message showing interest applied
    }

    // TODO: Override withdraw method
    @Override
    public boolean withdraw(double amount) {
        // Check if balance - amount >= MIN_BALANCE
        // If yes, call super.withdraw(amount)
        // If no, print error and return false
    }

    // TODO: Override getAccountInfo to show interest rate
    @Override
    public void getAccountInfo() {
        // Call super.getAccountInfo()
        // Print interest rate
    }
}
```

### File 3: `Main.java`
```java
public class Main {
    public static void main(String[] args) {
        System.out.println("=== Bank Account System ===\n");

        // TODO: Create a regular BankAccount
        // BankAccount account1 = new BankAccount(1001, "John Doe", 1000.0);

        // TODO: Create a SavingsAccount
        // SavingsAccount account2 = new SavingsAccount(1002, "Jane Smith", 5000.0, 0.05);

        // TODO: Test deposit and withdraw on both accounts

        // TODO: Test applyInterest on savings account

        // TODO: Test minimum balance restriction on savings account

        // TODO: Display final account information
    }
}
```

## Key Concepts to Learn

### 1. Encapsulation
```java
// WRONG - C style (public data)
public class BankAccount {
    public double balance;  // Anyone can modify!
}

// CORRECT - Java OOP style
public class BankAccount {
    private double balance;  // Protected

    public void deposit(double amount) {  // Controlled access
        if (amount > 0) {
            balance += amount;
        }
    }
}
```

### 2. Constructor
```java
public BankAccount(int accountNumber, String accountHolder, double initialBalance) {
    this.accountNumber = accountNumber;  // 'this' refers to current object
    this.accountHolder = accountHolder;
    this.balance = initialBalance;
}
```

### 3. Inheritance
```java
// SavingsAccount inherits all fields and methods from BankAccount
public class SavingsAccount extends BankAccount {
    public SavingsAccount(int accountNumber, String accountHolder, double initialBalance, double interestRate) {
        super(accountNumber, accountHolder, initialBalance);  // Call parent constructor
        this.interestRate = interestRate;
    }
}
```

### 4. Method Overriding
```java
@Override  // Annotation tells compiler this overrides parent method
public boolean withdraw(double amount) {
    // Custom logic for savings account
    if (getBalance() - amount >= MIN_BALANCE) {
        return super.withdraw(amount);  // Call parent method
    }
    return false;
}
```

## Testing Your Code

### Compile
```bash
javac BankAccount.java SavingsAccount.java Main.java
```

### Run
```bash
java Main
```

### Expected Behavior
- Regular account allows withdrawal until balance reaches 0
- Savings account maintains minimum $100 balance
- Interest calculation works correctly
- All validations prevent invalid operations

## Common Mistakes to Avoid

1. **Forgetting `this` keyword**
   ```java
   // WRONG
   public BankAccount(int accountNumber) {
       accountNumber = accountNumber;  // Assigns parameter to itself!
   }

   // CORRECT
   public BankAccount(int accountNumber) {
       this.accountNumber = accountNumber;  // this.field refers to instance variable
   }
   ```

2. **Not validating input**
   ```java
   // WRONG
   public void deposit(double amount) {
       balance += amount;  // What if amount is negative?
   }

   // CORRECT
   public void deposit(double amount) {
       if (amount > 0) {
           balance += amount;
       } else {
           System.out.println("Invalid deposit amount!");
       }
   }
   ```

3. **Accessing private fields directly in subclass**
   ```java
   // WRONG (in SavingsAccount)
   public void applyInterest() {
       balance += balance * interestRate;  // balance is private in parent!
   }

   // CORRECT
   public void applyInterest() {
       double interest = getBalance() * interestRate;
       deposit(interest);  // Use public methods
   }
   ```

## Extension Challenges (Optional)

Once you complete the basic requirements, try these:

1. **Transaction History**
   - Add `ArrayList<String> transactions` to store all transactions
   - Method `printTransactionHistory()`

2. **Account Number Validation**
   - Ensure account numbers are unique
   - Static field to track all created accounts

3. **Different Account Types**
   - Create `CheckingAccount` with overdraft protection
   - Add `MoneyMarketAccount` with withdrawal limits

4. **Transfer Between Accounts**
   - Static method `transfer(BankAccount from, BankAccount to, double amount)`

## Comparison with C

| Aspect | C | Java |
|--------|---|------|
| Data structure | `struct BankAccount` | `class BankAccount` |
| Functions | Free functions `deposit(account*, amount)` | Methods `account.deposit(amount)` |
| Access control | None (everything public) | `private`, `public`, `protected` |
| Memory | Manual `malloc/free` | Automatic garbage collection |
| Code reuse | Copy-paste or composition | Inheritance + composition |

## Review Checklist

Before moving to Module 2, ensure you:
- [ ] Understand difference between class and object
- [ ] Can explain why fields are private
- [ ] Know when to use `this` and `super`
- [ ] Understand constructor purpose
- [ ] Can override methods correctly
- [ ] Code compiles without errors
- [ ] All test cases pass
- [ ] Code follows Java naming conventions

## Next Steps

1. Complete the implementation
2. Test thoroughly
3. Push code to GitHub
4. Request code review (tag me!)
5. Move to Module 2: Shape Calculator

---

**Time to code!** Start with `BankAccount.java` and build incrementally. 🚀

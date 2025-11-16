# Phase 1: OOP Concepts - Detailed Guide

This guide accompanies the visual architecture diagram `phase1-oop-concepts.svg` and provides detailed explanations of each concept.

## Table of Contents
1. [Encapsulation](#1-encapsulation---data-hiding)
2. [Constructors & this Keyword](#2-constructors--this-keyword)
3. [Inheritance](#3-inheritance---code-reuse)
4. [Polymorphism](#4-polymorphism---many-forms)
5. [Interfaces vs Abstract Classes](#5-interfaces-vs-abstract-classes)
6. [Composition Over Inheritance](#6-composition-over-inheritance)

---

## 1. Encapsulation - Data Hiding

### What is it?
Encapsulation bundles data (fields) and methods that operate on that data into a single unit (class) and restricts direct access to internal state.

### C vs Java Comparison

**C Approach (No Encapsulation):**
```c
struct BankAccount {
    int accountNumber;
    double balance;  // Public - anyone can modify!
};

// Problem: No validation
struct BankAccount acc = {1001, 1000.0};
acc.balance = -500;  // Oops! Negative balance allowed
```

**Java Approach (With Encapsulation):**
```java
public class BankAccount {
    private int accountNumber;    // Hidden from outside
    private double balance;        // Protected

    // Controlled access with validation
    public void deposit(double amount) {
        if (amount > 0) {           // Validation!
            balance += amount;
        } else {
            System.out.println("Invalid amount!");
        }
    }

    public double getBalance() {    // Read-only access
        return balance;
    }
}
```

### Access Modifiers

| Modifier | Class | Package | Subclass | World |
|----------|-------|---------|----------|-------|
| `private` | ✅ | ❌ | ❌ | ❌ |
| default (no modifier) | ✅ | ✅ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

### Best Practices
- **Always** make fields `private`
- Provide `public` getters/setters only when needed
- Add validation in setters
- Use meaningful method names (e.g., `deposit()` instead of `setBalance()`)

### Real-World Analogy
Think of a bank ATM:
- You can't directly access the vault (private balance)
- You interact through controlled operations (deposit/withdraw methods)
- The ATM validates your actions (amount > 0)

---

## 2. Constructors & this Keyword

### Constructors

A constructor is a special method that initializes an object when it's created.

**Key Characteristics:**
- Same name as the class
- No return type (not even `void`)
- Called automatically when using `new`

**Example:**
```java
public class BankAccount {
    private int accountNumber;
    private double balance;

    // Constructor
    public BankAccount(int accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
    }
}

// Usage
BankAccount acc = new BankAccount(1001, 1000.0);  // Constructor called here
```

### The `this` Keyword

`this` is a reference to the current object.

**Use Cases:**

#### 1. Distinguish Fields from Parameters
```java
public BankAccount(int accountNumber, double balance) {
    this.accountNumber = accountNumber;  // this.field = parameter
    this.balance = balance;
}
```

Without `this`:
```java
public BankAccount(int accountNumber, double balance) {
    accountNumber = accountNumber;  // ❌ Assigns parameter to itself!
    balance = balance;              // ❌ Doesn't set the field
}
```

#### 2. Call Another Constructor (Constructor Chaining)
```java
public BankAccount(int accountNumber) {
    this(accountNumber, 0.0);  // Calls the 2-parameter constructor
}

public BankAccount(int accountNumber, double balance) {
    this.accountNumber = accountNumber;
    this.balance = balance;
}
```

#### 3. Pass Current Object as Parameter
```java
public void registerAccount() {
    AccountRegistry.register(this);  // Pass current object
}
```

### Constructor Overloading

Multiple constructors with different parameters:

```java
public class BankAccount {
    private int accountNumber;
    private double balance;

    // Constructor 1: Both parameters
    public BankAccount(int accountNumber, double balance) {
        this.accountNumber = accountNumber;
        this.balance = balance;
    }

    // Constructor 2: Account number only (default balance to 0)
    public BankAccount(int accountNumber) {
        this(accountNumber, 0.0);  // Calls Constructor 1
    }

    // Constructor 3: No parameters (generate account number)
    public BankAccount() {
        this(generateAccountNumber(), 0.0);  // Calls Constructor 1
    }
}
```

### Default Constructor

If you don't write any constructor, Java provides a default no-arg constructor:

```java
public class Simple {
    // Java automatically adds:
    // public Simple() { }
}
```

**Important:** If you write ANY constructor, Java won't provide the default one!

---

## 3. Inheritance - Code Reuse

### What is it?
Inheritance allows a class (child/subclass) to inherit fields and methods from another class (parent/superclass).

### Syntax
```java
public class SavingsAccount extends BankAccount {
    // SavingsAccount inherits all fields and methods from BankAccount
}
```

### Example

**Parent Class:**
```java
public class BankAccount {
    private int accountNumber;
    private double balance;

    public BankAccount(int accountNumber, double balance) {
        this.accountNumber = accountNumber;
        this.balance = balance;
    }

    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        }
    }

    public boolean withdraw(double amount) {
        if (amount > 0 && balance >= amount) {
            balance -= amount;
            return true;
        }
        return false;
    }

    public double getBalance() {
        return balance;
    }
}
```

**Child Class:**
```java
public class SavingsAccount extends BankAccount {
    private double interestRate;
    private static final double MIN_BALANCE = 100.0;

    // Constructor
    public SavingsAccount(int accountNumber, double balance, double interestRate) {
        super(accountNumber, balance);  // Call parent constructor
        this.interestRate = interestRate;
    }

    // New method (not in parent)
    public void applyInterest() {
        double interest = getBalance() * interestRate;
        deposit(interest);  // Use inherited method
    }

    // Override parent method
    @Override
    public boolean withdraw(double amount) {
        if (getBalance() - amount >= MIN_BALANCE) {
            return super.withdraw(amount);  // Call parent's withdraw
        }
        System.out.println("Cannot withdraw: minimum balance required");
        return false;
    }
}
```

### The `super` Keyword

`super` refers to the parent class.

**Use Cases:**

#### 1. Call Parent Constructor
```java
public SavingsAccount(int accountNumber, double balance, double interestRate) {
    super(accountNumber, balance);  // Must be FIRST line
    this.interestRate = interestRate;
}
```

#### 2. Call Parent Method
```java
@Override
public boolean withdraw(double amount) {
    // Custom logic first
    if (getBalance() - amount >= MIN_BALANCE) {
        return super.withdraw(amount);  // Call parent's implementation
    }
    return false;
}
```

#### 3. Access Parent Field (if protected)
```java
// In parent class
protected double balance;

// In child class
public void showBalance() {
    System.out.println(super.balance);  // Access parent's field
}
```

### Inheritance Chain

Java supports single inheritance only (one parent per class), but you can have inheritance chains:

```
Object (root of all Java classes)
  ↑
BankAccount
  ↑
SavingsAccount
  ↑
PremiumSavingsAccount
```

### What Gets Inherited?

| Item | Inherited? | Accessible? |
|------|------------|-------------|
| `public` fields/methods | ✅ | ✅ |
| `protected` fields/methods | ✅ | ✅ |
| default fields/methods | ✅ | ✅ (same package) |
| `private` fields/methods | ✅ | ❌ (use getters/setters) |
| Constructors | ❌ | (use `super()`) |
| `static` methods | ✅ | ✅ (but not overridden) |

---

## 4. Polymorphism - Many Forms

### What is it?
Polymorphism allows objects of different types to be treated as objects of a common parent type. The actual method called is determined at runtime.

### Types of Polymorphism

#### 1. Compile-time Polymorphism (Method Overloading)
Same method name, different parameters:

```java
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public double add(double a, double b) {  // Different parameter types
        return a + b;
    }

    public int add(int a, int b, int c) {    // Different number of parameters
        return a + b + c;
    }
}
```

#### 2. Runtime Polymorphism (Method Overriding)
Child class provides specific implementation of parent method:

```java
BankAccount[] accounts = {
    new BankAccount(1001, 1000),
    new SavingsAccount(1002, 5000, 0.05),
    new CheckingAccount(1003, 2000)
};

for (BankAccount acc : accounts) {
    acc.withdraw(100);  // Calls correct withdraw() for each type!
}
```

**What happens at runtime:**
- First iteration: Calls `BankAccount.withdraw()`
- Second iteration: Calls `SavingsAccount.withdraw()` (overridden)
- Third iteration: Calls `CheckingAccount.withdraw()` (overridden)

### Method Overriding Rules

1. **Same method signature** (name, parameters, return type)
2. **Cannot reduce access level**
   ```java
   // Parent
   public void withdraw(double amount) { }

   // Child - VALID
   public void withdraw(double amount) { }

   // Child - INVALID (can't reduce from public to private)
   private void withdraw(double amount) { }
   ```

3. **Use `@Override` annotation** (not required but recommended)
   ```java
   @Override  // Compiler checks this is actually overriding
   public boolean withdraw(double amount) {
       // implementation
   }
   ```

4. **Cannot override `final` methods**
   ```java
   // Parent
   public final void deposit(double amount) { }

   // Child - COMPILE ERROR
   @Override
   public void deposit(double amount) { }  // Can't override final
   ```

### Real-World Example

```java
// Payment processing system
public class PaymentProcessor {
    public void processPayment(Payment payment) {
        payment.process();  // Polymorphism in action
    }
}

Payment[] payments = {
    new CreditCardPayment(100),
    new PayPalPayment(200),
    new BitcoinPayment(300)
};

PaymentProcessor processor = new PaymentProcessor();
for (Payment payment : payments) {
    processor.processPayment(payment);  // Each calls their own process()
}
```

### Benefits
- **Flexibility**: Add new types without changing existing code
- **Extensibility**: Easy to extend with new subclasses
- **Maintainability**: Code written against interfaces/parent classes

---

## 5. Interfaces vs Abstract Classes

### Interface

A contract specifying what a class can do (but not how).

**Characteristics:**
- All methods are `abstract` by default (Java 8+ allows `default` methods)
- Cannot have instance variables (only `static final` constants)
- A class can implement multiple interfaces
- Use `implements` keyword

**Example:**
```java
public interface Drawable {
    void draw();           // abstract method
    void resize(double scale);

    // Java 8+ default method
    default void display() {
        System.out.println("Displaying...");
    }

    // Constant
    int MAX_SIZE = 1000;
}

public class Circle implements Drawable {
    @Override
    public void draw() {
        System.out.println("Drawing circle");
    }

    @Override
    public void resize(double scale) {
        // resize implementation
    }
}
```

### Abstract Class

A partially implemented class that can't be instantiated.

**Characteristics:**
- Can have both abstract and concrete methods
- Can have instance variables
- Can have constructors
- A class can extend only one abstract class
- Use `extends` keyword

**Example:**
```java
public abstract class Shape {
    protected String color;  // Instance variable

    // Constructor
    public Shape(String color) {
        this.color = color;
    }

    // Abstract method (must be implemented by child)
    public abstract double calculateArea();

    // Concrete method (already implemented)
    public void printInfo() {
        System.out.println("Color: " + color);
        System.out.println("Area: " + calculateArea());
    }
}

public class Circle extends Shape {
    private double radius;

    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }

    @Override
    public double calculateArea() {
        return Math.PI * radius * radius;
    }
}
```

### Comparison Table

| Feature | Interface | Abstract Class |
|---------|-----------|----------------|
| Methods | Abstract (default in Java 8+) | Both abstract and concrete |
| Variables | Only constants (`static final`) | Any type |
| Constructor | No | Yes |
| Multiple inheritance | Yes (implement multiple) | No (extend only one) |
| Access modifiers | All public | Any modifier |
| When to use | Define capability/contract | Share code among related classes |

### When to Use Which?

**Use Interface when:**
- You want to define a contract/capability
- Unrelated classes should share behavior
- You need multiple inheritance
- Examples: `Serializable`, `Comparable`, `Runnable`

```java
// Different classes sharing a capability
public interface Flyable {
    void fly();
}

public class Bird implements Flyable {
    public void fly() { /* bird flying */ }
}

public class Airplane implements Flyable {
    public void fly() { /* airplane flying */ }
}
```

**Use Abstract Class when:**
- Classes are related and share common code
- You need to share state (instance variables)
- You want to provide default implementations
- Examples: `Animal`, `Shape`, `Vehicle`

```java
public abstract class Animal {
    protected String name;

    public Animal(String name) {
        this.name = name;
    }

    // Common method
    public void sleep() {
        System.out.println(name + " is sleeping");
    }

    // Each animal makes different sound
    public abstract void makeSound();
}

public class Dog extends Animal {
    public Dog(String name) {
        super(name);
    }

    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
}
```

### Modern Java (8+) Interface Features

```java
public interface ModernInterface {
    // Abstract method (classic)
    void doSomething();

    // Default method (Java 8+)
    default void doSomethingElse() {
        System.out.println("Default implementation");
    }

    // Static method (Java 8+)
    static void utilityMethod() {
        System.out.println("Utility method");
    }

    // Private method (Java 9+)
    private void helperMethod() {
        System.out.println("Helper for default methods");
    }
}
```

---

## 6. Composition Over Inheritance

### The Problem with Deep Inheritance

**Bad Example:**
```java
// Inheritance hierarchy getting out of control
class Entity { }
class MovableEntity extends Entity { }
class AnimatedEntity extends MovableEntity { }
class SoundEntity extends AnimatedEntity { }
class Player extends SoundEntity { }

// Problems:
// 1. Player inherits everything (even things it doesn't need)
// 2. Hard to change behavior
// 3. Rigid structure
// 4. What if we want Player that's not Animated but has Sound?
```

### The Solution: Composition

Instead of IS-A relationship (inheritance), use HAS-A relationship (composition).

**Good Example:**
```java
// Components (capabilities)
public interface MovementComponent {
    void move(int dx, int dy);
}

public interface HealthComponent {
    void takeDamage(int amount);
    void heal(int amount);
    int getHealth();
}

public interface InventoryComponent {
    void addItem(Item item);
    void removeItem(Item item);
}

// Entity composed of components
public class Player {
    private Position position;
    private MovementComponent movement;
    private HealthComponent health;
    private InventoryComponent inventory;

    public Player(MovementComponent movement,
                  HealthComponent health,
                  InventoryComponent inventory) {
        this.position = new Position(0, 0);
        this.movement = movement;
        this.health = health;
        this.inventory = inventory;
    }

    public void move(int dx, int dy) {
        movement.move(dx, dy);  // Delegate to component
    }

    public void takeDamage(int amount) {
        health.takeDamage(amount);  // Delegate to component
    }

    // Easy to add/remove/swap components!
    public void setMovement(MovementComponent newMovement) {
        this.movement = newMovement;
    }
}
```

### Benefits of Composition

1. **Flexibility**: Mix and match components at runtime
   ```java
   Player player = new Player(
       new WalkMovement(),    // Can swap to FlyMovement later!
       new StandardHealth(),
       new LargeInventory()
   );

   // Later in game...
   player.setMovement(new FlyMovement());  // Player can now fly!
   ```

2. **Reusability**: Components can be shared across unrelated classes
   ```java
   // Both Player and Enemy can have health
   Player player = new Player(..., new StandardHealth(), ...);
   Enemy enemy = new Enemy(..., new StandardHealth(), ...);
   ```

3. **Testability**: Easy to mock components
   ```java
   // Unit test with mock health component
   Player player = new Player(..., new MockHealthComponent(), ...);
   ```

4. **Single Responsibility**: Each component does one thing well
   ```java
   // Each component has clear responsibility
   class WalkMovement implements MovementComponent {
       @Override
       public void move(int dx, int dy) {
           // Just handle walking logic
       }
   }
   ```

### Real-World Example: Game Entities

```java
// Unity/Unreal-style component system
public class GameObject {
    private List<Component> components = new ArrayList<>();

    public void addComponent(Component component) {
        components.add(component);
    }

    public <T extends Component> T getComponent(Class<T> type) {
        for (Component component : components) {
            if (type.isInstance(component)) {
                return type.cast(component);
            }
        }
        return null;
    }

    public void update() {
        for (Component component : components) {
            component.update();
        }
    }
}

// Usage
GameObject player = new GameObject();
player.addComponent(new SpriteRenderer());
player.addComponent(new RigidBody());
player.addComponent(new PlayerController());
player.addComponent(new HealthBar());

// Easy to create different types
GameObject enemy = new GameObject();
enemy.addComponent(new SpriteRenderer());
enemy.addComponent(new AIController());
enemy.addComponent(new HealthBar());
```

### When to Still Use Inheritance

Inheritance is fine when:
- You have a clear IS-A relationship
- The hierarchy is shallow (1-2 levels)
- The relationship won't change

```java
// Good use of inheritance
class Animal { }
class Dog extends Animal { }  // Dog IS-A Animal ✅

// Bad use of inheritance
class ArrayList extends Vector { }  // Should use composition!
```

### The Principle

> **"Favor composition over inheritance"** - Gang of Four (Design Patterns)

This doesn't mean "never use inheritance," but rather:
- **Prefer composition** as the default approach
- **Use inheritance** only when it makes sense
- **Combine both** when appropriate

---

## Summary: The Big Picture

These 6 concepts work together to create flexible, maintainable, object-oriented systems:

1. **Encapsulation**: Hide internal details, expose controlled interfaces
2. **Constructors/this**: Initialize objects properly
3. **Inheritance**: Reuse code through parent-child relationships
4. **Polymorphism**: Write flexible code that works with multiple types
5. **Interfaces/Abstract Classes**: Define contracts and share common code
6. **Composition**: Build complex objects from simple parts

### Learning Path

As you progress through Phase 1, you'll build projects that combine these concepts:

- **Module 1 (Bank Account)**: Encapsulation + Constructors + Inheritance
- **Module 2 (Shape Calculator)**: Inheritance + Polymorphism
- **Module 3 (Plugin Architecture)**: Interfaces + Polymorphism
- **Module 4 (Library Management)**: All concepts + Package organization
- **Module 5 (Game Entities)**: Composition + Interfaces
- **Final Project (Task Manager)**: Everything combined!

### From C to Java: Mental Model Shift

| C Thinking | Java Thinking |
|------------|---------------|
| Functions + Data | Objects (data + behavior) |
| Manual memory | Automatic GC |
| Direct access | Controlled access |
| Composition only | Inheritance + Composition |
| Function pointers | Polymorphism |
| Header files | Packages + Imports |

---

**Next**: Start coding! Head to `phase1-oop/01-bank-account/` and apply these concepts in your first project! 🚀

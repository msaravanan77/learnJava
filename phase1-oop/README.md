# Phase 1: Java OOP Mastery

## Overview
This phase focuses on understanding Object-Oriented Programming in Java, coming from a C background. You'll learn how Java's OOP differs from C's struct-based approach.

## Learning Objectives
- Master classes, objects, and encapsulation
- Understand inheritance vs composition
- Learn when to use interfaces vs abstract classes
- Proper package organization
- Design patterns and best practices

## Modules

### Module 1: Bank Account System
**Focus**: Classes, Objects, Encapsulation
- Learn: Constructors, getters/setters, private fields
- Build: Simple banking system with deposits/withdrawals
- Time: 2-3 hours

📁 `01-bank-account/`

---

### Module 2: Shape Calculator
**Focus**: Inheritance and Polymorphism
- Learn: `extends` keyword, method overriding, `super`, dynamic dispatch
- Build: Geometric shape calculator (Circle, Rectangle, Triangle)
- Time: 2-3 hours

📁 `02-shape-calculator/`

---

### Module 3: Plugin Architecture
**Focus**: Interfaces vs Abstract Classes
- Learn: `interface`, `implements`, design by contract
- Build: Simple plugin system that loads different implementations
- Time: 3-4 hours

📁 `03-plugin-architecture/`

---

### Module 4: Library Management System
**Focus**: Packages and Access Modifiers
- Learn: Package organization, `public`, `private`, `protected`, default
- Build: Library system with books, members, and transactions
- Time: 3-4 hours

📁 `04-library-management/`

---

### Module 5: Game Entity System
**Focus**: Composition over Inheritance
- Learn: Favor composition, avoid deep hierarchies, strategy pattern
- Build: Game entities with component-based architecture
- Time: 3-4 hours

📁 `05-game-entities/`

---

### Final Project: CLI Task Manager
**Focus**: Combine ALL Phase 1 concepts
- Build: Command-line task manager with:
  - User management (encapsulation)
  - Different task types (inheritance/polymorphism)
  - Plugin-based storage backends (interfaces)
  - Proper package structure
  - Component-based task features
- Time: 6-8 hours

📁 `final-task-manager/`

---

## Key Differences: C vs Java OOP

### C Structs vs Java Classes
```c
// C approach - data only
struct BankAccount {
    int accountNumber;
    double balance;
};

void deposit(struct BankAccount* acc, double amount) {
    acc->balance += amount;
}
```

```java
// Java approach - data + behavior together
public class BankAccount {
    private int accountNumber;
    private double balance;

    public void deposit(double amount) {
        this.balance += amount;
    }
}
```

### Key Takeaways
1. **Encapsulation**: Data + methods bundled together
2. **Access Control**: `private`, `protected`, `public` modifiers
3. **No Pointers**: References are automatic, garbage collected
4. **Inheritance**: Code reuse through `extends`
5. **Polymorphism**: Same interface, different implementations

## Progress Checklist

- [ ] Module 1: Bank Account System
- [ ] Module 2: Shape Calculator
- [ ] Module 3: Plugin Architecture
- [ ] Module 4: Library Management System
- [ ] Module 5: Game Entity System
- [ ] Final Project: CLI Task Manager
- [ ] Code review and refactoring

## Tips for Success

1. **Don't skip the exercises** - Each builds on the previous
2. **Ask for code reviews** - Push code and request feedback
3. **Compare with C** - Note what's easier/harder in Java
4. **Refactor often** - Come back and improve old code
5. **Read error messages** - Java compiler is very helpful

## Resources

- [Oracle Java Tutorials - OOP Concepts](https://docs.oracle.com/javase/tutorial/java/concepts/)
- [MOOC.fi Part 5-7](https://java-programming.mooc.fi/) - OOP sections
- [Effective Java Chapter 4](https://www.oreilly.com/library/view/effective-java/9780134686097/) - Classes and interfaces

---

**Ready to start?** Head to `01-bank-account/` and begin! 🎯

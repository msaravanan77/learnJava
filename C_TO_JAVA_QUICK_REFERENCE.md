# C to Java Quick Reference Guide

## Language Paradigm
| Aspect | C | Java |
|--------|---|------|
| Paradigm | Procedural | Object-Oriented |
| Compilation | Compiled to native code | Compiled to bytecode (runs on JVM) |
| Memory | Manual (`malloc`/`free`) | Automatic (Garbage Collection) |
| Platform | Platform-specific binary | Write once, run anywhere (WORA) |

## Basic Syntax

### Hello World
```c
// C
#include <stdio.h>

int main() {
    printf("Hello, World!\n");
    return 0;
}
```

```java
// Java
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

### Variables and Types
```c
// C - primitive types
int x = 10;
float y = 3.14f;
char c = 'A';
char* str = "Hello";  // Pointer to string

// Array
int arr[5] = {1, 2, 3, 4, 5};
```

```java
// Java - primitive types
int x = 10;
float y = 3.14f;
char c = 'A';
String str = "Hello";  // Object, not pointer

// Array
int[] arr = {1, 2, 3, 4, 5};
// or
int[] arr = new int[5];
```

### Structures vs Classes
```c
// C - struct (data only)
struct Point {
    int x;
    int y;
};

// Functions operate on structs
void movePoint(struct Point* p, int dx, int dy) {
    p->x += dx;
    p->y += dy;
}

// Usage
struct Point p = {0, 0};
movePoint(&p, 5, 10);
```

```java
// Java - class (data + behavior)
public class Point {
    private int x;
    private int y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public void move(int dx, int dy) {
        this.x += dx;
        this.y += dy;
    }
}

// Usage
Point p = new Point(0, 0);
p.move(5, 10);  // No pointers needed!
```

## Memory Management

### Dynamic Memory
```c
// C - manual memory management
int* arr = (int*)malloc(10 * sizeof(int));
if (arr == NULL) {
    // Handle allocation failure
}
// ... use array ...
free(arr);  // Must free manually!
arr = NULL;
```

```java
// Java - automatic memory management
int[] arr = new int[10];
// ... use array ...
// No free() needed - garbage collector handles it
```

### Pointers vs References
```c
// C - explicit pointers
void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int x = 5, y = 10;
swap(&x, &y);  // Pass addresses
```

```java
// Java - no pointers, only references
// Note: Can't swap primitives this way in Java
// But for objects:
public class Container {
    int value;
}

void swap(Container a, Container b) {
    int temp = a.value;
    a.value = b.value;
    b.value = temp;
}

Container x = new Container();
Container y = new Container();
x.value = 5;
y.value = 10;
swap(x, y);  // References passed automatically
```

## Object-Oriented Concepts

### Encapsulation
```c
// C - no built-in encapsulation
struct BankAccount {
    int accountNumber;
    double balance;  // Anyone can modify!
};

struct BankAccount acc = {1001, 1000.0};
acc.balance = -500;  // Oops! No protection
```

```java
// Java - encapsulation with access modifiers
public class BankAccount {
    private int accountNumber;
    private double balance;  // Protected!

    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        }
    }

    public double getBalance() {
        return balance;
    }
}

BankAccount acc = new BankAccount();
// acc.balance = -500;  // Compile error!
acc.deposit(500);  // Must use controlled method
```

### Inheritance
```c
// C - composition only
struct Animal {
    char name[50];
};

struct Dog {
    struct Animal animal;  // Composition
    char breed[50];
};
```

```java
// Java - true inheritance
public class Animal {
    protected String name;

    public void eat() {
        System.out.println(name + " is eating");
    }
}

public class Dog extends Animal {
    private String breed;

    @Override
    public void eat() {
        System.out.println(name + " the dog is eating");
    }

    public void bark() {
        System.out.println("Woof!");
    }
}
```

### Polymorphism
```c
// C - function pointers for polymorphism
struct Animal {
    void (*makeSound)(struct Animal*);
};

void dogSound(struct Animal* a) {
    printf("Woof!\n");
}

void catSound(struct Animal* a) {
    printf("Meow!\n");
}

struct Animal dog = {dogSound};
dog.makeSound(&dog);  // Woof!
```

```java
// Java - built-in polymorphism
public abstract class Animal {
    public abstract void makeSound();
}

public class Dog extends Animal {
    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
}

public class Cat extends Animal {
    @Override
    public void makeSound() {
        System.out.println("Meow!");
    }
}

Animal[] animals = {new Dog(), new Cat()};
for (Animal animal : animals) {
    animal.makeSound();  // Runtime polymorphism
}
```

## Strings

### String Handling
```c
// C - char arrays
char str[50] = "Hello";
strcat(str, " World");  // Must manage buffer size!

// String comparison
if (strcmp(str1, str2) == 0) {
    // Equal
}
```

```java
// Java - String objects (immutable)
String str = "Hello";
str = str + " World";  // Creates new string

// String comparison
if (str1.equals(str2)) {  // Never use ==
    // Equal
}

// StringBuilder for mutable strings
StringBuilder sb = new StringBuilder("Hello");
sb.append(" World");  // Modifies in place
```

## Error Handling

### Error Checking
```c
// C - return codes and errno
FILE* file = fopen("file.txt", "r");
if (file == NULL) {
    perror("Error opening file");
    return -1;
}
// ... use file ...
fclose(file);
```

```java
// Java - exceptions
try {
    FileReader file = new FileReader("file.txt");
    // ... use file ...
    file.close();
} catch (FileNotFoundException e) {
    System.err.println("Error: " + e.getMessage());
} catch (IOException e) {
    System.err.println("IO Error: " + e.getMessage());
}

// Or with try-with-resources (automatic close)
try (FileReader file = new FileReader("file.txt")) {
    // ... use file ...
} catch (IOException e) {
    System.err.println("Error: " + e.getMessage());
}
```

## Collections

### Arrays and Lists
```c
// C - fixed size arrays
int arr[10];
int size = sizeof(arr) / sizeof(arr[0]);

// Dynamic arrays require manual management
int* dynamic = (int*)malloc(10 * sizeof(int));
// ... later need to resize ...
dynamic = (int*)realloc(dynamic, 20 * sizeof(int));
free(dynamic);
```

```java
// Java - arrays (fixed size)
int[] arr = new int[10];
int size = arr.length;

// ArrayList (dynamic size)
ArrayList<Integer> list = new ArrayList<>();
list.add(1);
list.add(2);
list.remove(0);
int size = list.size();
// Automatic memory management!
```

## Common Patterns

### Iteration
```c
// C - traditional for loop
for (int i = 0; i < 10; i++) {
    printf("%d\n", i);
}

// Array iteration
int arr[] = {1, 2, 3, 4, 5};
int size = sizeof(arr) / sizeof(arr[0]);
for (int i = 0; i < size; i++) {
    printf("%d\n", arr[i]);
}
```

```java
// Java - traditional for loop
for (int i = 0; i < 10; i++) {
    System.out.println(i);
}

// Enhanced for loop (for-each)
int[] arr = {1, 2, 3, 4, 5};
for (int num : arr) {
    System.out.println(num);
}

// Modern streams (Java 8+)
Arrays.stream(arr).forEach(System.out::println);
```

### Function Pointers vs Lambdas
```c
// C - function pointers
int add(int a, int b) { return a + b; }
int subtract(int a, int b) { return a - b; }

typedef int (*Operation)(int, int);

int calculate(int a, int b, Operation op) {
    return op(a, b);
}

int result = calculate(5, 3, add);  // 8
```

```java
// Java - lambdas (Java 8+)
interface Operation {
    int apply(int a, int b);
}

int calculate(int a, int b, Operation op) {
    return op.apply(a, b);
}

// Lambda expressions
int result = calculate(5, 3, (a, b) -> a + b);  // 8
int result2 = calculate(5, 3, (a, b) -> a - b); // 2
```

## Key Takeaways for C Programmers

1. **No Manual Memory Management**: Let garbage collector handle it
2. **Everything is an Object** (except primitives): Even arrays
3. **No Pointers**: References are automatic and safe
4. **Strong Type System**: More compile-time checking
5. **Exception Handling**: Instead of return codes
6. **Built-in OOP**: Classes, inheritance, polymorphism
7. **Rich Standard Library**: Collections, I/O, networking, etc.
8. **Platform Independent**: Same code runs everywhere with JVM

## Things You'll Miss from C

- Direct memory control
- Pointer arithmetic
- Preprocessor macros
- Manual optimization control
- Smaller binary sizes
- Faster startup time

## Things You'll Love About Java

- No memory leaks (usually!)
- Rich standard library
- Easier string handling
- Built-in collections
- Cross-platform
- Strong IDE support
- Huge ecosystem

---

**Pro Tip**: When learning Java, stop thinking in C! Embrace objects, let go of manual memory management, and trust the garbage collector. 🎯

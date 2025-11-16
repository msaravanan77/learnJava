# Java Learning Journey - From C to Production-Ready Java

> **Philosophy**: Learn by building, not by reading. Every concept = one working project.

## 🎯 About This Journey

As a C programmer, you already understand memory, pointers, and procedural programming. This roadmap focuses on what makes Java unique: **OOP mastery, JVM ecosystem, and enterprise patterns**. Each module includes mini-projects - no dry theory!

## 📚 Recommended MOOCs (Pick One)

1. **[University of Helsinki - Java Programming (MOOC.fi)](https://java-programming.mooc.fi/)** ⭐ **HIGHLY RECOMMENDED**
   - Free, project-based, auto-graded exercises
   - Skippable basics, jump to Part 5+ (OOP)
   - 200+ coding exercises

2. **[Coursera - Object Oriented Programming in Java (UCSD)](https://www.coursera.org/learn/object-oriented-java)**
   - Strong OOP focus with real projects

3. **[Spring Academy (Official Spring Boot)](https://spring.academy/)**
   - Free official Spring training (after core Java)

## 🛤️ Learning Path

### Phase 1: Java OOP Mastery (2-3 weeks)
**Goal**: Understand Java's OOP model vs C's struct-based approach

| Topic | Mini-Project | Key Learnings |
|-------|--------------|---------------|
| Classes & Objects | Bank Account System | Encapsulation, getters/setters, constructors |
| Inheritance & Polymorphism | Shape Calculator | extends, method overriding, dynamic dispatch |
| Interfaces & Abstract Classes | Plugin Architecture | interface vs abstract, design by contract |
| Packages & Access Modifiers | Library Management System | Code organization, visibility control |
| Composition over Inheritance | Game Entity System | Favor composition, avoid deep hierarchies |

**Hands-on**: Build a **CLI Task Manager** using all OOP concepts

📁 Code: `phase1-oop/`

---

### Phase 2: Java Core Features (2 weeks)
**Goal**: Master Java-specific features missing in C

| Topic | Mini-Project | Key Learnings |
|-------|--------------|---------------|
| Exceptions & Error Handling | File Processor with Validation | try-catch-finally, custom exceptions, checked vs unchecked |
| Collections Framework | Student Grade Analyzer | List, Set, Map, when to use what |
| Generics | Type-Safe Cache Implementation | Type parameters, bounded types, wildcards |
| Enums & Records | Config Manager | Modern Java data modeling |
| String & StringBuilder | Log Parser | String immutability, performance |

**Hands-on**: Build a **CSV Data Processor** with error handling, collections, and generics

📁 Code: `phase2-core/`

---

### Phase 3: Modern Java (Java 8+) (2 weeks)
**Goal**: Functional programming meets OOP

| Topic | Mini-Project | Key Learnings |
|-------|--------------|---------------|
| Lambda Expressions | Event Handler System | Functional interfaces, closure concepts |
| Streams API | Data Analytics Pipeline | map, filter, reduce, collectors |
| Optional | Safe API Design | Avoiding null pointer exceptions |
| Date/Time API | Scheduling System | java.time package (vs old Date) |
| Method References | Sorting & Filtering Engine | :: operator, cleaner code |

**Hands-on**: Build a **Log Analyzer** that processes large files using streams and lambdas

📁 Code: `phase3-modern-java/`

---

### Phase 4: Concurrency & Multithreading (1.5 weeks)
**Goal**: Thread-safe programming (crucial for server apps)

| Topic | Mini-Project | Key Learnings |
|-------|--------------|---------------|
| Threads & Runnables | Parallel File Downloader | Thread basics, lifecycle |
| Synchronization | Thread-Safe Counter | synchronized, volatile, race conditions |
| Executor Framework | Task Queue System | Thread pools, Future, Callable |
| CompletableFuture | Async HTTP Client | Async programming, chaining |
| Concurrent Collections | Producer-Consumer | BlockingQueue, ConcurrentHashMap |

**Hands-on**: Build a **Multi-threaded Web Scraper** with thread pool

📁 Code: `phase4-concurrency/`

---

### Phase 5: I/O, Serialization & Networking (1 week)
**Goal**: Real-world data handling

| Topic | Mini-Project | Key Learnings |
|-------|--------------|---------------|
| File I/O (NIO.2) | Directory Scanner | Paths, Files, try-with-resources |
| Serialization | Object Persistence Layer | Serializable, transient, best practices |
| Networking (Sockets) | Chat Server/Client | TCP/UDP, client-server model |
| HTTP Clients | REST API Consumer | HttpClient (Java 11+) |

**Hands-on**: Build a **Simple HTTP Server** from scratch using sockets

📁 Code: `phase5-io-networking/`

---

### Phase 6: Build Tools & Testing (1 week)
**Goal**: Professional development workflow

| Topic | Mini-Project | Key Learnings |
|-------|--------------|---------------|
| Maven Basics | Multi-module Project Setup | pom.xml, dependencies, lifecycle |
| JUnit 5 | Test Suite for Previous Projects | @Test, assertions, parameterized tests |
| Mockito | Testing with Dependencies | Mocking, stubbing, verification |
| Test-Driven Development | Calculator Library (TDD) | Write tests first |

**Hands-on**: Retrofit **Phase 2 CSV Processor** with full test coverage

📁 Code: `phase6-build-test/`

---

### Phase 7: Spring Core & Dependency Injection (1.5 weeks)
**Goal**: Understanding Spring's magic

| Topic | Mini-Project | Key Learnings |
|-------|--------------|---------------|
| IoC Container | Bean Configuration | ApplicationContext, bean lifecycle |
| Dependency Injection | Service Layer Pattern | @Autowired, constructor injection |
| Spring Annotations | Annotation-based Config | @Component, @Service, @Repository |
| AOP Basics | Logging Aspect | Cross-cutting concerns |
| Properties & Profiles | Multi-environment Config | @Value, application.properties |

**Hands-on**: Build a **Book Library Backend** (no web yet, just services)

📁 Code: `phase7-spring-core/`

---

### Phase 8: Spring Boot & REST APIs (2 weeks)
**Goal**: Build production-ready microservices

| Topic | Mini-Project | Key Learnings |
|-------|--------------|---------------|
| Spring Boot Basics | REST API Scaffold | @SpringBootApplication, auto-config |
| REST Controllers | CRUD API | @RestController, @RequestMapping |
| JPA & Hibernate | Database Integration | @Entity, repositories, relationships |
| Validation & Exception Handling | Robust API | @Valid, @ControllerAdvice |
| Spring Security | Authentication API | JWT, basic auth, role-based access |

**Hands-on**: Build a **Task Management REST API** with PostgreSQL

📁 Code: `phase8-spring-boot/`

---

### Phase 9: Real-World Project (2-3 weeks)
**Goal**: Combine everything into production-grade app

**Project Options** (pick one):
1. **Expense Tracker API** - REST API with categories, reports, user auth
2. **URL Shortener** - Like bit.ly with analytics and QR codes
3. **Code Snippet Manager** - Store, tag, and search code snippets (useful for your learning!)
4. **CI/CD Dashboard** - Monitor build pipelines (integrate with Jenkins API)

**Requirements**:
- Spring Boot REST API
- PostgreSQL with JPA
- JWT authentication
- Unit + Integration tests (80%+ coverage)
- Docker containerization
- Basic CI/CD (GitHub Actions)
- API documentation (Swagger/OpenAPI)

📁 Code: `phase9-capstone/`

---

## 📖 Recommended Resources

### Books (for reference, not cover-to-cover reading)
- **Effective Java (3rd Edition)** by Joshua Bloch - Best practices bible
- **Head First Design Patterns** - OOP patterns in Java context
- **Spring in Action (6th Edition)** - Spring Boot deep dive

### Practice Platforms
- **[LeetCode](https://leetcode.com/)** - Daily problems (easy/medium)
- **[Exercism Java Track](https://exercism.org/tracks/java)** - Mentored exercises
- **[CodeWars](https://www.codewars.com/)** - Kata challenges

### Communities
- **r/learnjava** - Beginner-friendly Reddit
- **Spring Boot Discord** - Official community
- **Stack Overflow** - Tag: [java] [spring-boot]

---

## 🔄 Review Process

After completing each mini-project:
1. Push code to GitHub
2. Request code review (from me!)
3. Refactor based on feedback
4. Document learnings in module README

---

## 📊 Progress Tracking

| Phase | Status | Completion Date | Notes |
|-------|--------|-----------------|-------|
| Phase 1: OOP Mastery | 🔜 Not Started | - | - |
| Phase 2: Core Features | 🔜 Not Started | - | - |
| Phase 3: Modern Java | 🔜 Not Started | - | - |
| Phase 4: Concurrency | 🔜 Not Started | - | - |
| Phase 5: I/O & Networking | 🔜 Not Started | - | - |
| Phase 6: Build & Test | 🔜 Not Started | - | - |
| Phase 7: Spring Core | 🔜 Not Started | - | - |
| Phase 8: Spring Boot | 🔜 Not Started | - | - |
| Phase 9: Capstone | 🔜 Not Started | - | - |

---

## 🚀 Getting Started

### Environment Setup
```bash
# Install Java 17+ (LTS)
java -version  # Verify installation

# Install Maven
mvn -version

# Your IDE (pick one)
# - IntelliJ IDEA Community (Recommended)
# - VS Code with Java extensions
# - Eclipse
```

### Ready to Start?
1. Complete environment setup
2. Start with Phase 1, Module 1: Bank Account System
3. Code → Test → Review → Iterate
4. Update progress table as you go

---

## 💡 Learning Tips from a C Programmer's Perspective

| C Concept | Java Equivalent | Key Difference |
|-----------|-----------------|----------------|
| `struct` | `class` | Classes have behavior (methods) + data |
| Pointers | References | No pointer arithmetic, garbage collected |
| `malloc/free` | `new` | Automatic memory management (GC) |
| Header files | `import` | Package-based organization |
| `void*` | `Object` / Generics | Type-safe polymorphism |
| Function pointers | Lambdas / Method refs | First-class functions (Java 8+) |
| Manual locking | `synchronized` | Built-in monitors |
| Preprocessor | Annotations | Metadata-driven programming |

---

**Next Step**: Set up Java 17+ and Maven, then dive into Phase 1! 🎯

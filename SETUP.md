# Environment Setup Guide

## Quick Start (Ubuntu/Debian Linux)

### 1. Install Java 17 (LTS)
```bash
# Update package index
sudo apt update

# Install Java 17 JDK
sudo apt install openjdk-17-jdk -y

# Verify installation
java -version
javac -version
```

Expected output:
```
openjdk version "17.0.x" ...
```

### 2. Install Maven
```bash
# Install Maven
sudo apt install maven -y

# Verify installation
mvn -version
```

Expected output:
```
Apache Maven 3.x.x
Maven home: /usr/share/maven
Java version: 17.0.x
```

### 3. Set Up IDE (Choose One)

#### Option A: IntelliJ IDEA Community (Recommended)
```bash
# Download and install via snap
sudo snap install intellij-idea-community --classic

# Or download from: https://www.jetbrains.com/idea/download/
```

#### Option B: VS Code with Java Extensions
```bash
# Install VS Code
sudo snap install code --classic

# Install Java Extension Pack from marketplace
code --install-extension vscjava.vscode-java-pack
```

#### Option C: Eclipse IDE
```bash
# Download from: https://www.eclipse.org/downloads/
wget https://mirror.download.eclipse.org/technology/epp/downloads/release/2024-09/R/eclipse-java-2024-09-R-linux-gtk-x86_64.tar.gz
tar -xzf eclipse-java-2024-09-R-linux-gtk-x86_64.tar.gz
sudo mv eclipse /opt/
```

### 4. Configure Git (if not already done)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 5. Verify Everything Works
```bash
cd learnJava/phase1-oop/01-bank-account
javac BankAccount.java
java BankAccount
```

## Environment Variables (Optional but Recommended)

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

Apply changes:
```bash
source ~/.bashrc
```

## Troubleshooting

### Issue: `javac: command not found`
**Solution**: Java JDK not installed correctly
```bash
sudo apt install openjdk-17-jdk -y
which javac  # Should show /usr/bin/javac
```

### Issue: Multiple Java versions installed
**Solution**: Set default Java version
```bash
sudo update-alternatives --config java
sudo update-alternatives --config javac
```

### Issue: Maven build fails
**Solution**: Clean Maven cache
```bash
rm -rf ~/.m2/repository
```

## Next Steps

Once environment is ready:
1. Navigate to `phase1-oop/01-bank-account/`
2. Read the README.md
3. Start coding!
4. Test your code: `javac *.java && java Main`

---

**Ready?** Let's start learning Java! 🚀

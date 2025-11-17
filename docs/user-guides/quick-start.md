# User Guide - Quick Start

Welcome to Workspace Intelligence! This guide will help you get started with AI-powered code search and completion.

## What is Workspace Intelligence?

Workspace Intelligence is an AI-powered coding assistant that provides:

- 🔍 **Semantic Code Search**: Find code using natural language
- 🤖 **AI Code Completion**: Context-aware code suggestions
- 💡 **Code Understanding**: Explain and analyze your codebase
- 📚 **Codebase Q&A**: Ask questions about your code

---

## Installation

### VSCode Extension

1. Open VSCode
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Workspace Intelligence"
4. Click **Install**

### IntelliJ Plugin

1. Open IntelliJ IDEA
2. Go to Settings → Plugins
3. Search for "Workspace Intelligence"
4. Click **Install** and restart IDE

---

## Initial Setup

### 1. Sign In

After installation:

1. Click the Workspace Intelligence icon in your IDE
2. Click **Sign In**
3. Authorize the extension
4. You're ready to go!

### 2. Index Your Workspace

For first-time setup:

1. Open your project in the IDE
2. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Type: **"Workspace Intelligence: Index Workspace"**
4. Wait for indexing to complete (progress shown in status bar)

**Indexing Time**: ~5 seconds per 1000 files

---

## Features & Usage

### 1. 🔍 Semantic Code Search

**Find code using natural language:**

#### Method 1: Command Palette
1. Open Command Palette (Ctrl+Shift+P)
2. Type: **"Workspace Intelligence: Search Code"**
3. Enter your query: *"function that validates email addresses"*
4. Select from results

#### Method 2: Search Panel
1. Click Workspace Intelligence icon
2. Type your query in the search box
3. Browse results with preview

**Example Queries:**
- "authentication logic"
- "database connection setup"
- "API endpoints for users"
- "error handling in payment"

---

### 2. 🤖 AI Code Completion

**Get intelligent code suggestions as you type:**

#### Inline Completions (Like Copilot)

Just start typing! Completions appear automatically as ghost text.

```java
public void processPayment(// Press Tab to accept suggestion
```

**Keyboard Shortcuts:**
- **Tab**: Accept suggestion
- **Esc**: Dismiss suggestion
- **Alt+]**: Next suggestion
- **Alt+[**: Previous suggestion

#### Completion Settings

1. Open Settings
2. Search: "Workspace Intelligence"
3. Configure:
   - Auto-trigger delay
   - Max suggestions
   - Temperature (creativity)

---

### 3. 💡 Explain Code

**Understand any piece of code:**

1. Select code in editor
2. Right-click → **"Workspace Intelligence: Explain Code"**
3. View explanation in side panel

**Example:**
```java
// Select this code and ask for explanation
public String hash(String password) {
    return BCrypt.hashpw(password, BCrypt.gensalt(12));
}
```

**Explanation will cover:**
- What the code does
- How it works
- Security considerations
- Best practices

---

### 4. 🔄 Refactor Code

**Get AI-powered refactoring suggestions:**

1. Select code
2. Right-click → **"Workspace Intelligence: Suggest Refactoring"**
3. Review suggestions
4. Apply changes

**Common Refactorings:**
- Extract method
- Simplify logic
- Improve naming
- Optimize performance
- Enhance error handling

---

### 5. 🧪 Generate Tests

**Automatically generate unit tests:**

1. Place cursor in function
2. Command Palette: **"Workspace Intelligence: Generate Tests"**
3. Review generated tests
4. Edit and save

**Generated Tests Include:**
- Happy path scenarios
- Edge cases
- Error conditions
- Mocking setup

---

### 6. 💬 Chat with Codebase

**Ask questions about your code:**

1. Click **Chat** icon
2. Ask questions:
   - "Where is user authentication implemented?"
   - "How does the payment flow work?"
   - "What database models exist?"
   - "Show me all API endpoints"

**Chat Features:**
- Context-aware responses
- Code references
- File navigation
- Follow-up questions

---

## Tips & Tricks

### Improve Search Results

**Be specific:**
- ❌ "user code"
- ✅ "user authentication with JWT tokens"

**Use technical terms:**
- ❌ "code that saves stuff"
- ✅ "repository pattern for database persistence"

**Mention technologies:**
- ❌ "API endpoint"
- ✅ "REST API endpoint using Spring Boot"

---

### Get Better Completions

**1. Provide context with comments:**
```java
// Validate email format and check if domain exists
public boolean validateEmail(String email) {
    // Completion will understand the intent
}
```

**2. Use descriptive function names:**
```java
// Good - clear intent
public void sendPasswordResetEmail(User user) {

// Bad - unclear intent
public void process(User user) {
```

**3. Write type annotations:**
```python
# Good - completions know types
def calculate_total(prices: List[float]) -> float:

# Bad - completions must guess types
def calculate_total(prices):
```

---

### Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Search Code | Ctrl+Shift+F | Cmd+Shift+F |
| Explain Code | Ctrl+Shift+E | Cmd+Shift+E |
| Open Chat | Ctrl+Shift+C | Cmd+Shift+C |
| Accept Completion | Tab | Tab |
| Dismiss Completion | Esc | Esc |
| Next Suggestion | Alt+] | Opt+] |
| Previous Suggestion | Alt+[ | Opt+[ |

---

## Settings

### Access Settings

**VSCode:**
1. Settings → Extensions → Workspace Intelligence

**IntelliJ:**
1. Settings → Tools → Workspace Intelligence

### Key Settings

| Setting | Description | Default |
|---------|-------------|---------|
| **Auto-completion** | Enable inline completions | On |
| **Trigger Delay** | Delay before showing suggestions | 300ms |
| **Max Suggestions** | Number of suggestions | 3 |
| **Temperature** | Creativity level (0-1) | 0.3 |
| **Context Strategy** | How much context to use | Smart |
| **Auto-index** | Auto-index on file changes | On |
| **Telemetry** | Share usage data | Off |

---

## Privacy & Security

### What Data is Sent?

**Sent to our servers:**
- Code snippets (for completion context)
- Search queries
- File structure (not content)
- Usage metrics (if enabled)

**Never sent:**
- Entire files
- API keys or secrets
- Passwords
- Personal information

### Data Retention

- Completion requests: Not stored
- Search queries: 30 days
- Indexed code: In your workspace only
- Telemetry: Anonymized, 90 days

### Opt-Out

To disable data collection:
1. Settings → Workspace Intelligence
2. Turn off **"Send Telemetry"**

---

## Troubleshooting

### Completions Not Working

**Check:**
1. Extension is activated (icon in status bar)
2. Workspace is indexed (check status)
3. Internet connection is active
4. API key is valid (if self-hosted)

**Fix:**
```
Command Palette → "Workspace Intelligence: Restart Extension"
```

### Slow Search

**Causes:**
- Large workspace (>100k files)
- First-time search (building cache)
- Network latency

**Solutions:**
- Wait for initial indexing to complete
- Use more specific queries
- Enable local mode (settings)

### Indexing Stuck

**Fix:**
```
Command Palette → "Workspace Intelligence: Clear Index and Reindex"
```

---

## FAQs

**Q: How much does it cost?**
A: See pricing page. Free tier: 1000 completions/month.

**Q: Does it work offline?**
A: Search works offline. Completions require internet (or local model).

**Q: What languages are supported?**
A: Java, Python, JavaScript, TypeScript, Go, Rust, C++, and more.

**Q: Can I use my own API keys?**
A: Yes! Configure in settings for self-hosted mode.

**Q: Is my code secure?**
A: Yes. See our [Security Whitepaper](./security.md).

---

## Getting Help

- **Documentation**: [docs.workspaceintelligence.com](https://docs.workspaceintelligence.com)
- **Community**: [Discord](https://discord.gg/workspace-intel)
- **Email Support**: support@workspaceintelligence.com
- **GitHub Issues**: [github.com/workspace-intel/issues](https://github.com/workspace-intel/issues)

---

## Next Steps

1. **Explore Advanced Features**: See [Advanced Guide](./advanced-features.md)
2. **Configure for Your Team**: See [Team Setup](./team-setup.md)
3. **API Access**: See [API Documentation](../api/openapi-spec.yaml)

---

**Last Updated**: 2025-11-17
**Version**: 1.0

# Workspace Intelligence - VSCode Extension

AI-powered code completion and chat for your workspace.

## Features

- **Semantic Code Search**: Search your codebase using natural language
- **AI Completion**: Context-aware code completion powered by LLMs
- **Chat with Codebase**: Ask questions about your code
- **Code Explanation**: Get explanations for selected code
- **Workspace Indexing**: Index your workspace for fast retrieval

## Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Compile the extension:
   ```bash
   npm run compile
   ```

3. Press F5 in VSCode to launch the extension in development mode

## Configuration

Configure the extension in VSCode settings:

- `workspaceIntelligence.apiUrl`: API Gateway URL (default: http://localhost:8080)
- `workspaceIntelligence.apiKey`: Your API key
- `workspaceIntelligence.enableAutoCompletion`: Enable/disable auto-completion

## Commands

- `Workspace Intelligence: Search Code Semantically`
- `Workspace Intelligence: Chat with Codebase`
- `Workspace Intelligence: Explain Selected Code`
- `Workspace Intelligence: Index Workspace`

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode
npm run watch

# Run linter
npm run lint
```

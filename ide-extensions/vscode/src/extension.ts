import * as vscode from 'vscode';
import axios from 'axios';

let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
    console.log('Workspace Intelligence extension activated');

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(globe) WI";
    statusBarItem.tooltip = "Workspace Intelligence";
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('workspace-intelligence.searchCode', searchCode)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('workspace-intelligence.chatWithCodebase', chatWithCodebase)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('workspace-intelligence.explainCode', explainCode)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('workspace-intelligence.indexWorkspace', indexWorkspace)
    );

    // Register inline completion provider
    const config = vscode.workspace.getConfiguration('workspaceIntelligence');
    if (config.get('enableAutoCompletion')) {
        registerCompletionProvider(context);
    }
}

function registerCompletionProvider(context: vscode.ExtensionContext) {
    const provider = vscode.languages.registerCompletionItemProvider(
        { scheme: 'file' },
        {
            async provideCompletionItems(document: vscode.TextDocument, position: vscode.Position) {
                const config = vscode.workspace.getConfiguration('workspaceIntelligence');
                const apiUrl = config.get('apiUrl') as string;
                const apiKey = config.get('apiKey') as string;

                try {
                    const response = await axios.post(
                        `${apiUrl}/api/v1/completion`,
                        {
                            file_path: document.fileName,
                            cursor_line: position.line,
                            cursor_column: position.character,
                            query: document.getText()
                        },
                        {
                            headers: { 'Authorization': `Bearer ${apiKey}` }
                        }
                    );

                    const completion = new vscode.CompletionItem(response.data.text);
                    completion.kind = vscode.CompletionItemKind.Snippet;
                    return [completion];
                } catch (error) {
                    console.error('Completion error:', error);
                    return [];
                }
            }
        },
        '.' // Trigger on dot
    );

    context.subscriptions.push(provider);
}

async function searchCode() {
    const query = await vscode.window.showInputBox({
        prompt: 'Enter search query',
        placeHolder: 'e.g., authentication logic'
    });

    if (!query) {
        return;
    }

    const config = vscode.workspace.getConfiguration('workspaceIntelligence');
    const apiUrl = config.get('apiUrl') as string;
    const apiKey = config.get('apiKey') as string;

    try {
        const response = await axios.post(
            `${apiUrl}/api/v1/search`,
            { query, top_k: 10 },
            { headers: { 'Authorization': `Bearer ${apiKey}` } }
        );

        // Display results in quickpick
        const items = response.data.results.map((result: any) => ({
            label: result.file,
            description: result.function,
            detail: `Score: ${result.score.toFixed(2)}`
        }));

        const selected = await vscode.window.showQuickPick(items);
        if (selected) {
            vscode.window.showInformationMessage(`Opening ${selected.label}`);
        }
    } catch (error) {
        vscode.window.showErrorMessage(`Search failed: ${error}`);
    }
}

async function chatWithCodebase() {
    const question = await vscode.window.showInputBox({
        prompt: 'Ask a question about your codebase',
        placeHolder: 'e.g., How does authentication work?'
    });

    if (!question) {
        return;
    }

    const config = vscode.workspace.getConfiguration('workspaceIntelligence');
    const apiUrl = config.get('apiUrl') as string;
    const apiKey = config.get('apiKey') as string;

    try {
        const response = await axios.post(
            `${apiUrl}/api/v1/chat`,
            { question },
            { headers: { 'Authorization': `Bearer ${apiKey}` } }
        );

        const panel = vscode.window.createWebviewPanel(
            'workspaceIntelligenceChat',
            'Chat Response',
            vscode.ViewColumn.Beside,
            {}
        );

        panel.webview.html = `
            <html>
                <body>
                    <h2>Answer:</h2>
                    <p>${response.data.text}</p>
                </body>
            </html>
        `;
    } catch (error) {
        vscode.window.showErrorMessage(`Chat failed: ${error}`);
    }
}

async function explainCode() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        return;
    }

    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);

    if (!selectedText) {
        vscode.window.showWarningMessage('Please select some code to explain');
        return;
    }

    // Use chat API to explain the code
    const config = vscode.workspace.getConfiguration('workspaceIntelligence');
    const apiUrl = config.get('apiUrl') as string;
    const apiKey = config.get('apiKey') as string;

    try {
        const response = await axios.post(
            `${apiUrl}/api/v1/chat`,
            { question: `Explain this code:\n\n${selectedText}` },
            { headers: { 'Authorization': `Bearer ${apiKey}` } }
        );

        vscode.window.showInformationMessage(response.data.text);
    } catch (error) {
        vscode.window.showErrorMessage(`Explanation failed: ${error}`);
    }
}

async function indexWorkspace() {
    const config = vscode.workspace.getConfiguration('workspaceIntelligence');
    const apiUrl = config.get('apiUrl') as string;
    const apiKey = config.get('apiKey') as string;

    try {
        statusBarItem.text = "$(sync~spin) Indexing...";

        await axios.post(
            `${apiUrl}/api/v1/index/workspace`,
            { workspace_path: vscode.workspace.rootPath },
            { headers: { 'Authorization': `Bearer ${apiKey}` } }
        );

        statusBarItem.text = "$(check) WI";
        vscode.window.showInformationMessage('Workspace indexed successfully');

        setTimeout(() => {
            statusBarItem.text = "$(globe) WI";
        }, 3000);
    } catch (error) {
        statusBarItem.text = "$(error) WI";
        vscode.window.showErrorMessage(`Indexing failed: ${error}`);
    }
}

export function deactivate() {
    if (statusBarItem) {
        statusBarItem.dispose();
    }
}

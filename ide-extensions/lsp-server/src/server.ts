import {
    createConnection,
    TextDocuments,
    ProposedFeatures,
    InitializeParams,
    CompletionItem,
    CompletionItemKind,
    TextDocumentPositionParams,
    TextDocumentSyncKind,
    InitializeResult
} from 'vscode-languageserver/node';

import { TextDocument } from 'vscode-languageserver-textdocument';
import axios from 'axios';

// Create a connection for the server
const connection = createConnection(ProposedFeatures.all);

// Create a simple text document manager
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);

let apiUrl: string = 'http://localhost:8080';
let apiKey: string = '';

connection.onInitialize((params: InitializeParams) => {
    const result: InitializeResult = {
        capabilities: {
            textDocumentSync: TextDocumentSyncKind.Incremental,
            completionProvider: {
                resolveProvider: true,
                triggerCharacters: ['.', '>', ':']
            }
        }
    };
    return result;
});

connection.onInitialized(() => {
    connection.console.log('Workspace Intelligence LSP Server initialized');
});

// Provide completions
connection.onCompletion(
    async (textDocumentPosition: TextDocumentPositionParams): Promise<CompletionItem[]> => {
        const document = documents.get(textDocumentPosition.textDocument.uri);
        if (!document) {
            return [];
        }

        try {
            const response = await axios.post(
                `${apiUrl}/api/v1/completion`,
                {
                    file_path: textDocumentPosition.textDocument.uri,
                    cursor_line: textDocumentPosition.position.line,
                    cursor_column: textDocumentPosition.position.character,
                    query: document.getText()
                },
                {
                    headers: { 'Authorization': `Bearer ${apiKey}` }
                }
            );

            const completionItem: CompletionItem = {
                label: 'AI Suggestion',
                kind: CompletionItemKind.Snippet,
                detail: 'Workspace Intelligence',
                documentation: response.data.text,
                insertText: response.data.text
            };

            return [completionItem];
        } catch (error) {
            connection.console.error(`Completion error: ${error}`);
            return [];
        }
    }
);

// Make the text document manager listen on the connection
documents.listen(connection);

// Listen on the connection
connection.listen();

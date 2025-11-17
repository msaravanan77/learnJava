"""
Tree-sitter manager for parsing code in multiple languages
"""

from typing import Dict, List, Optional
from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_java
import tree_sitter_javascript
import tree_sitter_typescript
import tree_sitter_go
import tree_sitter_rust


class TreeSitterManager:
    """Manages tree-sitter parsers for multiple languages"""

    def __init__(self):
        self.languages: Dict[str, Language] = {
            'python': Language(tree_sitter_python.language()),
            'java': Language(tree_sitter_java.language()),
            'javascript': Language(tree_sitter_javascript.language()),
            'typescript': Language(tree_sitter_typescript.language_typescript()),
            'go': Language(tree_sitter_go.language()),
            'rust': Language(tree_sitter_rust.language()),
        }
        self.parsers: Dict[str, Parser] = {}
        self._init_parsers()

    def _init_parsers(self):
        """Initialize parsers for each language"""
        for lang_name, language in self.languages.items():
            parser = Parser()
            parser.set_language(language)
            self.parsers[lang_name] = parser

    def parse(self, code: str, language: str) -> Optional['Tree']:
        """Parse code and return AST"""
        if language not in self.parsers:
            raise ValueError(f"Unsupported language: {language}")

        parser = self.parsers[language]
        tree = parser.parse(bytes(code, "utf8"))
        return tree

    def extract_functions(self, tree: 'Tree', language: str) -> List[Dict]:
        """Extract all functions from AST"""
        root_node = tree.root_node
        functions = []

        # Language-specific queries
        queries = {
            'python': """
                (function_definition
                    name: (identifier) @name
                    parameters: (parameters) @params
                    body: (block) @body) @function
            """,
            'java': """
                (method_declaration
                    name: (identifier) @name
                    parameters: (formal_parameters) @params
                    body: (block) @body) @method
            """,
            'javascript': """
                (function_declaration
                    name: (identifier) @name
                    parameters: (formal_parameters) @params
                    body: (statement_block) @body) @function
            """,
        }

        if language not in queries:
            return []

        query = self.languages[language].query(queries[language])
        captures = query.captures(root_node)

        current_function = {}
        for node, capture_name in captures:
            if capture_name in ['function', 'method']:
                if current_function:
                    functions.append(current_function)
                current_function = {
                    'start_line': node.start_point[0],
                    'end_line': node.end_point[0],
                    'start_byte': node.start_byte,
                    'end_byte': node.end_byte,
                }
            elif capture_name == 'name':
                current_function['name'] = node.text.decode('utf8')
            elif capture_name == 'params':
                current_function['parameters'] = node.text.decode('utf8')
            elif capture_name == 'body':
                current_function['body'] = node.text.decode('utf8')

        if current_function:
            functions.append(current_function)

        return functions


if __name__ == "__main__":
    # Example usage
    manager = TreeSitterManager()

    java_code = """
    public class Example {
        public void processData(List<String> data) {
            // Process data
            for (String item : data) {
                System.out.println(item);
            }
        }

        private int calculateSum(int a, int b) {
            return a + b;
        }
    }
    """

    tree = manager.parse(java_code, 'java')
    functions = manager.extract_functions(tree, 'java')

    for func in functions:
        print(f"Function: {func['name']}")
        print(f"Lines: {func['start_line']}-{func['end_line']}")
        print(f"Parameters: {func['parameters']}")
        print()

from flask import Flask, request, jsonify, render_template
import ast
import random
import sys
import traceback
from typing import List, Union, Any
import tempfile
import os

app = Flask(__name__)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

class ChaoticNodeTransformer(ast.NodeTransformer):
    """
    The heart of chaos - transforms AST nodes with deliberate bugs.
    Each method represents a different type of delightful mayhem.
    """
    
    def __init__(self, chaos_level: int = 5):
        self.chaos_level = chaos_level
        self.bug_probability = min(chaos_level * 0.1, 0.8)  # Max 80% chance
        self.bugs_injected = []
        self.variable_renames = {}
        
        # Funny variable suffixes
        self.bug_suffixes = ['_bug', '_oops', '_whoops', '_mystery', '_chaos', '_glitch']

    def should_inject_bug(self) -> bool:
        """Determines if we should inject a bug based on chaos level."""
        return random.random() < self.bug_probability

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Bug Type 1: Random Variable Renaming"""
        if isinstance(node.ctx, ast.Store) and self.should_inject_bug():
            original_name = node.id
            if original_name not in self.variable_renames and not original_name.startswith('_'):
                new_name = original_name + random.choice(self.bug_suffixes)
                self.variable_renames[original_name] = new_name
                self.bugs_injected.append(f"Renamed variable '{original_name}' to '{new_name}'")
        
        # Apply existing renames
        if node.id in self.variable_renames:
            node.id = self.variable_renames[node.id]
            
        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        """Bug Type 2: Off-by-One Errors in Numeric Constants"""
        if isinstance(node.value, int) and self.should_inject_bug():
            if node.value != 0:  # Don't mess with zero, that's too cruel
                adjustment = random.choice([-1, 1])
                old_value = node.value
                node.value += adjustment
                self.bugs_injected.append(f"Changed constant {old_value} to {node.value}")
                
        return self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> ast.BinOp:
        """Bug Type 3: Randomly Swap '+' and '-' in Expressions"""
        if self.should_inject_bug():
            if isinstance(node.op, ast.Add):
                node.op = ast.Sub()
                self.bugs_injected.append("Swapped '+' to '-' in expression")
            elif isinstance(node.op, ast.Sub):
                node.op = ast.Add()
                self.bugs_injected.append("Swapped '-' to '+' in expression")
                
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Bug Type 4: Random Print/Log Insertion"""
        if self.should_inject_bug() and node.body:
            debug_messages = [
                f"print(f'🐛 Entering function {node.name}')",
                f"print(f'🔍 Function {node.name} called with mysterious purposes')",
                f"print('✨ Magic happens here in {node.name}')",
                f"print(f'🎭 {node.name} is doing something... probably')"
            ]
            
            debug_stmt = ast.parse(random.choice(debug_messages)).body[0]
            node.body.insert(0, debug_stmt)
            self.bugs_injected.append(f"Added debug print to function '{node.name}'")
            
        return self.generic_visit(node)

    def visit_stmt(self, node: ast.stmt) -> Union[ast.stmt, List[ast.stmt]]:
        """Bug Type 5: Add Useless 'if True:' Wrappers"""
        if self.should_inject_bug() and not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.If)):
            if_node = ast.If(
                test=ast.Constant(value=True),
                body=[node],
                orelse=[]
            )
            self.bugs_injected.append(f"Wrapped statement in useless 'if True:' block")
            return self.generic_visit(if_node)
            
        return self.generic_visit(node)

    def visit_If(self, node: ast.If) -> ast.If:
        """Handle if statements without creating infinite recursion."""
        return self.generic_visit(node)

    def visit_For(self, node: ast.For) -> ast.For:
        """Handle for loops without creating infinite recursion.""" 
        return self.generic_visit(node)

    def visit_While(self, node: ast.While) -> ast.While:
        """Handle while loops without creating infinite recursion."""
        return self.generic_visit(node)

class DeliberateBugInjector:
    """The main orchestrator of chaos for web usage."""
    
    def __init__(self, chaos_level: int = 5):
        self.chaos_level = chaos_level
        self.transformer = ChaoticNodeTransformer(chaos_level)
        
    def inject_bugs(self, source_code: str) -> tuple[str, List[str]]:
        """Takes innocent Python code and returns it with personality."""
        try:
            # Parse the code into an AST
            tree = ast.parse(source_code)
            
            # Apply our chaotic transformations
            transformed_tree = self.transformer.visit(tree)
            
            # Convert back to source code using ast.unparse
            buggy_code = ast.unparse(transformed_tree)
            
            # Add a header comment to the buggy code
            header = f'''"""
🐛 DELIBERATELY BUGGED CODE 🐛
Chaos Level: {self.chaos_level}/10
Bugs Injected: {len(self.transformer.bugs_injected)}
Generated by: Deliberate Bug Injector Web

⚠️  WARNING: This code has been intentionally modified for educational/entertainment purposes.
⚠️  Do not use in production unless you enjoy living dangerously.
"""

'''
            
            return header + buggy_code, self.transformer.bugs_injected
            
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax in source code: {e}")

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/inject-bugs', methods=['POST'])
def inject_bugs_endpoint():
    """API endpoint to inject bugs into Python code."""
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
        
        source_code = data['code'].strip()
        chaos_level = int(data.get('chaos_level', 5))
        
        if not source_code:
            return jsonify({'error': 'Empty code provided'}), 400
        
        if chaos_level < 1 or chaos_level > 10:
            return jsonify({'error': 'Chaos level must be between 1 and 10'}), 400
        
        # Create bug injector and process code
        injector = DeliberateBugInjector(chaos_level=chaos_level)
        buggy_code, bugs_list = injector.inject_bugs(source_code)
        
        return jsonify({
            'success': True,
            'buggy_code': buggy_code,
            'bugs_injected': bugs_list,
            'chaos_level': chaos_level,
            'bug_count': len(bugs_list)
        })
        
    except ValueError as e:
        return jsonify({'error': f'Code error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.py'):
            return jsonify({'error': 'Please upload a .py file'}), 400
        
        # Read file content
        content = file.read().decode('utf-8')
        
        return jsonify({
            'success': True,
            'code': content,
            'filename': file.filename
        })
        
    except UnicodeDecodeError:
        return jsonify({'error': 'File contains invalid UTF-8 characters'}), 400
    except Exception as e:
        return jsonify({'error': f'Upload error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

"""
Improved code chunking service with semantic awareness.
Chunks at function/class boundaries instead of arbitrary line numbers.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class CodeChunk:
    """Represents a semantically meaningful chunk of code."""
    
    def __init__(
        self,
        text: str,
        start_line: int,
        end_line: int,
        chunk_type: str,  # 'class', 'function', 'file', 'import', 'docstring'
        name: Optional[str] = None,
        language: str = "python",
        context: Optional[Dict] = None
    ):
        self.text = text
        self.start_line = start_line
        self.end_line = end_line
        self.chunk_type = chunk_type
        self.name = name or "unknown"
        self.language = language
        self.context = context or {}
        self.character_count = len(text)
        self.line_count = end_line - start_line + 1


def chunk_python_file(file_path: Path, file_content: str) -> List[Dict]:
    """
    Parse Python files with AST to create semantic chunks.
    Groups related functions, classes, and maintains imports separately.
    """
    chunks = []
    lines = file_content.split('\n')
    
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        # Fallback to simple chunking if AST parsing fails
        return _chunk_by_size(file_content, max_lines=200)
    
    # === Extract file-level docstring ===
    file_docstring = ast.get_docstring(tree)
    if file_docstring:
        chunks.append({
            'text': f'"""File docstring:\n{file_docstring}\n"""',
            'start_line': 1,
            'end_line': len(file_docstring.split('\n')) + 2,
            'chunk_type': 'file_docstring',
            'name': f"{file_path.name}::module",
            'language': 'python'
        })
    
    # === Extract imports ===
    import_lines = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith(('import ', 'from ')):
            import_lines.append(line)
        elif import_lines and line.strip() and not line.strip().startswith('#'):
            # End of imports section
            break
    
    if import_lines:
        chunks.append({
            'text': '\n'.join(import_lines),
            'start_line': 1,
            'end_line': len(import_lines),
            'chunk_type': 'imports',
            'name': f"{file_path.name}::imports",
            'language': 'python'
        })
    
    # === Extract classes with their methods ===
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_start = node.lineno - 1
            class_end = node.end_lineno or len(lines)
            class_lines = lines[class_start:class_end]
            class_text = '\n'.join(class_lines)
            
            class_docstring = ast.get_docstring(node)
            description = class_docstring.split('\n')[0] if class_docstring else ""
            
            chunks.append({
                'text': class_text,
                'start_line': class_start + 1,
                'end_line': class_end,
                'chunk_type': 'class',
                'name': f"{file_path.stem}::{node.name}",
                'language': 'python',
                'context': {
                    'class_name': node.name,
                    'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    'description': description,
                    'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
                }
            })
            
            # === Extract individual methods ===
            for method in node.body:
                if isinstance(method, ast.FunctionDef):
                    method_start = method.lineno - 1
                    method_end = method.end_lineno or len(lines)
                    method_lines = lines[method_start:method_end]
                    method_text = '\n'.join(method_lines)
                    
                    method_docstring = ast.get_docstring(method)
                    
                    chunks.append({
                        'text': method_text,
                        'start_line': method_start + 1,
                        'end_line': method_end,
                        'chunk_type': 'method',
                        'name': f"{file_path.stem}::{node.name}::{method.name}",
                        'language': 'python',
                        'context': {
                            'class_name': node.name,
                            'method_name': method.name,
                            'parameters': [arg.arg for arg in method.args.args],
                            'description': method_docstring.split('\n')[0] if method_docstring else "",
                            'is_private': method.name.startswith('_'),
                            'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in method.decorator_list]
                        }
                    })
    
    # === Extract top-level functions ===
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not any(
            isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)
            if hasattr(parent, 'body') and node in parent.body
        ):
            func_start = node.lineno - 1
            func_end = node.end_lineno or len(lines)
            func_lines = lines[func_start:func_end]
            func_text = '\n'.join(func_lines)
            
            func_docstring = ast.get_docstring(node)
            
            chunks.append({
                'text': func_text,
                'start_line': func_start + 1,
                'end_line': func_end,
                'chunk_type': 'function',
                'name': f"{file_path.stem}::{node.name}",
                'language': 'python',
                'context': {
                    'function_name': node.name,
                    'parameters': [arg.arg for arg in node.args.args],
                    'description': func_docstring.split('\n')[0] if func_docstring else "",
                    'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
                }
            })
    
    return chunks


def chunk_javascript_file(file_path: Path, file_content: str) -> List[Dict]:
    """
    Parse JavaScript/TypeScript files using regex patterns to identify structures.
    (A full AST parser would require a JS parser library)
    """
    chunks = []
    lines = file_content.split('\n')
    
    # Extract file-level comments
    file_comment_match = re.match(r'^(\s*/\*[\s\S]*?\*/|^\s*//.*)', file_content)
    if file_comment_match:
        comment_text = file_comment_match.group(1)
        comment_lines = comment_text.count('\n') + 1
        chunks.append({
            'text': comment_text,
            'start_line': 1,
            'end_line': comment_lines,
            'chunk_type': 'file_comment',
            'name': f"{file_path.name}::file_doc",
            'language': 'javascript'
        })
    
    # Extract imports
    import_lines = []
    for i, line in enumerate(lines):
        if re.match(r'^\s*(import|require|export)', line):
            import_lines.append((i+1, line))
    
    if import_lines:
        import_text = '\n'.join([line for _, line in import_lines])
        chunks.append({
            'text': import_text,
            'start_line': import_lines[0][0],
            'end_line': import_lines[-1][0],
            'chunk_type': 'imports',
            'name': f"{file_path.name}::imports",
            'language': 'javascript'
        })
    
    # Extract classes
    class_pattern = r'^class\s+(\w+)'
    for match in re.finditer(class_pattern, file_content, re.MULTILINE):
        class_name = match.group(1)
        start_pos = match.start()
        start_line = file_content[:start_pos].count('\n') + 1
        
        # Find the matching closing brace
        brace_count = 0
        in_class = False
        end_line = start_line
        
        for i, line in enumerate(lines[start_line-1:], start=start_line):
            if '{' in line:
                brace_count += line.count('{')
                in_class = True
            if '}' in line:
                brace_count -= line.count('}')
                if in_class and brace_count == 0:
                    end_line = i
                    break
        
        class_text = '\n'.join(lines[start_line-1:end_line])
        chunks.append({
            'text': class_text,
            'start_line': start_line,
            'end_line': end_line,
            'chunk_type': 'class',
            'name': f"{file_path.stem}::{class_name}",
            'language': 'javascript'
        })
    
    # Extract functions
    func_pattern = r'^(async\s+)?function\s+(\w+)|const\s+(\w+)\s*=\s*(async\s*)?\('
    for match in re.finditer(func_pattern, file_content, re.MULTILINE):
        func_name = match.group(2) or match.group(3)
        start_pos = match.start()
        start_line = file_content[:start_pos].count('\n') + 1
        
        # Find function end (simple approach - find matching braces)
        brace_count = 0
        in_func = False
        end_line = start_line
        
        for i, line in enumerate(lines[start_line-1:], start=start_line):
            if '{' in line:
                brace_count += line.count('{')
                in_func = True
            if '}' in line:
                brace_count -= line.count('}')
                if in_func and brace_count == 0:
                    end_line = i
                    break
        
        func_text = '\n'.join(lines[start_line-1:end_line])
        chunks.append({
            'text': func_text,
            'start_line': start_line,
            'end_line': end_line,
            'chunk_type': 'function',
            'name': f"{file_path.stem}::{func_name}",
            'language': 'javascript'
        })
    
    return chunks


def chunk_markdown_file(file_path: Path, file_content: str) -> List[Dict]:
    """
    Parse markdown files (especially README) by sections.
    """
    chunks = []
    lines = file_content.split('\n')
    current_section = None
    section_start = 0
    section_content = []
    
    for i, line in enumerate(lines):
        # Detect headers
        if line.startswith('#'):
            # Save previous section
            if section_content:
                chunks.append({
                    'text': '\n'.join(section_content),
                    'start_line': section_start + 1,
                    'end_line': i,
                    'chunk_type': 'markdown_section',
                    'name': f"{file_path.name}::{current_section}" if current_section else f"{file_path.name}::intro",
                    'language': 'markdown'
                })
            
            # Start new section
            current_section = line.lstrip('#').strip()
            section_start = i
            section_content = [line]
        else:
            section_content.append(line)
    
    # Save last section
    if section_content:
        chunks.append({
            'text': '\n'.join(section_content),
            'start_line': section_start + 1,
            'end_line': len(lines),
            'chunk_type': 'markdown_section',
            'name': f"{file_path.name}::{current_section}" if current_section else f"{file_path.name}::conclusion",
            'language': 'markdown'
        })
    
    return chunks


def _chunk_by_size(content: str, max_lines: int = 200) -> List[Dict]:
    """
    Fallback chunking strategy - split by size with overlap.
    """
    lines = content.split('\n')
    chunks = []
    overlap = 10
    
    for i in range(0, len(lines), max_lines - overlap):
        chunk_lines = lines[i:i + max_lines]
        chunk_text = '\n'.join(chunk_lines)
        
        chunks.append({
            'text': chunk_text,
            'start_line': i + 1,
            'end_line': min(i + max_lines, len(lines)),
            'chunk_type': 'code_block',
            'name': f"chunk_{i//max_lines}",
            'language': 'unknown'
        })
    
    return chunks


def chunk_file(file_path: Path, file_content: Optional[str] = None) -> List[Dict]:
    """
    Main entry point for chunking any file type.
    Uses semantic chunking for code files, section-based chunking for markdown.
    """
    if file_content is None:
        file_content = file_path.read_text(encoding='utf-8', errors='ignore')
    
    suffix = file_path.suffix.lower()
    
    if suffix in {'.py'}:
        return chunk_python_file(file_path, file_content)
    elif suffix in {'.js', '.ts', '.jsx', '.tsx'}:
        return chunk_javascript_file(file_path, file_content)
    elif suffix in {'.md', '.markdown'}:
        return chunk_markdown_file(file_path, file_content)
    elif suffix in {'.java'}:
        # Similar to Python - would need AST parser
        return _chunk_by_size(file_content, max_lines=250)
    else:
        # Generic chunking
        return _chunk_by_size(file_content, max_lines=150)

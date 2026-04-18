"""
Improved ingestion service that orchestrates the entire pipeline.
- Processes all code files with semantic chunking
- Extracts and processes README.md
- Generates project metadata
- Creates embeddings with context enrichment
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
import re
from collections import Counter

# Import improved services
from backend.app.services.code_assist.improved_chunking_service import chunk_file
from backend.app.services.code_assist.improved_embedding_service import embed_chunks


def extract_readme_and_metadata(repo_dir: Path) -> Dict:
    """
    Extract README.md and generate project-level metadata.
    Returns metadata that helps contextualize the entire codebase.
    """
    
    metadata = {
        'project_name': repo_dir.name,
        'description': '',
        'languages': [],
        'key_files': [],
        'features': [],
        'architecture': '',
        'dependencies': []
    }
    
    # === Extract README.md ===
    readme_path = None
    for pattern in ['README.md', 'readme.md', 'README', 'readme.txt']:
        candidate = repo_dir / pattern
        if candidate.exists():
            readme_path = candidate
            break
    
    if readme_path:
        try:
            readme_content = readme_path.read_text(encoding='utf-8', errors='ignore')
            metadata['readme_content'] = readme_content
            
            # Extract structured information from README
            # Description (first paragraph)
            first_para = re.split(r'\n\n+', readme_content)[0]
            metadata['description'] = first_para[:200].strip()
            
            # Extract features section
            features_match = re.search(
                r'##\s*features?\s*\n(.*?)(?=\n##|\Z)',
                readme_content,
                re.IGNORECASE | re.DOTALL
            )
            if features_match:
                features_text = features_match.group(1)
                features = [line.strip('- * ') for line in features_text.split('\n') if line.strip()]
                metadata['features'] = features[:5]
            
            # Extract architecture section
            arch_match = re.search(
                r'##\s*(?:architecture|structure|design)\s*\n(.*?)(?=\n##|\Z)',
                readme_content,
                re.IGNORECASE | re.DOTALL
            )
            if arch_match:
                metadata['architecture'] = arch_match.group(1)[:300].strip()
                
        except Exception as e:
            print(f"Error reading README: {e}")
    
    # === Analyze directory structure for languages ===
    file_extensions = Counter()
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React',
        '.tsx': 'React/TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.sql': 'SQL',
        '.sh': 'Bash',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.json': 'JSON',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS'
    }
    
    for file_path in repo_dir.rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in language_map:
                file_extensions[ext] += 1
    
    # Get top languages
    top_langs = [language_map[ext] for ext, _ in file_extensions.most_common(3)]
    metadata['languages'] = top_langs
    
    # === Find key files ===
    key_file_patterns = [
        r'main\.py$', r'app\.py$', r'__main__\.py$',
        r'index\.js$', r'main\.js$', r'server\.js$',
        r'setup\.py$', r'package\.json$', r'requirements\.txt$',
        r'dockerfile$', r'docker-compose\.ya?ml$'
    ]
    
    key_files = []
    for file_path in repo_dir.rglob('*'):
        if file_path.is_file():
            rel_path = file_path.relative_to(repo_dir).as_posix()
            for pattern in key_file_patterns:
                if re.search(pattern, rel_path, re.IGNORECASE):
                    key_files.append(rel_path)
                    break
    
    metadata['key_files'] = list(dict.fromkeys(key_files))[:5]  # Remove duplicates, limit to 5
    
    # === Extract dependencies ===
    deps = set()
    
    # Check requirements.txt
    req_path = repo_dir / 'requirements.txt'
    if req_path.exists():
        try:
            for line in req_path.read_text().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    dep = line.split('[')[0].split('==')[0].split('>')[0].split('<')[0].strip()
                    if dep:
                        deps.add(dep)
        except:
            pass
    
    # Check package.json
    pkg_path = repo_dir / 'package.json'
    if pkg_path.exists():
        try:
            pkg_data = json.loads(pkg_path.read_text())
            for dep in pkg_data.get('dependencies', {}).keys():
                deps.add(dep)
            for dep in pkg_data.get('devDependencies', {}).keys():
                deps.add(dep)
        except:
            pass
    
    metadata['dependencies'] = list(deps)[:10]
    
    return metadata


def process_code_files(repo_dir: Path, exclude_dirs: Optional[List[str]] = None) -> List[Dict]:
    """
    Process all code files in the repository with semantic chunking.
    """
    
    if exclude_dirs is None:
        exclude_dirs = ['.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache', 'dist', 'build']
    
    all_chunks = []
    
    # File extensions to process
    processable_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java',
        '.cpp', '.c', '.cs', '.go', '.rs', '.rb',
        '.php', '.sql', '.sh', '.md', '.txt'
    }
    
    print("\n📂 Scanning repository for code files...")
    
    for file_path in repo_dir.rglob('*'):
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue
        
        if not file_path.is_file():
            continue
        
        # Skip large files (> 1MB)
        if file_path.stat().st_size > 1_000_000:
            continue
        
        # Only process known file types
        if file_path.suffix.lower() not in processable_extensions:
            continue
        
        try:
            file_content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Skip empty files
            if not file_content.strip():
                continue
            
            print(f"  Chunking: {file_path.relative_to(repo_dir)}")
            
            # Semantic chunking
            chunks = chunk_file(file_path, file_content)
            
            # Add file path to each chunk
            rel_path = file_path.relative_to(repo_dir).as_posix()
            for chunk in chunks:
                chunk['file_path'] = rel_path
                chunk['absolute_path'] = str(file_path)
            
            all_chunks.extend(chunks)
            
        except Exception as e:
            print(f"  ⚠️  Error processing {file_path.relative_to(repo_dir)}: {e}")
            continue
    
    print(f"\n✓ Found {len(all_chunks)} semantic chunks")
    return all_chunks


def ingest_repository(repo_id: str, repo_dir: Path):
    """
    Main ingestion pipeline:
    1. Extract README and project metadata
    2. Process all code files with semantic chunking
    3. Enrich chunks with metadata
    4. Generate embeddings
    5. Store in vector database
    """
    
    print(f"\n{'='*60}")
    print(f"INGESTING REPOSITORY: {repo_id}")
    print(f"{'='*60}")
    
    # === Step 1: Extract project metadata ===
    print("\n1️⃣  Extracting project metadata...")
    project_metadata = extract_readme_and_metadata(repo_dir)
    
    print(f"   Project: {project_metadata.get('project_name')}")
    print(f"   Languages: {', '.join(project_metadata.get('languages', []))}")
    print(f"   Key files: {', '.join(project_metadata.get('key_files', [])[:3])}")
    
    # === Step 2: Process code files ===
    print("\n2️⃣  Processing code files with semantic chunking...")
    chunks = process_code_files(repo_dir)
    
    if not chunks:
        print("⚠️  No code chunks found!")
        return {"status": "error", "message": "No code found to index"}
    
    # === Step 3: Add README content as chunks ===
    print("\n3️⃣  Processing README.md...")
    if 'readme_content' in project_metadata:
        readme_chunks = chunk_file(
            repo_dir / 'README.md',
            project_metadata['readme_content']
        )
        for chunk in readme_chunks:
            chunk['file_path'] = 'README.md'
            chunk['risk_level'] = 'low'
        chunks.extend(readme_chunks)
        print(f"   Added {len(readme_chunks)} README chunks")
    
    # === Step 4: Create project overview chunk ===
    print("\n4️⃣  Creating project overview chunk...")
    overview_text = f"""# Project: {project_metadata.get('project_name')}

## Description
{project_metadata.get('description', 'No description available')}

## Primary Languages
{', '.join(project_metadata.get('languages', ['Unknown']))}

## Key Files
{', '.join(project_metadata.get('key_files', []))}

## Features
{chr(10).join('- ' + f for f in project_metadata.get('features', ['Not specified']))}

## Architecture
{project_metadata.get('architecture', 'Not specified')}

## Dependencies
{', '.join(project_metadata.get('dependencies', ['None specified'])[:5])}
"""
    
    overview_chunk = {
        'text': overview_text,
        'start_line': 1,
        'end_line': 1,
        'chunk_type': 'project_metadata',
        'name': f"{repo_id}::project_overview",
        'language': 'markdown',
        'file_path': 'PROJECT_OVERVIEW',
        'risk_level': 'low',
        'context': {
            'description': project_metadata.get('description'),
            'languages': project_metadata.get('languages'),
            'features': project_metadata.get('features')
        }
    }
    chunks.insert(0, overview_chunk)
    
    # === Step 5: Generate embeddings ===
    print("\n5️⃣  Generating embeddings with semantic enrichment...")
    embedded_chunks = embed_chunks(chunks)
    
    if not embedded_chunks:
        print("⚠️  Failed to generate embeddings!")
        return {"status": "error", "message": "Embedding generation failed"}
    
    # === Step 6: Store in vector database ===
    print("\n6️⃣  Storing in vector database...")
    from backend.app.services.code_assist.improved_vector_store_service import store_embeddings
    
    try:
        store_embeddings(repo_id, embedded_chunks)
        print(f"   ✓ Stored {len(embedded_chunks)} embeddings")
    except Exception as e:
        print(f"   ✗ Storage failed: {e}")
        return {"status": "error", "message": f"Storage failed: {str(e)}"}
    
    # === Step 7: Generate summary ===
    print("\n7️⃣  Generating ingestion summary...")
    
    chunk_types = Counter(c.get('metadata', {}).get('chunk_type') for c in embedded_chunks)
    
    summary = {
        "status": "success",
        "repo_id": repo_id,
        "total_chunks": len(embedded_chunks),
        "chunk_breakdown": dict(chunk_types),
        "files_processed": len(set(c.get('file_path') for c in embedded_chunks)),
        "project_metadata": project_metadata,
        "indexing_complete": True,
        "ready_for_queries": True
    }
    
    print(f"\n{'='*60}")
    print(f"✓ INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total chunks: {summary['total_chunks']}")
    print(f"Files: {summary['files_processed']}")
    print(f"Breakdown: {dict(chunk_types)}")
    print(f"{'='*60}\n")
    
    return summary


def ingest_repository_from_path(repo_id: str, repo_path: str) -> Dict:
    """
    Convenience function to ingest from a file path.
    """
    repo_dir = Path(repo_path)
    if not repo_dir.exists():
        return {
            "status": "error",
            "message": f"Repository path not found: {repo_path}"
        }
    
    return ingest_repository(repo_id, repo_dir)


__all__ = [
    'ingest_repository',
    'ingest_repository_from_path',
    'extract_readme_and_metadata',
    'process_code_files'
]
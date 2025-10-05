import os
import json
import subprocess

def collect_git_files():
    """Use git ls-files to get tracked files and collect their contents"""
    try:
        # Get list of tracked files from git
        result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, check=True)
        file_paths = result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository or git command failed")
        return {}, 0, 0, {}
    
    # File extensions to skip (binary, generated, or build artifacts)
    skip_extensions = {
        '.pyc', '.pyo', '.pyd', '.so', '.dylib', '.dll',
        '.exe', '.bin', '.dmg', '.pkg', '.deb', '.rpm',
        '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z',
        '.jpg', '.jpeg', '.png', '.gif', '.ico', '.icns',
        '.mp3', '.mp4', '.wav', '.mov', '.avi',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.lock', '.log', '.tmp', '.cache',
        '.min.js', '.min.css',  # Minified assets
        '.blockmap'  # Electron builder files
    }

    flat_structure = {}
    file_count = 0
    total_lines = 0
    file_types = {}
    
    for file_path in file_paths:
        if not file_path:  # Skip empty lines
            continue
            
        # Skip files based on extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in skip_extensions:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Count lines in this file
                lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
                total_lines += lines
                
        except (UnicodeDecodeError, PermissionError, FileNotFoundError) as e:
            content = f"<Error reading file: {str(e)}>"
            lines = 1
            total_lines += 1

        # Store with full relative path as key
        flat_structure[file_path] = content
        file_count += 1
        
        # Track file types
        ext = file_ext or '<no extension>'
        file_types[ext] = file_types.get(ext, 0) + 1

    return flat_structure, file_count, total_lines, file_types

def validate_json(data):
    """Validate that data can be serialized as JSON"""
    try:
        json.dumps(data)
        return True, None
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    output_file = "llm-collector/results.json"
    
    print("Collecting git-tracked files...")
    structure, file_count, total_lines, file_types = collect_git_files()

    print(f"\nCodebase Summary:")
    print(f"  Total files: {file_count}")
    print(f"  Total lines: {total_lines:,}")
    print(f"  File types:")
    for ext, count in sorted(file_types.items()):
        print(f"    {ext}: {count} files")

    # Validate JSON before writing
    is_valid, error = validate_json(structure)
    if not is_valid:
        print(f"\nError: Generated structure is not valid JSON: {error}")
        exit(1)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)

    # Verify output file
    output_lines = 0
    with open(output_file, 'r', encoding='utf-8') as f:
        output_lines = sum(1 for _ in f)
    
    print(f"\nOutput:")
    print(f"  File: {output_file}")
    print(f"  Lines in JSON file: {output_lines:,}")
    print(f"  JSON is valid: ✓")
    
    # Show first few file paths as sample
    print(f"\nSample file paths (first 5):")
    for i, path in enumerate(sorted(structure.keys())[:5]):
        print(f"  {path}")
    
    if len(structure) > 5:
        print(f"  ... and {len(structure) - 5} more files")

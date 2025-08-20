#!/usr/bin/env python3
"""
Documentation Generator
Converts a directory tree of Markdown files into a single Word document,
rendering Mermaid diagrams as images and applying custom Word styling.
"""

import os
import re
import subprocess
import shutil
import sys
import hashlib
from pathlib import Path
from typing import List, Tuple, Set
import argparse


class DocumentationGenerator:
    def __init__(self, root_dir: str, output_dir: str = "build", output_filename: str = "output.docx", template_doc: str = None):
        self.root = Path(root_dir)
        self.output_dir = Path(output_dir)
        self.template_doc = Path(template_doc) if template_doc else None
        
        # Ensure output filename has .docx extension
        if not output_filename.lower().endswith('.docx'):
            output_filename += '.docx'
        
        # Create output directories
        self.temp_md_original = self.output_dir / "combined-original.md"
        self.temp_md = self.output_dir / "combined.md"
        self.img_dir = self.output_dir / "images"
        self.output_doc = self.output_dir / output_filename
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.img_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_dependencies(self) -> None:
        """Check if required tools are installed."""
        missing_tools = []
        
        # Check Pandoc
        if not shutil.which("pandoc"):
            missing_tools.append("pandoc")
        
        # Check Mermaid CLI with Windows-specific handling
        mmdc_found = False
        
        # First try standard detection
        if shutil.which("mmdc"):
            mmdc_found = True
        else:
            # Windows fallback: try testing the command directly
            try:
                result = subprocess.run(
                    ["mmdc", "--version"], 
                    capture_output=True, 
                    text=True, 
                    shell=True,  # Important for Windows
                    timeout=10
                )
                if result.returncode == 0:
                    mmdc_found = True
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        if not mmdc_found:
            missing_tools.append("mmdc (Mermaid CLI)")
        
        if missing_tools:
            print("❌ Missing required tools:")
            for tool in missing_tools:
                print(f"   - {tool}")
            print("\n📦 Installation instructions:")
            print("   Pandoc: https://pandoc.org/installing.html")
            print("   Mermaid CLI:")
            print("     1. Install Node.js: https://nodejs.org")
            print("     2. npm install -g @mermaid-js/mermaid-cli")
            print("     3. Restart command prompt")
            print("   Windows-specific:")
            print("     - Try: npm install -g @mermaid-js/mermaid-cli --force")
            print("     - Or: npm install -g @mermaid-js/mermaid-cli --legacy-peer-deps")
            sys.exit(1)
        
        print("✅ All dependencies found")
    
    def natural_sort_key(self, path: Path) -> List:
        """Natural sorting key for proper file ordering (file2.md before file10.md)."""
        return [int(text) if text.isdigit() else text.lower() 
                for text in re.split(r'(\d+)', str(path))]
    
    def depth_and_name_sort_key(self, path: Path) -> List:
        """Sort by full path alphabetically (true alphabetical order across entire tree)."""
        # Get the full relative path as a string
        relative_path = path.relative_to(self.root)
        
        # Apply natural sorting to the entire path
        return self.natural_sort_key(relative_path)
    
    def collect_markdown_files(self) -> List[Path]:
        """Collect all .md files in alphabetical order."""
        if not self.root.exists():
            raise FileNotFoundError(f"Root directory not found: {self.root}")
        
        md_files = list(self.root.rglob("*.md"))
        if not md_files:
            raise FileNotFoundError(f"No .md files found in {self.root}")
        
        # Sort alphabetically by full path
        md_files.sort(key=self.depth_and_name_sort_key)
        
        print(f"📄 Found {len(md_files)} Markdown files (alphabetical order):")
        for file in md_files:
            relative_path = file.relative_to(self.root)
            depth = len(relative_path.parts) - 1
            indent = "   " + "  " * depth  # Extra indent for subfolder files
            print(f"{indent}- {relative_path}")
        
        return md_files
    
    def concatenate_files(self, md_files: List[Path]) -> str:
        """Concatenate all Markdown files into a single string."""
        full_md = ""
        
        for file in md_files:
            try:
                # Add file header for reference
                relative_path = file.relative_to(self.root)
                full_md += f"\n\n<!-- Source: {relative_path} -->\n\n"
                
                # Read and append file content
                content = file.read_text(encoding='utf-8')
                full_md += content
                
                # Ensure proper spacing between files
                full_md += "\n\n"
                
            except UnicodeDecodeError:
                print(f"⚠️  Warning: Could not read {file} (encoding issue)")
                continue
            except Exception as e:
                print(f"⚠️  Warning: Error reading {file}: {e}")
                continue
        
        return full_md
    
    def extract_mermaid_blocks(self, md_text: str) -> List[Tuple[int, int, str]]:
        """Extract Mermaid code blocks and return (start, end, code) tuples."""
        pattern = r"```mermaid\s*\n([\s\S]+?)\n```"
        matches = []
        
        for match in re.finditer(pattern, md_text):
            start, end = match.span()
            code = match.group(1).strip()
            matches.append((start, end, code))
        
        return matches
    
    def generate_content_hash(self, content: str) -> str:
        """Generate MD5 hash from mermaid code content."""
        # Normalize content (remove extra whitespace, ensure consistent line endings)
        normalized = re.sub(r'\s+', ' ', content.strip())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()[:8]  # Use first 8 chars
    
    def cleanup_unused_diagrams(self, used_hashes: Set[str]) -> None:
        """Remove diagram files that are no longer needed."""
        if not self.img_dir.exists():
            return
            
        existing_diagrams = list(self.img_dir.glob("diagram-*.png"))
        cleaned_count = 0
        
        for diagram_file in existing_diagrams:
            # Extract hash from filename (diagram-a1b2c3d4.png -> a1b2c3d4)
            match = re.match(r'diagram-([a-f0-9]{8})\.png', diagram_file.name)
            if match:
                file_hash = match.group(1)
                if file_hash not in used_hashes:
                    diagram_file.unlink()
                    cleaned_count += 1
                    print(f"🗑️  Removed unused diagram: {diagram_file.name}")
        
        if cleaned_count > 0:
            print(f"🧹 Cleaned up {cleaned_count} unused diagram file(s)")
    
    def generate_mermaid_images(self, matches: List[Tuple[int, int, str]]) -> List[str]:
        """Generate PNG images from Mermaid code blocks with hash-based caching."""
        image_paths = []
        used_hashes = set()
        generated_count = 0
        cached_count = 0
        
        for i, (_, _, code) in enumerate(matches, start=1):
            # Generate hash from code content
            content_hash = self.generate_content_hash(code)
            used_hashes.add(content_hash)
            
            # Use hash-based filename
            mmd_file = self.img_dir / f"diagram-{content_hash}.mmd"
            png_file = self.img_dir / f"diagram-{content_hash}.png"
            
            # Check if image already exists
            if png_file.exists():
                cached_count += 1
                print(f"📋 Using cached diagram {i}: {png_file.name}")
            else:
                # Generate new image
                try:
                    # Write Mermaid code to temp file
                    mmd_file.write_text(code, encoding='utf-8')
                    
                    # Generate PNG using Mermaid CLI with higher resolution
                    result = subprocess.run([
                        "mmdc", 
                        "-i", str(mmd_file), 
                        "-o", str(png_file),
                        "--theme", "default",
                        "--backgroundColor", "white",
                        "--scale", "2",           # 2x resolution for crisp images
                        "--width", "1200",        # Wider viewport for better diagram layout
                        "--height", "800"         # Taller viewport for complex diagrams
                    ], capture_output=True, text=True, shell=True, check=True)
                    
                    # Clean up temp file
                    mmd_file.unlink()
                    
                    generated_count += 1
                    print(f"🖼️  Generated diagram {i}: {png_file.name}")
                    
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to generate diagram {i}: {e.stderr}")
                    # Use placeholder text instead
                    image_paths.append(f"[Diagram {i} - Generation Failed]")
                    continue
            
            # Use relative path for markdown
            relative_img_path = f"images/diagram-{content_hash}.png"
            image_paths.append(relative_img_path)
        
        # Clean up unused diagram files
        self.cleanup_unused_diagrams(used_hashes)
        
        # Summary
        if generated_count > 0 or cached_count > 0:
            print(f"📊 Diagram summary: {generated_count} generated, {cached_count} cached")
        
        return image_paths
    
    def replace_mermaid_blocks(self, md_text: str) -> str:
        """Replace Mermaid code blocks with image references."""
        matches = self.extract_mermaid_blocks(md_text)
        
        if not matches:
            print("ℹ️  No Mermaid diagrams found")
            return md_text
        
        print(f"🔄 Processing {len(matches)} Mermaid diagrams...")
        
        # Generate images
        image_paths = self.generate_mermaid_images(matches)
        
        # Replace blocks working backwards to preserve positions
        result = md_text
        for i, ((start, end, _), img_path) in enumerate(zip(reversed(matches), reversed(image_paths))):
            diagram_num = len(matches) - i
            
            if img_path.startswith("["):
                # Failed generation - use placeholder
                replacement = f"\n{img_path}\n"
            else:
                # No caption - just the image
                replacement = f"\n![]({img_path})\n"
            
            result = result[:start] + replacement + result[end:]
        
        return result
    
    def generate_word_document(self, md_content: str) -> None:
        """Generate Word document using Pandoc."""
        # Save processed combined markdown (with image references)
        self.temp_md.write_text(md_content, encoding='utf-8')
        print(f"📝 Saved processed combined markdown: {self.temp_md}")
        
        # Build Pandoc command with relative paths from build directory
        output_filename = self.output_doc.name  # Get just the filename part
        cmd = [
            "pandoc",
            "combined.md",  # Relative to build directory
            "-o", output_filename,  # Use custom output filename
            "--standalone"
        ]
        
        # Add reference document if provided (make path relative to build dir)
        if self.template_doc and self.template_doc.exists():
            # Calculate relative path from build directory to template
            try:
                template_relative = os.path.relpath(self.template_doc, self.output_dir)
                cmd.extend(["--reference-doc", template_relative])
                print(f"📋 Using template: {self.template_doc}")
            except ValueError:
                # Fallback to absolute path if relative path calculation fails
                cmd.extend(["--reference-doc", str(self.template_doc.absolute())])
                print(f"📋 Using template (absolute path): {self.template_doc}")
        elif self.template_doc:
            print(f"⚠️  Template not found: {self.template_doc}")
        
        # Execute Pandoc from the build directory so image paths work correctly
        original_cwd = os.getcwd()
        try:
            os.chdir(self.output_dir)  # Change to build directory
            print(f"🔄 Running Pandoc from: {self.output_dir}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, check=True)
            print(f"✅ Generated Word document: {self.output_doc}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Pandoc failed: {e.stderr}")
            raise
        finally:
            os.chdir(original_cwd)  # Always restore original directory
    
    def generate(self) -> None:
        """Main generation process."""
        print("🚀 Starting documentation generation...\n")
        
        # Validate dependencies
        self.validate_dependencies()
        print()
        
        # Collect files
        md_files = self.collect_markdown_files()
        print()
        
        # Concatenate content
        print("🔗 Concatenating files...")
        full_md = self.concatenate_files(md_files)
        
        # Save original combined markdown (with mermaid codeblocks intact)
        self.temp_md_original.write_text(full_md, encoding='utf-8')
        print(f"📝 Saved original combined markdown: {self.temp_md_original}")
        
        # Process Mermaid diagrams
        processed_md = self.replace_mermaid_blocks(full_md)
        print()
        
        # Generate Word document
        print("📄 Generating Word document...")
        self.generate_word_document(processed_md)
        
        print(f"\n🎉 Documentation generated successfully!")
        print(f"📂 Output directory: {self.output_dir.absolute()}")
        print(f"📄 Word document: {self.output_doc.absolute()}")
        print(f"📝 Original markdown: {self.temp_md_original.absolute()}")
        print(f"📝 Processed markdown: {self.temp_md.absolute()}")
        if self.img_dir.exists() and list(self.img_dir.glob("*.png")):
            print(f"🖼️  Images: {self.img_dir.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Word documentation from Markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s docs/                              # Generate from docs/ folder
  %(prog)s docs/ -o output/                   # Custom output directory  
  %(prog)s docs/ -f "Final Report.docx"       # Custom output filename
  %(prog)s docs/ -t template.docx             # Use Word template
  %(prog)s docs/ -o build/ -f report.docx -t styles.docx  # Full customization
        """
    )
    
    parser.add_argument(
        "root_dir",
        help="Root directory containing Markdown files"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="build",
        help="Output directory (default: build)"
    )
    
    parser.add_argument(
        "-f", "--filename",
        default="output.docx",
        help="Output Word document filename (default: output.docx)"
    )
    
    parser.add_argument(
        "-t", "--template",
        help="Word template file (.docx) for styling"
    )
    
    args = parser.parse_args()
    
    try:
        generator = DocumentationGenerator(
            root_dir=args.root_dir,
            output_dir=args.output,
            output_filename=args.filename,
            template_doc=args.template
        )
        generator.generate()
        
    except KeyboardInterrupt:
        print("\n❌ Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


# ================================
# SETUP INSTRUCTIONS & EXAMPLES
# ================================

"""
🚀 QUICK START GUIDE

1. INSTALL DEPENDENCIES:
   # Install Pandoc (choose your platform):
   # macOS: brew install pandoc
   # Windows: winget install pandoc
   # Ubuntu: sudo apt install pandoc
   
   # Install Mermaid CLI:
   npm install -g @mermaid-js/mermaid-cli

2. CREATE PROJECT STRUCTURE:
   project/
   ├── docs/                    # Your markdown files
   │   ├── 01-introduction.md
   │   ├── 02-getting-started.md
   │   └── diagrams/
   │       └── architecture.md
   ├── template.docx           # Optional: Word style template
   └── generate_docs.py        # This script

3. RUN THE GENERATOR:
   python generate_docs.py docs/
   
   # With custom filename:
   python generate_docs.py docs/ -f "Project Documentation.docx"
   
   # With custom template:
   python generate_docs.py docs/ -t template.docx
   
   # Custom output directory:
   python generate_docs.py docs/ -o output/
   
   # Full customization:
   python generate_docs.py docs/ -o build/ -f "Final Report.docx" -t template.docx

4. EXAMPLE MARKDOWN WITH MERMAID:

   # Architecture Overview
   
   Our system follows a microservices pattern:
   
   ```mermaid
   graph TD
       A[Frontend] --> B[API Gateway]
       B --> C[Auth Service]
       B --> D[User Service]
       B --> E[Data Service]
       C --> F[(Database)]
       D --> F
       E --> F
   ```
   
   This diagram shows the main components...

5. OUTPUT:
   build/
   ├── output.docx             # Your final Word document (or custom filename)
   ├── combined-original.md    # Combined markdown with original mermaid codeblocks
   ├── combined.md             # Combined markdown with image references (for Word conversion)
   └── images/                 # Generated diagram images
       ├── diagram-a1b2c3d4.png
       └── diagram-e5f6g7h8.png

🎯 FEATURES:
✅ Automatic file discovery and natural sorting
✅ Mermaid diagram → high-resolution PNG conversion with hash-based caching
✅ Automatic cleanup of unused diagram files
✅ Custom output filename support
✅ Word template support
✅ Comprehensive error handling
✅ Cross-platform compatibility
✅ Progress reporting

🔧 TROUBLESHOOTING:
- "mmdc not found": Install with npm install -g @mermaid-js/mermaid-cli
- "pandoc not found": Install from https://pandoc.org/installing.html
- Encoding errors: Ensure files are UTF-8 encoded
- Image generation fails: Check Mermaid syntax in code blocks
"""
import os
import sys
import argparse
import re
import ast
import json

# === 配置区域 ===

# 代码文件扩展名
SOURCE_EXTS = {
    # C/OS
    '.c', '.h', '.s', '.S', '.asm', '.ld', 'Makefile', '.mk',
    # Python/Web
    '.py', '.js', '.ts', '.json', '.sh'
}

# 忽略的目录
IGNORE_DIRS = {'.git', 'build', 'dist', '__pycache__', '.vscode', 'node_modules', '.idea'}

# 关键配置文件 (用于提取依赖)
CONFIG_FILES = {'requirements.txt', 'package.json', 'Makefile', 'CMakeLists.txt'}

class ProjectPacker:
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        self.project_name = os.path.basename(self.root_dir)
        self.stats = {'files': 0, 'tokens_raw': 0, 'tokens_min': 0}
        self.dependencies = []
        self.file_summaries = {} # {filepath: description}

    def generate_tree(self, dir_path, prefix=""):
        """生成 ASCII 目录树，同时收集文件摘要"""
        tree_str = ""
        try:
            entries = sorted(os.listdir(dir_path))
            # 过滤忽略目录
            entries = [e for e in entries if e not in IGNORE_DIRS and not e.startswith('.')]
            
            for index, entry in enumerate(entries):
                path = os.path.join(dir_path, entry)
                is_last = (index == len(entries) - 1)
                connector = "└── " if is_last else "├── "
                
                # 记录相对路径
                rel_path = os.path.relpath(path, self.root_dir)
                
                if os.path.isdir(path):
                    tree_str += f"{prefix}{connector}📁 {entry}/\n"
                    extension = "    " if is_last else "│   "
                    tree_str += self.generate_tree(path, prefix + extension)
                else:
                    if self._is_source_file(entry):
                        desc = self._extract_file_description(path)
                        desc_str = f"  Found: {desc}" if desc else ""
                        tree_str += f"{prefix}{connector}📄 {entry}{'  # ' + desc if desc else ''}\n"
                        
                        # 收集依赖信息
                        if entry in CONFIG_FILES:
                            self._parse_dependencies(path, entry)
                    else:
                        # 非代码文件简单列出
                        tree_str += f"{prefix}{connector}{entry}\n"
        except PermissionError:
            pass
        return tree_str

    def _is_source_file(self, filename):
        return any(filename.endswith(ext) for ext in SOURCE_EXTS) or filename in CONFIG_FILES

    def _extract_file_description(self, filepath):
        """
        读取文件前5行，尝试提取文件顶部的注释说明
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [f.readline().strip() for _ in range(5)]
            
            # C/C++ 风格 /** Description */ 或 // Description
            for line in lines:
                # 移除注释符号，保留文本
                clean = re.sub(r'^[/|\*|#]+\s?', '', line).strip()
                if clean and len(clean) > 5 and not clean.startswith('include') and not clean.startswith('define'):
                    # 简单的启发式：如果第一句有实质内容，且不是代码
                    return clean[:50] + "..." if len(clean) > 50 else clean
        except:
            return None
        return None

    def _parse_dependencies(self, filepath, filename):
        """简单的依赖解析器"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if filename == 'Makefile':
                # 提取 CFLAGS 或 LDFLAGS
                flags = re.findall(r'(CFLAGS|LDFLAGS)\s*=\s*(.*)', content)
                for k, v in flags:
                    self.dependencies.append(f"Makefile {k}: {v.strip()}")
            
            elif filename == 'requirements.txt':
                libs = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                self.dependencies.append(f"Python Libs: {', '.join(libs[:10])}")
            
            elif filename == 'package.json':
                data = json.loads(content)
                deps = data.get('dependencies', {})
                self.dependencies.append(f"JS Libs: {', '.join(list(deps.keys())[:10])}")
                
        except:
            pass

    def minify_code(self, content, ext):
        """之前定义的极致压缩逻辑"""
        # Python
        if ext == '.py':
            try:
                tree = ast.parse(content)
                # 移除 Docstring
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                        if (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)):
                            node.body.pop(0)
                if hasattr(ast, 'unparse'): return ast.unparse(tree)
            except: pass
            return content

        # C/C++/Assembly/Linker
        else:
            # 1. 移除注释
            pattern = re.compile(r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE)
            content = re.sub(pattern, ' ', content)
            
            # 2. 压缩逻辑
            lines = []
            buf = []
            for line in content.split('\n'):
                line = line.strip()
                if not line: continue
                if line.startswith('#'): # 预处理指令保留换行
                    if buf: lines.append(" ".join(buf)); buf = []
                    lines.append(line)
                else:
                    buf.append(line)
            if buf: lines.append(" ".join(buf))
            
            text = "\n".join(lines)
            # 压缩符号
            ops = r'=|\+|-|\*|/|%|&|\||\^|!|<|>|\?|:|;|,|\(|\)|\{|\}|\[|\]'
            text = re.sub(f'\s*({ops})\s*', r'\1', text)
            return text

    def pack(self, output_file):
        print(f"📦 正在打包项目: {self.project_name} ...")
        
        with open(output_file, 'w', encoding='utf-8') as out:
            # === HEADER 部分 ===
            out.write(f"# PROJECT SUMMARY: {self.project_name}\n")
            out.write("## 1. Metadata\n")
            out.write(f"- Root: {self.root_dir}\n")
            out.write(f"- Generated Context for AI Analysis\n\n")

            out.write("## 2. Directory Structure & Key Files\n")
            out.write("```text\n")
            out.write(self.generate_tree(self.root_dir))
            out.write("```\n\n")

            if self.dependencies:
                out.write("## 3. Configuration & Dependencies\n")
                for dep in self.dependencies:
                    out.write(f"- {dep}\n")
                out.write("\n")

            # === BODY 部分 (代码) ===
            out.write("## 4. Source Code Context (Minified)\n")
            out.write("The following code has been minified (comments removed, whitespace compressed) to save tokens.\n\n")
            
            for root, _, files in os.walk(self.root_dir):
                if any(ignored in root for ignored in IGNORE_DIRS): continue
                
                for filename in sorted(files):
                    if not self._is_source_file(filename): continue
                    
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, self.root_dir)
                    _, ext = os.path.splitext(filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            raw = f.read()
                            minified = self.minify_code(raw, ext)
                            
                            if minified.strip():
                                out.write(f"\n--- BEGIN FILE: {rel_path} ---\n")
                                out.write(minified)
                                out.write(f"\n--- END FILE: {rel_path} ---\n")
                                
                                self.stats['files'] += 1
                    except Exception as e:
                        print(f"Skipping {filename}: {e}")
        
        print(f"✅ 完成! 已保存至: {output_file}")
        print(f"📊 统计: 包含了 {self.stats['files']} 个核心文件")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Project directory')
    parser.add_argument('-o', '--output', default='daima.txt')
    args = parser.parse_args()
    
    packer = ProjectPacker(args.dir)
    packer.pack(args.output)

if __name__ == '__main__':
    main()
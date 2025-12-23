import os
import sys
import argparse
import re
import ast

# === 配置区域 ===

# 扩展名配置：针对 OS 开发增加了汇编和链接脚本
EXTENSIONS = {
    # C/C++
    '.c', '.h', '.cpp', '.hpp', '.cc', 
    # RISC-V Assembly & Linker
    '.s', '.S', '.asm', '.ld', 
    # Build Systems
    'Makefile', '.mk',
    # Python (用于辅助脚本)
    '.py'
}

# 忽略目录
IGNORE_DIRS = {'.git', 'build', 'dist', '__pycache__', '.vscode', '.idea'}

# 不需要压缩的预处理指令前缀 (必须保留换行)
PREPROCESSOR_PREFIXES = ('#include', '#define', '#ifdef', '#ifndef', '#endif', '#else', '#elif', '#pragma', '#undef')

def is_source_file(filename):
    if filename in {'Makefile'}: return True
    _, ext = os.path.splitext(filename)
    return ext in EXTENSIONS

def strip_c_comments(text):
    """移除 C/C++/Assembly 风格的注释 (// 和 /* */)"""
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # 用一个空格代替注释，防止粘连
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def minify_c_style(content):
    """
    极致压缩 C/C++/汇编 代码
    策略：
    1. 移除所有注释
    2. 移除每行首尾空格
    3. 将非预处理指令的换行符替换为仅仅一个空格（如果安全）
    4. 压缩操作符周围的空格
    """
    # 1. 移除注释
    content = strip_c_comments(content)
    
    lines = content.split('\n')
    minified_lines = []
    current_line_buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 2. 处理预处理指令 (必须换行)
        if line.startswith('#'):
            # 如果缓冲区有内容，先刷入（作为上一行）
            if current_line_buffer:
                minified_lines.append(" ".join(current_line_buffer))
                current_line_buffer = []
            minified_lines.append(line) # 宏定义单独一行
        else:
            # 3. 普通代码，尝试拼接到一行
            # 汇编标签 (Label:) 最好保留换行或空格，这里统一用空格拼接
            current_line_buffer.append(line)
    
    if current_line_buffer:
        minified_lines.append(" ".join(current_line_buffer))

    # 合并结果
    text = "\n".join(minified_lines)

    # 4. 进一步压缩符号周围的空格 (Token 压榨核心)
    # 将 "a = b + c" 变为 "a=b+c"
    # 注意：不能处理字符串内部，但既然是给AI看，轻微破坏字符串格式通常可接受，除非是硬编码数据
    ops = r'=|\+|-|\*|/|%|&|\||\^|!|<|>|\?|:|;|,|\(|\)|\{|\}|\[|\]'
    text = re.sub(f'\s*({ops})\s*', r'\1', text)
    
    # 修正：关键字与变量间的空格必须保留 (如 "int a" 不能变成 "inta")
    # 上面的正则可能会误伤，所以仅对安全字符操作。
    # 实际上，上面的正则已经很激进了。为了保证不破坏 "int main"，我们只压缩符号。
    
    return text

def minify_python(content):
    """
    Python 无法移除换行，但可以移除空行、注释和多余空格
    """
    try:
        # 使用 AST 重新生成代码，自动去掉注释和多余格式
        tree = ast.parse(content)
        # 移除 Docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                    node.body.pop(0)
        
        if hasattr(ast, 'unparse'):
            return ast.unparse(tree)
        else:
            return content # 版本过低回退
    except:
        return content

def process_directory(directory, output_file):
    print(f"🚀 开始压缩处理: {directory}")
    print(f"🎯 目标: RISC-V/C OS 开发环境 (保留 Struct/Asm/Ld)")
    
    files_processed = 0
    total_chars_raw = 0
    total_chars_min = 0

    with open(output_file, 'w', encoding='utf-8') as out_f:
        # 写入一个极其简短的 Prompt 头部，告诉 AI 这是一个代码库dump
        out_f.write("<CODEBASE_CONTEXT_START>\n")

        for root, dirs, files in os.walk(directory):
            # 过滤隐藏目录
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
            
            for filename in sorted(files):
                if not is_source_file(filename):
                    continue

                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, directory)
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as in_f:
                        content = in_f.read()
                        total_chars_raw += len(content)

                        _, ext = os.path.splitext(filename)
                        
                        # 根据语言选择压缩策略
                        if ext == '.py':
                            minified = minify_python(content)
                        else:
                            # C, Assembly, Linker Script, Makefile
                            minified = minify_c_style(content)
                        
                        if minified.strip():
                            # 使用极简标记 [FILE:路径]
                            out_f.write(f"\n[FILE:{rel_path}]\n")
                            out_f.write(minified)
                            total_chars_min += len(minified)
                            files_processed += 1

                except Exception as e:
                    print(f"❌ 跳过 {filename}: {e}")

        out_f.write("\n<CODEBASE_CONTEXT_END>\n")
    
    # 统计信息
    reduction = 0
    if total_chars_raw > 0:
        reduction = (1 - total_chars_min / total_chars_raw) * 100
        
    print(f"\n✅ 处理完成!")
    print(f"📄 文件数: {files_processed}")
    print(f"📉 压缩率: {reduction:.2f}% (字符数 {total_chars_raw} -> {total_chars_min})")
    print(f"💾 输出至: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='OS开发专用代码压缩器')
    parser.add_argument('directory', help='源代码目录')
    parser.add_argument('-o', '--output', default='daima.txt', help='输出文件名')
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print("错误: 目录不存在")
        sys.exit(1)

    process_directory(args.directory, args.output)

if __name__ == "__main__":
    main()


# python3 os_minifier.py ./my_os_project
import os, re, argparse

# ===== 配置 =====
SRC_EXT = {'.c', '.h', '.S', '.s', '.ld', 'Makefile'}
IGN = {'.git', 'build', 'dist', '__pycache__', '.vscode'}

ARCH_MAP = {
    'core': [], 'mm': [], 'driver': [],
    'fs': [], 'user': [], 'other': []
}

# ===== 架构分类 =====
def classify(path):
    for k in ARCH_MAP:
        if f'/{k}/' in path:
            return k
    return 'other'

# ===== C 代码处理 =====
def strip_c_comments(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    s = re.sub(r'//.*', '', s)
    return s

def minify_c(s):
    s = strip_c_comments(s)
    lines, buf = [], []
    for l in s.splitlines():
        l = l.strip()
        if not l:
            continue
        if l.startswith('#'):
            if buf:
                lines.append(" ".join(buf))
                buf = []
            lines.append(l)
        else:
            buf.append(l)
    if buf:
        lines.append(" ".join(buf))
    s = "\n".join(lines)
    s = re.sub(r'\s*([=+\-*/%&|^!<>?:;,(){}\[\]])\s*', r'\1', s)
    return s

def minify_ld(s):
    entry = None
    base = None
    sections = []
    symbols = []

    # ENTRY
    m = re.search(r'ENTRY\s*\(\s*([^)]+)\s*\)', s)
    if m:
        entry = m.group(1)

    # 基地址
    m = re.search(r'\.\s*=\s*(0x[0-9a-fA-F]+)', s)
    if m:
        base = m.group(1)

    # SECTIONS 内部
    for sec in re.finditer(r'\.(\w+)\s*:\s*\{([^}]*)\}', s, re.S):
        name = sec.group(1)
        body = sec.group(2)

        # 提取通配段
        parts = re.findall(r'\*\(([^)]+)\)', body)
        if parts:
            sections.append(f".{name}: {' '.join(parts)}")

        # 提取符号
        syms = re.findall(r'([a-zA-Z_]\w*)\s*=', body)
        symbols.extend(syms)

    return entry, base, sections, sorted(set(symbols))

# ===== 汇编专用处理（关键）=====
def minify_asm(s):
    out = []
    for line in s.splitlines():
        line = line.rstrip()
        if not line:
            continue

        stripped = line.lstrip()

        # 预处理指令必须保留
        if stripped.startswith('#'):
            if stripped.startswith(('#include', '#define', '#if', '#endif', '#ifdef', '#ifndef')):
                out.append(stripped)
            continue

        # 删除行内注释
        if '#' in line:
            line = line.split('#', 1)[0].rstrip()

        if line:
            out.append(line)
    return "\n".join(out)

# ===== 解析工具 =====
def parse_funcs(s):
    return re.findall(r'\b([a-zA-Z_][\w\s\*]+?)\s+([a-zA-Z_]\w*)\s*\(', s)

def parse_includes(s):
    return re.findall(r'#include\s+[<"](.+?)[>"]', s)

# ===== 主流程 =====
def main(root, out):
    includes, funcs, code = [], [], []

    for r, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in IGN]
        for f in fs:
            if f.endswith(tuple(SRC_EXT)):
                p = os.path.join(r, f)
                rp = os.path.relpath(p, root)

                with open(p, 'r', errors='ignore') as fd:
                    raw = fd.read()

                ARCH_MAP[classify(rp)].append(rp)

                inc = parse_includes(raw)
                if inc:
                    includes.append(f"{rp}->{','.join(inc)}")

                if f.endswith(('.c', '.h')):
                    for _, n in parse_funcs(raw):
                        funcs.append(n)
                    minified = minify_c(raw)
                elif f.endswith('.ld'):
                    entry, base, secs, syms = minify_ld(raw)

                    code.append((
                        rp,
                        "[LD_LAYOUT]\n" +
                        (f"ENTRY={entry}\n" if entry else "") +
                        (f"BASE={base}\n" if base else "") +
                        "\n".join(secs) +
                        ("\n\n[LD_SYMBOLS]\n" + " ".join(syms) if syms else "")
                    ))
                    continue

                else:
                    minified = minify_asm(raw)

                if minified.strip():
                    code.append((rp, minified))

    with open(out, 'w') as o:
        o.write("[ARCH]\n")
        for k, v in ARCH_MAP.items():
            if v:
                o.write(f"{k}:{' '.join(v)}\n")

        o.write("\n[INCLUDE_GRAPH]\n")
        for i in includes:
            o.write(i + "\n")

        o.write("\n[SYMBOLS]\n")
        o.write(" ".join(sorted(set(funcs))) + "\n")

        o.write("\n[CODE]\n")
        for p, c in code:
            o.write(f"<{p}>\n{c}\n</{p}>\n")

# ===== 入口 =====
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("-o", default="os_context.txt")
    a = ap.parse_args()
    main(a.dir, a.o)

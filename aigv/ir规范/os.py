import os, re, argparse

# ===== 基本配置 =====
SRC_EXT = {'.c', '.h', '.S', '.s', '.ld', 'Makefile'}
IGN = {'.git', 'build', 'dist', '__pycache__', '.vscode'}

PROFILE = 'os-riscv'

ARCH_MAP = {
    'core': [],
    'mm': [],
    'driver': [],
    'fs': [],
    'user': [],
    'link': [],
    'other': []
}

# ===== 工具函数 =====

def classify(path):
    for k in ARCH_MAP:
        if f'/{k}/' in path:
            return k
    return 'other'

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
                lines.append(' '.join(buf))
                buf = []
            lines.append(l)
        else:
            buf.append(l)
    if buf:
        lines.append(' '.join(buf))
    s = '\n'.join(lines)
    s = re.sub(r'\s*([=+\-*/%&|^!<>?:;,(){}\[\]])\s*', r'\1', s)
    return s

def minify_asm(s):
    out = []
    for line in s.splitlines():
        line = line.rstrip()
        if not line:
            continue
        if line.lstrip().startswith('#'):
            if line.lstrip().startswith(('#include','#define','#if','#endif','#ifdef','#ifndef')):
                out.append(line.strip())
            continue
        if '#' in line:
            line = line.split('#', 1)[0].rstrip()
        if line:
            out.append(line)
    return '\n'.join(out)

def parse_funcs(s):
    return re.findall(r'\b([a-zA-Z_][\w\s\*]+?)\s+([a-zA-Z_]\w*)\s*\(', s)

def parse_includes(s):
    return re.findall(r'#include\s+[<"](.+?)[>"]', s)

def parse_ld(s):
    entry = None
    base = None
    sections = []
    symbols = []

    m = re.search(r'ENTRY\s*\(\s*([^)]+)\s*\)', s)
    if m:
        entry = m.group(1)

    m = re.search(r'\.\s*=\s*(0x[0-9a-fA-F]+)', s)
    if m:
        base = m.group(1)

    for sec in re.finditer(r'\.(\w+)\s*:\s*\{([^}]*)\}', s, re.S):
        name = sec.group(1)
        body = sec.group(2)
        parts = re.findall(r'\*\(([^)]+)\)', body)
        if parts:
            sections.append((name, parts))
        syms = re.findall(r'([a-zA-Z_]\w*)\s*=', body)
        symbols.extend(syms)

    return entry, base, sections, sorted(set(symbols))

# ===== 主流程 =====

def main(root, out):
    units = []
    graph = []
    symbols = []
    layouts = []
    code = []

    unit_id = {}
    uid = 0

    includes = []

    # ===== 扫描源文件 =====
    for r, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in IGN]
        for f in fs:
            if not f.endswith(tuple(SRC_EXT)):
                continue

            p = os.path.join(r, f)
            rp = os.path.relpath(p, root)
            arch = 'link' if f.endswith('.ld') else classify(rp)
            ext = os.path.splitext(f)[1]

            u = f'u{uid}'
            unit_id[rp] = u
            units.append((u, rp, ext.upper().strip('.'), arch))
            ARCH_MAP[arch].append(u)
            uid += 1

            with open(p, 'r', errors='ignore') as fd:
                raw = fd.read()

            # include 依赖
            for inc in parse_includes(raw):
                includes.append((rp, inc))

            # 符号
            if ext in ('.c', '.h'):
                for (_, name) in parse_funcs(raw):
                    symbols.append((name, u, 'func'))

            # 代码最小证据
            if ext in ('.S', '.s'):
                code.append((u, minify_asm(raw)))
            elif ext in ('.c', '.h'):
                code.append((u, minify_c(raw)))
            elif ext == '.ld':
                entry, base, secs, syms = parse_ld(raw)
                layouts.append((entry, base, secs))
                for s in syms:
                    symbols.append((s, u, 'ld'))

    # ===== 构建 GRAPH =====
    for src, inc in includes:
        if src in unit_id:
            graph.append(f"{unit_id[src]}->include:{inc}")

    # ===== 输出 PIR =====
    with open(out, 'w') as o:
        o.write('<PIR>\n')

        # META
        o.write('<META>\n')
        o.write(f'name:{os.path.basename(root)}\n')
        o.write(f'root:{os.path.abspath(root)}\n')
        o.write(f'profile:{PROFILE}\n')
        o.write('lang:C,ASM,LD\n')
        o.write('</META>\n\n')

        # UNITS
        o.write('<UNITS>\n')
        for u, path, typ, arch in units:
            o.write(f'{u}:{path} type={typ} arch={arch}\n')
        o.write('</UNITS>\n\n')

        # GRAPH
        o.write('<GRAPH>\n')
        for g in graph:
            o.write(g + '\n')
        o.write('</GRAPH>\n\n')

        # SYMBOLS
        o.write('<SYMBOLS>\n')
        for name, u, role in sorted(set(symbols)):
            o.write(f'{name}:{u} {role}\n')
        o.write('</SYMBOLS>\n\n')

        # LAYOUT
        o.write('<LAYOUT>\n')
        for entry, base, secs in layouts:
            if entry:
                o.write(f'ENTRY={entry}\n')
            if base:
                o.write(f'BASE={base}\n')
            for sec, parts in secs:
                o.write(f'.{sec}:' + ' '.join(parts) + '\n')
        o.write('</LAYOUT>\n\n')

        # CODE
        o.write('<CODE>\n')
        for u, c in code:
            if c.strip():
                o.write(f'<{u}>\n{c}\n</{u}>\n')
        o.write('</CODE>\n')

        o.write('</PIR>\n')

# ===== CLI =====

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dir')
    ap.add_argument('-o', default='pir.txt')
    args = ap.parse_args()
    main(args.dir, args.o)

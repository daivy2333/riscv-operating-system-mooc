**非常关键**。
**可以直接放进仓库、作为“冻结规范”的 PIR v0.1 Spec**。

控制在**一页左右**，但做到：

* 语义严格
* 可扩展
* 对大模型 / 人类 / 工具都友好
* 明确哪些“能做”、哪些“不保证”

---

# **PIR — Project Intermediate Representation**

### Version: **v0.1**

### Status: **Frozen (Stable Core)**

---

## 1. 目标（Design Goals）

PIR 是一种 **面向项目级别的中间表示**，用于在不完整编译、不执行、不链接的前提下，**以最小 token 成本表达一个软件项目的结构与语义骨架**。

PIR 设计用于：

* 静态分析
* 架构理解
* LLM 项目理解 / 推理
* 跨语言统一表示
* 类编译器的“前端输出”

PIR **不是**：

* AST
* IR（LLVM-style）
* 可执行格式

---

## 2. 全局结构（Top-Level Layout）

PIR 使用**线性文本结构 + 显式区块标签**：

```text
<PIR>
  <META>...</META>
  <UNITS>...</UNITS>
  <GRAPH>...</GRAPH>
  <SYMBOLS>...</SYMBOLS>
  <LAYOUT>...</LAYOUT>        # 可选
  <CODE>...</CODE>
</PIR>
```

所有区块 **顺序固定**，但允许区块为空。

---

## 3. META 区块（Project Metadata）

### 作用

描述项目整体上下文与分析假设。

### 格式

```text
<META>
name:<project_name>
root:<absolute_path>
profile:<profile_id>
lang:<comma-separated>
</META>
```

### 语义

| 字段      | 含义                              |
| ------- | ------------------------------- |
| name    | 项目名                             |
| root    | 分析时的项目根                         |
| profile | 分析配置（如 `os-riscv`、`java-maven`） |
| lang    | 涉及的语言集合                         |

---

## 4. UNITS 区块（Translation Units）

### 作用

表示 **最小编译 / 解析单元**（文件级别）。

### 格式

```text
<UNITS>
u0:src/core/init.c type=C arch=core
u1:src/mm/page.c type=C arch=mm
u2:src/boot/start.S type=ASM arch=core
u3:linker/os.ld type=LD arch=link
</UNITS>
```

### 语义

| 字段   | 含义          |
| ---- | ----------- |
| uX   | 单元唯一 ID     |
| path | 相对 root 的路径 |
| type | 语言/格式       |
| arch | 架构归属（逻辑模块）  |

> **保证**：`uX` 在 PIR 内唯一
> **不保证**：arch 的语义统一（由 profile 定义）

---

## 5. GRAPH 区块（Dependency Graph）

### 作用

表达**文件级依赖关系**（非符号级）。

### 格式

```text
<GRAPH>
u0->include:stdio.h
u1->include:mm.h
u2->include:platform.h
</GRAPH>
```

### 语义

* 左侧必须是 `UNITS` 中的 `uX`
* 右侧为依赖类型 + 目标
* 当前 v0.1 仅标准化 `include`

> **不表示** 链接顺序
> **不保证** 可达性完备

---

## 6. SYMBOLS 区块（Symbol Table）

### 作用

提供**最小符号证据**，支持语义推理与链接理解。

### 格式

```text
<SYMBOLS>
start_kernel:u0 func
kalloc:u1 func
_bss_start:u3 ld
</SYMBOLS>
```

### 语义

| 字段   | 含义                         |
| ---- | -------------------------- |
| name | 符号名                        |
| uX   | 定义单元                       |
| role | func / ld / var / type（扩展） |

> **不区分** 可见性 / linkage
> **不保证** 完整符号覆盖

---

## 7. LAYOUT 区块（Link/Layout Info，可选）

### 作用

抽取链接脚本的**结构语义**。

### 格式

```text
<LAYOUT>
ENTRY=_start
BASE=0x80000000
.text:.text .text.*
.rodata:.rodata .rodata.*
.data:.data .data.*
.bss:.bss .bss.*
</LAYOUT>
```

### 语义

* 用于表达内存布局
* 顺序即布局顺序
* 不表达对齐 / 属性 / AT()

---

## 8. CODE 区块（Minimal Evidence）

### 作用

提供 **“不可再压缩”的最小代码证据**，支持上下文理解。

### 格式

```text
<CODE>
<u0>
int main(){return 0;}
</u0>
<u2>
_start:csrr t0,mhartid;bnez t0,park;
</u2>
</CODE>
```

### 语义

* 非完整源码
* 可安全截断
* 用于模式识别与上下文推断

---

## 9. 扩展规则（Extensibility Rules）

* **允许新增区块**（如 `<TYPES>`、`<CFG>`）
* **禁止修改已有区块语义**
* 新语言应通过 `profile` + 新 parser 接入

---

## 10. 版本约束（Versioning）

* `v0.1`：结构冻结，语义稳定
* 向后兼容优先
* 重大结构变更 → `v0.2`

---

## 11. 设计原则（Summary）

> PIR ≠ AST
> PIR ≠ IR
> PIR = **“项目级可编译思维模型”**

---

下一步我可以：

* ✍️ 帮你写 **README 中的 PIR 设计动机**
* 🔍 设计 **PIR → LLM Prompt Adapter**
* 🔧 设计 **PIR → Call Graph / Build Graph**


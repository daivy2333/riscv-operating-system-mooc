
import os
import sys
import argparse

def process_directory(directory, output_file):
    """
    处理指定目录，将所有文件名和内容按照指定格式写入输出文件

    Args:
        directory (str): 要处理的目录路径
        output_file (str): 输出文件路径
    """
    # 获取目录下所有文件，按名称排序
    files = []
    for filename in sorted(os.listdir(directory)):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            files.append(filename)

    # 打开输出文件
    with open(output_file, 'w', encoding='utf-8') as out_f:
        # 处理每个文件
        for filename in files:
            filepath = os.path.join(directory, filename)

            # 写入文件名
            out_f.write(f"{filename}\n")

            # 读取并写入文件内容
            try:
                with open(filepath, 'r', encoding='utf-8') as in_f:
                    content = in_f.read()
                    out_f.write(content)
            except UnicodeDecodeError:
                # 如果是二进制文件，尝试以二进制方式读取并转义
                with open(filepath, 'rb') as in_f:
                    content = in_f.read()
                    # 简单处理二进制内容，这里仅作为示例
                    out_f.write(f"[二进制文件，大小: {len(content)} 字节]")

            # 在文件之间添加一个空行分隔
            out_f.write("\n")

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='将指定目录中的所有文件名和内容合并到一个文本文件中')
    parser.add_argument('directory', help='要处理的目录路径')
    parser.add_argument('-o', '--output', default='daima.txt', help='输出文件名 (默认: daima.txt)')

    args = parser.parse_args()

    # 检查目录是否存在
    if not os.path.isdir(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在")
        sys.exit(1)

    # 处理目录
    print(f"正在处理目录: {args.directory}")
    process_directory(args.directory, args.output)
    print(f"处理完成，结果已保存到: {args.output}")

if __name__ == "__main__":
    main()

# pythone d.py /path/to/directory
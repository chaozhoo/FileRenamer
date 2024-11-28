import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Tuple

class FileRenamer:
    def __init__(self, master):
        self.master = master
        master.title("FileRenamer 文件名查改助手")
        master.geometry("500x400")

        self.files_to_rename: List[str] = []

        # 文件选择框架
        file_frame = ttk.LabelFrame(master, text="文件选择")
        file_frame.pack(padx=10, pady=10, fill=tk.X)

        self.file_listbox = tk.Listbox(file_frame, width=60, height=5)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # 按钮框架
        button_frame = ttk.Frame(master)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="选择文件", command=self.browse_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="选择文件夹", command=self.browse_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="粘贴路径和文件名", command=self.paste_paths).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除列表", command=self.clear_list).pack(side=tk.LEFT, padx=5)

        # 查找和替换框架
        replace_frame = ttk.LabelFrame(master, text="查找和替换")
        replace_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(replace_frame, text="查找内容:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.find_entry = ttk.Entry(replace_frame, width=40)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(replace_frame, text="替换为:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.replace_entry = ttk.Entry(replace_frame, width=40)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5)

        # 替换按钮
        ttk.Button(master, text="全部替换", command=self.replace_all).pack(pady=10)

        # 统计信息
        self.stats_label = ttk.Label(master, text="")
        self.stats_label.pack(pady=5)

    def browse_files(self):
        files = filedialog.askopenfilenames(title="选择文件")
        self.add_files(files) # type: ignore

    def browse_directory(self):
        directory = filedialog.askdirectory(title="选择文件夹")
        if directory:
            for root, _, files in os.walk(directory):
                self.add_files([os.path.join(root, file) for file in files])

    def add_files(self, files: List[str]):
        for file in files:
            if file not in self.files_to_rename:
                self.files_to_rename.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
        self.update_stats()

    def clear_list(self):
        self.files_to_rename.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_stats()

    def replace_all(self):
        target_str = self.find_entry.get()
        replacement_str = self.replace_entry.get()

        if not self.files_to_rename or not target_str or not replacement_str:
            messagebox.showerror("错误", "请选择文件并填写所有字段")
            return

        renamed, skipped = self.rename_files(target_str, replacement_str)
        self.show_result(renamed, skipped)

    def rename_files(self, target_str: str, replacement_str: str) -> Tuple[int, int]:
        renamed, skipped = 0, 0
        for old_path in self.files_to_rename:
            try:
                new_name = os.path.basename(old_path).replace(target_str, replacement_str)
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                if old_path != new_path:
                    os.rename(old_path, new_path)
                    renamed += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"重命名文件 {old_path} 时出错: {str(e)}")
                skipped += 1
        return renamed, skipped

    def show_result(self, renamed: int, skipped: int):
        result = f"操作完成\n成功重命名: {renamed} 个文件\n跳过: {skipped} 个文件"
        messagebox.showinfo("结果", result)
        self.clear_list()

    def update_stats(self):
        total_files = len(self.files_to_rename)
        self.stats_label.config(text=f"待处理文件数: {total_files}")

    # 新增方法：处理粘贴路径
    def paste_paths(self):
        # 创建对话框窗口
        dialog = tk.Toplevel(self.master)
        dialog.title("粘贴绝对路径和文件名")
        dialog.geometry("400x300")
        
        # 创建文本框
        text_area = tk.Text(dialog, width=45, height=10)
        text_area.pack(padx=10, pady=10)
        
        def process_paths():
            # 获取文本内容并按行分割
            paths = text_area.get("1.0", tk.END).strip().split('\n')
            # 过滤空行
            valid_paths = [path.strip() for path in paths if path.strip()]
            
            # 验证路径是否存在
            existing_paths = []
            for path in valid_paths:
                if os.path.exists(path):
                    existing_paths.append(path)
                else:
                    print(f"路径不存在: {path}")
            
            # 添加有效路径到文件列表
            self.add_files(existing_paths)
            dialog.destroy()
        
        # 添加确定按钮
        ttk.Button(dialog, text="确定", command=process_paths).pack(pady=5)
        
        # 使对话框成为模态窗口
        dialog.transient(self.master)
        dialog.grab_set()
        self.master.wait_window(dialog)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamer(root)
    root.mainloop()
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from send2trash import send2trash


class FileFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件筛选删除工具")
        self.root.geometry("800x700")

        # 初始化变量
        self.folder_path = tk.StringVar()
        self.filter_text = tk.StringVar()
        self.file_formats = tk.StringVar()
        self.include_subfolders = tk.BooleanVar(value=True)
        self.status_text = tk.StringVar(value="准备就绪")

        self.create_widgets()


    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 文件夹选择部分
        folder_frame = ttk.LabelFrame(main_frame, text="文件夹选择", padding="10")
        folder_frame.pack(fill=tk.X, pady=5)

        ttk.Label(folder_frame, text="文件夹路径:").grid(row=0, column=0, sticky=tk.W)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.grid(row=0, column=1, padx=5)

        browse_btn = ttk.Button(folder_frame, text="浏览...", command=self.browse_folder)
        browse_btn.grid(row=0, column=2)

        # 筛选条件部分
        filter_frame = ttk.LabelFrame(main_frame, text="筛选条件", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)

        # 文件名筛选
        ttk.Label(filter_frame, text="文件名必须包含:").grid(row=0, column=0, sticky=tk.W)
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_text, width=30)
        filter_entry.grid(row=0, column=1, padx=5, sticky=tk.W)

        # 文件格式筛选（新增部分）
        ttk.Label(filter_frame, text="文件格式（多个用逗号分隔）:").grid(row=1, column=0, sticky=tk.W)
        format_entry = ttk.Entry(filter_frame, textvariable=self.file_formats, width=30)
        format_entry.grid(row=1, column=1, padx=5, sticky=tk.W)
        ttk.Label(filter_frame, text="示例: txt, jpg, docx（留空表示所有格式）").grid(row=1, column=2, sticky=tk.W)

        # 选项部分
        option_frame = ttk.Frame(main_frame)
        option_frame.pack(fill=tk.X, pady=5)

        subfolder_check = ttk.Checkbutton(
            option_frame,
            text="包含子文件夹",
            variable=self.include_subfolders
        )
        subfolder_check.pack(side=tk.LEFT, padx=5)

        # 文件列表
        list_frame = ttk.LabelFrame(main_frame, text="不匹配的文件列表（将移至回收站）", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 使用Treeview显示文件路径
        self.file_tree = ttk.Treeview(
            list_frame,
            columns=('path'),
            show='headings',
            selectmode='extended'
        )
        self.file_tree.heading('#0', text='文件名')
        self.file_tree.heading('path', text='文件路径')
        self.file_tree.column('#0', width=200)
        self.file_tree.column('path', width=450)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 进度条
        self.progress_bar = ttk.Progressbar(
            main_frame,
            orient=tk.HORIZONTAL,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.progress_bar.pack_forget()

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        preview_btn = ttk.Button(button_frame, text="预览文件", command=self.preview_files)
        preview_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = ttk.Button(button_frame, text="移动选中文件到回收站", command=self.move_selected_to_trash)
        delete_btn.pack(side=tk.LEFT, padx=5)

        delete_all_btn = ttk.Button(button_frame, text="移动所有不匹配文件到回收站",
                                    command=self.move_all_unmatched_to_trash)
        delete_all_btn.pack(side=tk.LEFT, padx=5)

        # 状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X)

        ttk.Label(status_frame, textvariable=self.status_text).pack(side=tk.LEFT)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def get_all_files(self, folder):
        """递归获取文件夹下所有文件（新增格式过滤）"""
        all_files = []
        format_list = self.process_file_formats()

        if self.include_subfolders.get():
            for root, _, files in os.walk(folder):
                for file in files:
                    if not self.check_file_format(file, format_list):
                        continue
                    file_path = os.path.join(root, file)
                    all_files.append((file, file_path))
        else:
            for item in os.listdir(folder):
                file_path = os.path.join(folder, item)
                if os.path.isfile(file_path):
                    if not self.check_file_format(item, format_list):
                        continue
                    all_files.append((item, file_path))
        return all_files

    def process_file_formats(self):
        """处理文件格式输入"""
        input_text = self.file_formats.get().strip()
        if not input_text:
            return []
        return [f.strip().lower().lstrip('.') for f in input_text.split(',') if f.strip()]

    def check_file_format(self, filename, format_list):
        """检查文件格式是否符合要求"""
        if not format_list:
            return True
        file_ext = os.path.splitext(filename)[1].lstrip('.').lower()
        return file_ext in format_list

    def preview_files(self):
        self.filter_text.set(self.filter_text.get().strip())
        format_input = self.file_formats.get().strip()

        # 输入验证
        if not self.folder_path.get():
            messagebox.showwarning("警告", "请先选择文件夹!")
            return

        # 格式输入验证
        if format_input:
            format_list = self.process_file_formats()
            if not all(format_list):
                messagebox.showwarning("警告", "文件格式输入包含空值，请检查！")
                return

        # 清空当前列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        try:
            all_files = self.get_all_files(self.folder_path.get())
            matched_files = []
            unmatched_files = []

            for file_name, file_path in all_files:
                # 文件名匹配检查
                if self.filter_text.get().lower() in file_name.lower():
                    matched_files.append((file_name, file_path))
                else:
                    unmatched_files.append((file_name, file_path))

            # 显示不匹配的文件
            for file_name, file_path in unmatched_files:
                self.file_tree.insert('', tk.END, text=file_name, values=(file_path,))

            # 显示统计信息
            self.status_text.set(
                f"找到 {len(matched_files)} 个匹配文件，{len(unmatched_files)} 个不匹配文件（将移至回收站）"
            )

        except Exception as e:
            messagebox.showerror("错误", f"读取文件时出错: {str(e)}")

    def move_selected_to_trash(self):
        if not self.folder_path.get():
            messagebox.showwarning("警告", "请先选择文件夹!")
            return

        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要移动的文件!")
            return

        confirm = messagebox.askyesno(
            "确认",
            f"确定要将选中的 {len(selected_items)} 个文件移动到回收站吗?"
        )

        if confirm:
            self.progress_bar.pack(fill=tk.X, pady=5)
            self.progress_bar["maximum"] = len(selected_items)
            self.progress_bar["value"] = 0
            self.root.update()

            moved_count = 0
            error_count = 0

            for i, item_id in enumerate(selected_items):
                file_path = self.file_tree.item(item_id, 'values')[0]
                try:
                    send2trash(file_path)
                    self.file_tree.delete(item_id)
                    moved_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"移动文件 {file_path} 到回收站时出错: {str(e)}")

                self.progress_bar["value"] = i + 1
                self.root.update()

            self.progress_bar.pack_forget()
            messagebox.showinfo(
                "完成",
                f"已移动 {moved_count} 个文件到回收站, {error_count} 个文件操作失败"
            )

    def move_all_unmatched_to_trash(self):
        if not self.folder_path.get():
            messagebox.showwarning("警告", "请先选择文件夹!")
            return

        all_items = self.file_tree.get_children()
        if not all_items:
            messagebox.showwarning("警告", "没有可移动的文件!")
            return

        confirm = messagebox.askyesno(
            "确认",
            f"确定要将所有 {len(all_items)} 个不匹配文件移动到回收站吗?"
        )

        if confirm:
            self.progress_bar.pack(fill=tk.X, pady=5)
            self.progress_bar["maximum"] = len(all_items)
            self.progress_bar["value"] = 0
            self.root.update()

            moved_count = 0
            error_count = 0

            for i, item_id in enumerate(all_items):
                file_path = self.file_tree.item(item_id, 'values')[0]
                try:
                    send2trash(file_path)
                    moved_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"移动文件 {file_path} 到回收站时出错: {str(e)}")

                self.progress_bar["value"] = i + 1
                self.root.update()

            # 清空列表
            for item in all_items:
                self.file_tree.delete(item)

            self.progress_bar.pack_forget()
            messagebox.showinfo(
                "完成",
                f"已移动 {moved_count} 个文件到回收站, {error_count} 个文件操作失败"
            )



if __name__ == "__main__":
    root = tk.Tk()
    # 设置窗口图标（可选）
    try:
        root.iconbitmap(default='trash.ico')
    except:
        pass

    # 设置样式
    style = ttk.Style()
    style.configure('Treeview', rowheight=25)

    app = FileFilterApp(root)
    root.mainloop()
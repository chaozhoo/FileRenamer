import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QListWidget, 
                            QLabel, QFileDialog, QMessageBox, QFrame, 
                            QDialog, QTextEdit, QListWidgetItem, QCheckBox)
from PyQt5.QtCore import Qt
from typing import List, Optional

class FileRenamer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files_to_rename: List[str] = []
        self.load_stylesheet()
        self.initUI()

    def load_stylesheet(self):
        try:
            if hasattr(sys, '_MEIPASS'):  # 判断是否是打包后的环境
                qss_path = os.path.join(sys._MEIPASS, 'style.qss')
            else:  # 开发环境
                qss_path = 'style.qss'
            
            with open(qss_path, 'r', encoding='utf-8') as f:
                style = f.read()
                self.setStyleSheet(style)
        except Exception as e:
            print(f"加载样式表失败: {str(e)}")

    def initUI(self):
        self.setWindowTitle("FileRenamer 文件名查改助手 by Oahc")
        self.setMinimumSize(600, 400)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 文件列表区域
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # 统计标签
        self.stats_label = QLabel("待处理文件数: 0")
        layout.addWidget(self.stats_label)

        # 按钮区域
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        self.select_files_btn = QPushButton("选择文件")
        self.select_folder_btn = QPushButton("选择文件夹")
        self.paste_paths_btn = QPushButton("粘贴路径")
        self.clear_btn = QPushButton("清除列表")
        
        for btn in [self.select_files_btn, self.select_folder_btn, 
                   self.paste_paths_btn, self.clear_btn]:
            button_layout.addWidget(btn)
        
        layout.addWidget(button_frame)

        # 查找替换区域
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("查找内容")
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("替换为")
        
        input_layout.addWidget(self.find_input)
        input_layout.addWidget(self.replace_input)
        
        layout.addWidget(input_frame)

        # 添加折叠面板
        self.advanced_frame = QFrame()
        self.advanced_frame.setVisible(False)  # 默认折叠
        advanced_layout = QVBoxLayout(self.advanced_frame)
        
        # 添加更多选项
        self.case_insensitive = QCheckBox("不区分大小写")
        self.use_regex = QCheckBox("启用正则表达式")
        
        advanced_layout.addWidget(self.case_insensitive)
        advanced_layout.addWidget(self.use_regex)
        
        layout.addWidget(self.advanced_frame)
        
        # 添加展开/折叠按钮
        self.toggle_btn = QPushButton("更多选项 ▼")
        self.toggle_btn.setFixedWidth(100)
        self.toggle_btn.clicked.connect(self.toggle_advanced)
        layout.addWidget(self.toggle_btn)

        # 替换按钮
        self.replace_btn = QPushButton("替换")
        layout.addWidget(self.replace_btn)

        # 连接信号
        self.select_files_btn.clicked.connect(self.browse_files)
        self.select_folder_btn.clicked.connect(self.browse_directory)
        self.paste_paths_btn.clicked.connect(self.paste_paths)
        self.clear_btn.clicked.connect(self.clear_list)
        self.replace_btn.clicked.connect(self.replace_all)

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文件",
            "",
            "所有文件 (*.*)"
        )
        if files:
            self.add_files(files)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            "",
            QFileDialog.ShowDirsOnly
        )
        if directory:
            files = []
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            self.add_files(files)

    def paste_paths(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("粘贴绝对路径和文件名")
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("请粘贴文件路径，每行一个")
        layout.addWidget(text_edit)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        def process_paths():
            paths = text_edit.toPlainText().strip().split('\n')
            valid_paths = [path.strip() for path in paths if path.strip()]
            
            existing_paths = []
            for path in valid_paths:
                if os.path.exists(path):
                    existing_paths.append(path)
                else:
                    print(f"路径不存在: {path}")
            
            self.add_files(existing_paths)
            dialog.accept()
        
        ok_button.clicked.connect(process_paths)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec_()

    def add_files(self, files: List[str]):
        for file in files:
            if file not in self.files_to_rename:
                self.files_to_rename.append(file)
                self.file_list.addItem(file)
        self.update_stats()

    def clear_list(self):
        self.files_to_rename.clear()
        self.file_list.clear()
        self.update_stats()

    def toggle_advanced(self):
        is_visible = self.advanced_frame.isVisible()
        self.advanced_frame.setVisible(not is_visible)
        self.toggle_btn.setText("更多选项 ▼" if is_visible else "更多选项 ▲")

    def replace_all(self):
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            QMessageBox.warning(self, "警告", "请输入要查找的文本")
            return

        renamed = skipped = 0
        
        for file_path in self.files_to_rename[:]:
            dir_name = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            
            # 根据选项处理文件名匹配
            if self.case_insensitive.isChecked():
                pattern = search_text.lower()
                target = file_name.lower()
            else:
                pattern = search_text
                target = file_name
                
            if self.use_regex.isChecked():
                import re
                if re.search(pattern, target):
                    new_name = re.sub(pattern, replace_text, file_name)
                    new_path = os.path.join(dir_name, new_name)
                    try:
                        os.rename(file_path, new_path)
                        renamed += 1
                    except OSError:
                        skipped += 1
                else:
                    skipped += 1
            else:
                if pattern in target:
                    if self.case_insensitive.isChecked():
                        # 保持原始大小写的替换
                        pos = target.find(pattern)
                        new_name = file_name[:pos] + replace_text + file_name[pos + len(pattern):]
                    else:
                        new_name = file_name.replace(search_text, replace_text)
                    new_path = os.path.join(dir_name, new_name)
                    try:
                        os.rename(file_path, new_path)
                        renamed += 1
                    except OSError:
                        skipped += 1
                else:
                    skipped += 1

        self.show_result(renamed, skipped)

    def show_result(self, renamed: int, skipped: int):
        result = f"操作完成\n成功重命名: {renamed} 个文件\n跳过: {skipped} 个文件"
        QMessageBox.information(self, "结果", result)
        self.clear_list()

    def update_stats(self):
        total_files = len(self.files_to_rename)
        self.stats_label.setText(f"待处理文件数: {total_files}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileRenamer()
    ex.show()
    sys.exit(app.exec_())
# -*- coding: utf-8 -*-

import os
import sys
import convert_csv_to_tomolinks
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
from tkinterdnd2 import *
import glob
from error_code import ErrorCode
import utils

import validate_oneroster_csv

search_dir = os.path.expanduser("~")

class TargetFileDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title, preset_oneroster = '', preset_tomolinks = '', preset_output = ''):
        self.oneroster_file_var = tk.StringVar()
        self.tomolinks_file_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()

        if len(preset_oneroster):
            self.oneroster_file_var.set(preset_oneroster)
        if len(preset_tomolinks):
            self.tomolinks_file_var.set(preset_tomolinks)
        if len(preset_output):
            self.output_folder_var.set(preset_output)

        self.canceled = True
        super().__init__(parent, title)

    def drop_input_oneroster(self, event):
        self.oneroster_file_var.set(event.data)

    def drop_input_tomolinks(self, event):
        self.tomolinks_file_var.set(event.data)

    def drop_output_folder(self, event):
        self.output_folder_var.set(event.data)

    def body(self, frame):
        global search_dir
        self.img = tk.PhotoImage(file=utils.get_resource_path('logo_120X120.png'))
        self.logo_lavel = tk.Label(frame, image=self.img)
        self.logo_lavel.grid(row=6, column=0)

        self.oneroster_label = tk.Label(frame, width=48, text="OneRoster csvファイルのzipファイルをセットしてください。", anchor="w")
        self.oneroster_label.grid(row=0, column=0, sticky="w")
        self.oneroster_box = tk.Entry(frame, width=50, text=self.oneroster_file_var)
        self.oneroster_box.drop_target_register(DND_FILES)
        self.oneroster_box.dnd_bind('<<Drop>>', self.drop_input_oneroster)
        self.oneroster_box.grid(
            row=1,
            column=0,
        )
        self.oneroster_button = tk.Button(
            frame, text="open", width=12, command=self.file_dialog_oneroster
        )
        self.oneroster_button.grid(row=1, column=1, padx=5, sticky="e")

        self.tomolinks_label = tk.Label(
            frame, width=48, text="tomoLinks csvファイルのzipファイルをセットしてください。", anchor="w"
        )
        self.tomolinks_label.grid(row=2, column=0, sticky='w')
        self.tomolinks_box = tk.Entry(frame, width=50, text=self.tomolinks_file_var)
        self.tomolinks_box.drop_target_register(DND_FILES)
        self.tomolinks_box.dnd_bind('<<Drop>>', self.drop_input_tomolinks)
        self.tomolinks_box.grid(row=3, column=0)
        self.tomolinks_button = tk.Button(
            frame, text="open", width=12, command=self.file_dialog_tomolinks
        )
        self.tomolinks_button.grid(row=3, column=1, padx=5, sticky="e")

        self.output_label = tk.Label(
            frame, width=48, text="出力先のフォルダを指定してください。", anchor="w"
        )
        self.output_label.grid(row=4, column=0, sticky='w')
        self.output_box = tk.Entry(frame, width=50, text=self.output_folder_var)
        self.output_box.drop_target_register(DND_FILES)
        self.output_box.dnd_bind('<<Drop>>', self.drop_output_folder)
        self.output_box.grid(row=5, column=0)
        self.output_button = tk.Button(
            frame, text="open", width=12, command=self.dialog_output_folder
        )
        self.output_button.grid(row=5, column=1, padx=5, sticky="e")

        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(2, weight=0)

        return frame

    def buttonbox(self):
        frame = tk.Frame(self)
        self.button1 = tk.Button(frame, text="変換開始", width=10, command=self.ok)
        self.button1.pack(side=tk.LEFT, padx=5, pady=5)
        self.button2 = tk.Button(frame, text="終了", width=10, command=self.cancel)
        self.button2.pack(side=tk.LEFT, padx=5, pady=5) 

        frame.pack()

    def apply(self):
        self.oneroster_file = self.oneroster_file_var.get()
        self.tomolinks_file = self.tomolinks_file_var.get()
        self.output_folder = self.output_folder_var.get()
        if len(self.oneroster_file) == 0:
            self.oneroster_file = None

        self.canceled = False
        self.destroy()

    def validate_path(self, path):
        if len(path) == 0:
            return True
        if not os.path.exists(path):
            tk.messagebox.showerror("", "ファイル %sをひらけません" % path)
            return False
        return True

    def remove_bracket(self, str):
        i = 0
        if str[0] == '{':
            fd = str.find('}', i)
            return str[i+1:fd]
        else:
            return str

    def validate(self):
        if len(self.oneroster_file_var.get()) == 0 or len(self.tomolinks_file_var.get()) == 0 or len(self.output_folder_var.get()) == 0:
            tk.messagebox.showerror("", "ファイル・フォルダを設定してください")
            return False

        self.oneroster_file_var.set(self.remove_bracket(self.oneroster_file_var.get()))
        self.tomolinks_file_var.set(self.remove_bracket(self.tomolinks_file_var.get()))
        self.output_folder_var.set(self.remove_bracket(self.output_folder_var.get()))

        if not self.validate_path(self.oneroster_file_var.get()):
            return False
        if not self.validate_path(self.tomolinks_file_var.get()):
            return False
        if not self.validate_path(self.output_folder_var.get()):
            return False

        return True

    def file_dialog_oneroster(self):
        fTyp = [("", ".zip")]
        global search_dir
        file_name = tk.filedialog.askopenfilename(filetypes=fTyp, initialdir=search_dir)

        if len(file_name) == 0:
            return
        else:
            self.oneroster_file_var.set(os.path.abspath(file_name))
            search_dir = os.path.dirname(file_name)

    def file_dialog_tomolinks(self):
        fTyp = [("", ".zip")]
        global search_dir
        file_name = tk.filedialog.askopenfilename(filetypes=fTyp, initialdir=search_dir)

        if len(file_name) == 0:
            return
        else:
            self.tomolinks_file_var.set(os.path.abspath(file_name))
            search_dir = os.path.dirname(file_name)

    def dialog_output_folder(self):
        iDir = os.path.abspath(os.path.dirname(__file__))
        folder_name = tk.filedialog.askdirectory(initialdir=iDir)

        if len(folder_name) == 0:
            pass
        else:
            self.output_folder_var.set(folder_name)

def main():
    preset_oneroster = ''
    preset_tomolinks = ''
    preset_output = ''
    while True:
        app = TkinterDnD.Tk()
        app.withdraw()
        dialog = TargetFileDialog(title="oneroster csv converter", parent=app, preset_oneroster = preset_oneroster, preset_tomolinks = preset_tomolinks, preset_output = preset_output)
        
        if dialog.canceled:
            app.destroy()
            return
            
        preset_oneroster = dialog.oneroster_file
        preset_tomolinks = dialog.tomolinks_file
        preset_output = dialog.output_folder

        # validation: 無効なOneRoster Bulk formatのファイル/CSVのチェック
        validation_result = validate_oneroster_csv.validateBulk(dialog.oneroster_file)
        if not validation_result['is_success']:
            tk.messagebox.showerror("エラー",validation_result['error_message'])
            app.destroy()
            continue

        ret_code, excuse_list = convert_csv_to_tomolinks.convert_csv(dialog.oneroster_file, dialog.tomolinks_file, dialog.output_folder)
        if ret_code == ErrorCode.convert_success:
            show_str = '変換に成功しました。tomoLinksへインポートしてください。\n'
            for excuse in excuse_list:
                show_str = show_str + excuse + '\n'
            tk.messagebox.showinfo('変換成功', show_str)
        else:
            tk.messagebox.showerror("変換エラー",ErrorCode.get_error_reason(ErrorCode, code = ret_code))

        app.destroy()

if __name__ == "__main__":
    main()

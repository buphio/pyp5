"""
pyp5 - GUI
gui wrapper for pyp5 module.
"""

from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import configparser
import datetime as dt
import os
import tkinter as tk
import postbote
import pyp5


__version__ = "A06"


def get_time():
    """return current time with specific format"""
    return dt.datetime.now().replace(microsecond=0)


class RestoreGUI(tk.Tk):
    """main window class"""

    def __init__(self):
        super().__init__()

        # === VARIABLES =======================================================
        self.title(f"pyp5 GUI ({__version__})")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1, minsize="800")
        self.grid_rowconfigure(0, weight=1, minsize="600")

        self.selected_file = str()
        self.entries = set()
        self.sum_entries = 0
        self.config_file = f"{os.path.expanduser('~')}/.pyp5conf"

        self.selected_items = set()

        self.bug_report_text = tk.Text()

        # === GUI =============================================================
        frame_main = tk.Frame(self)
        frame_main.grid(column=0, row=0, padx=10, pady=(10, 5), sticky=tk.NSEW)
        frame_main.grid_rowconfigure(2, weight=1)

        # --- ENTRIES FOUND
        frame_00 = tk.Frame(frame_main)
        frame_00.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)
        self.label_entries = tk.Label(
            frame_00, text="Entries found:", background="green", foreground="white"
        )
        self.label_entries.grid()

        frame_10 = tk.Frame(frame_main, background="light blue")
        frame_10.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW)
        frame_10.grid_columnconfigure(0, weight=1)
        self.edit_item = None
        self.list_entries = tk.Listbox(
            frame_10, border=0, width=60, height=20, selectmode="multiple"
        )
        self.list_entries.configure(font=("Andale Mono", 14))
        self.list_entries.grid(column=0, row=0, sticky=tk.W)
        self.list_entries.bind("<Double-1>", self.start_edit)
        self.scrollbar_list_entries = tk.Scrollbar(
            frame_10, orient="vertical", command=self.list_entries.yview()
        )
        self.scrollbar_list_entries.grid(column=1, row=0, sticky=tk.NS)
        self.list_entries["yscrollcommand"] = self.scrollbar_list_entries.set

        # --- LOG OUTPUT
        frame_04 = tk.Frame(frame_main)
        frame_04.grid(row=0, column=4, padx=(10, 0), sticky=tk.NSEW)
        self.label_log = tk.Label(
            frame_04, text="Log Output:", background="blue", foreground="white"
        )
        self.label_log.grid()

        frame_14 = tk.Frame(frame_main)
        frame_14.grid(row=1, column=4, rowspan=5, padx=(10, 0), sticky=tk.NSEW)
        self.text_log_output = ScrolledText(
            frame_14,
            highlightthickness=0,
            height=41,
            width=80,
            background="black",
            foreground="white",
            wrap=tk.WORD,
        )
        self.text_log_output.configure(font=("Andale Mono", 14))
        self.text_log_output.grid()

        # --- BUTTONS
        frame_20 = tk.Frame(frame_main)
        frame_20.grid(row=2, column=0, sticky=tk.NSEW)
        frame_20.grid_columnconfigure(0, weight=1)
        frame_20.grid_rowconfigure(0, weight=1)
        self.button_open = tk.Button(frame_20, text="Open File", width=8)
        self.button_open["command"] = self.open_file
        self.button_open.grid(sticky=tk.W)

        frame_21 = tk.Frame(frame_main)
        frame_21.grid(row=2, column=1, sticky=tk.NSEW)
        frame_21.grid_columnconfigure(0, weight=1)
        frame_21.grid_rowconfigure(0, weight=1)
        self.button_save_config = tk.Button(frame_21, text="Save Config", width=8)
        self.button_save_config["command"] = self.config_update
        self.button_save_config.grid()

        frame_22 = tk.Frame(frame_main)
        frame_22.grid(row=2, column=2, sticky=tk.NSEW)
        frame_22.grid_columnconfigure(0, weight=1)
        frame_22.grid_rowconfigure(0, weight=1)
        self.button_restore = tk.Button(frame_22, text="Restore", width=8)
        self.button_restore.grid()
        self.button_restore["command"] = self.restore

        frame_23 = tk.Frame(frame_main)
        frame_23.grid(row=2, column=3, sticky=tk.NSEW)
        frame_23.grid_columnconfigure(0, weight=1)
        frame_23.grid_rowconfigure(0, weight=1)
        self.button_save_log = tk.Button(frame_23, text="Save Log", width=8)
        self.button_save_log.grid(sticky=tk.E)
        self.button_save_log["command"] = self.save_logfile

        # --- OPTIONS
        frame_30 = tk.Frame(frame_main)
        frame_30.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW)
        frame_30.grid_columnconfigure(0, weight=1)
        frame_30.grid_rowconfigure(0, weight=1)
        self.combobox_archvive_id = ttk.Combobox(frame_30)
        self.combobox_archvive_id["values"] = "Archiv_p5", "Axle"
        self.combobox_archvive_id["state"] = "readonly"
        self.combobox_archvive_id.bind("<<ComboboxSelected>>", self.archive_id_changed)
        self.combobox_archvive_id.grid(pady=(0, 5), padx=(2, 10), sticky=tk.EW)

        frame_32 = tk.Frame(frame_main)
        frame_32.grid(row=3, column=2, sticky=tk.NSEW)
        frame_32.grid_columnconfigure(0, weight=1)
        frame_32.grid_rowconfigure(0, weight=1)
        self.check_dryrun_state = tk.IntVar()
        self.check_dryrun = tk.Checkbutton(
            frame_32, text="Dry run", variable=self.check_dryrun_state
        )
        self.check_dryrun.select()
        self.check_dryrun.grid(pady=(0, 5))

        frame_33 = tk.Frame(frame_main)
        frame_33.grid(row=3, column=3, sticky=tk.NSEW)
        frame_33.grid_columnconfigure(0, weight=1)
        frame_33.grid_rowconfigure(0, weight=1)
        self.check_mail_state = tk.IntVar()
        self.check_mail = tk.Checkbutton(
            frame_33, text="Send log", variable=self.check_mail_state
        )
        self.check_mail.grid(pady=(0, 5))

        # --- CONFIG
        frame_40 = tk.Frame(frame_main)
        frame_40.grid(row=4, column=0, columnspan=4, sticky=tk.NSEW)
        self.label_config = tk.Label(
            frame_40, text="Config:", background="orange", foreground="white"
        )
        self.label_config.grid(row=0, column=0, sticky=tk.SW)

        frame_50 = tk.Frame(frame_main, background="white")
        frame_50.grid(row=5, column=0, columnspan=4, sticky=tk.NSEW)
        self.text_config = tk.Text(frame_50, highlightthickness=0, height=14, width=61)
        self.text_config.configure(font=("Andale Mono", 14))
        self.text_config.grid(sticky=tk.S)

        # --- STATUS BAR
        frame_60 = tk.Frame(frame_main)
        frame_60.grid(row=6, column=0, columnspan=4, sticky=tk.NSEW)
        frame_60.grid_columnconfigure(0, weight=1)
        frame_60.grid_rowconfigure(0, weight=1)
        self.label_file = tk.Label(
            frame_60, text=f"Current file: {self.selected_file}", foreground="grey"
        )
        self.label_file.configure(font=("TkDefaultFont", 11))
        self.label_file.grid(row=0, column=0, sticky=tk.W)

        def background_on_enter(event=None):
            self.label_bug_report.configure(background="light grey")

        def background_on_leave(event=None):
            self.label_bug_report.configure(background="SystemButtonFace")

        def bug_report(event=None):
            BugReport(self)

        # --- BUG REPORT
        frame_64 = tk.Frame(frame_main)
        frame_64.grid(row=6, column=4, padx=(10, 0), sticky=tk.NSEW)
        frame_64.grid_columnconfigure(0, weight=1)
        frame_64.grid_rowconfigure(0, weight=1)
        self.label_bug_report = tk.Label(
            frame_64, text="Bug Report", foreground="grey", cursor="hand"
        )
        self.label_bug_report.configure(font=("TkDefaultFont", 11))
        self.label_bug_report.grid(row=0, column=0, ipadx=5, sticky=tk.NE)
        self.label_bug_report.bind("<Button-1>", bug_report)
        self.label_bug_report.bind("<Enter>", background_on_enter)
        self.label_bug_report.bind("<Leave>", background_on_leave)

        # create configparser object
        self.config_parser = configparser.ConfigParser()
        self.config_load()
        self.config_print()

    # === FUNCTIONS ======================================================================
    def start_edit(self, event):
        """Allow editing of configuration file"""
        index = self.list_entries.index(f"@{event.x},{event.y}")
        self.edit_item = index
        text = self.list_entries.get(index).strip("\n")
        y_axis = self.list_entries.bbox(index)[1]
        self.item_to_edit = tk.Entry(
            master=self.list_entries, borderwidth=0, highlightthickness=1
        )
        self.item_to_edit.bind("<Return>", self.save_edit)
        self.item_to_edit.bind("<Escape>", self.cancel_edit)
        self.item_to_edit.insert(0, text)
        self.item_to_edit.selection_from(0)
        self.item_to_edit.selection_to("end")
        self.item_to_edit.place(relx=0, y=y_axis, relwidth=1, width=-1)
        self.item_to_edit.focus_set()
        self.item_to_edit.grab_set()
        # print(f"{index}, {y_axis}: {text}")

    def cancel_edit(self, event):
        """Cancel edits of configuration file"""
        event.widget.destroy()

    def save_edit(self, event):
        """Save edits made on configuration file"""
        new_data = event.widget.get()
        self.list_entries.delete(self.edit_item)
        self.list_entries.insert(self.edit_item, new_data)
        event.widget.destroy()

    def archive_id_changed(self, event):
        """Refresh archive id"""
        self.config_change(self.combobox_archvive_id.get())

    def config_load(self):
        """tries to load config file and populate parser object"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as config:
                self.config_parser.read_file(config)
        except IOError:
            self.text_log_output.insert(
                tk.END, f"[{get_time()}] ERROR: no valid config file found."
            )
            self.text_config["state"] = "disabled"
            self.button_restore["state"] = "disabled"
            self.button_save_config["state"] = "disabled"
            self.combobox_archvive_id["state"] = "disabled"

    def config_print(self):
        """prints out parser object to text_config widget"""
        self.text_config.delete("1.0", tk.END)
        for section_name in self.config_parser.sections():
            self.text_config.insert(tk.END, f"[{section_name}]\n")
            for name, value in self.config_parser.items(section_name):
                self.text_config.insert(tk.END, f"{name}={value}\n")
                if name == "archive_id":
                    self.combobox_archvive_id.set(value)
            self.text_config.insert(tk.END, "\n")

    def config_change(self, selected_index):
        """update config with selected archive index"""
        config_modified = "".join(
            [
                s
                for s in self.text_config.get(1.0, tk.END).strip().splitlines(True)
                if s.strip("\r\n").strip()
            ]
        )
        self.config_parser.read_string(config_modified)
        self.config_parser["RESTORE"]["archive_id"] = selected_index
        self.config_save()

    def config_save(self):
        """write modified config file to disk"""
        with open(self.config_file, "w", encoding="utf-8") as config:
            self.config_parser.write(config)
        self.config_print()

    def config_update(self):
        """try to update .pyp5conf file if changes occured"""
        config_modified = "".join(
            [
                s
                for s in self.text_config.get(1.0, tk.END).strip().splitlines(True)
                if s.strip("\r\n").strip()
            ]
        )
        if not config_modified:
            mb.showerror("Error", "Nothing to save!")
            return
        self.config_parser.read_string(config_modified)
        self.config_save()

    def open_file(self):
        """Open file mask with extension filters"""
        filetypes = (
            ("ALE files", "*.ale"),
            ("AAF files", "*.aaf"),
            ("EDL files", "*.edl"),
        )
        self.selected_file = fd.askopenfilename(
            parent=self, initialdir=f'{os.path.expanduser("~")}', filetypes=filetypes
        )

        if not self.selected_file:
            return

        if self.selected_file.split(".")[1] == "ale":
            self.entries = set(pyp5.parse_ale(self.selected_file))
        elif self.selected_file.split(".")[1] == "aaf":
            self.entries = set(pyp5.parse_aaf(self.selected_file))
        elif self.selected_file.split(".")[1] == "edl":
            self.entries = set(pyp5.parse_edl(self.selected_file))

        if "ERROR" in self.entries:
            self.text_log_output.insert(
                tk.INSERT,
                f"[{get_time()}] '{os.path.basename(self.selected_file)}': "
                f"{': '.join(self.entries)}\n",
            )
            return

        self.list_entries.delete(0, tk.END)
        self.text_log_output.delete("1.0", tk.END)
        for item in sorted(list(self.entries)):
            self.list_entries.insert(tk.END, item.split(".")[0] + "\n")

        self.sum_entries = len(self.entries)

        self.update_labels()
        self.text_log_output.insert(
            tk.INSERT,
            f"[{get_time()}] Opened file: "
            f'"{os.path.basename(self.selected_file)}"\n',
        )
        self.text_log_output.insert(
            tk.INSERT, f"[{get_time()}] Found {self.sum_entries} entries in file.\n"
        )

    def update_labels(self):
        """Update label of entries and file dialog boxes"""
        self.label_entries.config(text=f"Entries found: {self.sum_entries}")
        self.label_file.config(text=f"Current file: '{self.selected_file}'")

    def restore(self):
        """start restore of selected entries"""
        search_items = []

        # self.selected_items = self.list_entries.curselection()
        self.text_log_output.delete("1.0", tk.END)

        for i in self.list_entries.curselection():
            search_items.append(self.list_entries.get(i).strip())

        archive_id = self.config_parser.get("RESTORE", "archive_id")
        nsdchat = [
            self.config_parser.get("GENERAL", "nsdchat")
        ] + self.config_parser.get("GENERAL", "awsock").split()

        # are there any items to search?
        if len(search_items) == 0:
            self.text_log_output.insert(
                tk.END, f"[{get_time()}] ERROR: no search items selected.\n"
            )
            return

        # check connection
        p5_connection = pyp5.check_p5_connection(nsdchat)
        if p5_connection:
            self.text_log_output.insert(tk.END, f"[{get_time()}] {p5_connection}\n")
            return

        # try to create restore selection
        restore_selection = pyp5.new_restore_selection(nsdchat).strip("\n")
        if not restore_selection:
            self.text_log_output.insert(
                tk.END, f"[{get_time()}] ERROR: Could not create restore selection.\n"
            )
            return

        self.text_log_output.insert(
            tk.END, f"\n[{get_time()}] INFO: Created {restore_selection}\n"
        )
        self.text_log_output.insert(
            tk.END, f"[{get_time()}] INFO: Restoring from archive id {archive_id}\n\n"
        )

        # --- search for entries and add to restore selection
        for item in search_items:
            self.update()
            result = pyp5.find_entry(
                nsdchat, restore_selection, archive_id, item.strip()
            ).strip("\n")
            if result == "0" or not result:
                self.text_log_output.insert(
                    tk.END, f"[{get_time()}] {item.strip()} not found.\n"
                )
            else:
                self.text_log_output.insert(
                    tk.END, f"[{get_time()}] {item.strip()}: {result}\n"
                )
            self.text_log_output.yview(tk.END)

        entries = (
            pyp5.check_output(
                nsdchat + ["-c", "RestoreSelection", restore_selection, "entries"]
            )
            .decode("utf-8")
            .strip("\n")
        )
        if not entries or entries == "0":
            self.text_log_output.insert(
                tk.END, f"\n[{get_time()}] WARNING: No entries in {restore_selection}\n"
            )
            return

        self.text_log_output.insert(
            tk.END,
            f"\n[{get_time()}] INFO: Added {entries} items to {restore_selection}\n",
        )

        volumes = pyp5.get_volumes(nsdchat, restore_selection)
        if not volumes:
            self.text_log_output.insert(
                tk.END,
                f"[{get_time()}] ERROR: No volumes found for {restore_selection}.\n",
            )
            return

        volumes_list = volumes.strip("\n").split(" ")

        self.text_log_output.insert(
            tk.END, f"\n[{get_time()}] INFO: Volumes needed for restore:\n"
        )
        for volume in sorted(volumes_list):
            self.update()
            # label = pyp5.get_label(nsdchat, volume).strip("\n")
            barcode = pyp5.get_barcode(nsdchat, volume).strip("\n")
            self.text_log_output.insert(tk.END, f"[{get_time()}] {volume}: {barcode}\n")

        title = pyp5.describe(
            nsdchat, restore_selection, os.path.basename(self.selected_file)
        )

        if not self.check_dryrun_state.get():
            job_id = pyp5.submit_restore(nsdchat, restore_selection)
            if not job_id:
                self.text_log_output.insert(
                    tk.END,
                    f"\n[{get_time()}] ERROR: Could not submit {restore_selection}.\n",
                )
            else:
                self.text_log_output.insert(
                    tk.END,
                    f"\n[{get_time()}] INFO: Created restore job {job_id} named "
                    f'"{title}".\n',
                )
        else:
            self.text_log_output.insert(
                tk.END, f"\n[{get_time()}] INFO: Dry run finished.\n"
            )
            # print(pyp5.destroy(nsdchat, restore_selection))

        if self.check_mail_state.get():
            content = self.text_log_output.get("1.0", tk.END).strip()
            postbote.send(
                list(self.config_parser.get("NOTIFICATION", "email").split(",")),
                f"Log Output: {os.path.basename(self.selected_file)}",
                content,
            )

        self.text_log_output.yview(tk.END)

    def save_logfile(self):
        """save contents of log box to file"""
        output = self.text_log_output.get("1.0", tk.END).strip()
        if not output:
            mb.showerror("Error", "Nothing to save.", parent=self)
            return

        with open(
            f"{os.path.expanduser('~')}/pyp5_restore-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.log",
            "w",
            encoding="utf-8"
        ) as log_file:
            log_file.write(output)
            mb.showinfo(
                "Information",
                f'Logfile saved to {os.path.expanduser("~")}',
                parent=self,
            )


class BugReport(tk.Tk):
    """bug report window"""

    def __init__(self, parent):
        super().__init__()

        self.title("Bug Report")
        self.resizable(False, False)

        frame_bug_report = tk.Frame(self)
        frame_bug_report.grid(column=0, row=0, padx=10, pady=10, sticky=tk.NSEW)
        frame_bug_report.grid_columnconfigure(0, weight=1)

        bug_report_description = tk.Label(frame_bug_report, text="Description:")
        bug_report_description.grid(row=0, column=0, sticky=tk.W)
        self.bug_report_text = tk.Text(
            frame_bug_report, highlightthickness=0, height=10, width=80
        )
        self.bug_report_text.configure(font=("Andale Mono", 14))
        self.bug_report_text.grid(row=1, column=0, sticky=tk.NSEW)

        label_log_output = tk.Label(frame_bug_report, text="Log Output:")
        label_log_output.grid(row=2, column=0, sticky=tk.W)
        self.text_log_output = tk.Text(
            frame_bug_report, highlightthickness=0, height=5, width=80, wrap=tk.WORD
        )
        self.text_log_output.configure(font=("Andale Mono", 14))
        self.text_log_output.grid(row=3, column=0, sticky=tk.NSEW)
        self.text_log_output.insert(tk.END, parent.text_log_output.get("1.0", tk.END))
        self.text_log_output["state"] = "disabled"

        button_send_bug_report = tk.Button(frame_bug_report, text="Send")
        button_send_bug_report.grid(row=4, column=0, sticky=tk.E)
        button_send_bug_report["command"] = self.send_bug_report

    def send_bug_report(self):
        """send bug report to specified mail address"""
        message = self.bug_report_text.get("1.0", tk.END)
        if "".join(message.split()):
            message = (
                message
                + "\n\n--------------------\n\n"
                + self.text_log_output.get("1.0", tk.END)
            )
            postbote.send(
                "insert_mail_here", "BUG REPORT: p5_restore_gui", message
            )
            self.destroy()
        else:
            mb.showerror("ERROR", "Message is empty")


if __name__ == "__main__":
    restore_gui = RestoreGUI()
    restore_gui.mainloop()

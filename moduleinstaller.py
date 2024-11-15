#!/usr/bin/env python3

# see https://github.com/socal-nerdtastic/moduleinstaller for definitive version

"""
packages are in the format {importname:installname}.
These are often the same name, but sometimes not.

HOW TO USE for command-line programs:
Save this python file into your project folder. Then add this code to your main program:

    import moduleinstaller
    moduleinstaller.cli_check_and_prompt({"PIL":"pillow", "openpyxl":"openpyxl"})

---

HOW TO USE for GUI programs:
Save this python file into your project folder. Then add this code to your main program:

    import moduleinstaller
    moduleinstaller.gui_check_and_prompt({"PIL":"pillow", "openpyxl":"openpyxl"})

This is required for GUI programs that don't have a CLI at all
But is also allowed for CLI programs that want a GUI prompt.

---

ALTERNATE USE:
pass in a string of modules to be installed, or leave
  blank to use requirements.txt file from the same folder.
This alternate method is MUCH SLOWER than the dictionary method.

    import moduleinstaller
    moduleinstaller.cli_check_and_prompt("pillow openpyxl")

or

    import moduleinstaller
    moduleinstaller.cli_check_and_prompt() # use requirements.txt

You can get the speed advantage back if you wrap your attempted import

    try:
        from PIL import Image
        import openpyxl
    except ImportError:
        import moduleinstaller
        moduleinstaller.cli_check_and_prompt("pillow openpyxl")

---

The force_kill argument sets what happens if modules are missing, after moduleinstaller is finished:
None (default) = kill the main program only if the user declines to install missing modules
True = kill the main program, whether or not the user opts to install missing modules
False = allow main program to continue, whether or not the user opts to install missing modules

---

Normal pip versioning strings can be used. For example

    import moduleinstaller
    moduleinstaller.cli_check_and_prompt({"serial":"pyserial", "openpyxl":"openpyxl==2.2"})

or

    import moduleinstaller
    moduleinstaller.cli_check_and_prompt("pyserial pillow openpyxl==2.2")

"""

class ModuleInstallerCore:
    __version__ = 2024,11,15
    def __init__(self, install:str|dict=None, force_kill:bool=None) -> None:
        if (modules := self.find_missing(install)): # if modules are missing
            modulenames = ", ".join(repr(importname) if importname==installname else f"{importname!r}({installname})" for importname, installname in modules.items())
            if self.promt_user(modulenames): # if the user agrees
                self.run_pip(list(modules.values()), force_kill) # install missing modules from pip
            elif force_kill is None: # user declined to install
                raise SystemExit
            if force_kill:
                raise SystemExit

    def find_missing(self, install:str|dict=None) -> dict:
        if isinstance(install, dict):
            return self.find_missing_via_imports(install)
        else: # string, None, or Path
            return self.find_missing_via_pip(install)

    def find_missing_via_pip(self, install:str=None) -> dict:
        import subprocess
        import sys
        from pathlib import Path
        to_be_installed = {}
        if install is None:
            req = Path(__file__).parent / "requirements.txt"
            if req.exists():
                install = req.read_text()
            else:
                raise FileNotFoundError(f"No module list supplied and no requirements.txt found at {req}")
        resp = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True)
        installed = resp.stdout.decode().splitlines()
        for modulename in install.strip().split():
            if not any(line.startswith(modulename) for line in installed):
                to_be_installed[modulename] = modulename
        return to_be_installed

    def find_missing_via_imports(self, install:dict) -> dict:
        # install is a dict of  {importname:installname}
        to_be_installed = {}
        for importname, installname in install.items():
            try:
                __import__(importname)
            except (ImportError, ModuleNotFoundError):
                to_be_installed[importname] = installname
        return to_be_installed

class ModuleInstallerGUI(ModuleInstallerCore):
    def promt_user(self, modules:str):
        from tkinter import messagebox
        return messagebox.askyesno(
            "Missing modules", # window title
            f"The following modules are missing:\n"
            f'  {modules}\n'
            f"\nWould you like to install them now?")

    def run_pip(self, modules:list, force_kill:bool=None):
        from subprocess import Popen, PIPE
        import sys
        import threading
        import tkinter as tk
        from tkinter import ttk
        from tkinter.scrolledtext import ScrolledText

        def pipe_reader(pipe, term=False):
            for line in iter(pipe.readline, b''):
                st.insert(tk.END, line)
                st.see(tk.END)
            if term:
                root.install_done = True
                if force_kill:
                    tk.Label(root, fg='red', text="DONE. Restart required.", font=('bold',14)).pack()
                    ttk.Button(root, text="Exit program", command=on_closing).pack()
                else:
                    tk.Label(root, fg='red', text="INSTALL FINISHED", font=('bold',14)).pack()
                    ttk.Button(root, text="Continue", command=on_closing).pack()

        def on_closing(*args):
            root.destroy()
            root.quit()
            if not root.install_done:
                raise SystemExit # kill the main program if the install is interupted.

        root = tk.Tk()
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.install_done = False
        tk.Label(root, text=f'Installing: {", ".join(modules)}', font=('bold',14)).pack()
        st= ScrolledText(root, width=60, height=12)
        st.pack(expand=True, fill=tk.BOTH)
        sub_proc = Popen([sys.executable, '-m', 'pip', 'install'] + modules, stdout=PIPE, stderr=PIPE)
        threading.Thread(target=pipe_reader, args=[sub_proc.stdout], daemon=True).start()
        threading.Thread(target=pipe_reader, args=[sub_proc.stderr, True], daemon=True).start()
        root.mainloop()

class ModuleInstallerCLI(ModuleInstallerCore):
    def promt_user(self, modules:str):
        print("MISSING MODULES")
        print("The following modules are missing:")
        print(" ", modules)
        print("\nWould you like to install them now? [no]/yes")
        return input().lower().startswith('y')

    def run_pip(self, modules:list, force_kill:bool=None):
        import subprocess
        import sys

        subprocess.run([sys.executable, '-m', 'pip', 'install'] + modules)
        print()
        if force_kill:
            print("DONE. Restart required.")
            input("press enter to complete")
        else:
            print("INSTALL FINISHED")

def cli_check_and_prompt(install:str|dict=None, force_kill:bool=None) -> None:
    """
    checks if the given modules are installed or not
    prompts the user to install them if they are not
    """
    ModuleInstallerCLI(install, force_kill)

def gui_check_and_prompt(install:str|dict=None, force_kill:bool=None) -> None:
    """
    checks if the given modules are installed or not
    shows GUI prompt to install them if they are not
    """
    ModuleInstallerGUI(install, force_kill)

def test():
    gui_check_and_prompt({"bogusmodule":"pillow"}, force_kill=False)
    cli_check_and_prompt({"pandas":"pillow","bogusmod":"bogusmod",})

if __name__ == "__main__":
    test()
    pass

# moduleinstaller
Prompt user to install missing python modules from pip. This module will check if the user has requirements installed. If not it will prompt the user to install them.

## HOW TO USE for command-line programs:
Save this python file into your project folder. Then add this code to your main program:

    import moduleinstaller
    moduleinstaller.cli_check_and_prompt({"PIL":"pillow", "openpyxl":"openpyxl"})

## HOW TO USE for GUI programs:
Save this python file into your project folder. Then add this code to your main program:

    import moduleinstaller
    moduleinstaller.gui_check_and_prompt({"PIL":"pillow", "openpyxl":"openpyxl"})

This is required for GUI programs that don't have a CLI at all
But is also allowed for CLI programs that want a GUI prompt.

## Extra arguments:
The force_kill argument sets what happens if modules are missing, after moduleinstaller is finished:  
None (default) = kill the main program only if the user declines to install missing modules  
True = kill the main program, whether or not the user opts to install missing modules  
False = allow main program to continue, whether or not the user opts to install missing modules  

## ALTERNATE USE:
pass in a string of modules to be installed, or leave
  blank to use requirements.txt file from the same folder.
This alternate method is MUCH SLOWER than the dictionary method above.

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

## Notes

packages are in the format {importname:installname}. These are often the same name, but sometimes not.

If you want to keep your code in a single file (sometimes you make monsters; I get it) you can copy the classes to the top of your file instead of importing

Normal pip versioning strings can be used. For example

    import moduleinstaller
    moduleinstaller.cli_check_and_prompt({"serial":"pyserial", "openpyxl":"openpyxl==2.2"})

or

    import moduleinstaller
    moduleinstaller.cli_check_and_prompt("pyserial pillow openpyxl==2.2")


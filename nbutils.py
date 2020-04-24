
import IPython
import IPython.display

def in_notebook():
    return IPython.get_ipython().__class__.__name__ == 'TerminalInteractiveShell'    

def display(text, end="\n"):
    if in_notebook():
        print(text, end=end)
    else:
        IPython.display.display(text)
    

def display_markdown(markdown):
    if in_notebook():
        print(markdown)
    else:
        IPython.display.display(IPython.display.Markdown(markdown))

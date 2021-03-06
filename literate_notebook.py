
"""
# Literate Notebook

## Motivation

I've found the most productive way to write and document code is by building it up in a Jupyter notebook.  I use the notebook to define the problem, the inputs and outputs, include examples, references and links, and then build up to a final set of solutions.  Along the way I end up writing functions which are similar or identical to a set functions to be collected into a module (the python name for libraries of functions).  Modules are critical because they can be imported and used in other notebooks/modules.  

Unfortunately, the notebook and the module can get out of sync.  I'll find a bug in the module as I am using it, and then go fix it.  Or I'll add a bit of functionality.  Gradually the notebook becomes stale.  Most of the info in the notebook is still true, but it doesn't reflect the final details accurately.

It would be way better if the **Notebook was the Module** and the **Module was the Notebook**.  

The code in this notebook/module provides a means to unify these concepts.
"""

#### Cell #3 Type: module ######################################################

# Load some modules
import os               # For paths and files.
import json             # Notebook files are in JSON
import itertools as it  # Useful tools for manipulating streams
import re               # regular expressions
import logging          # logging of errors, warnings, etc.

#### Cell #4 Type: module ######################################################

# Some basic routines for reading and writing from files.
def read_notebook(notebook_path):
    "Read the JSON encoding of the notebook ipynb file."
    with open(notebook_path, 'r') as fs:
        nb = json.load(fs)
    return nb

def save_notebook(notebook, notebook_path):
    "Write the JSON encoding of the notebook to an ipynb file."
    with open(notebook_path, 'w') as fs:
        json.dump(notebook, fs)

def read_lines(path):
    "Read the lines of a file specified by PATH."
    with open(path, 'r') as fs:
        for line in fs:
            yield line

def save_lines(file_path, lines):
    "Save lines to file."
    with open(file_path, 'w') as fs:
        for line in lines:
            fs.write(line)

#### Cell #8 Type: module ######################################################

# Code will process each cell in turn, handling markdown and code cells differents.

# Code cells are further differentiated by their cell tag.  For now the list of valid cell tags is:
VALID_CELL_TAGS = {'notebook', 'module', 'test'}

# The cell tag is the first word on the first line.
REGEX_CELL_TAG = re.compile(r"#\s*([a-zA-Z]+).*", re.IGNORECASE)

def extract_cell_tag(line):
    "Return the cell tag on this line."
    m = REGEX_CELL_TAG.match(line)
    if m is not None:
        tag = m.group(1).casefold()
        if tag in VALID_CELL_TAGS:
            return tag
    # default is module
    return 'module'


#### Cell #10 Type: module #####################################################

# Recall there are two goals 
#  1) create a python module from a literate notebook. 
#  2) roundtrip from literate notebook to python and back.
#
# The two solutions will end up using many of the same pieces.
#
# Each cell will be rendered as a "chunk", and the chunks are delimeted by special comment lines.
#
# These functions are used to flag the beginning and end of chunks.

# Match a cell marker comment
REGEX_CHUNK_MARKER = re.compile(r'#### Cell #(\d+) Type: (\w+) #+$')

def make_chunk_marker(num, cell_type, line_length=80):
    "A magic line which flags the beginning of a chunk."
    return f"#### Cell #{num} Type: {cell_type} {'#' * line_length}"[:line_length]

def is_chunk_marker(line):
    "Returns the cell number and cell type IFF the line is a chunk marker."
    m = REGEX_CHUNK_MARKER.match(line)
    if m is not None:
        return int(m.group(1)), m.group(2)
    return None

def make_chunk_separator(num, cell_type):
    "Surround the marker by blank lines."
    # Add empty lines for readability
    return ["\n", make_chunk_marker(num, cell_type) + "\n", ""]

# Helpers to construct the list of text lines destined for the python file.
def add_line(results, line):
    "Add a single line to the current list of lines stored in RESULT.  By convention a single line is not newline terminated, so we will add one."
    results.append(line + "\n")


def add_lines(results, list_of_lines):
    "Add multiple lines to the current list of lines stored in RESULT. By convention all lines but the last are newline terminated"
    if len(list_of_lines) > 0:
        results.extend(list_of_lines[:-1])
        results.append(list_of_lines[-1] + "\n")


#### Cell #12 Type: module #####################################################

def notebook_to_module(notebook_json, use_chunks=True):
    "Extract the **module** code from the notebook JSON datastructure.  Returns a list of lines."
    res = []

    for num, cell in zip(it.count(), notebook_json['cells']):
        if num == 0 and cell['cell_type'] == 'markdown':
            add_line(res, "")
            # first cell is markdown, create the documentation string for the module
            add_line(res, '"""')
            add_lines(res, cell['source'])
            add_line(res, '"""')
        elif cell['cell_type'] == 'code':
            # Otherwise the code 
            source = cell.get('source', [])
            if len(source) > 0 and extract_cell_tag(source[0]) == 'module':
                if use_chunks:
                    add_lines(res, make_chunk_separator(num, 'module'))
                add_lines(res, cell['source'])
    return res

#### Cell #15 Type: module #####################################################

# Working toward roundtrip.

# Unlike "compile to module", roundtrip will attempt to store the contents of all cells. 
# To encode markdown regions we'll use python comments.

COMMENT_TEXT = "#: "

def comment_line(line):
    "Turn a line into a Python comment line."
    return COMMENT_TEXT + line

REGEX_WHITESPACE_ONLY = re.compile("^\s*$")

def uncomment_line(line):
    "Take a commented line and remove the comment."
    if REGEX_WHITESPACE_ONLY.match(line):
        return line
    if line.startswith(COMMENT_TEXT):
        return line[len(COMMENT_TEXT):]
    else:
        raise Exception(f"Attempt to uncomment a line which is not commented.")

#### Cell #17 Type: module #####################################################

# Serialize a notebook into a roundtrip-able python file.

# In the interest of being more like a "literate program", let's present the top-level function first.
def notebook_to_roundtrip(notebook_json):
    "Create a roundtrip-able python script from the JSON notebook structure."
    res = []
    for num, cell in zip(it.count(), notebook_json['cells']):
        ctype = cell['cell_type']
        if ctype == 'markdown':
            add_markdown_chunk(res, num, cell)
        elif ctype == 'code':
            add_code_chunk(res, num, cell)
        else:
            loggging.warning(f"Found a ctype = {ctype} which is not supported.")
    # Finally add a chunk that includes notebook metadata
    add_metadata_chunk(res, num+1, notebook_json)
    # Finish the last chunk
    add_lines(res, make_chunk_separator(num+2, 'finish'))
    return res

def add_markdown_chunk(res, num, cell):
    "Add a markdown chunk to the list of lines in RES."
    source = cell.get('source', [])
    add_lines(res, make_chunk_separator(num, 'markdown'))
    # markdown text must be commented.
    add_lines(res, [comment_line(l) for l in source])

def add_code_chunk(res, num, cell):
    "Add a code chunk to the list of lines in RES."
    # Otherwise the code 
    source = cell.get('source', [])
    if len(source) == 0:
        # empty cell is by default a module
        ctag = 'module'
    else:
        ctag = extract_cell_tag(source[0])
    add_lines(res, make_chunk_separator(num, ctag))
    add_lines(res, source)

def notebook_metadata(notebook_json):
    "Extract metadata portion of the the notebook and serialize as JSON."
    # metadata is everything but the cells
    metadata = copy.copy(notebook_json)
    del metadata['cells']
    # Format so it is readable and editable.  
    jstring = json.dumps(metadata, indent=2)
    return jstring.splitlines(True)

def add_metadata_chunk(res, num, notebook_json):
    add_lines(res, make_chunk_separator(num, 'metadata'))
    json_of_metadata = notebook_metadata(notebook_json)
    # Comment each line of JSON
    add_lines(res, [comment_line(l) for l in json_of_metadata])

#### Cell #19 Type: module #####################################################

# Code to read a rountrip notebook

# All the code below relies on file_lines acting as an interator.  Iterators have state, and iterating over 
# them (with a for loop) has the side effect of consuming elements.  

def notebook_from_roundtrip(file_lines):
    "Create a notebook datastructure from the content of a roundtrip-able python file."
    notebook = {}
    cells = []
    for chunk in notebook_chunks(iter(file_lines)):
        num, ctype, lines = chunk
        if ctype in ['module', 'notebook', 'test', 'markdown']:
            cells.append(create_jupyter_cell(ctype, lines))
        elif ctype == 'metadata':
            notebook = extract_metadata(lines)
    notebook['cells'] = cells
    return notebook

def notebook_chunks(file_lines):
    "Iterator which yields chunks in file."
    num, ctype = read_to_first_chunk(file_lines)
    chunk_lines = []
    for line in file_lines:
        marker = is_chunk_marker(line)
        if marker is not None:
            # Found a marker, its the end of the previous chunk
            logging.info(f"Found {marker}")
            yield num, ctype, chunk_lines
            # Start the next chunk
            chunk_lines = []
            num, ctype = marker
        else:
            chunk_lines.append(line)

def read_to_first_chunk(file_lines):
    "Read to the first chunk marker and return number and type."
    for line in file_lines:
        marker = is_chunk_marker(line)
        if marker is not None:
            # Found a marker, extract a new chunk
            logging.info(f"Found first marker: {marker}")        
            return marker
    raise Exception("Could not fine a chunk marker.")
            
def empty_code_cell():
    "Create an empty code cell."
    cell = dict(cell_type = 'code',
                execution_count = 1,
                metadata = {},
                outputs = [])
    return cell

def empty_markdown_cell():
    "Create an empty markdown cell."
    cell = dict(cell_type = 'markdown',
                metadata = {})
    return cell

def create_jupyter_cell(chunk_type, lines):
    "Create a cell from a chunk."
    if chunk_type in ['module', 'notebook', 'test']:
        # all of these chunk types map to the code cell type.
        cell = empty_code_cell()
    elif chunk_type == 'markdown':
        cell = empty_markdown_cell()
        # Remove comments from the markdown
        lines = [uncomment_line(l) for l in lines]
    else:
        raise Exception(f"Can't create notebook cell of type = {chunk_type}.")
    # Trim blank readability lines from front and back
    lines = lines[1:-1]
    if len(lines) > 0:
        # Strip the last newline
        lines[-1] = lines[-1].rstrip()
    cell['source'] = lines
    return cell

def extract_metadata(lines):
    "Deserialize the JSON in the metadata section."
    lines = [uncomment_line(l) for l in lines]
    return json.loads(" ".join(lines))

#### Cell #20 Type: module #####################################################

# roundtrip-ing functions

def module_filename(notebook_filename):
    """
    By convention notebook names destined for module-hood will be Capitilized and
    underscore delimited.  The conversion downcases.  Double check for spaces and invalid
    characters, since that would screw things up when defining a module.
    """
    base, extension = os.path.splitext(notebook_filename)
    regex = re.compile(r"[\s\W]+")  # Matches non-alphanumeric and whitespace
    if regex.search(base):
        raise Exception("Filename: {notebook_filename} contains invalid characters.")
    module_filename = base.lower() + ".py"
    return module_filename

def convert_notebook_to_roundtrip(notebook_path, output_path):
    "Create a roundtrip file."
    notebook = read_notebook(notebook_path)
    save_lines(output_path, notebook_to_roundtrip(notebook))

def convert_notebook_to_module(notebook_path):
    "Given a notebook (ipynb), extract the module and write file."
    path, filename = os.path.split(notebook_path)
    output_filename = module_filename(filename)
    notebook = read_notebook(notebook_path)
    logging.info(f"Creating module {output_filename}.")
    save_lines(os.path.join(path, output_filename), notebook_to_module(notebook))


def convert_roundtrip_to_notebook(roundtrip_path, notebook_path):
    lines = read_lines(roundtrip_path)
    notebook = notebook_from_roundtrip(lines)
    save_notebook(notebook, notebook_path)


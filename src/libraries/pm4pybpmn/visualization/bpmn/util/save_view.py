import os
import shutil
import subprocess
import sys


def view(bpmn_figure):
    """
    View on the screen a BPMN figure that has been rendered

    Parameters
    ----------
    bpmn_figure
        BPMN figure
    """
    try:
        filename = bpmn_figure.name
        bpmn_figure = filename
    except AttributeError:
        # continue without problems, a proper path has been provided
        pass

    is_ipynb = False

    try:
        get_ipython()
        is_ipynb = True
    except NameError:
        pass

    if is_ipynb:
        from IPython.display import Image
        return Image(open(bpmn_figure, "rb").read())
    else:
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', bpmn_figure))
        elif os.name == 'nt':  # For Windows
            os.startfile(bpmn_figure)
        elif os.name == 'posix':  # For Linux, Mac, etc.
            subprocess.call(('xdg-open', bpmn_figure))


def save(bpmn_figure, output_file_path):
    """
    Save a BPMN figure that has been rendered

    Parameters
    -----------
    bpmn_figure
        BPMN figure
    output_file_path
        Path where the figure should be saved
    """
    try:
        filename = bpmn_figure.name
        bpmn_figure = filename
    except AttributeError:
        # continue without problems, a proper path has been provided
        pass

    shutil.copyfile(bpmn_figure, output_file_path)

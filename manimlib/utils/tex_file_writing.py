import logging
import sys
# import os
# import hashlib

from manimlib.utils.directories import get_tex_dir
from manimlib.config import get_manim_dir
from manimlib.config import get_custom_config


SAVED_TEX_CONFIG = {}


def get_tex_config():
    """
    Returns a dict which should look something like this:
    {
        "text_to_replace": "YourTextHere",
        "template_file": "tex_template.tex",
        "tex_body": "..."
    }
    """
    # Only load once, then save thereafter
    if not SAVED_TEX_CONFIG:
        custom_config = get_custom_config()
        SAVED_TEX_CONFIG.update(custom_config["tex"])
    return SAVED_TEX_CONFIG


def tex_hash(tex_file_content):
    # Truncating at 16 bytes for cleanliness
    hasher = hashlib.sha256(tex_file_content.encode())
    return hasher.hexdigest()[:16]


def tex_to_svg_file(tex_file_content):
    svg_file = os.path.join(
        get_tex_dir(), tex_hash(tex_file_content) + ".svg"
    )
    if not os.path.exists(svg_file):
        # If svg doesn't exist, create it
        tex_to_svg(tex_file_content, svg_file)
    return svg_file


def tex_to_svg(tex_file_content):
    tex_config = get_tex_config()
    try:
        window.util.tex_to_svg(tex_file_content)
    except Exception as err:
        log_file = tex_file.replace(".tex", ".log")
        logging.log(
            logging.ERROR,
            "\n\n LaTeX Error!  Not a worry, it happens to the best of us.\n"
        )
        logging.log(logging.DEBUG, str(err))

    return svg_file



def dvi_to_svg(dvi_file, regen_if_exists=False):
    """
    Converts a dvi, which potentially has multiple slides, into a
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    file_type = get_tex_config()["intermediate_filetype"]
    result = dvi_file.replace("." + file_type, ".svg")
    if not os.path.exists(result):
        commands = [
            "dvisvgm",
            "\"{}\"".format(dvi_file),
            "-n",
            "-v",
            "0",
            "-o",
            "\"{}\"".format(result),
            ">",
            os.devnull
        ]
        os.system(" ".join(commands))
    return result


# TODO, perhaps this should live elsewhere
@contextmanager
def display_during_execution(message):
    # Only show top line
    to_print = message.split("\n")[0]
    try:
        print(to_print, end="\r")
        yield
    finally:
        print(" " * len(to_print), end="\r")

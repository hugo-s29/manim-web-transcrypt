# import os
# import tempfile

import manimlib.config as config

CUSTOMIZATION = {}


def get_customization():
    if not CUSTOMIZATION:
        CUSTOMIZATION.update(config.get_custom_config())
        directories = CUSTOMIZATION["directories"]
        # Unless user has specified otherwise, use the system default temp
        # directory for storing tex files, mobject_data, etc.
        if not directories["temporary_storage"]:
            directories["temporary_storage"] = tempfile.gettempdir()

        # Assumes all shaders are written into manimlib/shaders
        directories["shaders"] = os.path.join(
            get_manim_dir(), "manimlib", "shaders"
        )
    return CUSTOMIZATION

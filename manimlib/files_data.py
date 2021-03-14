# File generated automatically based on the config files, the tex template...
# Please look at scripts.fill_files_data.py for more information

import manimlib.modules.json

config = {
  "break_into_partial_movies": False,
  "camera_qualities": {
    "default_quality": "high",
    "high": {
      "frame_rate": 30,
      "resolution": "1920x1080"
    },
    "low": {
      "frame_rate": 15,
      "resolution": "854x480"
    },
    "medium": {
      "frame_rate": 30,
      "resolution": "1280x720"
    },
    "ultra_high": {
      "frame_rate": 60,
      "resolution": "3840x2160"
    }
  },
  "directories": {
    "mirror_module_path": False,
    "output": "",
    "raster_images": "",
    "sounds": "",
    "temporary_storage": "",
    "vector_images": ""
  },
  "style": {
    "background_color": "#333333",
    "font": "Consolas"
  },
  "tex": {
    "executable": "latex",
    "intermediate_filetype": "dvi",
    "template_file": "tex_template.tex",
    "tex_body": "\\documentclass[preview]{standalone}\n\n\\usepackage[english]{babel}\n\\usepackage[utf8]{inputenc}\n\\usepackage[T1]{fontenc}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{dsfont}\n\\usepackage{setspace}\n\\usepackage{tipa}\n\\usepackage{relsize}\n\\usepackage{textcomp}\n\\usepackage{mathrsfs}\n\\usepackage{calligra}\n\\usepackage{wasysym}\n\\usepackage{ragged2e}\n\\usepackage{physics}\n\\usepackage{xcolor}\n\\usepackage{microtype}\n\\usepackage{pifont}\n\\DisableLigatures{encoding = *, family = * }\n\\linespread{1}\n\n\\begin{document}\n\n[tex_expression]\n\n\\end{document}\n",
    "text_to_replace": "[tex_expression]"
  },
  "universal_import_line": "from manimlib import *",
  "window_monitor": 0,
  "window_position": "UR"
}

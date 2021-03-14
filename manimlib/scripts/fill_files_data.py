import os, yaml, json

def fill_files_data():
    file_name = os.path.join(os.getcwd(), "manimlib", "files_data.py")
    with open(file_name, 'w') as writer:
        writer.write("# File generated automatically based on the config files, the tex template...\n")
        writer.write("# Please look at scripts.fill_files_data.py for more information\n")
        writer.write('\n')
        writer.write("import manimlib.modules.json\n")
        writer.write("\n")
        config = get_custom_config()

        config['tex']['tex_body'] = get_tex_template_content(config['tex']['template_file'])

        writer.write(f'config = {formatted(config)}\n')

def get_manim_dir():
    return os.getcwd()

def formatted(val):
    json_val = json.dumps(val, indent=2, sort_keys=True)
    return json_val \
        .replace('false', 'False') \
        .replace('True', 'True') \
        .replace('null', 'None')

def get_custom_config():
    filename = "custom_config.yml"
    global_defaults_file = os.path.join(get_manim_dir(), "manimlib", "default_config.yml")

    if os.path.exists(global_defaults_file):
        with open(global_defaults_file, "r") as file:
            config = yaml.safe_load(file)

        if os.path.exists(filename):
            with open(filename, "r") as file:
                local_defaults = yaml.safe_load(file)
            if local_defaults:
                config = merge_dicts_recursively(
                    config,
                    local_defaults,
                )
    else:
        with open(filename, "r") as file:
            config = yaml.safe_load(file)

    return config

def get_tex_template_content(file):
    filename = os.path.join(get_manim_dir(), 'manimlib', 'tex_templates', file)
    with open(filename, 'r') as data:
        return data.read()

if __name__ == "__main__":
    fill_files_data()

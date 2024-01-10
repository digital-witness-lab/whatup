from pathlib import Path
import string

static_dir = Path(__file__).parent.absolute()
static_files = {file.stem: file for file in static_dir.glob("*")}


class Template(string.Template):
    delimiter = "#"


def format_template(template_name, **kwargs) -> str:
    template = Template(static_files[template_name].open().read())
    return template.safe_substitute(kwargs)

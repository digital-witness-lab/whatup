from pathlib import Path
import string
import typing as T

import yaml


static_dir = Path(__file__).parent.absolute()
template_dir = Path(__file__).parent.absolute() / "templates/"

static_files = {file.stem: file for file in static_dir.glob("*")}
template_files = {file.stem: file for file in template_dir.glob("*")}


class Template(string.Template):
    delimiter = "#"


def substitute(message, **kwargs):
    return Template(message).safe_substitute(**kwargs)


def format_lang_template(template_name, lang, **kwargs) -> T.List[str]:
    data = template_files[template_name].read_text("utf8")
    messages = yaml.safe_load(data)[lang]
    return [substitute(message, **kwargs) for message in messages]

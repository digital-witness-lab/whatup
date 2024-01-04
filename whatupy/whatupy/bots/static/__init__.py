from pathlib import Path
import string

static_dir = Path(__file__).parent.absolute()
static_files = {
    "group_selection": static_dir / "group-selection.html",
    "unregister_final_message": static_dir / "unregister_final_message.txt",
}


def format_template(template_name, **kwargs) -> str:
    template = string.Template(static_files[template_name].open().read())
    return template.safe_substitute(kwargs)

from pathlib import Path
import string

static_dir = Path(__file__).parent.absolute()
static_files = {
    "group_selection": static_dir / "group-selection.html",
    "unregister_final_message": static_dir / "unregister_final_message.txt",
    "group_selection_thumbnail": static_dir / "group-selection-thumbnail.jpg",
}


class Template(string.Template):
    delimiter = "#"


def format_template(template_name, **kwargs) -> str:
    print("making template", kwargs)
    template = Template(static_files[template_name].open().read())
    return template.safe_substitute(kwargs)

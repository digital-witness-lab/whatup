from pathlib import Path

static_dir = Path(__file__).parent.absolute()
static_files = {
    "group_selection": static_dir / "group-selection.html",
    "unregister_final_message": static_dir / "unregister_final_message.txt",
}

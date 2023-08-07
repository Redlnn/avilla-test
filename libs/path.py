from pathlib import Path

root_path: Path = Path(__file__).parent.parent.resolve()
logs_path: Path = Path(root_path, 'logs')
modules_path: Path = Path(root_path, 'modules')
data_path: Path = Path(root_path, 'data')
libs_path: Path = Path(root_path, 'libs')
static_path: Path = Path(root_path, 'static')

logs_path.mkdir(parents=True, exist_ok=True)
modules_path.mkdir(parents=True, exist_ok=True)
data_path.mkdir(parents=True, exist_ok=True)
libs_path.mkdir(parents=True, exist_ok=True)
static_path.mkdir(parents=True, exist_ok=True)

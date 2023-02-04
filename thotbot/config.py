import json
from dataclasses import InitVar, asdict, dataclass, field
from pathlib import Path
from typing import Any, Final


@dataclass(kw_only=True)
class _Config:
    accent_color: str = ""
    owner_id: int = 0
    home_guild_id: int = 0
    channels: dict[str, int] = field(default_factory=dict)

    file_path: InitVar[Path | None] = None
    _file_path: Path = Path(__file__).parent / "config.json"

    def __post_init__(self, file_path: Path | None) -> None:
        if file_path:
            self._file_path = file_path

        self.reload_from_file()

    def reload_from_file(self) -> None:
        if self._file_path.is_dir():
            error_message = f"Expected a file, but found a directory: {self._file_path}"
            raise IsADirectoryError(error_message)

        if self._file_path.suffix != ".json":
            raise ValueError(f"Config path ({self._file_path}) must end in '.json'.")

        if self._file_path.exists():
            file_data = json.loads(self._file_path.read_text())

            for attr_name, attr_value in self.to_dict().items():
                if (attr_name in file_data) and (
                    isinstance(saved_value := file_data[attr_name], type(attr_value))
                ):
                    self.__dict__[attr_name] = saved_value

        self.save_to_file()

    def save_to_file(self, indent: int | None = 2) -> None:
        self._file_path.write_text(f"{self.to_string(indent)}\n", newline="\n")

    def to_dict(self) -> dict[str, Any]:
        internal_attr_names = ("file_path", "_file_path")
        return {
            attr_name: attr_value
            for attr_name, attr_value in asdict(self).items()
            if attr_name not in internal_attr_names
        }

    def to_string(self, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


Config: Final[_Config] = _Config()

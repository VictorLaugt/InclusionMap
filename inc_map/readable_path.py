from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Collection
    from pathlib import Path

def readable_path(root_dirs: Collection[Path], file: Path) -> Path:
    for root in root_dirs:
        if file.is_relative_to(root):
            if len(root_dirs) == 1:
                return file.relative_to(root)
            return Path(root.name, file.relative_to(root))
    raise ValueError(f'Unknown file "{file}"')

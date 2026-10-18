# SPDX-License-Identifier: AGPL-3.0-or-later
#
# HydraStream: "Concurrent HTTP downloader with in-memory stream reordering.".
# Copyright (C) 2026 Valentyn Zhukovetskyi <zukovetski@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://gnu.org/licenses/>.


from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar, dataclass_transform, overload

_T = TypeVar("_T")


@dataclass_transform(kw_only_default=True, order_default=False)
@overload
def hydra_dataclass(cls: type[_T], /) -> type[_T]: ...  # noqa: UP047


@dataclass_transform(kw_only_default=True, order_default=False)
@overload
def hydra_dataclass(
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = True,
    slots: bool = True,
    weakref_slot: bool = False,
) -> Callable[[type[_T]], type[_T]]: ...


# Реализация функции (внутри нее мы можем использовать чистый 3.12 синтаксис)
def hydra_dataclass(cls: Any = None, /, **kwargs: Any) -> Any:
    params = {"kw_only": True, "slots": True}
    params.update(kwargs)

    def wrap[ObjType](obj: type[ObjType]) -> type[ObjType]:
        return dataclass(**params)(obj)

    if cls is None:
        return wrap
    return wrap(cls)

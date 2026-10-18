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


from dataclasses import field

from hydrastream.domain.entities import Checksum
from hydrastream.domain.hydra_dataclass import hydra_dataclass


@hydra_dataclass(frozen=True)
class LinkData:
    id: int
    url: str
    checksum: Checksum | None


@hydra_dataclass(order=True, frozen=True)
class WriteChunk:
    fd: int
    offset: int
    length: int = field(compare=False)
    data: list[bytes] = field(compare=False)

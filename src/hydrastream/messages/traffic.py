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


import asyncio

from hydrastream.domain.hydra_dataclass import hydra_dataclass
from hydrastream.interfaces import NetworkStream
from hydrastream.messages.io import WriteChunk


@hydra_dataclass(frozen=True)
class MaxLimitSignal:
    pass


@hydra_dataclass(frozen=True)
class ScaleUpSignal:
    pass


@hydra_dataclass(frozen=True)
class ScaleDownSignal:
    pass


@hydra_dataclass(frozen=True)
class NetworkCongestionSignal:
    pass


@hydra_dataclass(frozen=True)
class TooManyRequests:
    pass


type TrafficSignal = (
    ScaleDownSignal | ScaleUpSignal | NetworkCongestionSignal | TooManyRequests
)


@hydra_dataclass(frozen=True)
class CheckpointReachedCmd:
    new_btc: int


@hydra_dataclass(frozen=True)
class RegisterStreamCmd:
    stream: NetworkStream


@hydra_dataclass(frozen=True)
class RemoveStreamCmd:
    stream: NetworkStream


@hydra_dataclass(frozen=True)
class DiskBufferFullSignal:
    pass


@hydra_dataclass(frozen=True)
class DiskBufferClearedSignal:
    pass


type ThrottlerMsg = (
    CheckpointReachedCmd
    | RegisterStreamCmd
    | RemoveStreamCmd
    | DiskBufferFullSignal
    | DiskBufferClearedSignal
)


@hydra_dataclass(frozen=True)
class FlushCmd:
    reply_to: asyncio.Future[bool]

    @classmethod
    def create_request(cls, future: asyncio.Future[bool]) -> "FlushCmd":
        return cls(reply_to=future)


type DiskMsg = WriteChunk | FlushCmd


@hydra_dataclass(frozen=True)
class WriteCompleted:
    pass


@hydra_dataclass(frozen=True)
class FileCompleted:
    pass


@hydra_dataclass(frozen=True)
class AnalyzerCheckpointEvent:
    pass


@hydra_dataclass(frozen=True)
class ThrottlerCheckpointEvent:
    pass


@hydra_dataclass(frozen=True)
class GoToSleepPill:
    pass


@hydra_dataclass(frozen=True)
class WakeUpPill:
    pass


@hydra_dataclass
class CheckpointEvent:
    pass

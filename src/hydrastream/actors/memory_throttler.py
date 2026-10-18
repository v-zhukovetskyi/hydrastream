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


from typing import assert_never, override

from hydrastream.domain.base_actor import BaseActor
from hydrastream.domain.entities import Chunk
from hydrastream.domain.hydra_dataclass import hydra_dataclass
from hydrastream.exceptions import GracefulShutdownError
from hydrastream.messages.base import (
    ActorFifoQueue,
    ActorPriorityQueue,
    PoisonPill,
    StandardPill,
    TerminalPill,
)


@hydra_dataclass
class MemoryThrottler(BaseActor[Chunk]):
    chunk_outbox: ActorPriorityQueue[Chunk | PoisonPill]
    credit_inbox: ActorFifoQueue[int | PoisonPill]

    num_workers: int
    budget: int

    @override
    async def _handle_msg(self, msg: Chunk) -> None:
        match msg:
            case Chunk() as pending_chunk:
                while pending_chunk.size > self.budget:
                    credit = await self.credit_inbox.get()
                    if isinstance(credit, StandardPill | TerminalPill):
                        raise GracefulShutdownError
                    self.budget += credit

                self.budget -= pending_chunk.size
                await self.chunk_outbox.send_data(
                    sort_key=(msg.file.meta.id, msg.current_pos), data=msg
                )
            case _ as unreachable:
                await super()._handle_msg(unreachable)
                assert_never(unreachable)

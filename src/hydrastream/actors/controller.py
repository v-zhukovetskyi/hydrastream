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
from hydrastream.domain.hydra_dataclass import hydra_dataclass
from hydrastream.messages.base import ActorFifoQueue, PoisonPill
from hydrastream.messages.traffic import (
    GoToSleepPill,
    NetworkCongestionSignal,
    ScaleDownSignal,
    ScaleUpSignal,
    TooManyRequests,
    TrafficSignal,
    WakeUpPill,
)


@hydra_dataclass
class TrafficController(BaseActor[TrafficSignal]):
    sleep_signals_outbox: ActorFifoQueue[GoToSleepPill | PoisonPill]
    wait_in_sleep_outbox: ActorFifoQueue[WakeUpPill | PoisonPill]
    workers: int
    dynamic_limit: int
    prev_dynamic_limit: int

    @override
    async def _on_start(self) -> None:
        for _ in range(self.workers - self.dynamic_limit):
            await self.sleep_signals_outbox.send_data(GoToSleepPill())

    @override
    async def _handle_msg(self, msg: TrafficSignal) -> None:
        match msg:
            case NetworkCongestionSignal() | ScaleDownSignal():
                self.dynamic_limit = max(1, self.dynamic_limit - 1)

            case ScaleUpSignal():
                self.dynamic_limit = min(self.workers, self.dynamic_limit + 1)

            case TooManyRequests():
                self.dynamic_limit = max(1, int(self.dynamic_limit / 2))

            case _ as unreachable:
                await super()._handle_msg(unreachable)
                assert_never(unreachable)

        if self.dynamic_limit != self.prev_dynamic_limit:
            await self._update_lights()

    async def _update_lights(self) -> None:
        if self.dynamic_limit > self.prev_dynamic_limit:
            for _ in range(self.dynamic_limit - self.prev_dynamic_limit):
                await self.wait_in_sleep_outbox.send_data(WakeUpPill())

        else:
            for _ in range(self.prev_dynamic_limit - self.dynamic_limit):
                await self.sleep_signals_outbox.send_data(GoToSleepPill())

        self.prev_dynamic_limit = self.dynamic_limit

    @override
    async def _on_terminal_pill(self) -> None:
        self.prev_dynamic_limit = self.dynamic_limit
        self.dynamic_limit = self.workers
        await self._update_lights()

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

# ruff: noqa :ERA001

from typing import Any

from hydrastream.hydrastream_core import (
    extract_filename as rust_extract_filename,
)
from hydrastream.hydrastream_core import (
    format_size as rust_format_size,
)
from hydrastream.hydrastream_core import (
    lognorm_delay as rust_lognorm_delay,
)
from hydrastream.hydrastream_core import (
    redact_url as rust_redact_url,
)


def format_size(size_bytes: float) -> str:
    return rust_format_size(size_bytes)


def redact_url(url: str) -> str:
    return rust_redact_url(url)


def lognorm_delay(target_seconds: float, max_delay: float | None = None) -> float:
    return rust_lognorm_delay(target_seconds, max_delay)


def extract_filename(url: str, headers: Any) -> str:  # noqa: ANN401
    # Передаем headers (они преобразуются в dict на стороне PyO3)
    return rust_extract_filename(url, dict(headers))


# import math
# import mimetypes
# import random
# import re
# from email.utils import unquote
# from pathlib import Path
# from urllib.parse import urlsplit, urlunsplit

# from curl_cffi import Headers


# def format_size(size_bytes: float) -> str:
#     for unit in ("B", "KB", "MB", "GB", "TB"):
#         if abs(size_bytes) < 1024:
#             return f"{size_bytes:.2f} {unit}"
#         size_bytes /= 1024
#     return f"{size_bytes:.2f} PB"


# def redact_url(url: str) -> str:
#     """Return the URL with any embedded userinfo (user:pass) masked.

#     Prevents basic-auth credentials from leaking into logs, error messages,
#     or structured JSON output when the user supplies URLs of the form
#     ``https://user:pass@host/path``.
#     """
#     try:
#         parts = urlsplit(url)
#     except ValueError:
#         return url

#     if "@" not in (parts.netloc or ""):
#         return url

#     host = parts.hostname or ""
#     if parts.port is not None:
#         host = f"{host}:{parts.port}"

#     netloc = f"***:***@{host}" if host else "***:***@"
#     return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


# def extract_filename(url: str, headers: Headers) -> str:
#     filename = None
#     cd = headers.get("Content-Disposition", "")

#     match_utf8 = re.search(r"filename\*=\s*([^']+)''([^;]+)", cd)
#     if match_utf8:
#         filename = unquote(match_utf8.group(2))

#     if not filename:
#         match_std = re.search(r'filename="?([^";]+)"?', cd)
#         if match_std:
#             filename = unquote(match_std.group(1))

#     if not filename:
#         clean_url = url.rstrip("/")
#         clean_url = clean_url.split("?")[0].split("#")[0]
#         clean_url, name = clean_url.rsplit("/", 1)
#         if "/" in clean_url and not clean_url.endswith(":/"):
#             filename = unquote(name)

#     if not filename or filename in {".", ""}:
#         filename = "downloaded_file"

#     filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
#     filename = Path(filename).name

#     if "." not in filename:
#         content_type = headers.get("Content-Type", "").split(";")[0]
#         ext = mimetypes.guess_extension(content_type)
#         if ext:
#             filename += ext
#         elif not filename.endswith(".bin"):
#             filename += ".bin"

#     return filename


# def lognorm_delay(target_seconds: float, max_delay: float | None = None) -> float:
#     """Генерирует задержку со случайным коэффициентом разброса от 10% до 30%.

#     :param target_seconds: Желаемое среднее время ожидания (в секундах).
#     :param max_delay: Максимально допустимая задержка в секундах.
#     :return: Случайное число секунд (float) > 0.
#     """
#     if target_seconds <= 0:
#         return 0.0

#     # Генерируем случайный разброс от 10% до 30% при каждом вызове функции
#     variance_fraction = random.uniform(0.1, 0.3)  # noqa: S311

#     # Переводим физический разброс в параметр sigma
#     sigma = math.sqrt(math.log(1 + variance_fraction**2))

#     # Рассчитываем mu так, чтобы среднее значение равнялось target_seconds
#     mu = math.log(target_seconds) - (sigma**2) / 2

#     # Генерируем случайное логнормальное число
#     delay = random.lognormvariate(mu, sigma)

#     # Применяем ограничение сверху
#     if max_delay is not None:
#         delay = min(delay, max_delay)

#     return delay

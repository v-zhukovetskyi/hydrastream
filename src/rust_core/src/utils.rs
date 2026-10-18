// SPDX-License-Identifier: AGPL-3.0-or-later
//
// HydraStream: "Concurrent HTTP downloader with in-memory stream reordering.".
// Copyright (C) 2026 Valentyn Zhukovetskyi <zukovetski@gmail.com>
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://gnu.org/licenses/>.

use percent_encoding::percent_decode_str;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use rand::{rng, RngExt};
use rand_distr::{Distribution, LogNormal};
use regex::Regex;
use std::path::Path;
use url::Url;

#[pyfunction]
pub fn format_size(mut size_bytes: f64) -> String {
    let units = ["B", "KB", "MB", "GB", "TB"];
    for unit in units.iter() {
        if size_bytes.abs() < 1024.0 {
            return format!("{:.2} {}", size_bytes, unit);
        }
        size_bytes /= 1024.0;
    }
    format!("{:.2} PB", size_bytes)
}

#[pyfunction]
pub fn redact_url(url: &str) -> String {
    // Используем крейт url для парсинга. Если URL невалидный — возвращаем как есть
    let mut parsed = match Url::parse(url) {
        Ok(u) => u,
        Err(_) => return url.to_string(),
    };

    // Если в блоке авторизации нет пароля или пользователя, возвращаем оригинал
    if parsed.username().is_empty() && parsed.password().is_none() {
        return url.to_string();
    }

    // Маскируем учетные данные
    let _ = parsed.set_username("***");
    let _ = parsed.set_password(Some("***"));
    parsed.to_string()
}

#[pyfunction]
pub fn lognorm_delay(target_seconds: f64, max_delay: Option<f64>) -> f64 {
    if target_seconds <= 0.0 {
        return 0.0;
    }

    // В rand v0.10 вместо thread_rng() вызывается просто rng()
    let mut r = rng();

    // Вместо gen_range теперь используется метод random_range
    let variance_fraction: f64 = r.random_range(0.1_f64..0.3_f64);

    // Расчет параметров логнормального распределения (f64)
    let sigma = (1.0_f64 + variance_fraction.powi(2)).ln().sqrt();
    let mu = target_seconds.ln() - (sigma.powi(2)) / 2.0;

    // Инициализируем распределение из крейта rand_distr
    let log_normal = match LogNormal::new(mu, sigma) {
        Ok(dist) => dist,
        Err(_) => return target_seconds,
    };

    // Сэмплируем значение задержки
    let mut delay = log_normal.sample(&mut r);

    if let Some(max) = max_delay {
        delay = delay.min(max);
    }

    delay
}

// Так как Headers из curl_cffi ведет себя как словарь, мы принимаем его как &Bound<'_, PyDict>
#[pyfunction]
pub fn extract_filename(url: &str, headers: &Bound<'_, PyDict>) -> String {
    let mut filename: Option<String> = None;

    // Извлекаем заголовок Content-Disposition (регистронезависимо или дефолт)
    let cd = headers
        .get_item("Content-Disposition")
        .unwrap_or(None)
        .map(|v| v.to_string())
        .unwrap_or_default();

    // Паттерн UTF-8: filename*=
    let re_utf8 = Regex::new(r"filename\*=\s*([^']+)''([^;]+)").unwrap();
    if let Some(caps) = re_utf8.captures(&cd) {
        if let Some(m) = caps.get(2) {
            filename = Some(
                percent_decode_str(m.as_str())
                    .decode_utf8_lossy()
                    .into_owned(),
            );
        }
    }

    // Стандартный паттерн: filename=
    if filename.is_none() {
        let re_std = Regex::new(r#"filename="?([^";]+)"?"#).unwrap();
        if let Some(caps) = re_std.captures(&cd) {
            if let Some(m) = caps.get(1) {
                filename = Some(
                    percent_decode_str(m.as_str())
                        .decode_utf8_lossy()
                        .into_owned(),
                );
            }
        }
    }

    // Если из заголовков не достали, выковыриваем из URL
    if filename.is_none() {
        let clean_url = url.trim_end_matches('/');
        let no_query = clean_url
            .split('?')
            .next()
            .unwrap_or("")
            .split('#')
            .next()
            .unwrap_or("");

        if let Some(name) = no_query.split('/').next_back() {
            if !name.is_empty() && !clean_url.ends_with(":/") {
                filename = Some(percent_decode_str(name).decode_utf8_lossy().into_owned());
            }
        }
    }

    let mut fname = match filename {
        Some(f) if f != "." && !f.is_empty() => f,
        _ => "downloaded_file".to_string(),
    };

    // Очищаем от запрещенных символов: re.sub(r'[\\/*?:"<>|]', "_", filename)
    let re_clean = Regex::new(r#"[\\/*?:"<>|]"#).unwrap();
    fname = re_clean.replace_all(&fname, "_").into_owned();

    // Берем только имя файла (Path(filename).name)
    if let Some(name_os) = Path::new(&fname).file_name() {
        fname = name_os.to_string_lossy().into_owned();
    }

    // Обработка расширения (упрощенная базовая логика, mimetypes можно расширить при необходимости)
    if !fname.contains('.') {
        let content_type = headers
            .get_item("Content-Type")
            .unwrap_or(None)
            .map(|v| v.to_string())
            .unwrap_or_default();

        let main_type = content_type.split(';').next().unwrap_or("");

        // Быстрый базовый маппинг популярных типов для стримера (можно дополнить)
        let ext = match main_type {
            "application/gzip" | "application/x-gzip" => ".gz",
            "application/zip" => ".zip",
            "text/plain" => ".txt",
            "text/html" => ".html",
            "application/json" => ".json",
            _ => ".bin",
        };
        fname.push_str(ext);
    } else if !fname.ends_with(".bin") && !fname.contains('.') {
        // Защита из вашего кода
        fname.push_str(".bin");
    }

    fname
}

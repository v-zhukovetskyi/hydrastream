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

mod utils;

use pyo3::{
    pymodule,
    types::{PyModule, PyModuleMethods},
    wrap_pyfunction, Bound, PyResult,
};
use utils::{extract_filename, format_size, lognorm_delay, redact_url};

#[pymodule]
fn hydrastream_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(format_size, m)?)?;
    m.add_function(wrap_pyfunction!(redact_url, m)?)?;
    m.add_function(wrap_pyfunction!(lognorm_delay, m)?)?;
    m.add_function(wrap_pyfunction!(extract_filename, m)?)?;
    Ok(())
}

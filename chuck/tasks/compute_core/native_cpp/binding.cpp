#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cstdint>
#include <vector>

namespace py = pybind11;

py::dict solve(py::object payload_obj) {
    py::dict payload = payload_obj.cast<py::dict>();
    if (!payload.contains("left") || !payload.contains("right") || !payload.contains("block_size")) {
        throw py::value_error("compute_core payload missing required keys");
    }

    std::vector<std::vector<std::int64_t>> left = payload["left"].cast<std::vector<std::vector<std::int64_t>>>();
    std::vector<std::vector<std::int64_t>> right = payload["right"].cast<std::vector<std::vector<std::int64_t>>>();
    std::size_t block_size = payload["block_size"].cast<std::size_t>();
    std::size_t size = left.size();

    std::vector<std::vector<std::int64_t>> result(size, std::vector<std::int64_t>(size, 0));
    for (std::size_t row_block = 0; row_block < size; row_block += block_size) {
        for (std::size_t col_block = 0; col_block < size; col_block += block_size) {
            for (std::size_t inner_block = 0; inner_block < size; inner_block += block_size) {
                for (std::size_t i = row_block; i < std::min(row_block + block_size, size); ++i) {
                    const auto& left_row = left[i];
                    auto& result_row = result[i];
                    for (std::size_t k = inner_block; k < std::min(inner_block + block_size, size); ++k) {
                        auto factor = left_row[k];
                        const auto& right_row = right[k];
                        for (std::size_t j = col_block; j < std::min(col_block + block_size, size); ++j) {
                            result_row[j] += factor * right_row[j];
                        }
                    }
                }
            }
        }
    }

    std::int64_t trace = 0;
    std::int64_t checksum = 0;
    for (std::size_t i = 0; i < size; ++i) {
        trace += result[i][i];
        for (auto value : result[i]) {
            checksum += value;
        }
    }

    py::dict output;
    output["size"] = py::int_(size);
    output["trace"] = py::int_(trace);
    output["checksum"] = py::int_(checksum);
    return output;
}

PYBIND11_MODULE(chuck_cpp_compute_core, m) {
    m.doc() = "C++ binding for chuck compute_core";
    m.def("solve", &solve);
}

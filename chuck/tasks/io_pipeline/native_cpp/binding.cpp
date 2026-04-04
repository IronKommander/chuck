#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace py = pybind11;

py::dict solve(py::object payload_obj) {
    std::vector<std::string> records = payload_obj.cast<std::vector<std::string>>();

    std::map<std::string, std::int64_t> totals;
    std::int64_t total_value = 0;
    for (const auto& line : records) {
        const auto p1 = line.find('|');
        const auto p2 = line.find('|', p1 == std::string::npos ? p1 : p1 + 1);
        if (p1 == std::string::npos || p2 == std::string::npos) {
            continue;
        }
        const std::string account = line.substr(0, p1);
        const std::string bucket = line.substr(p1 + 1, p2 - p1 - 1);
        const std::string amount_text = line.substr(p2 + 1);
        const std::int64_t amount = std::stoll(amount_text);
        const std::string key = account + "|" + bucket;
        totals[key] += amount;
        total_value += amount;
    }

    std::string top_pair;
    std::int64_t top_value = -1;
    for (const auto& [key, value] : totals) {
        if (value > top_value || (value == top_value && key < top_pair)) {
            top_pair = key;
            top_value = value;
        }
    }

    py::dict output;
    output["records"] = py::int_(records.size());
    output["unique_pairs"] = py::int_(totals.size());
    output["total_value"] = py::int_(total_value);
    output["top_pair"] = py::str(top_pair);
    output["top_value"] = py::int_(top_value < 0 ? 0 : top_value);
    return output;
}

PYBIND11_MODULE(chuck_cpp_io_pipeline, m) {
    m.doc() = "C++ binding for chuck io_pipeline";
    m.def("solve", &solve);
}

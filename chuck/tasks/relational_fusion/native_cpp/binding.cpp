#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cstdint>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace py = pybind11;

py::dict solve(py::object payload_obj) {
    py::dict payload = payload_obj.cast<py::dict>();
    if (!payload.contains("left") || !payload.contains("right")) {
        throw py::value_error("relational_fusion payload missing required keys");
    }

    std::vector<std::pair<std::string, std::int64_t>> left =
        payload["left"].cast<std::vector<std::pair<std::string, std::int64_t>>>();
    std::vector<std::pair<std::string, std::int64_t>> right =
        payload["right"].cast<std::vector<std::pair<std::string, std::int64_t>>>();

    std::unordered_map<std::string, std::vector<std::int64_t>> index;
    for (const auto& [key, value] : right) {
        index[key].push_back(value);
    }

    std::int64_t join_rows = 0;
    std::int64_t aggregate = 0;
    for (const auto& [key, left_value] : left) {
        auto found = index.find(key);
        if (found == index.end()) {
            continue;
        }
        for (auto right_value : found->second) {
            ++join_rows;
            aggregate += left_value + right_value;
        }
    }

    py::dict output;
    output["left_rows"] = py::int_(left.size());
    output["right_rows"] = py::int_(right.size());
    output["join_rows"] = py::int_(join_rows);
    output["aggregate"] = py::int_(aggregate);
    return output;
}

PYBIND11_MODULE(chuck_cpp_relational_fusion, m) {
    m.doc() = "C++ binding for chuck relational_fusion";
    m.def("solve", &solve);
}

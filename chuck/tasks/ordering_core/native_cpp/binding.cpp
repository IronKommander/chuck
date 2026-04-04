#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cstdint>
#include <vector>

namespace py = pybind11;

py::dict solve(py::object payload_obj) {
    std::vector<std::int64_t> numbers = payload_obj.cast<std::vector<std::int64_t>>();
    std::sort(numbers.begin(), numbers.end());

    constexpr std::int64_t mod = 1'000'000'007;
    std::int64_t checksum = 0;
    for (std::size_t index = 0; index < numbers.size(); ++index) {
        checksum = (checksum + static_cast<std::int64_t>(index + 1) * numbers[index]) % mod;
        if (checksum < 0) {
            checksum += mod;
        }
    }

    py::dict output;
    output["count"] = py::int_(numbers.size());
    output["min"] = py::int_(numbers.empty() ? 0 : numbers.front());
    output["max"] = py::int_(numbers.empty() ? 0 : numbers.back());
    output["median"] = py::int_(numbers.empty() ? 0 : numbers[numbers.size() / 2]);
    output["checksum"] = py::int_(checksum);
    return output;
}

PYBIND11_MODULE(chuck_cpp_ordering_core, m) {
    m.doc() = "C++ binding for chuck ordering_core";
    m.def("solve", &solve);
}

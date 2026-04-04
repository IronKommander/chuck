#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

namespace py = pybind11;

py::dict solve(py::object payload_obj) {
    py::dict payload = payload_obj.cast<py::dict>();
    if (!payload.contains("capacity") || !payload.contains("accesses")) {
        throw py::value_error("memory_tier payload missing required keys");
    }

    const std::size_t capacity = payload["capacity"].cast<std::size_t>();
    std::vector<std::int64_t> accesses = payload["accesses"].cast<std::vector<std::int64_t>>();

    std::vector<std::int64_t> cache_keys;
    cache_keys.reserve(capacity + 1);
    std::int64_t hits = 0;
    std::int64_t misses = 0;

    for (auto key : accesses) {
        auto found = std::find(cache_keys.begin(), cache_keys.end(), key);
        if (found != cache_keys.end()) {
            ++hits;
            cache_keys.erase(found);
            cache_keys.push_back(key);
        } else {
            ++misses;
            cache_keys.push_back(key);
            if (cache_keys.size() > capacity) {
                cache_keys.erase(cache_keys.begin());
            }
        }
    }

    const double hit_rate = accesses.empty() ? 0.0 : static_cast<double>(hits) / static_cast<double>(accesses.size());

    py::dict output;
    output["requests"] = py::int_(accesses.size());
    output["hits"] = py::int_(hits);
    output["misses"] = py::int_(misses);
    output["hit_rate"] = py::float_(std::round(hit_rate * 10000.0) / 10000.0);
    output["final_keys"] = py::cast(cache_keys);
    return output;
}

PYBIND11_MODULE(chuck_cpp_memory_tier, m) {
    m.doc() = "C++ binding for chuck memory_tier";
    m.def("solve", &solve);
}

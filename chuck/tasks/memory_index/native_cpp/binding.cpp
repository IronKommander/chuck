#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <string>
#include <unordered_set>
#include <vector>

namespace py = pybind11;

namespace {

std::vector<std::size_t> bloom_hashes(const std::string& value, std::size_t bit_count, std::size_t hash_count) {
    std::hash<std::string> hasher;
    std::size_t digest_a = hasher(value);
    std::size_t digest_b = hasher("seed:" + value);
    std::vector<std::size_t> positions;
    positions.reserve(hash_count);
    for (std::size_t index = 0; index < hash_count; ++index) {
        positions.push_back((digest_a + index * digest_b) % bit_count);
    }
    return positions;
}

}  // namespace

py::dict solve(py::object payload_obj) {
    py::dict payload = payload_obj.cast<py::dict>();
    if (!payload.contains("items") || !payload.contains("probes") || !payload.contains("bit_count") || !payload.contains("hash_count")) {
        throw py::value_error("memory_index payload missing required keys");
    }

    std::vector<std::string> items = payload["items"].cast<std::vector<std::string>>();
    std::vector<std::string> probes = payload["probes"].cast<std::vector<std::string>>();
    std::size_t bit_count = payload["bit_count"].cast<std::size_t>();
    std::size_t hash_count = payload["hash_count"].cast<std::size_t>();

    std::vector<std::uint8_t> bits((bit_count + 7) / 8, 0);
    auto set_bit = [&bits](std::size_t position) {
        bits[position / 8] = static_cast<std::uint8_t>(bits[position / 8] | (1U << (position % 8)));
    };
    auto get_bit = [&bits](std::size_t position) {
        return (bits[position / 8] & static_cast<std::uint8_t>(1U << (position % 8))) != 0;
    };

    for (const auto& item : items) {
        for (auto position : bloom_hashes(item, bit_count, hash_count)) {
            set_bit(position);
        }
    }

    std::unordered_set<std::string> item_set(items.begin(), items.end());
    int positives = 0;
    int true_positives = 0;
    int false_positives = 0;
    for (const auto& probe : probes) {
        auto positions = bloom_hashes(probe, bit_count, hash_count);
        bool seen = std::all_of(positions.begin(), positions.end(), get_bit);
        if (!seen) {
            continue;
        }
        ++positives;
        if (item_set.find(probe) != item_set.end()) {
            ++true_positives;
        } else {
            ++false_positives;
        }
    }

    int negative_count = std::max(1, static_cast<int>(probes.size()) - static_cast<int>(items.size() / 2));
    double false_positive_rate = static_cast<double>(false_positives) / static_cast<double>(negative_count);
    double confidence = std::max(0.70, 1.0 - false_positive_rate);

    py::dict output;
    output["items"] = py::int_(items.size());
    output["probes"] = py::int_(probes.size());
    output["positives"] = py::int_(positives);
    output["true_positives"] = py::int_(true_positives);
    output["false_positives"] = py::int_(false_positives);
    output["false_positive_rate"] = py::float_(std::round(false_positive_rate * 10000.0) / 10000.0);
    output["probabilistic"] = py::bool_(true);
    output["confidence"] = py::float_(std::round(confidence * 10000.0) / 10000.0);
    return output;
}

PYBIND11_MODULE(chuck_cpp_memory_index, m) {
    m.doc() = "C++ binding for chuck memory_index";
    m.def("solve", &solve);
}

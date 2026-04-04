#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cmath>
#include <map>
#include <string>
#include <vector>

namespace py = pybind11;

py::dict solve(py::object payload_obj) {
    std::map<std::string, std::vector<std::string>> graph = payload_obj.cast<std::map<std::string, std::vector<std::string>>>();
    std::vector<std::string> nodes;
    nodes.reserve(graph.size());
    for (const auto& [node, _] : graph) {
        nodes.push_back(node);
    }
    std::sort(nodes.begin(), nodes.end());

    if (nodes.empty()) {
        py::dict output;
        output["node_count"] = py::int_(0);
        output["top_node"] = py::str("");
        output["top_score"] = py::float_(0.0);
        output["checksum"] = py::float_(0.0);
        return output;
    }

    constexpr int iterations = 16;
    constexpr double damping = 0.85;
    std::map<std::string, double> rank;
    std::map<std::string, std::vector<std::string>> outgoing;
    for (const auto& node : nodes) {
        rank[node] = 1.0 / static_cast<double>(nodes.size());
        auto found = graph.find(node);
        if (found == graph.end() || found->second.empty()) {
            outgoing[node] = nodes;
        } else {
            outgoing[node] = found->second;
        }
    }

    const double base = (1.0 - damping) / static_cast<double>(nodes.size());
    for (int step = 0; step < iterations; ++step) {
        std::map<std::string, double> new_rank;
        for (const auto& node : nodes) {
            new_rank[node] = base;
        }
        for (const auto& node : nodes) {
            const auto& edges = outgoing[node];
            const double share = rank[node] / static_cast<double>(edges.size());
            for (const auto& target : edges) {
                new_rank[target] += damping * share;
            }
        }
        rank = std::move(new_rank);
    }

    std::string top_node;
    double top_score = -1.0;
    for (const auto& node : nodes) {
        double score = rank[node];
        if (score > top_score || (std::abs(score - top_score) < 1e-15 && node > top_node)) {
            top_score = score;
            top_node = node;
        }
    }

    double checksum = 0.0;
    for (std::size_t index = 0; index < nodes.size(); ++index) {
        checksum += static_cast<double>(index + 1) * rank[nodes[index]];
    }

    py::dict output;
    output["node_count"] = py::int_(nodes.size());
    output["top_node"] = py::str(top_node);
    output["top_score"] = py::float_(std::round(top_score * 1000000.0) / 1000000.0);
    output["checksum"] = py::float_(std::round(checksum * 1000000.0) / 1000000.0);
    return output;
}

PYBIND11_MODULE(chuck_cpp_graph_analytics, m) {
    m.doc() = "C++ binding for chuck graph_analytics";
    m.def("solve", &solve);
}

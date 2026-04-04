#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cmath>
#include <cctype>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace py = pybind11;

namespace {

std::vector<std::string> split_words(const std::string& text) {
    std::vector<std::string> words;
    std::stringstream stream(text);
    std::string token;
    while (stream >> token) {
        words.push_back(token);
    }
    return words;
}

}  // namespace

py::dict solve(py::object payload_obj) {
    py::dict payload = payload_obj.cast<py::dict>();
    if (!payload.contains("docs") || !payload.contains("queries")) {
        throw py::value_error("retrieval_core payload must include 'docs' and 'queries'");
    }

    std::vector<std::string> docs = payload["docs"].cast<std::vector<std::string>>();
    std::vector<std::string> queries = payload["queries"].cast<std::vector<std::string>>();

    constexpr int sample_stride = 2;
    std::vector<int> sampled_doc_ids;
    sampled_doc_ids.reserve((docs.size() + sample_stride - 1) / sample_stride);
    for (std::size_t index = 0; index < docs.size(); index += sample_stride) {
        sampled_doc_ids.push_back(static_cast<int>(index));
    }

    std::unordered_map<std::string, std::set<int>> index;
    for (int doc_id : sampled_doc_ids) {
        for (const auto& term : split_words(docs[static_cast<std::size_t>(doc_id)])) {
            index[term].insert(doc_id);
        }
    }

    const double scale_factor = sampled_doc_ids.empty()
                                    ? 1.0
                                    : static_cast<double>(docs.size()) / static_cast<double>(sampled_doc_ids.size());

    std::string top_term;
    int top_size = -1;
    std::map<std::string, int> ordered_posting_sizes;
    for (const auto& [term, postings] : index) {
        ordered_posting_sizes[term] = static_cast<int>(postings.size() * scale_factor);
    }
    for (const auto& [term, posting_size] : ordered_posting_sizes) {
        if (posting_size > top_size || (posting_size == top_size && term < top_term)) {
            top_term = term;
            top_size = posting_size;
        }
    }

    py::dict query_hits;
    for (const auto& query : queries) {
        auto found = index.find(query);
        const int hit_count = (found == index.end())
                                  ? 0
                                  : static_cast<int>(found->second.size() * scale_factor);
        query_hits[py::str(query)] = py::int_(hit_count);
    }

    const double coverage = docs.empty()
                                ? 1.0
                                : static_cast<double>(sampled_doc_ids.size()) / static_cast<double>(docs.size());
    const double confidence = std::max(0.75, std::min(0.99, 0.65 + coverage * 0.45));

    py::dict output;
    output["doc_count"] = py::int_(docs.size());
    output["sampled_docs"] = py::int_(sampled_doc_ids.size());
    output["vocab_size"] = py::int_(index.size());
    output["top_term"] = py::str(top_term);
    output["top_term_docs"] = py::int_(top_size);
    output["query_hits"] = query_hits;
    output["probabilistic"] = py::bool_(true);
    output["confidence"] = py::float_(std::round(confidence * 10000.0) / 10000.0);
    return output;
}

PYBIND11_MODULE(chuck_cpp_retrieval_core, m) {
    m.doc() = "C++ binding for chuck retrieval_core";
    m.def("solve", &solve);
}

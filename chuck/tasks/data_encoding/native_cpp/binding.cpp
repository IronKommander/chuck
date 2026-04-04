#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>

#include <cmath>

namespace py = pybind11;

py::dict solve(py::object payload_obj) {
    py::bytes payload = payload_obj.cast<py::bytes>();
    const std::size_t input_bytes = py::len(payload);

    py::module_ zlib = py::module_::import("zlib");
    py::module_ hashlib = py::module_::import("hashlib");

    py::bytes compressed = zlib.attr("compress")(payload, 6).cast<py::bytes>();
    py::bytes restored = zlib.attr("decompress")(compressed).cast<py::bytes>();

    const std::size_t compressed_bytes = py::len(compressed);
    const double ratio = input_bytes == 0
                             ? 0.0
                             : static_cast<double>(compressed_bytes) / static_cast<double>(input_bytes);
    const bool roundtrip = restored.equal(payload);
    py::str digest = hashlib.attr("sha256")(restored).attr("hexdigest")().cast<py::str>();

    py::dict output;
    output["input_bytes"] = py::int_(input_bytes);
    output["compressed_bytes"] = py::int_(compressed_bytes);
    output["ratio"] = py::float_(std::round(ratio * 10000.0) / 10000.0);
    output["roundtrip"] = py::bool_(roundtrip);
    output["sha256"] = digest;
    return output;
}

PYBIND11_MODULE(chuck_cpp_data_encoding, m) {
    m.doc() = "C++ binding for chuck data_encoding";
    m.def("solve", &solve);
}

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>
#include <cstdint>
#include <random>
#include <vector>

namespace py = pybind11;

namespace {

std::uint64_t mod_pow(std::uint64_t base, std::uint64_t exponent, std::uint64_t modulus) {
    std::uint64_t result = 1;
    base %= modulus;
    while (exponent > 0) {
        if (exponent & 1U) {
            result = (result * base) % modulus;
        }
        base = (base * base) % modulus;
        exponent >>= 1U;
    }
    return result;
}

bool is_probable_prime(std::uint64_t number, int rounds = 4) {
    if (number < 2) {
        return false;
    }
    constexpr std::uint64_t small_primes[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29};
    for (auto prime : small_primes) {
        if (number == prime) {
            return true;
        }
        if (number % prime == 0) {
            return false;
        }
    }

    std::uint64_t d = number - 1;
    int shifts = 0;
    while ((d % 2) == 0) {
        ++shifts;
        d /= 2;
    }

    std::mt19937_64 rng(number);
    std::uniform_int_distribution<std::uint64_t> dist(2, number - 2);
    for (int i = 0; i < rounds; ++i) {
        std::uint64_t a = dist(rng);
        std::uint64_t x = mod_pow(a, d, number);
        if (x == 1 || x == (number - 1)) {
            continue;
        }

        bool witness_found = true;
        for (int j = 0; j < shifts - 1; ++j) {
            x = mod_pow(x, 2, number);
            if (x == (number - 1)) {
                witness_found = false;
                break;
            }
        }
        if (witness_found) {
            return false;
        }
    }
    return true;
}

}  // namespace

py::dict solve(py::object payload_obj) {
    std::vector<std::uint64_t> candidates = payload_obj.cast<std::vector<std::uint64_t>>();
    std::size_t probable_primes = 0;
    std::uint64_t checksum = 0;
    constexpr std::uint64_t mod = 1'000'000'007;
    for (auto value : candidates) {
        if (is_probable_prime(value, 4)) {
            ++probable_primes;
            checksum = (checksum + value) % mod;
        }
    }

    double density = candidates.empty() ? 0.0 : static_cast<double>(probable_primes) / static_cast<double>(candidates.size());
    double confidence = 1.0 - std::pow(0.25, 4.0);

    py::dict output;
    output["candidates"] = py::int_(candidates.size());
    output["probable_primes"] = py::int_(probable_primes);
    output["prime_density_estimate"] = py::float_(std::round(density * 10000.0) / 10000.0);
    output["checksum"] = py::int_(checksum);
    output["probabilistic"] = py::bool_(true);
    output["confidence"] = py::float_(std::round(confidence * 10000.0) / 10000.0);
    return output;
}

PYBIND11_MODULE(chuck_cpp_prime_analytics, m) {
    m.doc() = "C++ binding for chuck prime_analytics";
    m.def("solve", &solve);
}

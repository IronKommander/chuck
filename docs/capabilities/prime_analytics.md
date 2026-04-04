# prime_analytics

What it does: Finds likely primes quickly from odd-number candidates.

Algorithm design:
- Filter obvious composites with small divisibility checks.
- Run Miller–Rabin primality rounds on remaining candidates.
- Estimate confidence from witness rounds.

Why this design:
- Much faster than exact primality for large batches.
- Accepts tiny error probability for strong speed gains.

Input: Large sets of odd integer candidates.

Output: `candidates`, `probable_primes`, `density`, `confidence`, `checksum`.

# batchmark

> CLI tool for benchmarking shell commands across multiple input sizes with CSV export

## Installation

```bash
pip install batchmark
```

## Usage

Run a benchmark against a command across multiple input sizes:

```bash
batchmark --cmd "sort {input}" --sizes 100 1000 10000 --output results.csv
```

### Options

| Flag | Description |
|------|-------------|
| `--cmd` | Shell command to benchmark (`{input}` is replaced with generated input) |
| `--sizes` | List of input sizes to test |
| `--runs` | Number of runs per size (default: 5) |
| `--output` | Path to CSV export file |

### Example Output

```
size     avg_time    min_time    max_time
100      0.0021s     0.0019s     0.0024s
1000     0.0187s     0.0181s     0.0193s
10000    0.2041s     0.1998s     0.2104s

Results saved to results.csv
```

## Requirements

- Python 3.8+
- Unix-like environment recommended

## License

MIT © 2024
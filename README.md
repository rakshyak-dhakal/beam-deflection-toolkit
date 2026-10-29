# Beam Deflection Toolkit

A Python toolkit for calculating beam deflection using analytical beam theory.

## Features

- Simply supported beam with a central point load
- Simply supported beam with an off-center point load
- Simply supported beam with a uniformly distributed load (UDL)
- Cantilever beam with a tip point load
- Cantilever beam with a uniformly distributed load
- JSON-based configuration
- Input validation and analytical self-checks
- CSV output of calculated results

## Requirements

- Python 3
- No external packages required for the main program

## Project Structure

| File | Description |
|---|---|
| `main.py` | Main program and calculations |
| `beams.py` | Beam deflection equations |
| `config.json` | Default input configuration |
| `config_bad_beam.json` | Invalid beam-case configuration |
| `config_bad_load.json` | Invalid load configuration |
| `config_bad_span.json` | Invalid span configuration |
| `cantilever beam.py` | Standalone cantilever script |

## How to Run

Run the main toolkit:

```powershell
python main.py
```

Run the standalone cantilever script:

```powershell
python "cantilever beam.py"
```

## Configuration

Edit `config.json` to change Young's modulus (`E`), second moment of area (`I`), spans, loads, and off-center load position.

## Output

The main program generates `results.csv`. The standalone script generates `beam results.csv`.

These generated CSV files are excluded from Git using `.gitignore`.

## Scope and Limitations

This project is intended for educational use. Verify units, assumptions, boundary conditions, and results before using calculations for engineering design.

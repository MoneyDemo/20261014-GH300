# Repository Guidelines

## Build and test

Run commands from the repository root. Use `uv` and the project environment; install dependencies through the configured Microsoft package proxy:

```powershell
uv sync --locked --group test --default-index https://packagefeedproxy.microsoft.io/pypi/simple/
```

Build the package with Hatchling:

```powershell
uv build --default-index https://packagefeedproxy.microsoft.io/pypi/simple/
```

Run the full test suite:

```powershell
uv run --locked --group test --default-index https://packagefeedproxy.microsoft.io/pypi/simple/ pytest -vv -ra --tb=long --showlocals
```

Run one test file or one test case:

```powershell
uv run --locked --group test --default-index https://packagefeedproxy.microsoft.io/pypi/simple/ pytest tests/test_calculate_bmi.py
uv run --locked --group test --default-index https://packagefeedproxy.microsoft.io/pypi/simple/ pytest tests/test_classify_bmi.py::test_classify_bmi_at_24_as_overweight
```

## Architecture

The root `app.py` is the console entry point and delegates to `bmi_calculator.app` in `src/bmi_calculator/`. The package separates measurement input, BMI calculation, classification, result display, and orchestration in `bmi_calculator()`. Both entry points guard execution with `if __name__ == "__main__"` so importing the module does not start interactive input.

Tests in `tests/` import the calculation and classification helpers directly; they do not exercise the console flow.

## Conventions

- BMI inputs are weight in kilograms and height in inches. `_calculate_bmi()` converts inches to meters and returns the unrounded BMI; rounding to two decimal places is for display, not classification.
- Preserve classification boundaries and exact result strings: `< 18.5` is `Underweight`, `< 24` is `Normal weight`, `< 27` is `Overweight`, and `>= 27` is `Obesity`.
- Keep each test scenario as an independent `test_...` function. Use `assertpy.assert_that(...).is_equal_to(...)`; for calculation tests, round the result in the assertion rather than changing the calculation.

## Rules
- 所有的回覆都一定要使用繁體中文，而且可以適當地包含表情符號。
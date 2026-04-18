# Changelog

All notable changes to the Ethical Riemann Hypothesis (ERH) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- R package installation support in CI/CD workflows
- PNG/JPG figure export from simulation workflow for thesis integration
- Microtype package for enhanced LaTeX typography
- Improved table float placement options ([htbp] instead of [h])

### Changed
- Updated LaTeX table float options from `[h]` to `[htbp]` for better layout flexibility
- R package installation now uses user library path to avoid permission issues

### Fixed
- Fixed R package installation permission errors in CI/CD
- Fixed trailing whitespace in workflow files

## [0.1.0] - 2024-12-18

### Added
- Initial release of ERH SDK
- Core simulation modules (action space, judgment systems, ethical primes)
- Analysis tools (zeta function, error metrics, statistics)
- Visualization modules for paper figures
- Python SDK with local and remote client support
- Jupyter notebook examples
- LaTeX thesis documents (English and Chinese versions)
- CI/CD workflows for testing and building

### Documentation
- README with installation and usage instructions
- API documentation via docstrings
- Project summary and implementation status documents


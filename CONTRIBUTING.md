# Contributing to Sentinel-AutoGen-Hunter

Thank you for your interest in contributing to Sentinel-AutoGen-Hunter! We welcome community contributions in multi-agent orchestration, cloud-native collectors, detection rules, and MCP tool expansions.

## Development Workflow

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/your-username/sentinel-autogen-hunter.git
   cd sentinel-autogen-hunter
   ```

2. **Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Running Tests**:
   Ensure all tests pass before opening a pull request:
   ```bash
   python -m pytest tests/ -v
   flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
   ```

4. **Pull Request Guidelines**:
   - Write descriptive commit messages using Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
   - Add unit tests for any new agent or MCP tool.
   - Update `README.md` if architectural changes or new environment variables are introduced.

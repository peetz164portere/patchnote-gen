# patchnote-gen

> Generates formatted changelogs from git commit history using configurable templates.

---

## Installation

```bash
pip install patchnote-gen
```

Or install from source:

```bash
git clone https://github.com/yourname/patchnote-gen.git
cd patchnote-gen
pip install .
```

---

## Usage

Run inside any git repository:

```bash
patchnote-gen
```

This will generate a `CHANGELOG.md` based on your commit history using the default template.

### Options

```bash
# Specify an output file
patchnote-gen --output RELEASE_NOTES.md

# Use a custom template
patchnote-gen --template ./templates/my_template.md

# Generate notes for a specific version range
patchnote-gen --from v1.0.0 --to v2.0.0
```

### Example Output

```markdown
## v2.1.0 - 2024-03-15

### Features
- Add support for custom templates (#42)
- Include author names in changelog entries (#38)

### Bug Fixes
- Fix date formatting on Windows (#45)
```

---

## Configuration

Place a `patchnote.toml` in your project root to customize behavior:

```toml
[patchnote-gen]
output = "CHANGELOG.md"
template = "default"
include_authors = true
```

---

## License

MIT © [yourname](https://github.com/yourname)
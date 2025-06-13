# Jamf Keyword Search

A Python utility that downloads all **Scripts** and **Policies** from a Jamf Pro server via the API, then searches for a given keyword within:

- **Scripts**: only the `<script_contents>` block
- **Policies**: only the `<scripts>` section

Search is **case-insensitive** by default; enable exact matching with `--case-sensitive`.

---

## 🛠️ Prerequisites

- Python 3.7 or later
- [`requests`](https://pypi.org/project/requests/)

Install dependencies:

```bash
pip install requests
````

---

## 📥 Installation

1. Clone this repository or copy `jamf_downloader.py` and `README.md` into your project directory.
2. Ensure the script is executable, or invoke via `python3`.

```bash
chmod +x jamf_downloader.py
```

---

## 🚀 Usage

```bash
python3 jamf_downloader.py \
  --url    https://your-jamf-server          # Base URL of Jamf Pro (no trailing slash)
  --user   api_username                       # Your Jamf API account
  --password api_password                     # Jamf API account password
  --keyword SEARCH_TERM                       # Keyword to find
  [--case-sensitive]                          # (Optional) exact, case-sensitive search
  [--output OUTPUT_DIR]                       # (Optional) folder to save XML (default: output)
```

### Flags

| Flag               | Description                                                               |
| ------------------ | ------------------------------------------------------------------------- |
| `--url`            | Base URL of your Jamf Pro server (e.g. `https://rocketman.jamfcloud.com`) |
| `--user`           | Jamf Pro API username                                                     |
| `--password`       | Jamf Pro API password                                                     |
| `--keyword`        | Keyword to search within scripts/policies                                 |
| `--case-sensitive` | Enable case-sensitive search (default: case-insensitive)                  |
| `--output`         | Directory to save downloaded XML files (defaults to `./output`)           |

---

## 📂 Output

- Creates two subdirectories inside `OUTPUT_DIR`:

  - `scripts/` — contains each Script as an XML file
  - `policies/` — contains each Policy as an XML file

- **Console output** highlights matches, e.g.:

  ```
  Keyword 'Jamf_API' found in Superman 4 b3 Script
    - URL: https://rocketman.jamfcloud.com/view/settings/computer-management/scripts/106?tab=script
    - Line 2481: check_jamf_api_credentials
    - Line 2482: delete_jamf_api_access_token

  Keyword 'Jamf_API' found in Add Computer to "FSA Tracking" Policy
    - URL: https://rocketman.jamfcloud.com/policies.html?id=203&o=r
  ```

---

## 🔧 Customization

- **Filter scope**: adjust the XML tags to search only specific parts.
- **Logging**: integrate Python’s `logging` module for file-based logs.
- **Parallelism**: add `concurrent.futures` to download/search in parallel for speed.

---

## 📝 License

MIT © Rocketman Tech

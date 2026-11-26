# Repository contents and maintenance

This note describes what belongs in the [public repository](https://github.com/jonatanlindblad/sweden-electricity-dashboard) and what to check before sharing an update.

## What is included

The shared files are 13 Python scripts, documentation, `requirements.txt`, `.gitignore`, source records and fingerprints, the verified AIB JSON extract, seven CSV outputs and the [current dashboard PDF (v7)](outputs/sweden_electricity_dashboard_v7.pdf). The previously published v5 PDF is retained as an earlier export. Readers can use the CSVs in Power BI without running Python.

Full source downloads, course documents, local Python environments, credentials, editor files and other drafts are excluded through [.gitignore](.gitignore). Editable Power BI report and model files are not included. The PDF is a static export; sharing it does not grant access to the online Power BI report.

To regenerate the data, restore the inputs using [SOURCES.md](SOURCES.md), then follow the [README](README.md). The [methods note](methods_note.md#validation) records which checks passed and what remains untested.

## Checks before sharing updates

- Review the changed files for credentials, personal paths, email addresses and unrelated course material.
- Check PDF text, metadata and attachments, as well as the visible pages.
- Keep source credits and method notes with exported results. Review sharing terms before adding new source files.
- Check the actual files selected for a commit and make sure local links point to files that will be included. Adding a file to `.gitignore` does not remove a file already tracked by Git.

Source data have their own [sharing terms](SOURCES.md). No licence has been assigned to the code; a public repository does not by itself grant an open-source licence.

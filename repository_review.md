# Repository contents and maintenance

The [Sweden electricity dashboard repository](https://github.com/jonatanlindblad/sweden-electricity-dashboard) was first published on 23 November 2026 and is currently private.

## What is included

The repository contains 13 Python scripts, documentation, `requirements.txt`, `.gitignore`, source manifests and fingerprints, the verified AIB JSON extract, seven CSV outputs and the v5 dashboard PDF. The CSVs let readers inspect the results and use them in Power BI without running Python.

Full source downloads, teacher materials, local Python environments, credentials, editor files, duplicate research downloads and older PDFs are excluded through [.gitignore](.gitignore). Editable Power BI report and model files are not included. The PDF is the shared report snapshot; publishing this repository does not grant access to the online Power BI report.

To regenerate the data, restore the inputs using [SOURCES.md](SOURCES.md), then follow the [README](README.md). The [methods note](methods_note.md#validation) records the validation results and their limits.

## Checks before sharing updates

- Review the changed files for credentials, personal paths, email addresses and unrelated course material.
- Check PDF text, metadata and attachments, as well as the visible pages.
- Keep source credits and method notes with exported results. Review sharing terms before adding new source files.
- Check the actual files selected for a commit. Adding a file to `.gitignore` does not remove a file already tracked by Git.

The publication review found no email addresses, personal filesystem paths, private-key markers or common access-token patterns in the selected text files. The four-page PDF had no author metadata, embedded attachments or annotation actions; its text contained no email addresses or personal filesystem paths. Repeat these checks when adding or replacing files.

Source data have their own [sharing terms](SOURCES.md). The project's code has no licence assigned; public availability alone does not make it open source.

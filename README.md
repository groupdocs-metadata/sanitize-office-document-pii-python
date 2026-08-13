# Office Document PII Sanitization

[![Product Page](https://img.shields.io/badge/Product%20Page-2865E0?style=for-the-badge&logo=appveyor&logoColor=white)](https://github.com/groupdocs-metadata/GroupDocs.Metadata-Docs) 
[![Docs](https://img.shields.io/badge/Docs-2865E0?style=for-the-badge&logo=Hugo&logoColor=white)](https://docs.groupdocs.com/metadata/python-net/) 
[![Blog](https://img.shields.io/badge/Blog-2865E0?style=for-the-badge&logo=WordPress&logoColor=white)](https://blog.groupdocs.com/categories/groupdocs.metadata-product-family/) 
[![Free Support](https://img.shields.io/badge/Free%20Support-2865E0?style=for-the-badge&logo=Discourse&logoColor=white)](https://forum.groupdocs.com/c/metadata/) 
[![Temporary License](https://img.shields.io/badge/Temporary%20License-2865E0?style=for-the-badge&logo=rocket&logoColor=white)](https://purchase.groupdocs.com/temp-license/100216)

## Overview

sanitize-office-document-pii-python is a runnable Python demo that strips personally identifiable information from the metadata layer of Office files before they leave your organization. It is built on GroupDocs.Metadata for Python via .NET (package `groupdocs-metadata-net`, pinned to 26.5) and ships with a seeded DOCX so every step runs out of the box. Six documented functions cover four targeted removal passes, a one-call full sanitize, and a verification scan that proves the cleanup worked. The code targets developers who automate pre-publication checks for GDPR, ISO 27001, or client-confidentiality workflows.

## Technology Stack

- **Platform**: Python via .NET
- **Product**: [GroupDocs.Metadata for Python via .NET](https://docs.groupdocs.com/metadata/python-net/)
- **Language**: Python 3
- **Dependency**: `groupdocs-metadata-net==26.5` (the only entry in `requirements.txt`)

## Problem Statement

A Word file remembers more than its text. Author, Manager, and Company fields name real people. Comment threads carry reviewer identities and timestamps. Revision counters and TotalEditingTime reconstruct who worked on the file and for how long, and SharePoint stamps workflow paths and approver IDs into custom properties on every save. I wired the leak check into this demo after a client's contract draft went out with the reviewing lawyer's name sitting in a leftover comment property. None of that is visible in the document body, which is exactly why it slips through manual review.

Scripting the cleanup against raw OOXML is unpleasant. Identity data is scattered across built-in document properties, custom property parts, and app-specific fields, and each Office format arranges them differently. A predicate that works for DOCX misses the XLSX equivalent unless you learn both layouts.

GroupDocs.Metadata collapses that work into one API. Its `remove_properties` call accepts a predicate and applies it across every metadata package the file carries, while the tagging system (`Tags.person.creator`, `Tags.corporate.company`) matches identity-bearing properties by meaning rather than by format-specific name. The [product documentation](https://docs.groupdocs.com/metadata/python-net/) lists 170+ supported formats, so the same six functions handle Word, Excel, and PowerPoint without separate code paths.

## Solution Overview

The demo composes six functions into a sanitize-then-verify pipeline. Four targeted passes remove specific PII groups, one call wipes everything, and a final scan separates true metadata leaks from content-level remnants that metadata APIs cannot reach. Key technical points:

- **Tag-based predicates**: person and company properties are matched via `Tags`, so no format-specific property names are hard-coded.
- **Name-pattern predicates**: comments, revisions, and SharePoint fields are matched by substring rules over `p.name`, catching custom properties that tags do not classify.
- **Full sanitize**: `metadata.sanitize()` removes every detected package in one call and returns the affected-property count.
- **Honest verification**: `run_leak_check` reports metadata leaks (must be zero) separately from Word comments and tracked changes, which live in document body XML and need a content-editing library such as Aspose.Words.
- **Countable results**: every removal function returns the number of affected properties, which the demo asserts on.

### When is targeted removal better than a full sanitize?

Use the targeted functions when the file must stay useful after cleaning. A legal team may need Title and Subject intact while author names disappear, and sanitize() would wipe all of it. Run the predicates during collaboration, then call sanitize_all_pii once before the file leaves your organization. The leak check confirms nothing identity-bearing survived either path.

## Prerequisites

Before running the demo, ensure you have:

- **Python 3** – any actively supported CPython release with pip available
- **GroupDocs.Metadata package** – `pip install groupdocs-metadata-net==26.5`
- **License (optional)** – without a license file the code runs in evaluation mode; set `LICENSE_PATH` in `main.py` to lift evaluation limits

## Getting Started

### Installation

**Using Package Manager:**

```bash
pip install groupdocs-metadata-net==26.5
```

**Manual Installation:**

Clone the repository, then install the pinned dependency from the project root with `pip install -r requirements.txt`.

### Configuration

1. Open `main.py` and point `LICENSE_PATH` at your `.lic` file, or leave the placeholder to run in evaluation mode.
2. Keep `resources/pii-sample.docx` in place; it is the seeded input every function reads.
3. Run `python main.py`. Five cleaned files land in `output/` and the console prints a PASS line per step.

## Repository Structure

```
sanitize-office-document-pii-python/
│
├── main.py
├── requirements.txt
├── methods/
│   ├── __init__.py
│   ├── clear_comments.py
│   ├── remove_author_and_company.py
│   ├── remove_document_server_properties.py
│   ├── run_leak_check.py
│   ├── sanitize_all_pii.py
│   └── strip_revision_history.py
├── output/
│   ├── fully-sanitized.docx
│   ├── no-author.docx
│   ├── no-comments.docx
│   ├── no-revisions.docx
│   └── no-server-props.docx
└── resources/
    └── pii-sample.docx
```

### File Descriptions

- **main.py** – runs all six functions against the sample and asserts each result
- **requirements.txt** – pins `groupdocs-metadata-net==26.5`
- **methods/remove_author_and_company.py** – tag-based removal of identity properties
- **methods/clear_comments.py** – name-pattern removal of comment and reviewer fields
- **methods/strip_revision_history.py** – clears revision counters and editing-time trails
- **methods/remove_document_server_properties.py** – drops SharePoint and workflow fields
- **methods/sanitize_all_pii.py** – one-call full metadata wipe
- **methods/run_leak_check.py** – post-cleanup scan that classifies residual PII
- **output/** – the five cleaned DOCX files a full run produces
- **resources/pii-sample.docx** – seeded input carrying every PII group the demo removes

## Code Implementation

### Implementation: Removes Author, LastSavedBy, Manager, and Company properties

The first pass targets the core identity fields Word, Excel, and PowerPoint leak when files are shared externally. Tag predicates match the properties by semantic role, which is what lets one function serve every Office format. This is the opening step of a GDPR or ISO 27001 pre-publication workflow.

```python
with Metadata(input_path) as metadata:
    affected = metadata.remove_properties(lambda p:
        Tags.person.creator in list(p.tags)
        or Tags.person.editor in list(p.tags)
        or Tags.person.manager in list(p.tags)
        or Tags.corporate.company in list(p.tags))
    metadata.save(output_path)
    return affected
```

#### Technical Details

`remove_properties` walks every metadata package in the file and deletes each property whose tag list intersects the four identity tags. The predicate never names an OOXML field, so custom formats that expose the same tags are covered automatically.

Key pieces: the `Metadata` context manager loads and saves the document, `remove_properties` runs the predicate across every package and returns the affected count, and `Tags.person` / `Tags.corporate` mark identity-bearing properties by meaning. The function takes `input_path` and `output_path`; the demo run produces `output/no-author.docx`.

---

### Implementation: Removes review comments, reviewer names, and comment metadata

Comment properties carry internal author names, timestamps, and draft discussion history. This pass matches them by name substring, which also catches custom comment-related fields the tag system does not classify. It runs after the identity pass when preparing a file for external distribution.

```python
with Metadata(input_path) as metadata:
    affected = metadata.remove_properties(lambda p:
        p.name is not None and (
            "Comment" in p.name
            or "Reviewer" in p.name
            or "Reviewed" in p.name))
    metadata.save(output_path)
    return affected
```

#### Technical Details

The predicate guards against nameless properties, then applies three substring rules. Substring matching is deliberately broad: `"Comment"` catches `Comments`, `CommentCount`, and vendor-specific variants in one rule.

The same `remove_properties` engine runs here, driven by rules over `p.name`, the qualified property name. Inputs match the identity pass, and the demo writes `output/no-comments.docx`.

---

### Implementation: Removes revision numbers, tracked-change authors, and last-printed timestamps

Revision, TrackedChanges, LastPrinted, and TotalEditingTime together reconstruct a document's editing timeline. For compliance-driven publishing that history is confidential, so this pass clears the trail before release.

```python
with Metadata(input_path) as metadata:
    affected = metadata.remove_properties(lambda p:
        p.name is not None and (
            "Revision" in p.name
            or "TrackedChange" in p.name
            or "LastPrinted" in p.name
            or "TotalEditingTime" in p.name
            or "EditTime" in p.name))
    metadata.save(output_path)
    return affected
```

#### Technical Details

Five substring rules cover the property family across Office formats. Note that tracked-change markup inside the document body is content, not metadata; the leak check below reports it separately for exactly that reason.

Five name rules (`Revision`, `TrackedChange`, `LastPrinted`, `TotalEditingTime`, `EditTime`) feed the same removal call. The demo writes `output/no-revisions.docx`.

---

### Implementation: Removes SharePoint / document-server workflow properties

Server-managed properties leak organizational structure: internal workflow paths, approver IDs, and content-type URIs travel with every file saved from SharePoint. This pass strips any property whose name references a server, workflow, template, or approval field.

```python
with Metadata(input_path) as metadata:
    affected = metadata.remove_properties(lambda p:
        p.name is not None and (
            "Server" in p.name
            or "Workflow" in p.name
            or "Approver" in p.name
            or "ContentType" in p.name
            or "Template" in p.name))
    metadata.save(output_path)
    return affected
```

#### Technical Details

These fields rarely appear in property inspectors, which makes them the least-audited PII group in the demo. The same five rules apply unchanged to XLSX and PPTX saved from the same server.

The predicate covers `Server`, `Workflow`, `Approver`, `ContentType`, and `Template` names. The demo writes `output/no-server-props.docx`.

---

### Implementation: Performs a full document sanitize using the built-in sanitize() call

When nothing in the metadata layer should survive, one call replaces the four targeted passes. `sanitize()` strips every detected package: document-info identity fields, comments, revision history, tracked-change authors, and custom OOXML parts. It is the preferred final gate before external publishing because it cannot miss a property a hand-written predicate forgot.

```python
with Metadata(input_path) as metadata:
    affected = metadata.sanitize()
    metadata.save(output_path)
    return affected
```

#### Technical Details

`sanitize()` is thorough by design and correspondingly blunt: Title, Subject, and other harmless descriptive fields disappear along with the PII. The demo runs it last and feeds its output straight into the verification scan. The [Clean metadata](https://docs.groupdocs.com/metadata/python-net/clean-metadata/) docs page describes the underlying behavior.

One call, `sanitize()`, removes every detected package and returns the count. The demo writes `output/fully-sanitized.docx`.

---

### Implementation: Scans a sanitized document for residual PII

Cleanup without verification is a guess. This function re-opens the sanitized file and hunts for anything identity-bearing that survived, using both tag predicates and the same name rules the removal passes applied.

```python
report = LeakReport()
with Metadata(path) as metadata:
    def is_pii(p):
        if p.name is None:
            return False
        tag_hit = (
            Tags.person.creator in list(p.tags)
            or Tags.person.editor in list(p.tags)
            or Tags.person.manager in list(p.tags)
            or Tags.corporate.company in list(p.tags)
        )
        name_hit = any(n in p.name for n in (
            "Comment", "Reviewer", "Revision", "TrackedChange",
            "Classification", "Department", "Server", "Workflow"))
        return tag_hit or name_hit
```

The second half walks every match, discards empty and zero values, and files each survivor into one of two buckets:

```python
    for p in metadata.find_properties(is_pii):
        value = (str(p.interpreted_value) if p.interpreted_value is not None
                 else (str(p.value) if p.value is not None else ""))
        if not value or value == "0" or value == "0.0":
            continue
        entry = f"{p.name}={value}"
        name = p.name or ""
        if (name.startswith("Comment") or name.startswith("Revision")
            or name.startswith("Inspection")):
            report.content_level_leaks.append(entry)
        else:
            report.metadata_leaks.append(entry)
return report
```

#### Technical Details

The two buckets encode an honest boundary. `metadata_leaks` must come back empty for the document to count as sanitized. `content_level_leaks` lists Word comments and tracked changes that live inside `word/document.xml`; those are body content, and removing them takes a content-editing library such as Aspose.Words. Reporting them instead of hiding them keeps the compliance verdict truthful.

`find_properties` performs the read-only search across all packages, `interpreted_value` supplies human-readable values, and the `LeakReport` value object carries the two buckets. The function takes the cleaned document's `path`, and the demo asserts `metadata_leaks` comes back empty.

## Best Practices

When implementing Office document PII sanitization, consider these practices:

- **Verify after every cleanup**: run a read-back scan like `run_leak_check` instead of trusting the removal call's return count.
- **Prefer tags over names where possible**: tag predicates survive format differences; keep name rules for fields the tag system does not classify.
- **Keep targeted and full passes separate**: predicates preserve useful descriptive fields during collaboration, `sanitize()` is the final gate at the trust boundary.
- **Mind the metadata/content boundary**: comments and tracked changes inside the document body need a content-editing tool; do not report a file clean while they remain.
- **Sanitize copies, not originals**: every function here writes to `output_path`, keeping the source intact for your records.

## Additional Resources

For more on metadata cleanup and the APIs this demo uses, explore these resources:

* **Step-by-step use case guide in the documentation** – the same PII workflow as a documented walkthrough: [Read the guide →](https://docs.groupdocs.com/metadata/python-net/use-cases/remove-pii-from-office-files/)

* **In-depth blog article about this project** – background, business context, and the full pipeline explained: [Read the article →](https://blog.groupdocs.com/metadata/remove-pii-from-office-files-python-net/)

* **Metadata Scrubbing - Online and Programmatic Approach** – how scrubbing works in the free online app and in code: [Read the article →](https://blog.groupdocs.com/metadata/metadata-scrubber/)

* **Edit Metadata in Python Applications** – the broader read/update/remove API surface in Python: [Read the article →](https://blog.groupdocs.com/metadata/edit-metadata-in-python/)

* **Remove metadata properties** – reference documentation for predicate-driven removal: [Read the docs →](https://docs.groupdocs.com/metadata/python-net/remove-metadata-properties/)

## Keywords

`remove pii from documents`, `document sanitization python`, `office metadata removal`, `docx metadata cleaner`, `gdpr document compliance`, `remove author from word`, `clear document comments`, `revision history removal`, `sharepoint metadata`, `metadata sanitize api`, `groupdocs metadata python`, `python via .net`, `remove_properties`, `metadata tags`, `document properties`, `xlsx metadata`, `pptx metadata`, `hidden document data`, `pre-publication check`, `metadata leak detection`

## Support

For technical support, visit:
- [Free Support Forum](https://forum.groupdocs.com/c/metadata/)
- [Product Documentation](https://docs.groupdocs.com/metadata/python-net/)
- [API Reference](https://reference.groupdocs.com/metadata/python-net/)

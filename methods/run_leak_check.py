from groupdocs.metadata import Metadata
from groupdocs.metadata.tagging import Tags


class LeakReport:
    def __init__(self):
        self.metadata_leaks = []
        self.content_level_leaks = []


def run_leak_check(path: str) -> LeakReport:
    """
    Scans a sanitized document for residual PII and separates metadata leaks from content-level leaks.

    Remarks:
        Metadata leaks (identity fields, custom OOXML properties, server URLs) must be empty
        to consider the document sanitized. Content-level leaks (Word comments and tracked
        changes that live inside word/document.xml) are reported informationally because
        GroupDocs.Metadata operates on metadata packages, not document body content — those
        require a content-editing library such as Aspose.Words to remove.
    """
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

        for p in metadata.find_properties(is_pii):
            value = str(p.interpreted_value) if p.interpreted_value is not None else (str(p.value) if p.value is not None else "")
            if not value or value == "0" or value == "0.0":
                continue
            entry = f"{p.name}={value}"
            name = p.name or ""
            if name.startswith("Comment") or name.startswith("Revision") or name.startswith("Inspection"):
                report.content_level_leaks.append(entry)
            else:
                report.metadata_leaks.append(entry)
    return report

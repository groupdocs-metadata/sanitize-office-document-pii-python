from groupdocs.metadata import Metadata


def strip_revision_history(input_path: str, output_path: str) -> int:
    """
    Removes revision numbers, tracked-change author names, and last-printed timestamps.

    Remarks:
        Targets Revision, TrackedChanges, LastPrinted, and TotalEditingTime properties which
        together expose the editing timeline and internal authorship trail of a document.
        Essential for compliance-driven publishing where the edit history is confidential.
    """
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

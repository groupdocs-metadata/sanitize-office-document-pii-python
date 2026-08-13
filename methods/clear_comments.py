from groupdocs.metadata import Metadata


def clear_comments(input_path: str, output_path: str) -> int:
    """
    Removes review comments, reviewer names, and comment metadata from an Office document.

    Remarks:
        Strips Comment, Reviewer, and Reviewed properties that carry internal author names,
        timestamps, and draft discussion history. Runs after remove_author_and_company when
        preparing a document for external distribution.
    """
    with Metadata(input_path) as metadata:
        affected = metadata.remove_properties(lambda p:
            p.name is not None and (
                "Comment" in p.name
                or "Reviewer" in p.name
                or "Reviewed" in p.name))
        metadata.save(output_path)
        return affected

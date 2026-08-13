from groupdocs.metadata import Metadata


def sanitize_all_pii(input_path: str, output_path: str) -> int:
    """
    Performs a full document sanitize using the built-in sanitize() call.

    Remarks:
        Uses metadata.sanitize() which strips every detected metadata package, including
        document-info identity fields, comments, revision history, tracked-change authors,
        and custom OOXML parts. Preferred as the final gate before external publishing
        because it is more thorough than a name-based remove_properties predicate.
    """
    with Metadata(input_path) as metadata:
        affected = metadata.sanitize()
        metadata.save(output_path)
        return affected

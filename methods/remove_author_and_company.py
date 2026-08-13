from groupdocs.metadata import Metadata
from groupdocs.metadata.tagging import Tags


def remove_author_and_company(input_path: str, output_path: str) -> int:
    """
    Removes Author, LastSavedBy, Manager, and Company properties from an Office document.

    Remarks:
        Uses GroupDocs.Metadata tag predicates to target the core identity-bearing properties
        leaked by Word, Excel, and PowerPoint when files are shared externally. First step
        of any GDPR or ISO 27001 pre-publication sanitization workflow.
    """
    with Metadata(input_path) as metadata:
        affected = metadata.remove_properties(lambda p:
            Tags.person.creator in list(p.tags)
            or Tags.person.editor in list(p.tags)
            or Tags.person.manager in list(p.tags)
            or Tags.corporate.company in list(p.tags))
        metadata.save(output_path)
        return affected

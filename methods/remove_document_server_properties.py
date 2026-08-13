from groupdocs.metadata import Metadata


def remove_document_server_properties(input_path: str, output_path: str) -> int:
    """
    Removes SharePoint / document-server workflow properties from an Office document.

    Remarks:
        Server-managed properties often carry internal workflow paths, approver IDs, and
        content-type URIs that leak organizational structure. Strips any property whose
        name references a server, workflow, template, or approval field.
    """
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

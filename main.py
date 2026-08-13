import os
import sys

from groupdocs.metadata import License

from methods.remove_author_and_company import remove_author_and_company
from methods.clear_comments import clear_comments
from methods.strip_revision_history import strip_revision_history
from methods.remove_document_server_properties import remove_document_server_properties
from methods.sanitize_all_pii import sanitize_all_pii
from methods.run_leak_check import run_leak_check


LICENSE_PATH = r"YOUR-LICENSE-PATH-HERE"
HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(HERE, "resources")
OUTPUT_DIR = os.path.join(HERE, "output")


def set_license():
    if os.path.exists(LICENSE_PATH):
        License().set_license(LICENSE_PATH)
        print("License applied")
    else:
        print(f"WARN license file not found at {LICENSE_PATH}; running in evaluation mode")


def do_assert(condition: bool, message: str):
    if not condition:
        raise AssertionError(f"assert failed: {message}")
    print(f"PASS {message}")


def main() -> int:
    try:
        set_license()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        src = os.path.join(INPUT_DIR, "pii-sample.docx")
        if not os.path.exists(src):
            print(f"FAIL missing input at {src}")
            return 2

        out1 = os.path.join(OUTPUT_DIR, "no-author.docx")
        n1 = remove_author_and_company(src, out1)
        do_assert(os.path.exists(out1),
                  f"remove_author_and_company removed {n1} properties, wrote {os.path.getsize(out1)} bytes")

        out2 = os.path.join(OUTPUT_DIR, "no-comments.docx")
        n2 = clear_comments(src, out2)
        do_assert(os.path.exists(out2),
                  f"clear_comments removed {n2} properties, wrote {os.path.getsize(out2)} bytes")

        out3 = os.path.join(OUTPUT_DIR, "no-revisions.docx")
        n3 = strip_revision_history(src, out3)
        do_assert(os.path.exists(out3),
                  f"strip_revision_history removed {n3} properties, wrote {os.path.getsize(out3)} bytes")

        out4 = os.path.join(OUTPUT_DIR, "no-server-props.docx")
        n4 = remove_document_server_properties(src, out4)
        do_assert(os.path.exists(out4),
                  f"remove_document_server_properties removed {n4} properties, wrote {os.path.getsize(out4)} bytes")

        out5 = os.path.join(OUTPUT_DIR, "fully-sanitized.docx")
        n5 = sanitize_all_pii(src, out5)
        do_assert(n5 > 0, f"sanitize_all_pii removed {n5} properties")

        report = run_leak_check(out5)
        for leak in report.content_level_leaks:
            print(f"  content-level (needs Aspose.Words): {leak}")
        for leak in report.metadata_leaks:
            print(f"  METADATA LEAK: {leak}")
        do_assert(len(report.metadata_leaks) == 0,
                  f"run_leak_check metadata leaks={len(report.metadata_leaks)} (must be 0); "
                  f"content-level={len(report.content_level_leaks)} (informational — Word comments + tracked changes remain, requires content editing)")

        print()
        print("ALL PASS")
        return 0
    except Exception as ex:
        print(f"FAIL {type(ex).__name__}: {ex}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

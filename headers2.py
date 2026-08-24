from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

REPO_1 = Path(r"C:\repos\deleteMeOne\app1")
REPO_2 = Path(r"C:\repos\deleteTwo\deleteMeTwo")

PARENT_DIRECTORY = Path("app1")

FILE_EXTENSIONS = {
    ".cs",
}


# ============================================================
# REPO 1 MARKERS
#
# Repo 1 is the canonical header/footer format.
# ============================================================

REPO1_HEADER_START = [
    "// ============================================================================",
    "// Copyright (c) 2026 Example Company",
]

REPO1_HEADER_END = [
    "// Description: Example source file used for testing.",
    "// ============================================================================",
]


REPO1_FOOTER_START = [
    "// ============================================================================",
    "// END OF FILE",
]

REPO1_FOOTER_END = [
    "// Example Company - Proprietary and Confidential",
    "// ============================================================================",
]


# ============================================================
# REPO 2 MARKERS
#
# These identify the old header/footer in Repo 2.
# ============================================================

REPO2_HEADER_START = [
    "// -----------------------------------------------------------------------------",
    "// ACME SOFTWARE SYSTEMS",
]

REPO2_HEADER_END = [
    "// Unauthorized distribution or modification is prohibited.",
    "// -----------------------------------------------------------------------------",
]


REPO2_FOOTER_START = [
    "// -----------------------------------------------------------------------------",
    "// [ ACME SOFTWARE SYSTEMS :: END OF SOURCE ]",
]

REPO2_FOOTER_END = [
    "// Document Revision: 2.4",
    "// -----------------------------------------------------------------------------",
]


# ============================================================
# NORMALIZATION FOR MARKER MATCHING
# ============================================================

def normalize_line(line: str) -> str:
    """
    Used ONLY when matching markers.

    Removes:
      - BOM
      - spaces
      - tabs
      - all other whitespace

    Actual file contents are never reformatted by this function.
    """

    line = line.replace("\ufeff", "")

    return "".join(line.split())


def normalize_marker(marker):
    return [
        normalize_line(line)
        for line in marker
    ]


# ============================================================
# FIND MARKER
# ============================================================

def find_marker(lines, marker, start_at=0):
    """
    Find a multi-line marker.

    Whitespace differences in the marker are ignored.

    Returns:
        starting line index

    Returns None if not found.
    """

    normalized_marker = normalize_marker(marker)

    marker_length = len(normalized_marker)

    if marker_length == 0:
        return None

    max_start = len(lines) - marker_length

    for i in range(start_at, max_start + 1):

        matches = True

        for j in range(marker_length):

            source_line = normalize_line(
                lines[i + j]
            )

            if source_line != normalized_marker[j]:
                matches = False
                break

        if matches:
            return i

    return None


# ============================================================
# FIND BLOCK
# ============================================================

def find_block(
    lines,
    start_marker,
    end_marker,
    search_from=0
):
    """
    Find everything from start_marker through end_marker.

    Returns:

        (start_line, end_line)

    end_line is exclusive.
    """

    start_index = find_marker(
        lines,
        start_marker,
        search_from
    )

    if start_index is None:
        return None

    end_search_from = (
        start_index
        + len(start_marker)
    )

    end_index = find_marker(
        lines,
        end_marker,
        end_search_from
    )

    if end_index is None:
        return None

    block_end = (
        end_index
        + len(end_marker)
    )

    return start_index, block_end


# ============================================================
# LOCATE HEADER / FOOTER
# ============================================================

def locate_parts(
    content: str,
    header_start_marker,
    header_end_marker,
    footer_start_marker,
    footer_end_marker
):
    """
    Locate the header and footer boundaries.

    Returns a dictionary containing:

        lines
        header_start
        header_end
        footer_start
        footer_end
    """

    lines = content.splitlines(
        keepends=True
    )

    if not lines:
        return None

    header_block = find_block(
        lines,
        header_start_marker,
        header_end_marker
    )

    if header_block is None:
        return None

    header_start, header_end = (
        header_block
    )

    footer_block = find_block(
        lines,
        footer_start_marker,
        footer_end_marker,
        search_from=header_end
    )

    if footer_block is None:
        return None

    footer_start, footer_end = (
        footer_block
    )

    if footer_start < header_end:
        return None

    return {
        "lines": lines,
        "header_start": header_start,
        "header_end": header_end,
        "footer_start": footer_start,
        "footer_end": footer_end,
    }


# ============================================================
# NEWLINE HELPERS
# ============================================================

def detect_newline(content: str) -> str:
    """
    Detect CRLF vs LF.
    """

    if "\r\n" in content:
        return "\r\n"

    return "\n"


def normalize_newlines(
    text: str,
    newline: str
) -> str:
    """
    Convert text to a requested newline format.
    """

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    return text.replace(
        "\n",
        newline
    )


# ============================================================
# GET LEADING / TRAILING NEWLINES
# ============================================================

def get_leading_newlines(text: str) -> str:
    """
    Return only newline characters at the beginning of text.

    Example:

        "\\r\\n\\r\\nnamespace..."

    returns:

        "\\r\\n\\r\\n"
    """

    index = 0

    while index < len(text):

        if text.startswith("\r\n", index):
            index += 2
            continue

        if text[index] == "\n":
            index += 1
            continue

        if text[index] == "\r":
            index += 1
            continue

        break

    return text[:index]


def get_trailing_newlines(text: str) -> str:
    """
    Return only newline characters at the end of text.
    """

    index = len(text)

    while index > 0:

        if (
            index >= 2
            and text[index - 2:index] == "\r\n"
        ):
            index -= 2
            continue

        if text[index - 1] in "\r\n":
            index -= 1
            continue

        break

    return text[index:]


def remove_leading_newlines(text: str) -> str:
    leading = get_leading_newlines(text)

    return text[len(leading):]


def remove_trailing_newlines(text: str) -> str:
    trailing = get_trailing_newlines(text)

    if not trailing:
        return text

    return text[:-len(trailing)]


# ============================================================
# EXTRACT REPO 1 FORMAT
# ============================================================

def extract_repo1_format(
    repo1_content: str,
    newline: str
):
    """
    Extract Repo 1's:

      - exact header
      - exact spacing after header
      - exact spacing before footer
      - exact footer

    Repo 1 therefore controls the resulting formatting.
    """

    parts = locate_parts(
        repo1_content,
        REPO1_HEADER_START,
        REPO1_HEADER_END,
        REPO1_FOOTER_START,
        REPO1_FOOTER_END
    )

    if parts is None:
        return None

    lines = parts["lines"]

    header = "".join(
        lines[
            parts["header_start"]:
            parts["header_end"]
        ]
    )

    body = "".join(
        lines[
            parts["header_end"]:
            parts["footer_start"]
        ]
    )

    footer = "".join(
        lines[
            parts["footer_start"]:
            parts["footer_end"]
        ]
    )

    # Exact whitespace separating Repo 1 header from code.
    spacing_after_header = (
        get_leading_newlines(body)
    )

    # Exact whitespace separating code from Repo 1 footer.
    spacing_before_footer = (
        get_trailing_newlines(body)
    )

    # Convert Repo 1 formatting to Repo 2's newline style.
    header = normalize_newlines(
        header,
        newline
    )

    spacing_after_header = normalize_newlines(
        spacing_after_header,
        newline
    )

    spacing_before_footer = normalize_newlines(
        spacing_before_footer,
        newline
    )

    footer = normalize_newlines(
        footer,
        newline
    )

    return {
        "header": header,
        "spacing_after_header": spacing_after_header,
        "spacing_before_footer": spacing_before_footer,
        "footer": footer,
    }


# ============================================================
# EXTRACT REPO 2 FUNCTIONAL BODY
# ============================================================

def extract_repo2_body(
    repo2_content: str
):
    """
    Remove Repo 2's header/footer while preserving its actual
    functional body.

    Only boundary newline characters are removed.

    Internal whitespace and formatting are untouched.
    """

    parts = locate_parts(
        repo2_content,
        REPO2_HEADER_START,
        REPO2_HEADER_END,
        REPO2_FOOTER_START,
        REPO2_FOOTER_END
    )

    if parts is None:
        return None

    lines = parts["lines"]

    body = "".join(
        lines[
            parts["header_end"]:
            parts["footer_start"]
        ]
    )

    # Remove only the old formatting surrounding Repo 2's body.
    #
    # We will replace those boundaries with Repo 1's exact
    # formatting.
    body = remove_leading_newlines(
        body
    )

    body = remove_trailing_newlines(
        body
    )

    return body


# ============================================================
# PROCESS ONE FILE
# ============================================================
def update_file(
    repo1_file: Path,
    repo2_file: Path
):
    try:
        # Use utf-8-sig so BOM is handled while reading.
        repo1_content = repo1_file.read_text(
            encoding="utf-8-sig"
        )

        repo2_content = repo2_file.read_text(
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        print(
            f"SKIP - encoding issue: {repo2_file}"
        )
        return

    # ========================================================
    # LOCATE REPO 1 PARTS
    # ========================================================

    repo1_parts = locate_parts(
        repo1_content,
        REPO1_HEADER_START,
        REPO1_HEADER_END,
        REPO1_FOOTER_START,
        REPO1_FOOTER_END
    )

    if repo1_parts is None:
        print(
            f"SKIP - Repo 1 markers not found: "
            f"{repo1_file}"
        )
        return

    # ========================================================
    # LOCATE REPO 2 PARTS
    # ========================================================

    repo2_parts = locate_parts(
        repo2_content,
        REPO2_HEADER_START,
        REPO2_HEADER_END,
        REPO2_FOOTER_START,
        REPO2_FOOTER_END
    )

    if repo2_parts is None:
        print(
            f"SKIP - Repo 2 markers not found: "
            f"{repo2_file}"
        )
        return

    # ========================================================
    # EXTRACT FUNCTIONAL BODIES
    # ========================================================

    repo1_lines = repo1_parts["lines"]
    repo2_lines = repo2_parts["lines"]

    repo1_body = "".join(
        repo1_lines[
            repo1_parts["header_end"]:
            repo1_parts["footer_start"]
        ]
    )

    repo2_body = "".join(
        repo2_lines[
            repo2_parts["header_end"]:
            repo2_parts["footer_start"]
        ]
    )

    # Remove ONLY blank-line boundaries caused by the headers.
    repo1_body = remove_leading_newlines(
        repo1_body
    )

    repo1_body = remove_trailing_newlines(
        repo1_body
    )

    repo2_body = remove_leading_newlines(
        repo2_body
    )

    repo2_body = remove_trailing_newlines(
        repo2_body
    )

    # ========================================================
    # NORMALIZE ONLY FOR BODY COMPARISON
    #
    # CRLF vs LF should not make us think functional code
    # changed.
    # ========================================================

    repo1_body_compare = (
        repo1_body
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    repo2_body_compare = (
        repo2_body
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    # ========================================================
    # IMPORTANT:
    #
    # If functional code is identical, make Repo 2 EXACTLY
    # Repo 1.
    #
    # This eliminates:
    #   - header differences
    #   - footer differences
    #   - blank line differences
    #   - CRLF/LF differences
    #   - final-newline differences
    # ========================================================

    if repo1_body_compare == repo2_body_compare:

        # Read the original bytes so we preserve Repo 1 exactly.
        repo1_bytes = repo1_file.read_bytes()
        repo2_bytes = repo2_file.read_bytes()

        if repo1_bytes == repo2_bytes:
            print(
                f"UNCHANGED: {repo2_file}"
            )
            return

        repo2_file.write_bytes(
            repo1_bytes
        )

        print(
            f"SYNCED EXACTLY: {repo2_file}"
        )

        return

    # ========================================================
    # FUNCTIONAL CODE IS ACTUALLY DIFFERENT
    #
    # Keep Repo 2 code, but apply Repo 1 header/footer.
    # ========================================================

    newline = detect_newline(
        repo1_content
    )

    repo1_format = extract_repo1_format(
        repo1_content,
        newline
    )

    if repo1_format is None:
        print(
            f"SKIP - couldn't extract Repo 1 format: "
            f"{repo1_file}"
        )
        return

    repo2_body = normalize_newlines(
        repo2_body,
        newline
    )

    new_content = (
        repo1_format["header"]
        + repo1_format["spacing_after_header"]
        + repo2_body
        + repo1_format["spacing_before_footer"]
        + repo1_format["footer"]
    )

    # Match Repo 1's encoding style as closely as possible.
    repo2_file.write_text(
        new_content,
        encoding="utf-8"
    )

    print(
        f"UPDATED WITH FUNCTIONAL DIFFERENCE: "
        f"{repo2_file}"
    )

# ============================================================
# MAIN
# ============================================================

def main():

    repo1_parent = (
        REPO_1 /
        PARENT_DIRECTORY
    )

    repo2_parent = (
        REPO_2 /
        PARENT_DIRECTORY
    )

    # --------------------------------------------------------
    # VALIDATE DIRECTORIES
    # --------------------------------------------------------

    if not repo1_parent.exists():

        raise FileNotFoundError(
            f"Repo 1 parent does not exist:\n"
            f"{repo1_parent}"
        )

    if not repo2_parent.exists():

        raise FileNotFoundError(
            f"Repo 2 parent does not exist:\n"
            f"{repo2_parent}"
        )

    print()
    print("Repo 1:")
    print(repo1_parent)

    print()
    print("Repo 2:")
    print(repo2_parent)

    print()
    print("Starting...")
    print()

    updated_count = 0
    no_match_count = 0

    # --------------------------------------------------------
    # WALK REPO 2
    # --------------------------------------------------------

    for repo2_file in repo2_parent.rglob("*"):

        if not repo2_file.is_file():
            continue

        if (
            repo2_file.suffix.lower()
            not in FILE_EXTENSIONS
        ):
            continue

        # ----------------------------------------------------
        # MATCH BY RELATIVE PATH
        #
        # Repo2:
        #
        # app1/Services/Test.cs
        #
        # matches:
        #
        # Repo1:
        #
        # app1/Services/Test.cs
        # ----------------------------------------------------

        relative_path = (
            repo2_file.relative_to(
                repo2_parent
            )
        )

        repo1_file = (
            repo1_parent /
            relative_path
        )

        # ----------------------------------------------------
        # NO MATCH = DO NOTHING
        # ----------------------------------------------------

        if not repo1_file.is_file():

            print(
                f"NO MATCH: "
                f"{relative_path}"
            )

            no_match_count += 1

            continue

        # ----------------------------------------------------
        # UPDATE MATCH
        # ----------------------------------------------------

        update_file(
            repo1_file,
            repo2_file
        )

    print()
    print("Finished.")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

REPO_1 = Path(r"C:\repos\deleteMeOne\app1")
REPO_2 = Path(r"C:\repos\deleteTwo\deleteMeTwo")

# Only process files underneath this directory in each repo.
# Example:
# Repo1/src/MyApp/...
# Repo2/src/MyApp/...
PARENT_DIRECTORY = Path("app1")

# Only modify these file types.
FILE_EXTENSIONS = {
    ".cs",
}


# ============================================================
# HEADER / FOOTER FUNCTIONS
# ============================================================

def split_file(content: str):
    """
    Splits a file into:
        header
        body
        footer

    Assumptions:
    - Header is the first contiguous comment block.
    - Footer is the last contiguous comment block.
    - Header/footer use // comments.
    - A blank line separates header/footer from functional code.

    Returns:
        (header, body, footer)
    """

    lines = content.splitlines(keepends=True)

    if not lines:
        return "", "", ""

    # --------------------------------------------------------
    # Find header
    # --------------------------------------------------------

    header_end = 0

    # Skip leading blank lines if there are any.
    while header_end < len(lines) and not lines[header_end].strip():
        header_end += 1

    header_start = header_end

    # Header must begin with //
    if (
        header_start >= len(lines)
        or not lines[header_start].lstrip().startswith("//")
    ):
        return "", content, ""

    while header_end < len(lines):
        stripped = lines[header_end].strip()

        if stripped.startswith("//") or stripped == "":
            header_end += 1
        else:
            break

    header = "".join(lines[:header_end])

    # --------------------------------------------------------
    # Find footer
    # --------------------------------------------------------

    footer_start = len(lines) - 1

    # Skip trailing blank lines
    while footer_start >= header_end and not lines[footer_start].strip():
        footer_start -= 1

    footer_end = footer_start + 1

    # Footer must end with a // comment
    if (
        footer_start < header_end
        or not lines[footer_start].lstrip().startswith("//")
    ):
        body = "".join(lines[header_end:])
        return header, body, ""

    while footer_start >= header_end:
        stripped = lines[footer_start].strip()

        if stripped.startswith("//") or stripped == "":
            footer_start -= 1
        else:
            break

    footer_start += 1

    body = "".join(lines[header_end:footer_start])
    footer = "".join(lines[footer_start:])

    return header, body, footer


# ============================================================
# PROCESS FILE
# ============================================================

def update_file(repo1_file: Path, repo2_file: Path):
    repo1_content = repo1_file.read_text(encoding="utf-8-sig")
    repo2_content = repo2_file.read_text(encoding="utf-8-sig")

    repo1_header, _, repo1_footer = split_file(repo1_content)

    _, repo2_body, _ = split_file(repo2_content)

    # If Repo 1 doesn't actually have a detectable header/footer,
    # don't modify Repo 2.
    if not repo1_header and not repo1_footer:
        print(f"SKIP - no header/footer: {repo1_file}")
        return

    new_content = (
        repo1_header
        + repo2_body
        + repo1_footer
    )

    # Don't touch the file if nothing actually changes.
    if new_content == repo2_content:
        print(f"UNCHANGED: {repo2_file}")
        return

    repo2_file.write_text(new_content, encoding="utf-8")

    print(f"UPDATED: {repo2_file}")


# ============================================================
# MAIN
# ============================================================

def main():

    repo1_parent = REPO_1 / PARENT_DIRECTORY
    repo2_parent = REPO_2 / PARENT_DIRECTORY

    if not repo1_parent.exists():
        raise FileNotFoundError(
            f"Repo 1 parent directory does not exist:\n{repo1_parent}"
        )

    if not repo2_parent.exists():
        raise FileNotFoundError(
            f"Repo 2 parent directory does not exist:\n{repo2_parent}"
        )

    for repo2_file in repo2_parent.rglob("*"):

        if not repo2_file.is_file():
            continue

        if repo2_file.suffix.lower() not in FILE_EXTENSIONS:
            continue

        # Relative path underneath the configured parent directory.
        relative_path = repo2_file.relative_to(repo2_parent)

        # Look for exactly the same path in Repo 1.
        repo1_file = repo1_parent / relative_path
        # print(f"Repo2 file:   {repo2_file}")
        # print(f"Relative:     {relative_path}")
        # print(f"Looking for:  {repo1_file}")
        # print(f"Exists:       {repo1_file.exists()}")
        # print()
        if not repo1_file.exists():
            print(f"NO MATCH: {relative_path}")
            continue

        update_file(repo1_file, repo2_file)


if __name__ == "__main__":
    main()
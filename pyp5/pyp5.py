"""
pyp5
Module that implements various functions to parse .aaf, .ale and .edl files
and create and start Archiware P5 restore selections.
"""

from subprocess import check_output
import aaf2


def parse_ale(file) -> list:
    """parse supplied ALE file for items to restore"""
    search_items = []
    state = "INIT"
    data = 0
    index = 0

    try:
        with open(file, "r", encoding="utf-8") as ale_file:
            lines = ale_file.readlines()
    except IOError as error:
        return ["ERROR", f"{str(error)}"]

    # -- search for 'Column' and 'Data' portions to get required index
    # -- of search entries and their starting point in file
    for line_nr, line in enumerate(lines):
        if "Column" in line:
            state = "COLUMN"
            for index, column in enumerate(lines[line_nr + 1].split("\t")):
                if "Source File" in column:
                    break
        if "Data" in line:
            state = "DATA"
            data = line_nr + 1
            break

    if state != "DATA" or len(lines[data:]) == 0:
        return ["ERROR", "No search items found."]

    for line in lines[data:]:
        search_items.append(line.split("\t")[index].strip("\n"))

    return search_items


def parse_aaf(file) -> list:
    """parse supplied AAF file for items to restore"""
    search_items = []

    try:
        with aaf2.open(file) as aaf_file:
            # aaf_file.dump()
            source_mobs = aaf_file.content.sourcemobs()
            for mob in source_mobs:
                search_items.append(mob.name)
                # for loc in mob.descriptor.locator:
                #    print(loc['URLString'].value)
    except IOError as error:
        return ["ERROR", f"{str(error)}"]

    return search_items


def parse_edl(file) -> list:
    """parse supplied EDL file for items to restore"""
    search_items = []

    try:
        with open(file, "r", encoding="utf-8") as edl_file:
            lines = edl_file.readlines()
    except IOError as error:
        return ["ERROR", f"{str(error)}"]

    for line in lines:
        if line[:2].isdigit():
            search_items.append(line.split()[1])

    return search_items


def check_p5_connection(nsdchat) -> str:
    """Check if connection to p5 server can be established."""
    try:
        return check_output(nsdchat + ["-c", "srvinfo", "hostname"]).decode("utf-8")
    except Exception as error:
        return str(error)


def new_restore_selection(nsdchat) -> str:
    """Creates a new restore selection.
    Returns restore ID on success, empty string on failure."""
    return check_output(
        nsdchat
        + [
            "-c",
            "RestoreSelection",
            "create",
            "localhost",
            "/Volumes/RESTORE/Archiware/",
        ]
    ).decode("utf-8")


def find_entry(nsdchat, restore_selection, archive_id, item) -> str:
    """Searches for supplied item and adds it to restore selection.
    Returns number of found entries on success, empty string on failure.
    When multiple entries are found, only newest entry gets added."""
    return check_output(
        nsdchat
        + [
            "-c",
            "RestoreSelection",
            restore_selection,
            "findentry",
            archive_id,
            f"{{name *= '{item}'}}",
        ]
    ).decode("utf-8")


def get_volumes(nsdchat, restore_selection):
    """Returns needed volumes for restore on success,
    empty string on failure."""
    return check_output(
        nsdchat + ["-c", "RestoreSelection", restore_selection, "volumes"]
    ).decode("utf-8")


def get_label(nsdchat, volume) -> str:
    """Returns label of volume on success, empty string on failure."""
    return check_output(nsdchat + ["-c", "Volume", volume, "label"]).decode("utf-8")


def get_barcode(nsdchat, volume) -> str:
    """Returns label of volume on success, empty string on failure."""
    return check_output(nsdchat + ["-c", "Volume", volume, "barcode"]).decode("utf-8")


def submit_restore(nsdchat, restore_selection) -> str:
    """Submits restore selection for processing.
    Returns job ID on success, empty string on failure."""
    return (
        check_output(nsdchat + ["-c", "RestoreSelection", restore_selection, "submit"])
        .decode("utf-8")
        .strip()
    )


def describe(nsdchat, restore_selection, title) -> str:
    """Set description for job monitor"""
    return (
        check_output(
            nsdchat + ["-c", "RestoreSelection", restore_selection, "describe", title]
        )
        .decode("utf-8")
        .strip()
    )


def destroy(nsdchat, restore_selection) -> str:
    """Set description for job monitor"""
    return (
        check_output(nsdchat + ["-c", "RestoreSelection", restore_selection, "destroy"])
        .decode("utf-8")
        .strip()
    )


def get_error(nsdchat) -> str:
    """Get last error from nsdchat application"""
    return check_output(nsdchat + ["-c", "geterror"]).decode("utf-8")


def get_archive_index(nsdchat) -> str:
    """Get all available archive plan indexes"""
    return check_output(nsdchat + ["-c", "ArchivPlan", "names"]).decode("utf-8")

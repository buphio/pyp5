"""
pyp5 - CLI
cli wrapper for pyp5 module.
"""

import argparse
import configparser
import glob
import logging
import os
import sys
import postbote
import pyp5


def init_logger(name, level, file):
    """initialize loggers"""
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.FileHandler(file)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def read_conf():
    """read pyp5conf to get required nsdchat options"""
    conf_file = f"{os.path.expanduser('~')}/.pyp5conf"

    try:
        with open(conf_file, "r", encoding="utf-8") as config_file:
            config = configparser.ConfigParser()
            config.read_file(config_file)
    except IOError:
        return "ERROR", [f"{conf_file} not found."], []

    try:
        archive_id = config.get("RESTORE", "archive_id")
        nsdchat = [config.get("GENERAL", "nsdchat")] + config.get(
            "GENERAL", "awsock"
        ).split()
        mail = list(config.get("NOTIFICATION", "email").split(","))
    except configparser.Error as error:
        return "ERROR", f"{conf_file}: {str(error)}", ""

    if not archive_id or not all(__ for __ in nsdchat):
        return "ERROR", f"{conf_file}: Empty entries found."

    return archive_id, nsdchat, mail


def main(current_dir, argv=None) -> int:
    """main function, returns exit code"""
    # --- argument parser to check flags
    parser = argparse.ArgumentParser(
        description="Restores files supplied via .aaf or .ale"
    )
    parser.add_argument(
        "-d",
        "--dry",
        action="store_true",
        help="does not submit restore selection"
    )
    parser.add_argument(
        "-m",
        "--mail",
        action="store_true",
        help="only send testmail (no execution of script)",
    )
    args = parser.parse_args(argv)

    # --- create logger
    app_logger = init_logger(
            "APP", logging.INFO, f"{current_dir}/logs/pyp5.log"
    )

    # --- try to read config file, check connection
    archive_id, nsdchat, mail = read_conf()
    if archive_id == "ERROR":
        app_logger.critical(nsdchat)
        return 1

    app_logger.info(nsdchat)

    if args.mail:
        print(postbote.send(mail, "Test-Mail", "Mail notification works."))
        return 0

    ale_files = list(glob.glob(f'{current_dir}/restore/*.[aA][lL][eE]'))
    aaf_files = list(glob.glob(f"{current_dir}/restore/*.[aA][aA][fF]"))
    files = ale_files + aaf_files

    if not files:
        app_logger.warning("No ALE or AAF files found.")
        print("--------------------------")
        print("No ALE or AAF files found!")
        print("--------------------------")
        return 1

    p5_connection = pyp5.check_p5_connection(nsdchat)
    if p5_connection:
        app_logger.critical(p5_connection)
        return 1

    for file in files:
        if file.split(".")[1] == "ale":
            search_items = pyp5.parse_ale(file)
        else:
            search_items = pyp5.parse_aaf(file)

        if search_items[0] == "ERROR":
            app_logger.error('"%s": %s', file, {search_items[1]})
            os.system(f"mv {file} {current_dir}/failed/")
            continue

        restore_selection = pyp5.new_restore_selection(nsdchat).strip("\n")
        if not restore_selection:
            app_logger.critical("Couldn't create restore selection: %s", file)
            app_logger.info(pyp5.get_error(nsdchat))
            continue

        file_logger = init_logger(
            "FILE",
            logging.INFO,
            f"{current_dir}/logs/{os.path.basename(file)}.log"
        )
        file_logger.info("Created RestoreSelection: %s", restore_selection)

        # --- search for entries and add to restore selection
        for item in search_items:
            result = pyp5.find_entry(
                nsdchat, restore_selection, archive_id, item
            ).strip("\n")
            print(f"{item}: {result}")
            if result == "0" or not result:
                file_logger.warning("%s not found in archive.", item)

        entries = (
            pyp5.check_output(
                nsdchat + ["-c", "RestoreSelection", restore_selection, "entries"]
            )
            .decode("utf-8")
            .strip("\n")
        )

        if not entries or entries == "0":
            file_logger.critical("No entries in Restore Selection.")
            continue

        file_logger.info("Added %s entries to Restore Selection", entries)

        # --- get volumes and corresponding labels
        volumes = pyp5.get_volumes(nsdchat, restore_selection)
        if not volumes:
            file_logger.critical("--- No volumes for restore found! ---")
            file_logger.critical(pyp5.get_error(nsdchat))
            continue

        volumes_list = volumes.strip("\n").split(" ")
        file_logger.info("--- Volumes needed for restore ---")

        volumes = {}

        for volume in sorted(volumes_list):
            label = pyp5.get_label(nsdchat, volume).strip("\n")
            volumes[f'"{volume}"'] = f'"{label}"'
            file_logger.info("%s: %s", volume, label)

        # --- submit selection if dry-run flag is not set
        if not args.dry:
            job_id = pyp5.submit_restore(nsdchat, restore_selection)

            if not job_id:
                file_logger.critical("Could not submit restore selection!")
                postbote.send(
                    mail, "ERROR", f'Could not submit restore selection of "{file}".'
                )
                continue

            file_logger.info("Created restore job with ID %s", job_id)

            # --- send mail with needed volumes
            message = "Volumes needed for restore:\n"
            for key, value in volumes.items():
                message += f"{key}: {value}\n"
            postbote.send(mail, f"Restore {job_id} started", message)

            os.system(f"mv {file} ../finished")

    return 0


if __name__ == "__main__":
    # --- get application/script path
    if getattr(sys, "frozen", False):
        app_dir = os.path.dirname(os.path.dirname(sys.executable))
    else:
        app_dir = os.path.dirname(sys.path[0])

    EXIT_CODE = main(app_dir)

    if EXIT_CODE != 0:
        print("ERRORS generated. Please check log file.")

    sys.exit(EXIT_CODE)

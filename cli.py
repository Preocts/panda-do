"""
Silly panda todo list for command line.

ヽ(￣(ｴ)￣)ﾉ

how to use?

    add a pado! <pado> <something to remember to do>
        python cli.py pado remember to get some water after this!

    mark pado, padone! <padone> <# of pado that is done>
        python cli.py padone 1

    what to do?
        python cli.py palist pado

    what was done?
        python cli.py palist padone
"""
import argparse
import datetime
import json
import os
import pathlib
import sys


# Keep them lowercase
ACTIONS = ["pado", "padone", "palist"]
LIST_TYPES = ["pado", "padone"]
SAVE_TO = pathlib.Path.home() / "pado.json"
DEFAULTS = {"pado": [], "padone": [], "padex": 1}


def valid_action(value):
    return value in ACTIONS


def test_valid_action():
    for action in ACTIONS:
        assert valid_action(action)
    assert not valid_action("")


def valid_add(value):
    return bool(value)


def test_valid_add():
    assert valid_add("true")
    assert not valid_add("")


def valid_remove(value):
    return value.isnumeric()


def test_valid_remove():
    assert valid_remove("1234567890")
    assert not valid_remove("1.1")


def valid_list(value):
    return value in LIST_TYPES


def test_valid_list():
    assert valid_list("padone")
    assert not valid_list("panda")


def read_savefile():
    if not SAVE_TO.exists():
        print("No save file found, creating new one")
        file_content = DEFAULTS
    else:
        with open(SAVE_TO, "r") as in_file:
            file_content = json.load(in_file)
    return file_content


def test_read_savefile():
    global SAVE_TO
    oldsave = SAVE_TO
    SAVE_TO = pathlib.Path("save_test.json")
    try:
        assert not SAVE_TO.exists()
        assert read_savefile() == DEFAULTS
        open(SAVE_TO, "w").write(json.dumps(DEFAULTS))
        assert SAVE_TO.exists()
        assert read_savefile() == DEFAULTS
    finally:
        os.remove(SAVE_TO)
        SAVE_TO = oldsave


def save_savefile(file_content):
    with open(SAVE_TO, "w") as out_file:
        json.dump(file_content, out_file, indent=4)


def test_save_file():
    global SAVE_TO
    oldsave = SAVE_TO
    SAVE_TO = pathlib.Path("save_test.json")
    try:
        assert not SAVE_TO.exists()
        save_savefile(DEFAULTS)
        assert SAVE_TO.exists()
    finally:
        os.remove(SAVE_TO)
        SAVE_TO = oldsave


def add_pado(value, file_content):
    now = datetime.datetime.utcnow()
    pado = f"{file_content['padex']}::{now}::{value}"
    file_content["pado"].append(pado)
    file_content["padex"] += 1
    return f"Added PADO: {pado}"


def test_add_pado():
    content = json.loads(json.dumps(DEFAULTS))
    assert content["padex"] == 1
    assert not len(content["pado"])
    add_pado("test", content)
    assert len(content["pado"]) == 1
    assert content["padex"] == 2


def move_pado(value, file_content):
    for idx, pados in enumerate(file_content["pado"]):
        if pados.startswith(value):
            padone = file_content["pado"].pop(idx)
            file_content["padone"].append(padone)
            return f"Padone: {padone}"


def test_move_pado():
    content = json.loads(json.dumps(DEFAULTS))
    assert not content["pado"]
    assert not content["padone"]
    content["pado"].append("123::xx::xx")
    move_pado("123", content)
    assert not content["pado"]
    assert content["padone"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="pado|padone|palist", type=str)
    parser.add_argument("value", default=[], nargs="*")

    args = parser.parse_args()
    action = args.action.lower()
    value = " ".join(args.value)

    if not valid_action(action):
        print(f"Unexpected action '{action}', expected one of: {ACTIONS}")
        sys.exit(1)

    file_content = read_savefile()

    if action == "pado" and valid_add(value):
        print(add_pado(value, file_content))

    elif action == "padone" and valid_remove(value):
        print(move_pado(value, file_content))

    elif action == "palist" and valid_list(value):
        print(f"{value}:\n", "-=-=-=-=-=" * 3)
        print("\n".join(file_content[value][:20]))

    save_savefile(file_content)

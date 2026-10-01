import sys

import gui
from shell import Shell

DEFAULT_VFS_NAME = "vfs"
EXIT_OK = 0


def main():
    args = sys.argv[1:]
    vfs_name = args[0] if args else DEFAULT_VFS_NAME
    shell = Shell(vfs_name)
    gui.run(shell)
    sys.exit(shell.exit_code or EXIT_OK)


if __name__ == "__main__":
    main()
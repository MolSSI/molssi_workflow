from datetime import datetime
import argparse
import json
import locale
import logging
import molssi_workflow
import molssi_util  # MUST come after molssi_workflow
import molssi_util.printing as printing
import os
import os.path
import shutil
import sys

logger = logging.getLogger(__name__)
variables = molssi_workflow.Variables()


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def run():
    """The standalone flowchart app
    """

    parser = argparse.ArgumentParser(description='Execute a MolSSI workflow')

    parser.add_argument(
        "-v", "--verbose", dest="verbose_count",
        action="count", default=0,
        help="increases log verbosity for each occurence."
    )
    parser.add_argument(
        "--directory", dest="directory",
        default=None, action="store",
        help="Directory to write output and other files."
    )
    parser.add_argument(
        "--force", dest="force", action='store_true'
    )
    parser.add_argument(
        "--output", choices=['files', 'stdout', 'both'],
        default='files',
        help='whether to put the output in files, direct to stdout, or both'
    )
    parser.add_argument(
        "filename", help='the filename of the workflow'
    )

    args = parser.parse_args()

    # Set up logging level to WARNING by default, going more verbose
    # for each new -v, to INFO and then DEBUG and finally ALL with 3 -v's

    numeric_level = max(3 - args.verbose_count, 0) * 10
    logging.basicConfig(level=numeric_level)

    # Create the working directory where files, output, etc. go

    if args.directory is None:
        wdir = os.path.join(
            os.getcwd(),
            datetime.now().isoformat(sep='_', timespec='seconds')
        )
    else:
        wdir = args.directory

    logging.info("The working directory is '{}'".format(wdir))

    if os.path.exists(wdir):
        if args.force:
            shutil.rmtree(wdir)
        else:
            msg = "Directory '{}' exists, use --force to overwrite"\
                  .format(wdir)

            logging.critical(msg)
            sys.exit(msg)

    os.makedirs(wdir, exist_ok=False)

    # Set up the root printer, and add handlers to print to the file
    # 'job.out' in the working directory and to stdout, as requested
    # in the options. Since all printers are children of the root
    # printer, all output at the right levels will flow here
    
    printer = printing.getPrinter()

    # Set up our formatter
    formatter = logging.Formatter(fmt='{message:s}', style='{')

    # A handler for stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(printing.JOB)
    console_handler.setFormatter(formatter)
    printer.addHandler(console_handler)

    # A handler for the file
    file_handler = logging.FileHandler(os.path.join(wdir, 'job.out'))
    file_handler.setLevel(printing.JOB)
    file_handler.setFormatter(formatter)
    printer.addHandler(file_handler)
    
    # And ... finally ... run!
    printer.job("Running in directory '{}'".format(wdir))

    # copy the flowchart to the root directory for later reference
    shutil.copy2(args.filename, os.path.join(wdir, 'flowchart.flow'))

    flowchart = molssi_workflow.Workflow(directory=wdir, output=args.output)
    flowchart.read(args.filename)

    exec = molssi_workflow.ExecWorkflow(flowchart)
    with cd(wdir):
        exec.run(root=wdir)


def open_workflow(name):
    with open(name, 'r') as fd:
        line = fd.readline(256)
        # There may be exec magic as first line
        if line[0:2] == '#!':
            line = fd.readline(256)
        if line[0:7] != '!MolSSI':
            raise RuntimeError('File is not a MolSSI file! -- ' + line)
        tmp = line.split()
        if len(tmp) < 3:
            raise RuntimeError(
                'File is not a proper MolSSI file! -- ' + line)
        if tmp[1] != 'workflow':
            raise RuntimeError('File is not a workflow! -- ' + line)
        workflow_version = tmp[2]
        logger.info('Reading workflow version {} from file {}'.format(
            workflow_version, name))

        data = json.load(fd, cls=molssi_util.JSONDecoder)

    if data['class'] != 'Workflow':
        raise RuntimeError('File {} does not contain a workflow!'.format(name))
        return

    # Restore the workflow
    workflow = molssi_workflow.Workflow()
    workflow.from_dict(data)

    return workflow


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    run()

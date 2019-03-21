# -*- coding: utf-8 -*-
"""Top-level package for MolSSI Workflow."""

import pint
import textwrap

__author__ = """Paul Saxe"""
__email__ = 'psaxe@molssi.org'
__version__ = '0.1.0'

# Unit handling!
ureg = pint.UnitRegistry(auto_reduce_dimensions=True)
pint.set_application_registry(ureg)
Q_ = ureg.Quantity
units_class = ureg('1 km').__class__

_d = pint.Context('chemistry')
_d.add_transformation('[mass]/[substance]', '[mass]',
                      lambda units, x: x / units.avogadro_number)
ureg.add_context(_d)
ureg.enable_contexts('chemistry')

# Text handling
from textwrap import dedent  # nopepe8
wrap_text = textwrap.TextWrapper(width=120)
wrap_stdout = textwrap.TextWrapper(width=120)

# Bring up the classes so that they appear to be directly in
# the molssi_workflow package.

from molssi_workflow.parameters import Parameter  # nopep8
from molssi_workflow.parameters import Parameters  # nopep8
from molssi_workflow.variables import Variables  # nopep8
from molssi_workflow.variables import workflow_variables  # nopep8
from molssi_workflow.plugin_manager import PluginManager  # nopep8
from molssi_workflow.workflow import Workflow  # nopep8
from molssi_workflow.tk_workflow import TkWorkflow  # nopep8
from molssi_workflow.graph import Graph  # nopep8
from molssi_workflow.graph import Edge  # nopep8
from molssi_workflow.exec_workflow import ExecWorkflow  # nopep8
from molssi_workflow.node import Node  # nopep8
from molssi_workflow.start_node import StartNode  # nopep8
from molssi_workflow.tk_edge import TkEdge  # nopep8
from molssi_workflow.tk_node import TkNode  # nopep8
from molssi_workflow.tk_start_node import TkStartNode  # nopep8
from molssi_workflow.exec_local import ExecLocal  # nopep8
from molssi_workflow.split_node import Split  # nopep8
from molssi_workflow.tk_split_node import TkSplit  # nopep8
from molssi_workflow.builtins import SplitStep  # nopep8
from molssi_workflow.join_node import Join  # nopep8
from molssi_workflow.tk_join_node import TkJoin  # nopep8
from molssi_workflow.builtins import JoinStep  # nopep8

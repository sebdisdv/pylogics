# -*- coding: utf-8 -*-
#
# Copyright 2021 WhiteMech
#
# ------------------------------
#
# This file is part of pylogics.
#
# pylogics is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pylogics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pylogics.  If not, see <https://www.gnu.org/licenses/>.
#

"""Utilities for docs tests."""
import traceback
from functools import partial
from pathlib import Path
from typing import Dict, List, Optional

import mistune
import pytest

MISTUNE_BLOCK_CODE_ID = "block_code"


def compile_and_exec(code: str, locals_dict: Optional[Dict] = None) -> Dict:
    """
    Compile and exec the code.

    :param code: the code to execute.
    :param locals_dict: the dictionary of local variables.
    :return: the dictionary of locals.
    """
    locals_dict = {} if locals_dict is None else locals_dict
    try:
        code_obj = compile(code, "fakemodule", "exec")
        exec(code_obj, locals_dict)  # nosec
    except Exception:  # type: ignore
        pytest.fail(
            "The execution of the following code:\n{}\nfailed with error:\n{}".format(
                code, traceback.format_exc()
            )
        )
    return locals_dict


class BaseTestMarkdownDocs:
    """Base test class for testing Markdown documents."""

    MD_FILE: Optional[Path] = None
    code_blocks: List[Dict] = []

    @classmethod
    def setup_class(cls):
        """Set up class."""
        if cls.MD_FILE is None:
            raise ValueError("cannot set up method as MD_FILE is None")
        content = cls.MD_FILE.read_text()
        markdown_parser = mistune.create_markdown(renderer=mistune.AstRenderer())
        cls.blocks = markdown_parser(content)
        cls.code_blocks = list(filter(cls.block_code_filter, cls.blocks))

    @staticmethod
    def block_code_filter(block: Dict) -> bool:
        """Check Mistune block is a code block."""
        return block["type"] == MISTUNE_BLOCK_CODE_ID

    @staticmethod
    def type_filter(type_: Optional[str], b: Dict) -> bool:
        """
        Check Mistune code block is of a certain type.

        If the field "info" is None, return False.
        If type_ is None, this function always return true.

        :param type_: the expected type of block (optional)
        :param b: the block dicionary.
        :return: True if the block should be accepted, false otherwise.
        """
        if type_ is None:
            return True
        return b["info"].strip() == type_ if b["info"] is not None else False

    @classmethod
    def extract_code_blocks(cls, filter_: Optional[str] = None):
        """Extract code blocks from .md files."""
        actual_type_filter = partial(cls.type_filter, filter_)
        bash_code_blocks = filter(actual_type_filter, cls.code_blocks)
        return list(b["text"] for b in bash_code_blocks)


class BasePythonMarkdownDocs(BaseTestMarkdownDocs):
    """Test Markdown documentation by running Python snippets in sequence."""

    @classmethod
    def setup_class(cls):
        """
        Set up class.

        It sets the initial value of locals and globals.
        """
        super().setup_class()
        cls.locals = {}
        cls.globals = {}

    @classmethod
    def _python_selector(cls, block: Dict) -> bool:
        return block["type"] == MISTUNE_BLOCK_CODE_ID and (
            block["info"].strip() == "python" if block["info"] else False
        )

    def _assert(self, locals_, *mocks):
        """Do assertions after Python code execution."""

    def test_python_blocks(self, *mocks):
        """Run Python code block in sequence."""
        python_blocks = list(filter(self._python_selector, self.blocks))

        globals_, locals_ = self.globals, self.locals
        for python_block in python_blocks:
            python_code = python_block["text"]
            exec(python_code, globals_, locals_)  # nosec
        self._assert(locals_, *mocks)

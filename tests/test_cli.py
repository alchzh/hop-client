#!/usr/bin/env python

__author__ = "Patrick Godwin (patrick.godwin@psu.edu)"
__description__ = "a module that tests entry points"


from unittest.mock import patch, mock_open
import pytest

from scimma.client import __version__


@pytest.mark.script_launch_mode("subprocess")
def test_cli_scimma(script_runner):
    ret = script_runner.run("scimma", "--help")
    assert ret.success

    ret = script_runner.run("scimma", "--version")
    assert ret.success

    assert ret.stdout == f"scimma-client version {__version__}\n"
    assert ret.stderr == ""


def test_cli_publish(script_runner, circular_text):
    ret = script_runner.run("scimma", "publish", "--help")
    assert ret.success

    gcn_mock = mock_open(read_data=circular_text)
    with patch("scimma.client.publish.open", gcn_mock) as mock_file, patch(
        "scimma.client.io.Stream.open", mock_open()
    ) as mock_stream:

        gcn_file = "example.gcn3"
        broker_url = "kafka://hostname:port/gcn"
        ret = script_runner.run("scimma", "publish", "-b", broker_url, gcn_file)

        # verify CLI output
        assert ret.success
        assert ret.stderr == ""

        # verify GCN was processed
        mock_file.assert_called_with(gcn_file, "r")
        mock_stream.assert_called_with(broker_url, "w")

def test_cli_subscribe(script_runner):
    ret = script_runner.run("scimma", "subscribe", "--help")
    assert ret.success

    with patch("scimma.client.io.Stream.open", mock_open()) as mock_stream:

        broker_url = "kafka://hostname:port/gcn"
        ret = script_runner.run("scimma", "subscribe", "-b", broker_url)

        # verify CLI output
        assert ret.success
        assert ret.stderr == ""

        # verify broker url was processed
        mock_stream.assert_called_with(broker_url, "r")

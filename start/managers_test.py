import shutil
from pathlib import Path

import pytest
import responses

from start.managers import PathManager, PyPiClient


@pytest.fixture
def current_dir():
    return Path.cwd()


def test_path_manager():
    pm = PathManager("My Project", "My Package")
    assert isinstance(pm, PathManager)


def test_path_manager_required_args():
    with pytest.raises(TypeError) as e:
        PathManager()
    assert "required positional arguments" in str(e.value)
    assert "project_name" in str(e.value)
    assert "package_name" in str(e.value)


def test_path_manager_sanitize_name_no_changes():
    pm = PathManager("My_Project", "My_Package")
    assert pm.sanitize_name("My_Project") == "My_Project"
    assert pm.sanitize_name("My_Package") == "My_Package"


def test_path_manager_sanitize_name_changes():
    pm = PathManager("My Project", "My Package")
    assert pm.sanitize_name("My Project") == "My_Project"
    assert pm.sanitize_name("My Package") == "My_Package"
    assert pm.sanitize_name("My-Project") == "My_Project"
    assert pm.sanitize_name("My.Package") == "My_Package"
    assert pm.sanitize_name("My Project 1") == "My_Project_1"
    assert pm.sanitize_name("My Project-1") == "My_Project_1"
    assert pm.sanitize_name("My Project.1") == "My_Project_1"
    assert pm.sanitize_name("My Project 1.0") == "My_Project_1_0"
    assert pm.sanitize_name("My Project-1.0") == "My_Project_1_0"
    assert pm.sanitize_name("My Project.1.0") == "My_Project_1_0"
    assert pm.sanitize_name("My Project 1.0.0") == "My_Project_1_0_0"
    assert pm.sanitize_name("My Project-1.0.0") == "My_Project_1_0_0"
    assert pm.sanitize_name("My Project.1.0.0") == "My_Project_1_0_0"


def test_path_manager_post_init():
    pm = PathManager("My Project", "My Package")
    assert pm.project_name is not None
    assert pm.package_name is not None
    assert pm.project_name == "My_Project"
    assert pm.package_name == "My_Package"
    assert pm.project_path == Path.cwd().parent / "My_Project"
    assert pm.package_path == Path.cwd().parent / "My_Project" / "My_Package"


def test_path_manager_get_cwd(current_dir):
    pm = PathManager("", "")
    assert pm.get_cwd() == current_dir


def test_path_manager_path_exists(tmp_path):
    p_name = tmp_path / "My_Project"
    p_name.mkdir()
    pm = PathManager("My Project", "My Package")
    assert pm.path_exists(p_name) is True
    p_name.rmdir()
    assert pm.path_exists(p_name) is False


def test_path_manager_create_project_path():
    pm = PathManager("My Project", "My Package")
    assert pm.project_path.exists() is False
    pm.create_project_path()
    assert pm.project_path.exists() is True

    # clean up after test
    shutil.rmtree(pm.project_path)
    assert pm.project_path.exists() is False


def test_pypi_client():
    pypi = PyPiClient()
    assert isinstance(pypi, PyPiClient)


@responses.activate
def test_pypi_client_reduce_versions():
    responses.add(
        responses.GET,
        "https://pypi.org/pypi/wagtail/json",
        json={"releases": {"2.9": {}, "2.9.1": {}, "2.9.2": {}}},
    )
    pypi = PyPiClient()
    assert pypi.base_versions == ["2.9", "2.9.1", "2.9.2"]

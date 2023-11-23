import pytest
import responses
from installer import WagtailVersionInstaller


@responses.activate
def test_installer_latest_version():
    responses.add(
        responses.GET,
        "https://pypi.org/pypi/wagtail/json",
        json={"info": {"version": "3.0.3"}},
    )
    installer = WagtailVersionInstaller()
    assert installer.wagtail_version == "3.0.3"


def test_change_version():
    installer = WagtailVersionInstaller()
    installer.change_version("2.9.1")
    assert installer.wagtail_version == "2.9.1"


@pytest.fixture
def installer_incorrect_version():
    installer = WagtailVersionInstaller()
    installer.change_version("2.9.100")
    return installer


@responses.activate
def test_install_wagtail_response_not_200(installer_incorrect_version):
    responses.add(
        responses.GET,
        "https://pypi.org/pypi/wagtail/2.9.100/json",
        status=404,
    )
    result = installer_incorrect_version.install_wagtail()
    assert result is False


@pytest.fixture
def installer():
    installer = WagtailVersionInstaller()
    return installer


@responses.activate
def test_install_wagtail_success(installer):
    v = installer.wagtail_version
    responses.add(
        responses.GET,
        f"https://pypi.org/pypi/wagtail/{v}/json",
        json={"info": {"version": "{v}"}},
    )
    result = installer.install_wagtail()
    assert result is True

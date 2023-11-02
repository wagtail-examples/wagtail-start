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


def test_installer_value_four_numbers():
    with pytest.raises(ValueError) as e:
        WagtailVersionInstaller("2.9.1.1")
    assert "The version of wagtail is not valid" in str(e.value)


def test_installer_value_three_numbers():
    wvi = WagtailVersionInstaller("2.9.1")
    assert wvi.wagtail_version == "2.9.1"


def test_installer_value_two_numbers():
    wvi = WagtailVersionInstaller("2.9")
    assert wvi.wagtail_version == "2.9.0"


def test_installer_value_single_number():
    installer = WagtailVersionInstaller("2")
    assert installer.wagtail_version == "2.0.0"


def test_change_version():
    installer = WagtailVersionInstaller("2.9")
    installer.change_version("2.9.1")
    assert installer.wagtail_version == "2.9.1"


# @responses.activate
# def test_install_wagtail_response_not_200():
#     responses.add(
#         responses.GET,
#         "https://pypi.org/pypi/wagtail/2.9.1/json",
#         json={"info": {"version": "2.9.1"}},
#         status=404,
#     )
#     installer = WagtailVersionInstaller()
#     with pytest.raises(ValueError) as e:
#         installer.install_wagtail()

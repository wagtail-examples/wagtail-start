import subprocess

import requests


def clean_site_name(site_name):
    """Clean the site name
    by removing spaces, dashes and dots"""
    remove_chars = ["-", ".", " "]
    for char in remove_chars:
        if char in site_name:
            site_name = site_name.replace(char, "")

    return site_name.lower()


def get_current_wagtail_version():
    # get the current latest wagtail version from pypi
    # using requests
    url = "https://pypi.org/pypi/wagtail/json"
    response = requests.get(url)
    data = response.json()
    return str(data["info"]["version"])


def install_wagtail_in_virtualenv(cmd):
    subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

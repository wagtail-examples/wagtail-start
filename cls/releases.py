from dataclasses import dataclass

import httpx


@dataclass
class PyPiParser:
    """
    A client for the PyPi API

    Attributes:
        package_name: The name of the package
        base_url: The base url for the PyPi json API
    """

    package_name: str = "wagtail"
    base_url: str = f"https://pypi.org/pypi/{package_name}/json"

    def __post_init__(self) -> None:
        resp = httpx.get(self.base_url)
        self.base_response = resp.json()
        self.base_versions = self._reduce_versions(
            list(self.base_response["releases"].keys())
        )
        self.release_groups = self.parse_release_groups()
        self.latest_release = self.parse_latest_release()

    def _reduce_versions(self, versions: list) -> list:
        reduced_versions = []
        for version in versions:
            if "rc" not in version and "b" not in version and "a" not in version:
                # remove pre-release versions
                reduced_versions.append(version)

        return reduced_versions

    def parse_release_groups(self):
        grouped_releases = {}
        for item in self.base_versions:
            first_digit = item.split(".")[0]
            if first_digit in grouped_releases:
                grouped_releases[first_digit].append(item)
            else:
                grouped_releases[first_digit] = [item]

        # sort grouped_releases by first digit desc
        grouped_releases = dict(
            sorted(grouped_releases.items(), key=lambda x: int(x[0]), reverse=True)
        )
        return grouped_releases

    def parse_latest_release(self):
        major = list(self.release_groups.keys())[0]
        releases = self.release_groups[major]
        return releases[-1]

    def get_release_group(self, major):
        return self.release_groups[major]


if __name__ == "__main__":
    pypi = PyPiParser()
    # print(pypi.base_versions)
    # print(pypi.release_groups)
    print(pypi.get_release_group("2"))

import importlib.metadata
import unittest


class TestPackagesInstallation(unittest.TestCase):
    """Test that all packages are installed."""

    def test_requirements_txt(self):
        with open("/usr/src/requirements.txt", encoding='utf-8') as file:
            requirements = file.read().splitlines()
            # Remove versions from package names
            requirements_unversioned = [package.split("==")[0] for package in requirements]
            # Ignore local package sources ./ and extras []
            packages = [package.strip("./").split("[")[0] for package in requirements_unversioned]
            for package in packages:
                try:
                    importlib.metadata.version(package)
                    print(f"Package is installed: {package}")
                except importlib.metadata.PackageNotFoundError:
                    print(f"Package is not installed: {package}")
                    raise


if __name__ == "__main__":
    unittest.main()

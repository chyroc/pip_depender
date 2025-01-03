"""
pip_depender - A tool to find the most suitable package versions for your Python project
"""

import json
from typing import Dict, List, Optional, Union, Tuple
import httpx
from packaging.version import Version, parse
from packaging.specifiers import SpecifierSet
from collections import defaultdict

class DependencyVersion:
    def __init__(self, version: str, python_version: Optional[str] = None):
        self.version = version
        self.python_version = python_version

    def to_dict(self) -> Dict:
        if self.python_version:
            return {"version": self.version, "python": self.python_version}
        return self.version

class DependencyFinder:
    def __init__(self):
        self.client = httpx.Client()

    def get_package_info(self, package_name: str) -> Tuple[List[str], Dict]:
        """Get all versions and latest version info of a package"""
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()
        return list(data["releases"].keys()), data["info"]

    def get_version_info(self, package_name: str, version: str) -> Dict:
        """Get information for a specific version"""
        url = f"https://pypi.org/pypi/{package_name}/{version}/json"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def find_suitable_versions(
        self, package_name: str, python_version: str = ">=3.11"
    ) -> Union[str, List[Dict[str, str]]]:
        """
        Find suitable versions for the specified Python version requirement
        
        Args:
            package_name: Package name
            python_version: Python version requirement, e.g. ">=3.11"
            
        Returns:
            A single version string or a list of version dictionaries
        """
        versions, info = self.get_package_info(package_name)
        # Sort versions
        sorted_versions = sorted([parse(v) for v in versions if not parse(v).is_prerelease])
        
        if not sorted_versions:
            raise ValueError(f"No suitable versions found for {package_name}")

        # Group by Python version requirements
        python_version_groups = defaultdict(list)
        for version in sorted_versions:
            version_info = self.get_version_info(package_name, str(version))
            requires_python = version_info["info"].get("requires_python", "")
            if not requires_python:
                requires_python = ">= 2.7"  # Default Python version requirement
            python_version_groups[requires_python].append(version)

        # If only one Python version requirement group
        if len(python_version_groups) == 1:
            latest_version = sorted_versions[-1]
            version_str = f"^{latest_version.major}.{latest_version.minor}.{latest_version.micro}"
            requires_python = next(iter(python_version_groups.keys()))
            return DependencyVersion(version_str, requires_python).to_dict()

        # Multiple Python version requirement groups
        result = []
        for requires_python, versions in python_version_groups.items():
            if not versions:
                continue
            latest_version = sorted(versions)[-1]
            version_str = f"^{latest_version.major}.{latest_version.minor}.{latest_version.micro}"
            result.append(DependencyVersion(version_str, requires_python))

        if len(result) > 1:
            # Sort by Python version requirement, newer versions first
            result.sort(key=lambda x: parse(x.python_version.replace(">=", "").replace("<=", "").strip()), reverse=True)
            return [v.to_dict() for v in result]

        return result[0].to_dict()

    def close(self):
        """Close the HTTP client"""
        self.client.close() 
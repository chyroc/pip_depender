"""
pip_depender - A tool to find the most suitable package versions for your Python project
"""

from typing import Dict, List, Optional, Union, Tuple, Set
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
        self._python_requirements_cache = {}

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

    def get_min_python_version(self, requires_python: str) -> Optional[str]:
        """Extract minimum Python version from requirement string"""
        if not requires_python:
            return "2.7"
        spec = SpecifierSet(requires_python)
        min_version = None
        for s in spec:
            if s.operator in (">=", ">"):
                if not min_version or parse(s.version) > parse(min_version):
                    min_version = s.version
        return min_version or "2.7"

    def get_package_dependencies(self, package_name: str, version: str, visited: Optional[Set[str]] = None) -> str:
        """Get the minimum Python version required by the package and its dependencies"""
        if visited is None:
            visited = set()
        
        cache_key = f"{package_name}=={version}"
        if cache_key in self._python_requirements_cache:
            return self._python_requirements_cache[cache_key]
        
        if package_name in visited:
            return "2.7"
        
        visited.add(package_name)
        version_info = self.get_version_info(package_name, version)
        requires_python = version_info["info"].get("requires_python", "")
        min_python = self.get_min_python_version(requires_python)
        
        # Check dependencies
        requires_dist = version_info["info"].get("requires_dist", []) or []
        for req in requires_dist:
            try:
                # Parse requirement string to get package name and version
                parts = req.split(";")[0].strip().split(" ")
                dep_name = parts[0]
                dep_version = None
                for part in parts[1:]:
                    if part.startswith(">=") or part.startswith("=="):
                        dep_version = part.replace(">=", "").replace("==", "").strip()
                        break
                
                if dep_version:
                    dep_min_python = self.get_package_dependencies(dep_name, dep_version, visited)
                    if parse(dep_min_python) > parse(min_python):
                        min_python = dep_min_python
            except:
                continue
        
        self._python_requirements_cache[cache_key] = min_python
        return min_python

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

        # Get version info and group by Python version
        version_info_map = {}
        python_version_groups = defaultdict(list)
        
        for version in sorted_versions:
            # Check both package and its dependencies Python requirements
            min_python = self.get_package_dependencies(package_name, str(version))
            version_info_map[version] = min_python
            python_version_groups[min_python].append(version)

        # Sort Python versions
        sorted_python_versions = sorted(python_version_groups.keys(), key=parse, reverse=True)
        
        # Create version ranges
        result = []
        for i, py_version in enumerate(sorted_python_versions):
            versions = python_version_groups[py_version]
            latest_version = max(versions)
            version_str = f"^{latest_version.major}.{latest_version.minor}.{latest_version.micro}"
            
            # Set Python version range
            if i == 0:  # Highest Python version
                python_range = f">={py_version}"
            else:
                python_range = f">={py_version},<{sorted_python_versions[i-1]}"
            
            # Skip versions that don't match the target Python version
            try:
                target_spec = SpecifierSet(python_version)
                version_spec = SpecifierSet(python_range)
                # Check if there's any overlap in the version ranges
                if any(v in version_spec for v in target_spec):
                    result.append(DependencyVersion(version_str, python_range))
            except:
                # If there's any error in parsing version specs, include the version anyway
                result.append(DependencyVersion(version_str, python_range))

        if not result:
            # If no versions match the Python requirement, return the latest compatible version
            latest_version = sorted_versions[-1]
            version_str = f"^{latest_version.major}.{latest_version.minor}.{latest_version.micro}"
            requires_python = version_info_map[latest_version]
            return DependencyVersion(version_str, f">={requires_python}").to_dict()

        if len(result) == 1:
            return result[0].to_dict()

        return [v.to_dict() for v in result]

    def close(self):
        """Close the HTTP client"""
        self.client.close() 
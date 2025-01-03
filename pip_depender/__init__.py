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
        """获取包的所有版本和最新版本的信息"""
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()
        return list(data["releases"].keys()), data["info"]

    def get_version_info(self, package_name: str, version: str) -> Dict:
        """获取特定版本的信息"""
        url = f"https://pypi.org/pypi/{package_name}/{version}/json"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def find_suitable_versions(
        self, package_name: str, python_version: str = ">=3.11"
    ) -> Union[str, List[Dict[str, str]]]:
        """
        找到适合指定 Python 版本的包版本
        
        Args:
            package_name: 包名
            python_version: Python 版本要求，例如 ">=3.11"
            
        Returns:
            如果只有一个版本，返回版本字符串
            如果有多个版本，返回版本列表
        """
        versions, info = self.get_package_info(package_name)
        # 按版本号排序
        sorted_versions = sorted([parse(v) for v in versions if not parse(v).is_prerelease])
        
        if not sorted_versions:
            raise ValueError(f"No suitable versions found for {package_name}")

        # 按 Python 版本要求分组
        python_version_groups = defaultdict(list)
        for version in sorted_versions:
            version_info = self.get_version_info(package_name, str(version))
            requires_python = version_info["info"].get("requires_python", "")
            if not requires_python:
                requires_python = ">= 2.7"  # 默认 Python 版本要求
            python_version_groups[requires_python].append(version)

        # 如果只有一个 Python 版本要求组
        if len(python_version_groups) == 1:
            latest_version = sorted_versions[-1]
            version_str = f"^{latest_version.major}.{latest_version.minor}.{latest_version.micro}"
            requires_python = next(iter(python_version_groups.keys()))
            return DependencyVersion(version_str, requires_python).to_dict()

        # 多个 Python 版本要求组
        result = []
        for requires_python, versions in python_version_groups.items():
            if not versions:
                continue
            latest_version = sorted(versions)[-1]
            version_str = f"^{latest_version.major}.{latest_version.minor}.{latest_version.micro}"
            result.append(DependencyVersion(version_str, requires_python))

        if len(result) > 1:
            # 按 Python 版本要求排序，让更新的版本在前面
            result.sort(key=lambda x: parse(x.python_version.replace(">=", "").replace("<=", "").strip()), reverse=True)
            return [v.to_dict() for v in result]

        return result[0].to_dict()

    def close(self):
        """关闭 HTTP 客户端"""
        self.client.close() 
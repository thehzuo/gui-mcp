from __future__ import annotations

from setuptools import find_packages, setup

setup(
    name="gui2-artifact-mcp-py",
    version="0.1.0",
    description="Python MCP server that renders GUI 2.0 ArtifactSpec JSON into HTML.",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.11",
    install_requires=["mcp[cli]>=1.9.0", "pydantic>=2.7"],
    extras_require={"dev": ["pytest>=8", "ruff>=0.5"]},
    entry_points={
        "console_scripts": [
            "gui2-artifact-mcp=gui2_artifact_mcp.server:main",
            "gui2-artifact-mcp-py=gui2_artifact_mcp.server:main",
            "gui2-render-example=gui2_artifact_mcp.cli:render_example_main",
        ]
    },
)

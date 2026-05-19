from __future__ import annotations

from setuptools import find_packages, setup

setup(
    name="web-gui-mcp",
    version="0.1.0",
    description="Python MCP server that renders Web GUI ArtifactSpec JSON into HTML.",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.11",
    install_requires=["mcp[cli]>=1.9.0", "pydantic>=2.7"],
    extras_require={"dev": ["playwright>=1.45", "pytest>=8", "ruff>=0.5"]},
    entry_points={
        "console_scripts": [
            "web-gui-mcp=web_gui_mcp.server:main",
            "web-gui-render-example=web_gui_mcp.cli:render_example_main",
        ]
    },
)

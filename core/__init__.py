"""gcontext-core — the shared library behind the CLI and the cloud platform.

Four concerns, nothing else:

  manifest    read/write module.yaml, the manifest model, cadence parsing
  schemas     validate names and file paths at trust boundaries
  kind_specs  per-kind disk layout (integration / task / workflow)
  llms_gen    regenerate workspace files (llms.txt, system.md, structure.md)

Import from the package root: `from core import read_manifest, KIND_SPECS`.
See llms.txt for the full public API with signatures.
"""

# manifest
from core.manifest import (
    ModuleKind,
    JobSpec,
    ModuleManifest,
    parse_every,
    read_manifest,
    write_manifest,
    render_schema_md,
)

# schemas
from core.schemas import validate_module_name, validate_module_file_path

# kind_specs
from core.kind_specs import (
    KindSpec,
    KIND_SPECS,
    InfoSection,
    INTEGRATION_INFO_SECTIONS,
    render_kind_specs_md,
    render_info_md_sections_md,
)

# llms_gen
from core.llms_gen import (
    extract_module_summary,
    generate_root_llms_txt,
    generate_structure_md,
    generate_system_md,
)

# This list IS the public API. If it's not here, it's an implementation detail.
__all__ = [
    # manifest
    "ModuleKind",
    "JobSpec",
    "ModuleManifest",
    "parse_every",
    "read_manifest",
    "write_manifest",
    "render_schema_md",
    # schemas
    "validate_module_name",
    "validate_module_file_path",
    # kind_specs
    "KindSpec",
    "KIND_SPECS",
    "InfoSection",
    "INTEGRATION_INFO_SECTIONS",
    "render_kind_specs_md",
    "render_info_md_sections_md",
    # llms_gen
    "extract_module_summary",
    "generate_root_llms_txt",
    "generate_structure_md",
    "generate_system_md",
]

from datetime import datetime
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.genai import types


async def create_report(
    filename: str,
    title: str,
    content: str,
    tool_context: ToolContext,
) -> dict:
    """Creates a new report and saves it as a text artifact (version 0).

    Args:
        filename: File name for the report, ending in .txt, e.g. "q3_sales.txt".
        title: The report title.
        content: The full report body, written from the user's details.
    """
    if filename in await tool_context.list_artifacts():
        return {
            "status": "error",
            "message": f"{filename} already exists. Use update_report to change it.",
        }

    version = await tool_context.save_artifact(
        filename=filename,
        artifact=types.Part(text=f"{title}\n\n{content}"),
        custom_metadata={"change": "Created report"},
    )
    return {"status": "success", "filename": filename, "version": version}


async def read_report(
    filename: str,
    tool_context: ToolContext,
    version: Optional[int] = None,
) -> dict:
    """Reads a report. Returns the latest version unless a version is given.

    Args:
        filename: The report's file name.
        version: A specific version number to read. Leave empty for the latest.
    """
    part = await tool_context.load_artifact(filename=filename, version=version)
    if part is None:
        return {"status": "error", "message": f"{filename} (version {version}) not found."}

    info = await tool_context.get_artifact_version(filename=filename, version=version)
    return {
        "status": "success",
        "filename": filename,
        "version": info.version,
        "content": part.text,
    }


async def update_report(
    filename: str,
    updated_content: str,
    change_summary: str,
    tool_context: ToolContext,
) -> dict:
    """Saves a modified report as a new version. Earlier versions are kept.

    Args:
        filename: The report's file name. It must already exist.
        updated_content: The complete new report text (title and body), with the
            user's changes applied to the latest version.
        change_summary: One short line describing what changed.
    """
    if filename not in await tool_context.list_artifacts():
        return {"status": "error", "message": f"{filename} not found. Create it first."}

    version = await tool_context.save_artifact(
        filename=filename,
        artifact=types.Part(text=updated_content),
        custom_metadata={"change": change_summary},
    )
    return {"status": "success", "filename": filename, "version": version}


async def report_history(filename: str, tool_context: ToolContext) -> dict:
    """Lists every version of a report with when it was saved and what changed.

    Args:
        filename: The report's file name.
    """
    latest = await tool_context.get_artifact_version(filename=filename)
    if latest is None:
        return {"status": "error", "message": f"{filename} not found."}

    versions = []
    for v in range(latest.version + 1):
        info = await tool_context.get_artifact_version(filename=filename, version=v)
        if info:
            versions.append({
                "version": info.version,
                "saved_at": datetime.fromtimestamp(info.create_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "change": (info.custom_metadata or {}).get("change", ""),
            })
    return {"status": "success", "filename": filename, "versions": versions}


async def list_reports(tool_context: ToolContext) -> dict:
    """Lists all reports saved in this session."""
    return {"status": "success", "reports": await tool_context.list_artifacts()}


root_agent = LlmAgent(
    name="dynamic_report_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a report assistant. You write reports from the user's details,
    save them, and keep every change as a new version.

    - New report: write a clear title and body from the user's details, pick a
      short descriptive filename ending in .txt, and call create_report.
    - Change a report: first call read_report to get the latest version, apply
      the user's changes to that text, then call update_report with the full
      updated text and a one-line change_summary. Never drop parts the user
      didn't ask to change.
    - Show a report or an older version: call read_report (with version if given).
    - History: call report_history.
    - Which reports exist: call list_reports.

    After saving, always tell the user the filename and the version number,
    then show the report text.
    """,
    tools=[create_report, read_report, update_report, report_history, list_reports],
)

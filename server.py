from fastmcp import FastMCP
from ifc_tools import calculate_coverage_ratio
from regulation_client import get_regulatory_grz

mcp = FastMCP("ifc-compliance-mcp")


@mcp.tool()
def check_grz_compliance(ifc_path: str, plot_number: str, location: str = "Stuttgart") -> dict:
    computed = calculate_coverage_ratio(ifc_path)
    regulation = get_regulatory_grz(plot_number, location=location)
    extracted = regulation["extracted_grz"]

    if extracted is None:
        outcome = "N/A - no value asserted"
    elif computed["computed_coverage_ratio"] <= extracted + 0.02:
        outcome = "Within regulatory limit"
    else:
        outcome = "Exceeds regulatory limit"

    return {
        "plot_number": plot_number,
        "computed_coverage_ratio": computed["computed_coverage_ratio"],
        "regulatory_grz": extracted,
        "outcome": outcome,
        "system_analysis_text": regulation["analysis_text"],
    }


if __name__ == "__main__":
    # NOTE: check your installed FastMCP version's docs for the exact run() signature —
    # newer versions typically accept a transport argument like this:
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
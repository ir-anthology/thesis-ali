def format(results: dict) -> str:
    if "error" in results:
        return results["error"]

    try:
        variables = results["head"]["vars"]
        bindings = results["results"]["bindings"]

        if not bindings:
            return "No results found."

        headers = ["#"] + [f"?{v}" for v in variables]
        rows = []

        for i, row in enumerate(bindings, start=1):
            values = [str(i)]
            for var in variables:
                if var in row:
                    values.append(row[var].get("value", ""))
                else:
                    values.append("")
            rows.append(values)

        col_widths = [len(h) for h in headers]
        for row in rows:
            for j, val in enumerate(row):
                col_widths[j] = max(col_widths[j], len(val))

        lines = []
        header_line = (
            "| "
            + " | ".join(
                h.rjust(col_widths[i]) if i > 0 else h.ljust(col_widths[i])
                for i, h in enumerate(headers)
            )
            + " |"
        )
        lines.append(header_line)

        separator = (
            "| "
            + " | ".join(
                ("-" * col_widths[0])
                if i == 0
                else ("-" * col_widths[i]).rjust(col_widths[i])
                for i in range(len(headers))
            )
            + " |"
        )
        lines.append(separator)

        for row in rows:
            row_line = (
                "| "
                + " | ".join(
                    val.rjust(col_widths[j]) if j > 0 else val.ljust(col_widths[j])
                    for j, val in enumerate(row)
                )
                + " |"
            )
            lines.append(row_line)

        return "\n".join(lines)
    except (KeyError, IndexError) as e:
        return f"Failed to parse SPARQL results: {e}"

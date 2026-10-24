#!/usr/bin/env python3

import ipaddress
import os
from typing import Any

import yaml


INPUT_FILE = os.path.join("data", "inventory.yaml")
OUTPUT_FILE = os.path.join("docs", "inventory.md")


def validate_ip(ip_value: Any) -> bool:
    """
    بررسی می‌کند که مقدار ورودی یک آدرس IPv4 معتبر باشد.
    """
    if not isinstance(ip_value, str) or not ip_value.strip():
        return False

    try:
        ipaddress.IPv4Address(ip_value.strip())
        return True
    except ipaddress.AddressValueError:
        return False


def safe_text(value: Any, default: str = "Unknown") -> str:
    """
    تبدیل مقدار به متن مناسب برای Markdown.
    مقدارهای خالی یا None با مقدار پیش‌فرض جایگزین می‌شوند.
    """
    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


def escape_markdown_cell(value: Any, default: str = "Unknown") -> str:
    """
    آماده‌سازی مقدار برای قرارگرفتن داخل سلول جدول Markdown.
    """
    text = safe_text(value, default)

    # جلوگیری از شکستن ساختار جدول Markdown
    text = text.replace("|", r"\|")

    # جلوگیری از شکستن ردیف جدول به‌وسیلهٔ خط جدید
    text = text.replace("\r", " ").replace("\n", " ")

    return text


def format_code_value(value: Any, default: str = "Unknown") -> str:
    """
    نمایش مقدارهای فنی مانند نام دستگاه و IP داخل بک‌تیک.
    """
    text = escape_markdown_cell(value, default)

    # جلوگیری از خراب‌شدن نمایش کد درون‌خطی Markdown
    text = text.replace("`", r"\`")

    return f"`{text}`"


def load_inventory(file_path: str) -> dict[str, Any] | None:
    """
    خواندن و text = text.replace("`", r"\`")

    return f"`{text}`"


def load_inventory(file_path: str) -> dict[str, Any] | None:
    """
    خواندن و اعتبارسنجی اولیهٔ فایل YAML.
    """
    if not os.path.isfile(file_path):
        print(f"[ERROR] Input file not found: { as error:
        print(f"[ERROR] Invalid YAML syntax in {file_path}: {error}")
        return None
    except OSError as error:
        print(f"[ERROR] Could not read {file_path}: {error}")
        return None

    if data is None:
        data = {}

    if not isinstance(data, dict):
        print("[ERROR] The root of the YAML file must be a mapping/object.")
        return None

    return data


def get_devices(data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    دریافت فهرست دستگاه‌ها و حذف مواردی که ساختار دیکشنری ندارند.
    """
    raw_devices = data.get("devices", [])

    if raw_devices is None:
        return []

    if not isinstance(raw_devices, list):
        print("[ERROR] The 'devices' field must be a list.")
        return []

    devices = []

    for index, device in enumerate(raw_devices, start=1):
        if not isinstance(device, dict):
            print(
                f"[WARNING] Device entry #{index} is not an object and "
                "will be skipped."
            )
            continue

        devices.append(device)

    return devices


def group_devices_by_site(
    devices: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """
    گروه‌بندی دستگاه‌ها بر اساس سایت.
    """
    sites: dict[str, list[dict[str, Any]]] = {}

    for device in devices:
        device_name = safe_text(device.get("name"), f"Device #{len(sites) + 1}")
        ip_value = device.get("ip", "")

        if not validate_ip(ip_value):
            print(
                f"[WARNING] Invalid IPv4 address for device: "
                f"{device_name} ({safe_text(ip_value, 'Empty')})"
            )

        site_name = safe_text(device.get("site"), "Unknown")
        sites.setdefault(site_name, []).append(device)

    return sites


def build_device_row(device: dict[str, Any]) -> str:
    """
    ساخت یک ردیف جدول Markdown برای یک دستگاه.
    """
    criticality = safe_text(device.get("criticality"))

    if criticality == "High":
        criticality_cell = f"**{criticality}**"
    else:
        criticality_cell = escape_markdown_cell(criticality)

    return (
        f"| {format_code_value(device.get('name'))} "
        f"| {escape_markdown_cell(device.get('type'))} "
        f"| {format_code_value(device.get('ip'))} "
        f"| {escape_markdown_cell(device.get('os_or_model'))} "
        f"| {escape_markdown_cell(device.get('role'))} "
        f"| {criticality_cell} "
        f"| {escape_markdown_cell(device.get('owner'))} |"
    )


def build_markdown(
    data: dict[str, Any],
    devices: list[dict[str, Any]],
    sites: dict[str, list[dict[str, Any]]]
) -> str:
    """
    ساخت محتوای کامل فایل Markdown.
    """
    company = escape_markdown_cell(
        data.get("company"),
        "Infrastructure"
    )

    environment = escape_markdown_cell(
        data.get("environment"),
        "Standard"
    )

    lines = [
        f"# {company} - Network Inventory",
        f"**Environment:** `{environment}` | "
        f"**Total Assets:** `{len(devices)}`",
        "",
        "> Auto-generated via `scripts/render_inventory.py`. "
        "Do not edit manually.",
        ""
    ]

    for site_name in sorted(sites):
        dev_list = sites[site_name]

        lines.extend(
            [
                f"## Site: {escape_markdown_cell(site_name)}",
                "",
                "| Device Name | Type | IP Address | Model / OS | "
                "Primary Role | Criticality | Owner |",
                "| :--- | :--- | :--- | :--- | :--- | :---: | :--- |"
            ]
        )

        sorted_devices = sorted(
            dev_list,
            key=lambda device: (
                safe_text(device.get("type"), "").casefold(),
                safe_text(device.get("name"), "").casefold()
            )
        )

        for device in sorted_devices:
            lines.append(build_device_row(device))

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_output(file_path: str, content: str) -> bool:
    """
    ایجاد پوشهٔ خروجی و نوشتن محتوای Markdown.
    """
    output_directory = os.path.dirname(file_path)

    if output_directory:
        os.makedirs(output_directory, exist_ok=True)

    try:
        with open(file_path, "w", encoding="utf-8", newline="\n") as file:
            file.write(content)
    except OSError as error:
        print(f"[ERROR] Could not write {file_path}: {error}")
        return False

    return True


def generate_markdown() -> bool:
    """
    اجرای کامل فرایند تولید گزارش.
    """
    data = load_inventory(INPUT_FILE)

    if data is None:
        return False

    devices = get_devices(data)
    sites = group_devices_by_site(devices)
    markdown = build_markdown(data, devices, sites)

    if not write_output(OUTPUT_FILE, markdown):
        return False

    print(f"[SUCCESS] Inventory markdown written to {OUTPUT_FILE}")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if generate_markdown() else 1)


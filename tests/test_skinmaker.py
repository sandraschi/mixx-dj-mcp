from mixx_dj_mcp.skinmaker import scheme_path
from mixx_dj_mcp.skinmaker.palette import load_scheme
from mixx_dj_mcp.skinmaker.qss_patch import apply_hex_replacements


def test_daylight_scheme_bundled():
    path = scheme_path("daylight-v2")
    assert path.is_file()
    scheme = load_scheme(path)
    assert scheme["name"] == "daylight-v2"
    assert scheme["tokens"]["waveform_well"] == "#e8eaef"


def test_apply_hex_replacements():
    content = "background-color: #151517; border: 1px solid #19191a;"
    patched, count = apply_hex_replacements(
        content,
        {"#151517": "#eef0f4", "#19191a": "#e8eaef"},
    )
    assert count == 2
    assert "#eef0f4" in patched
    assert "#151517" not in patched

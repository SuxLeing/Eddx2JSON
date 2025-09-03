import json, re, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
from typing import Literal

# 转换模式：
# - "topic_root"：以 MainTopic 和 Floating 为根
# - "idea_root" ：以 MainIdea 和 Floating 为根
Mode = Literal["topic_root", "idea_root"]

# 作为“子节点”参与构树的类型（两种模式一致）
CHILD_TYPES = {"MainTopic", "SubTopic", "Floating", "MainIdea"}

def _get_text(shape: ET.Element) -> str:
    texts = []
    for pp in shape.findall(".//pp"):
        tps = [("".join(tp.itertext())).strip() for tp in pp.findall(".//tp")]
        if tps:
            texts.append("".join(tps))
    return " ".join([t for t in texts if t]).strip()

def _parse_page_xml(data: bytes):
    """返回 shapes: {id: {type,text}}, children_map: {id: [child_ids]}"""
    root = ET.fromstring(data)
    shapes, children_map = {}, {}
    for sh in root.findall(".//Shape"):
        t = sh.get("Type")
        if t not in CHILD_TYPES:
            continue
        sid = sh.get("ID")
        txt = _get_text(sh)
        # 关系
        sub_ids = []
        ld = sh.find("./LevelData")
        if ld is not None:
            sub = ld.find("./SubLevel")
            if sub is not None and sub.get("V"):
                sub_ids = [s for s in sub.get("V").split(";") if s]
        shapes[sid] = {"type": t, "text": txt}
        children_map[sid] = sub_ids
    # 仅保留有效子链接
    for sid in list(children_map):
        children_map[sid] = [c for c in children_map[sid] if c in shapes]
    return shapes, children_map

def _unique_key(d: dict, key: str) -> str:
    key = (key or "未命名").strip()
    if key not in d:
        return key
    i = 2
    while f"{key}({i})" in d:
        i += 1
    return f"{key}({i})"

def _build_value(sid: str, shapes: dict, children_map: dict):
    """无子→返回本节点文本；有子→{子文本: 子值}"""
    kids = children_map.get(sid, [])
    if not kids:
        return shapes[sid]["text"] or "未命名"
    val = {}
    for cid in kids:
        child_key = _unique_key(val, shapes[cid]["text"] or "未命名")
        val[child_key] = _build_value(cid, shapes, children_map)
    return val

def _dump_root_json(root_sid: str, page_dir: Path, shapes: dict, children_map: dict):
    root_key = (shapes[root_sid]["text"] or f"{shapes[root_sid]['type']}_{root_sid}").strip()
    data = {root_key: _build_value(root_sid, shapes, children_map)}
    safe = re.sub(r"[^\w\-\u4e00-\u9fff]+", "_", root_key).strip("_") or f"{shapes[root_sid]['type']}_{root_sid}"
    target = page_dir / f"{safe}.json"
    i = 2
    while target.exists():
        target = page_dir / f"{safe}_{i}.json"
        i += 1
    with open(target, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _pick_roots(shapes: dict, mode: Mode):
    if mode == "topic_root":
        prim = "MainTopic"
    elif mode == "idea_root":
        prim = "MainIdea"
    else:
        raise ValueError("mode must be 'topic_root' or 'idea_root'")
    main_roots = [sid for sid, n in shapes.items() if n["type"] == prim]
    float_roots = [sid for sid, n in shapes.items() if n["type"] == "Floating"]
    return main_roots, float_roots

def export_eddx(eddx_path: str, mode: Mode = "topic_root", out_dir: str | None = None):
    """
    mode:
      - 'topic_root'：MainTopic + Floating 为根
      - 'idea_root' ：MainIdea  + Floating 为根
    """
    eddx_path = Path(eddx_path)
    out_root = Path(out_dir) if out_dir else eddx_path.with_suffix("")
    out_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(eddx_path, "r") as zf:
        pages = [n for n in zf.namelist() if n.lower().startswith("pages/") and n.lower().endswith(".xml")]
        for name in pages:
            data = zf.read(name)
            shapes, children_map = _parse_page_xml(data)
            main_roots, float_roots = _pick_roots(shapes, mode)

            m = re.search(r"page(\d+)\.xml$", name, re.IGNORECASE)
            page_tag = f"page{m.group(1)}" if m else Path(name).stem
            page_dir = out_root / page_tag
            page_dir.mkdir(parents=True, exist_ok=True)

            for sid in main_roots:
                _dump_root_json(sid, page_dir, shapes, children_map)
            for sid in float_roots:
                _dump_root_json(sid, page_dir, shapes, children_map)

# 单独解析已解压的 page*.xml
def export_single_page_xml(page_xml_path: str, mode: Mode = "topic_root", out_dir: str = "./out"):
    page_xml_path = Path(page_xml_path)
    with open(page_xml_path, "rb") as f:
        data = f.read()
    shapes, children_map = _parse_page_xml(data)
    main_roots, float_roots = _pick_roots(shapes, mode)

    page_dir = Path(out_dir)
    page_dir.mkdir(parents=True, exist_ok=True)
    for sid in main_roots:
        _dump_root_json(sid, page_dir, shapes, children_map)
    for sid in float_roots:
        _dump_root_json(sid, page_dir, shapes, children_map)

if __name__ == "__main__":
    export_eddx("./your_eddx_file_name.eddx", mode="topic_root")


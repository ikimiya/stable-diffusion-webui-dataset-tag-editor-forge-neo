from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import re

import gradio as gr

from .ui_common import *
from .uibase import UIBase

if TYPE_CHECKING:
    from .ui_classes import *


def _clean_tag(t: str) -> str:
    return t.strip().strip(",").strip()


def _parse_tags(raw: str) -> list[str]:
    return [_clean_tag(t) for t in raw.split(",") if _clean_tag(t)]


class TagImplicationUI(UIBase):

    def __init__(self):
        self._groups: dict[str, list[list]] = {}
        self._counts: dict[str, int] = {}

    def _get_tag_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for data in dte_instance.dataset.datas.values():
            for tag in data.tags:
                t = _clean_tag(tag)
                if t:
                    counts[t] = counts.get(t, 0) + 1
        return counts

    def _build_implication_groups(self) -> dict[str, list[list]]:
        counts = self._get_tag_counts()
        all_tags = list(counts.keys())
        groups: dict[str, list[list]] = {}
        for parent in all_tags:
            children = []
            pattern = r'(?<![a-zA-Z0-9_])' + re.escape(parent) + r'(?![a-zA-Z0-9_])'
            for child in all_tags:
                if child == parent:
                    continue
                if re.search(pattern, child):
                    children.append([child, counts[child]])
            if children:
                children.sort(key=lambda x: x[1], reverse=True)
                groups[parent] = children
        return groups

    def _sorted_parents(self, sort_by: str) -> list[str]:
        if sort_by == "Frequency (highest first)":
            return sorted(self._groups.keys(), key=lambda p: self._counts.get(p, 0), reverse=True)
        return sorted(self._groups.keys())

    def _parent_choices(self, sort_by: str) -> list[str]:
        return [
            f"{p}  ({self._counts.get(p, 0)})"
            for p in self._sorted_parents(sort_by)
        ]

    def _child_choices(self, parent_label: str) -> list[str]:
        parent = self._strip_count(parent_label) if parent_label else ""
        children = self._groups.get(parent, [])
        return [f"{c}  ({n})" for c, n in children]

    @staticmethod
    def _strip_count(label: str) -> str:
        if "  (" in label:
            return label.split("  (")[0].strip()
        return label.strip()

    def create_ui(self):
        gr.HTML(
            value=(
                "<b>Tag Implication / Consolidation</b> &mdash; "
                "Pick a parent tag, then choose which related tags to <b style='color:#8fda9f'>add</b> "
                "or <b style='color:#f88'>delete</b>, then apply."
            )
        )

        with gr.Row():
            self.btn_scan = gr.Button(value="🔍 Scan Dataset", variant="primary")
            self.rb_sort = gr.Radio(
                choices=["Frequency (highest first)", "Alphabetical"],
                value="Frequency (highest first)",
                label="Sort parents by",
            )

        self.html_status = gr.HTML(
            value="<p style='color:#aaa;font-size:0.88em'>Click <b>Scan</b> to load tags.</p>"
        )

        with gr.Row(equal_height=False):
            with gr.Column(scale=1):
                gr.HTML(value="<div style='font-weight:bold;margin-bottom:4px'>① Select Parent Tag</div>")
                self.dd_parent = gr.Dropdown(
                    choices=[],
                    value=None,
                    label="Parent tag (generic tag to replace)",
                    interactive=True,
                )

            with gr.Column(scale=2):
                gr.HTML(value="<div style='font-weight:bold;margin-bottom:4px'>② Choose What To Do With Related Tags</div>")

                gr.HTML(value="<div style='color:#8fda9f;font-size:0.88em;margin-bottom:2px'>✓ ADD — check tags to add to all images that have the parent</div>")
                self.cbg_add = gr.CheckboxGroup(
                    choices=[],
                    value=[],
                    label="Add these tags",
                    interactive=True,
                )

                gr.HTML(value="<div style='color:#f88;font-size:0.88em;margin:8px 0 2px 0'>✗ DELETE — check tags to remove from entire dataset</div>")
                self.cbg_delete = gr.CheckboxGroup(
                    choices=[],
                    value=[],
                    label="Delete these tags from entire dataset",
                    interactive=True,
                )

                self.tb_custom_add = gr.Textbox(
                    label="➕ Add custom tags to add (comma-separated)",
                    placeholder="e.g. fingerless gloves, lace gloves",
                )
                self.tb_custom_delete = gr.Textbox(
                    label="🗑 Add custom tags to delete (comma-separated)",
                    placeholder="e.g. white gloves",
                )

        gr.HTML(value="<hr style='border-color:#333;margin:10px 0'>")
        gr.HTML(value="<div style='font-weight:bold;margin-bottom:6px'>③ Apply</div>")

        with gr.Row():
            self.rb_target = gr.Radio(
                choices=["All Displayed Images", "All Images in Dataset"],
                value="All Displayed Images",
                label="Apply ADD action to",
            )

        with gr.Row():
            self.cb_remove_parent = gr.Checkbox(
                value=True,
                label="Remove parent tag after applying (recommended)",
            )
            self.cb_remove_dup = gr.Checkbox(
                value=True,
                label="Skip child tags the image already has",
            )

        self.btn_apply = gr.Button(value="✅ Apply", variant="primary")
        self.html_result = gr.HTML(value="")

    def set_callbacks(
            self,
            o_update_filter_and_gallery: list,
            load_dataset,
            get_filters: Callable,
            update_filter_and_gallery: Callable,
    ):
        def scan(sort_by: str):
            self._groups = self._build_implication_groups()
            self._counts = self._get_tag_counts()
            choices = self._parent_choices(sort_by)
            n = len(choices)
            status = f"<p style='color:#8f8;font-size:0.88em'>Found <b>{n}</b> parent tags with related children.</p>"
            return (
                status,
                gr.Dropdown(choices=choices, value=None),
                gr.CheckboxGroup(choices=[], value=[]),
                gr.CheckboxGroup(choices=[], value=[]),
            )

        self.btn_scan.click(
            fn=scan,
            inputs=[self.rb_sort],
            outputs=[self.html_status, self.dd_parent, self.cbg_add, self.cbg_delete],
        )

        load_dataset.btn_load_datasets.click(
            fn=lambda sort_by: scan(sort_by),
            inputs=[self.rb_sort],
            outputs=[self.html_status, self.dd_parent, self.cbg_add, self.cbg_delete],
        )

        def resort(sort_by: str):
            if not self._groups:
                return gr.Dropdown(choices=[], value=None)
            return gr.Dropdown(choices=self._parent_choices(sort_by), value=None)

        self.rb_sort.change(
            fn=resort,
            inputs=[self.rb_sort],
            outputs=[self.dd_parent],
        )

        def on_parent_selected(parent_label: str):
            if not parent_label:
                empty = gr.CheckboxGroup(choices=[], value=[])
                return empty, empty
            choices = self._child_choices(parent_label)
            return (
                gr.CheckboxGroup(choices=choices, value=[]),
                gr.CheckboxGroup(choices=choices, value=[]),
            )

        self.dd_parent.change(
            fn=on_parent_selected,
            inputs=[self.dd_parent],
            outputs=[self.cbg_add, self.cbg_delete],
        )

        def apply_implication(
            parent_label: str,
            checked_add: list[str],
            checked_delete: list[str],
            custom_add_raw: str,
            custom_delete_raw: str,
            target: str,
            remove_parent: bool,
            remove_dup: bool,
            sort_by: str,
        ):
            parent_tag = self._strip_count(parent_label) if parent_label else ""

            add_tags = [self._strip_count(c) for c in (checked_add or [])]
            add_tags += _parse_tags(custom_add_raw)
            add_tags = list(dict.fromkeys(_clean_tag(t) for t in add_tags if _clean_tag(t)))

            delete_tags = [self._strip_count(c) for c in (checked_delete or [])]
            delete_tags += _parse_tags(custom_delete_raw)
            delete_tags = list(dict.fromkeys(_clean_tag(t) for t in delete_tags if _clean_tag(t)))

            if not parent_tag and not add_tags and not delete_tags:
                return (
                    "<p style='color:#f88'>Nothing selected. Pick a parent and/or tags to delete.</p>",
                    gr.Dropdown(choices=[], value=None),
                    *update_filter_and_gallery(),
                )

            if parent_tag and parent_tag in add_tags:
                return (
                    "<p style='color:#f88'>Parent tag cannot also be in the add list.</p>",
                    gr.Dropdown(choices=[], value=None),
                    *update_filter_and_gallery(),
                )
            overlap = set(add_tags) & set(delete_tags)
            if overlap:
                return (
                    "<p style='color:#f88'>Conflict: these tags are in both Add and Delete lists: "
                    + ", ".join(f"<b>{t}</b>" for t in overlap) + "</p>",
                    gr.Dropdown(choices=[], value=None),
                    *update_filter_and_gallery(),
                )

            add_changed = 0
            if parent_tag and add_tags:
                if target == "All Displayed Images":
                    img_paths = dte_instance.get_filtered_imgpaths(filters=get_filters())
                else:
                    img_paths = list(dte_instance.dataset.datas.keys())

                for img_path in img_paths:
                    data = dte_instance.dataset.get_data(img_path)
                    if data is None:
                        continue
                    existing = [_clean_tag(t) for t in data.tags if _clean_tag(t)]
                    if parent_tag not in existing:
                        continue

                    existing_set = set(existing)
                    to_insert = [
                        ct for ct in add_tags
                        if not (remove_dup and ct in existing_set)
                    ]

                    new_tags = []
                    inserted = False
                    for t in existing:
                        if t == parent_tag:
                            if remove_parent:
                                if not inserted:
                                    new_tags.extend(to_insert)
                                    inserted = True

                            else:
                                new_tags.append(t)
                                if not inserted:
                                    new_tags.extend(to_insert)
                                    inserted = True
                        else:
                            new_tags.append(t)

                    seen: set[str] = set()
                    deduped = []
                    for t in new_tags:
                        if t not in seen:
                            seen.add(t)
                            deduped.append(t)

                    data.tags = deduped
                    data.tagset = set(deduped)
                    add_changed += 1

            delete_changed = 0
            if delete_tags:
                delete_set = set(delete_tags)
                for img_path, data in dte_instance.dataset.datas.items():
                    existing = [_clean_tag(t) for t in data.tags if _clean_tag(t)]
                    if not delete_set & set(existing):
                        continue
                    new_tags = [t for t in existing if t not in delete_set]
                    data.tags = new_tags
                    data.tagset = set(new_tags)
                    delete_changed += 1

            dte_instance.construct_tag_infos()

            parts = []
            if add_tags and parent_tag:
                child_display = ", ".join(f"<b>{c}</b>" for c in add_tags)
                parts.append(
                    f"Added {child_display} to <b>{add_changed}</b> image(s) with <b>{parent_tag}</b>"
                )
            if delete_tags:
                del_display = ", ".join(f"<b>{d}</b>" for d in delete_tags)
                parts.append(
                    f"Deleted {del_display} from <b>{delete_changed}</b> image(s) across dataset"
                )

            self._groups = self._build_implication_groups()
            self._counts = self._get_tag_counts()
            new_choices = self._parent_choices(sort_by)
            n = len(new_choices)
            status = f"<p style='color:#8f8;font-size:0.88em'>Found <b>{n}</b> parent tags with related children.</p>"
            result_html = "<p style='color:#8f8'>✓ " + " &nbsp;|&nbsp; ".join(parts) + "</p>"
            return (result_html, status, gr.Dropdown(choices=new_choices, value=None), *update_filter_and_gallery())

        self.btn_apply.click(
            fn=apply_implication,
            inputs=[
                self.dd_parent,
                self.cbg_add,
                self.cbg_delete,
                self.tb_custom_add,
                self.tb_custom_delete,
                self.rb_target,
                self.cb_remove_parent,
                self.cb_remove_dup,
                self.rb_sort,
            ],
            outputs=[self.html_result, self.html_status, self.dd_parent] + o_update_filter_and_gallery,
        )
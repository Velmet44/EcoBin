#!/usr/bin/env python3
"""Validate a lifecycle BOM/configuration contract and report declared cost totals.

This checks JSON structure and cross-references. It does not access FreeCAD,
ERP/PLM/MES systems, verify external evidence, approve sources, or accept hardware.
"""

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


STATES = {"concept", "prototype", "production_candidate", "released"}
VIEW_TYPES = {"ebom", "mbom", "as_planned", "as_built", "as_maintained"}
ITEM_TYPES = {
    "make", "buy", "standard", "bulk", "consumable", "software",
    "firmware", "packaging", "reference", "tooling",
}
SOURCE_STATUSES = {"proposed", "qualified", "approved", "blocked", "obsolete"}
ALT_CLASSES = {"equivalent", "conditional", "deviation_only"}
CHANGE_STATES = {"proposed", "approved", "implemented", "verified", "cancelled"}
RECONCILIATION_TYPES = {"cad_to_ebom", "ebom_to_mbom", "mbom_to_as_built"}
DECISIONS = {"approved", "rejected", "conditional"}
PLACEHOLDERS = {"", "tbd", "unknown", "unassigned", "n/a", "na", "none", "null", "pending", "yyyy-mm-dd", "?"}
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


def present(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in PLACEHOLDERS
    return True


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def objects(data, key, errors):
    value = data.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} must be a list")
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{key}[{index}] must be an object")
            result.append({})
        else:
            result.append(item)
    return result


def require(item, keys, path, errors):
    for key in keys:
        if not present(item.get(key)):
            errors.append(f"{path}.{key} is required")


def decimal_number(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return result if result.is_finite() else None


def serial_key(value):
    """Natural ordering for mixed prefix/numeric serial identifiers."""
    return tuple(
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", str(value))
        if part != ""
    )


def effectivity_ok(effectivity, config_ids, path, errors):
    if not isinstance(effectivity, dict):
        errors.append(f"{path} must be a structured object")
        return
    memberships = effectivity.get("configurations")
    if not isinstance(memberships, list) or not memberships:
        errors.append(f"{path}.configurations must be a non-empty list")
    elif set(memberships) - config_ids:
        errors.append(f"{path}.configurations references unknown configurations")
    serial_from = effectivity.get("serial_from")
    serial_to = effectivity.get("serial_to")
    if serial_from is not None and serial_to is not None and serial_key(serial_from) > serial_key(serial_to):
        errors.append(f"{path} serial range is reversed")
    date_from = effectivity.get("date_from")
    date_to = effectivity.get("date_to")
    for key, value in (("date_from", date_from), ("date_to", date_to)):
        if value is not None and not valid_date(value):
            errors.append(f"{path}.{key} must be an ISO date or null")
    if valid_date(date_from) and valid_date(date_to) and date_from > date_to:
        errors.append(f"{path} date range is reversed")
    if "sites" in effectivity and not isinstance(effectivity.get("sites"), list):
        errors.append(f"{path}.sites must be a list")


def effectivity_applies(effectivity, configuration_id, product_serial, event_date, site):
    """Return whether a previously validated effectivity covers a built unit."""
    if not isinstance(effectivity, dict):
        return False
    configurations = effectivity.get("configurations")
    if not isinstance(configurations, list) or configuration_id not in configurations:
        return False
    serial_from, serial_to = effectivity.get("serial_from"), effectivity.get("serial_to")
    serial = str(product_serial)
    if serial_from is not None and serial_key(serial) < serial_key(serial_from):
        return False
    if serial_to is not None and serial_key(serial) > serial_key(serial_to):
        return False
    date_from, date_to = effectivity.get("date_from"), effectivity.get("date_to")
    if date_from is not None and (not valid_date(event_date) or event_date < date_from):
        return False
    if date_to is not None and (not valid_date(event_date) or event_date > date_to):
        return False
    sites = effectivity.get("sites")
    if isinstance(sites, list) and sites and site not in sites:
        return False
    return True


def validate(data):
    errors = []
    warnings = []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["contract root must be an object"], "warnings": [], "metrics": {}}
    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")
    record_state = data.get("record_state")
    if record_state not in RECORD_STATES:
        errors.append(f"record_state must be one of {sorted(RECORD_STATES)}")

    product = data.get("product")
    if not isinstance(product, dict):
        errors.append("product must be an object")
        product = {}
    require(
        product,
        (
            "part_number", "revision", "name", "lifecycle_state", "owner",
            "units", "currency", "cost_basis_date", "configuration_procedure",
            "acceptance_authority_role",
        ),
        "product",
        errors,
    )
    if product.get("lifecycle_state") not in STATES:
        errors.append(f"product.lifecycle_state must be one of {sorted(STATES)}")
    if present(product.get("cost_basis_date")) and not valid_date(product.get("cost_basis_date")):
        errors.append("product.cost_basis_date must be an ISO date")
    candidate = product.get("lifecycle_state") in {"production_candidate", "released"}

    source_systems = objects(data, "source_systems", errors)
    configs = objects(data, "configurations", errors)
    definitions = objects(data, "definitions", errors)
    views = objects(data, "views", errors)
    occurrences = objects(data, "occurrences", errors)
    transformations = objects(data, "transformations", errors)
    approved_sources = objects(data, "approved_sources", errors)
    alternates = objects(data, "alternates", errors)
    deviations = objects(data, "deviations", errors)
    changes = objects(data, "changes", errors)
    costs = objects(data, "cost_records", errors)
    built_units = objects(data, "as_built_units", errors)
    maintenance = objects(data, "maintenance_events", errors)
    reconciliations = objects(data, "reconciliations", errors)
    approvals = objects(data, "approvals", errors)

    for index, source in enumerate(source_systems):
        require(source, ("domain", "system", "extract_id", "extracted_at", "source_hash"), f"source_systems[{index}]", errors)
        if present(source.get("source_hash")) and not SHA256.fullmatch(
            str(source.get("source_hash"))
        ):
            errors.append(
                f"source_systems[{index}].source_hash must be a controlled SHA-256"
            )
    if candidate and not source_systems:
        errors.append("production candidate requires source_systems provenance")

    config_ids = [item.get("id") for item in configs]
    if not configs or any(not present(item) for item in config_ids):
        errors.append("at least one named configuration is required")
    if len(config_ids) != len(set(config_ids)):
        errors.append("configuration IDs must be unique")
    config_set = set(config_ids)
    for index, config in enumerate(configs):
        require(config, ("id", "status"), f"configurations[{index}]", errors)
        effectivity_ok(config.get("effectivity"), config_set, f"configurations[{index}].effectivity", errors)

    definition_keys = []
    definition_by_key = {}
    for index, definition in enumerate(definitions):
        require(
            definition,
            ("part_number", "revision", "description", "item_type", "uom", "criticality"),
            f"definitions[{index}]",
            errors,
        )
        key = (definition.get("part_number"), definition.get("revision"))
        definition_keys.append(key)
        definition_by_key[key] = definition
        if definition.get("item_type") not in ITEM_TYPES:
            errors.append(f"definitions[{index}].item_type must be one of {sorted(ITEM_TYPES)}")
        if definition.get("item_type") == "make":
            require(definition, ("material_spec", "finish"), f"definitions[{index}]", errors)
    if len(definition_keys) != len(set(definition_keys)):
        errors.append("definition part_number/revision keys must be unique")
    known_definitions = set(definition_keys)

    view_ids = []
    view_type_by_id = {}
    for index, view in enumerate(views):
        require(view, ("id", "type", "revision", "authority", "status"), f"views[{index}]", errors)
        view_ids.append(view.get("id"))
        view_type_by_id[view.get("id")] = view.get("type")
        if view.get("type") not in VIEW_TYPES:
            errors.append(f"views[{index}].type must be one of {sorted(VIEW_TYPES)}")
    if len(view_ids) != len(set(view_ids)):
        errors.append("view IDs must be unique")
    if candidate and not {"ebom", "mbom"}.issubset(set(view_type_by_id.values())):
        errors.append("production candidate requires explicit ebom and mbom views")
    view_set = set(view_ids)

    occurrence_ids = [item.get("id") for item in occurrences]
    if len(occurrence_ids) != len(set(occurrence_ids)) or any(not present(item) for item in occurrence_ids):
        errors.append("occurrence IDs must be present and unique")
    occurrence_set = set(occurrence_ids)
    occurrence_by_id = {item.get("id"): item for item in occurrences}
    children = defaultdict(list)
    for index, occurrence in enumerate(occurrences):
        require(
            occurrence,
            ("id", "view_id", "part_number", "revision", "quantity", "configuration_ids"),
            f"occurrences[{index}]",
            errors,
        )
        if occurrence.get("view_id") not in view_set:
            errors.append(f"occurrences[{index}] references unknown view")
        key = (occurrence.get("part_number"), occurrence.get("revision"))
        if key not in known_definitions:
            errors.append(f"occurrences[{index}] references unknown definition {key}")
        quantity = decimal_number(occurrence.get("quantity"))
        if quantity is None or quantity <= 0:
            errors.append(f"occurrences[{index}].quantity must be positive")
        parent = occurrence.get("parent_id")
        if parent is not None and parent not in occurrence_set:
            errors.append(f"occurrences[{index}] references unknown parent")
        elif parent is not None and occurrence_by_id.get(parent, {}).get(
            "view_id"
        ) != occurrence.get("view_id"):
            errors.append(
                f"occurrences[{index}].parent_id must belong to the same view"
            )
        children[parent].append(occurrence.get("id"))
        memberships = occurrence.get("configuration_ids")
        if not isinstance(memberships, list) or not memberships or set(memberships) - config_set:
            errors.append(f"occurrences[{index}].configuration_ids must be valid")

    colors = {node: 0 for node in occurrence_set}
    def visit(node):
        if colors.get(node) == 1:
            errors.append(f"occurrence hierarchy cycle detected at {node}")
            return
        if colors.get(node) == 2:
            return
        colors[node] = 1
        for child in children.get(node, []):
            if child in colors:
                visit(child)
        colors[node] = 2
    for occurrence_id in occurrence_set:
        visit(occurrence_id)
    for view_id in view_set:
        view_occurrences = [
            item for item in occurrences if item.get("view_id") == view_id
        ]
        roots = [item for item in view_occurrences if item.get("parent_id") is None]
        if len(roots) != 1:
            errors.append(f"view {view_id} must have exactly one root occurrence")
            continue
        reachable = set()
        stack = [roots[0].get("id")]
        while stack:
            node = stack.pop()
            if node in reachable:
                continue
            reachable.add(node)
            stack.extend(children.get(node, []))
        missing = {
            item.get("id") for item in view_occurrences
        } - reachable
        if missing:
            errors.append(
                f"view {view_id} has occurrences disconnected from its root: {sorted(missing)}"
            )

    transformation_ids = []
    has_ebom_to_mbom_mapping = False
    for index, transformation in enumerate(transformations):
        require(
            transformation,
            ("id", "source_occurrence_ids", "target_occurrence_ids", "quantity_factor", "reason", "approval", "effectivity"),
            f"transformations[{index}]",
            errors,
        )
        transformation_ids.append(transformation.get("id"))
        for key in ("source_occurrence_ids", "target_occurrence_ids"):
            refs = transformation.get(key)
            if not isinstance(refs, list) or not refs or set(refs) - occurrence_set:
                errors.append(f"transformations[{index}].{key} must reference known occurrences")
        source_views = {
            view_type_by_id.get(item.get("view_id"))
            for item in occurrences
            if item.get("id") in set(transformation.get("source_occurrence_ids") or [])
        }
        target_views = {
            view_type_by_id.get(item.get("view_id"))
            for item in occurrences
            if item.get("id") in set(transformation.get("target_occurrence_ids") or [])
        }
        if "ebom" in source_views and "mbom" in target_views:
            has_ebom_to_mbom_mapping = True
        factor = decimal_number(transformation.get("quantity_factor"))
        if factor is None or factor <= 0:
            errors.append(f"transformations[{index}].quantity_factor must be positive")
        else:
            source_quantity = sum(
                (
                    decimal_number(occurrence_by_id.get(item, {}).get("quantity"))
                    or Decimal("0")
                )
                for item in transformation.get("source_occurrence_ids", [])
            )
            target_quantity = sum(
                (
                    decimal_number(occurrence_by_id.get(item, {}).get("quantity"))
                    or Decimal("0")
                )
                for item in transformation.get("target_occurrence_ids", [])
            )
            if source_quantity * factor != target_quantity:
                errors.append(
                    f"transformations[{index}] does not conserve mapped quantity"
                )
        effectivity_ok(transformation.get("effectivity"), config_set, f"transformations[{index}].effectivity", errors)
    if len(transformation_ids) != len(set(transformation_ids)):
        errors.append("transformation IDs must be unique")
    if candidate and not transformations:
        errors.append("production candidate requires eBOM/mBOM transformations")
    elif candidate and not has_ebom_to_mbom_mapping:
        errors.append("production candidate requires an explicit eBOM-to-mBOM transformation")

    source_ids = []
    approved_part_keys = set()
    for index, source in enumerate(approved_sources):
        require(
            source,
            (
                "id", "part_number", "revision", "manufacturer", "manufacturer_part_number",
                "supplier", "supplier_part_number", "status", "lifecycle", "lead_time_days",
                "moq", "order_multiple", "evidence",
            ),
            f"approved_sources[{index}]",
            errors,
        )
        source_ids.append(source.get("id"))
        key = (source.get("part_number"), source.get("revision"))
        if key not in known_definitions:
            errors.append(f"approved_sources[{index}] references unknown definition")
        if source.get("status") not in SOURCE_STATUSES:
            errors.append(f"approved_sources[{index}].status must be one of {sorted(SOURCE_STATUSES)}")
        if source.get("status") == "approved":
            approved_part_keys.add(key)
        for field in ("lead_time_days", "moq", "order_multiple"):
            value = decimal_number(source.get(field))
            if value is None or value < 0 or (field != "lead_time_days" and value == 0):
                errors.append(f"approved_sources[{index}].{field} is invalid")
    if len(source_ids) != len(set(source_ids)):
        errors.append("approved source IDs must be unique")
    if candidate:
        for key, definition in definition_by_key.items():
            if definition.get("item_type") in {"buy", "standard"} and key not in approved_part_keys:
                errors.append(f"production candidate buy/standard definition {key} lacks an approved source")

    for index, alternate in enumerate(alternates):
        require(
            alternate,
            ("primary_part", "alternate_part", "class", "restrictions", "qualification_evidence", "approval", "effectivity"),
            f"alternates[{index}]",
            errors,
        )
        for field in ("primary_part", "alternate_part"):
            value = alternate.get(field)
            if not isinstance(value, dict) or (value.get("part_number"), value.get("revision")) not in known_definitions:
                errors.append(f"alternates[{index}].{field} must reference a known definition")
        if alternate.get("class") not in ALT_CLASSES:
            errors.append(f"alternates[{index}].class must be one of {sorted(ALT_CLASSES)}")
        effectivity_ok(alternate.get("effectivity"), config_set, f"alternates[{index}].effectivity", errors)

    approved_deviations = {}
    deviation_ids = []
    for index, deviation in enumerate(deviations):
        require(
            deviation,
            (
                "id", "status", "nominal_part", "substitute_part",
                "product_serials", "reason", "evidence", "approval",
            ),
            f"deviations[{index}]",
            errors,
        )
        deviation_ids.append(deviation.get("id"))
        for field in ("nominal_part", "substitute_part"):
            value = deviation.get(field)
            if not isinstance(value, dict) or (value.get("part_number"), value.get("revision")) not in known_definitions:
                errors.append(f"deviations[{index}].{field} must reference a known definition")
        serial_scope = deviation.get("product_serials")
        if not isinstance(serial_scope, list) or not serial_scope or any(not present(item) for item in serial_scope):
            errors.append(f"deviations[{index}].product_serials must be a non-empty explicit serial list")
        approval = deviation.get("approval")
        if not isinstance(approval, dict):
            errors.append(f"deviations[{index}].approval must be a structured human approval")
        else:
            require(approval, ("approver", "role", "date", "decision"), f"deviations[{index}].approval", errors)
            if present(approval.get("date")) and not valid_date(approval.get("date")):
                errors.append(f"deviations[{index}].approval.date must be an ISO date")
            if approval.get("decision") != "approved":
                errors.append(f"deviations[{index}].approval.decision must be approved")
        if deviation.get("status") != "approved":
            errors.append(f"deviations[{index}].status must be approved before as-built use")
        elif isinstance(approval, dict) and approval.get("decision") == "approved":
            approved_deviations[deviation.get("id")] = deviation
    if len(deviation_ids) != len(set(deviation_ids)):
        errors.append("deviation IDs must be unique")

    for index, change in enumerate(changes):
        require(
            change,
            ("id", "state", "reason", "affected_definition_keys", "affected_view_ids", "where_used_evidence", "effectivity", "approval"),
            f"changes[{index}]",
            errors,
        )
        if change.get("state") not in CHANGE_STATES:
            errors.append(f"changes[{index}].state must be one of {sorted(CHANGE_STATES)}")
        refs = change.get("affected_view_ids")
        if not isinstance(refs, list) or not refs or set(refs) - view_set:
            errors.append(f"changes[{index}].affected_view_ids must reference known views")
        keys = change.get("affected_definition_keys")
        if not isinstance(keys, list) or not keys:
            errors.append(f"changes[{index}].affected_definition_keys must be non-empty")
        else:
            for key in keys:
                if not isinstance(key, dict) or (key.get("part_number"), key.get("revision")) not in known_definitions:
                    errors.append(f"changes[{index}] references unknown affected definition")
        effectivity_ok(change.get("effectivity"), config_set, f"changes[{index}].effectivity", errors)

    declared_cost_total = Decimal("0")
    cost_by_key = defaultdict(lambda: Decimal("0"))
    costed_keys = set()
    for index, cost in enumerate(costs):
        require(
            cost,
            ("part_number", "revision", "cost_type", "unit_cost", "currency", "quantity_basis", "source", "valid_from", "valid_to"),
            f"cost_records[{index}]",
            errors,
        )
        key = (cost.get("part_number"), cost.get("revision"))
        if key not in known_definitions:
            errors.append(f"cost_records[{index}] references unknown definition")
        value = decimal_number(cost.get("unit_cost"))
        quantity = decimal_number(cost.get("quantity_basis"))
        if value is None or value < 0:
            errors.append(f"cost_records[{index}].unit_cost must be non-negative")
        if quantity is None or quantity <= 0:
            errors.append(f"cost_records[{index}].quantity_basis must be positive")
        if cost.get("currency") != product.get("currency"):
            errors.append(f"cost_records[{index}].currency differs from product currency")
        if not valid_date(cost.get("valid_from")) or not valid_date(cost.get("valid_to")):
            errors.append(f"cost_records[{index}] requires ISO validity dates")
        elif cost.get("valid_from") > cost.get("valid_to"):
            errors.append(f"cost_records[{index}] validity range is reversed")
        elif valid_date(product.get("cost_basis_date")) and not (
            cost.get("valid_from")
            <= product.get("cost_basis_date")
            <= cost.get("valid_to")
        ):
            errors.append(
                f"cost_records[{index}] is not valid on product.cost_basis_date"
            )
        if value is not None:
            declared_cost_total += value
            cost_by_key[key] += value
            costed_keys.add(key)
    if candidate:
        missing_cost = sorted(
            key for key, definition in definition_by_key.items()
            if definition.get("item_type") not in {"reference", "software", "firmware", "tooling"} and key not in costed_keys
        )
        if missing_cost:
            errors.append(f"production candidate has uncosted definitions: {missing_cost}")

    configured_costs = {}
    ebom_view_ids = {
        view_id
        for view_id, view_type in view_type_by_id.items()
        if view_type == "ebom"
    }
    for configuration_id in config_ids:
        applicable_ebom = [
            item
            for item in occurrences
            if item.get("view_id") in ebom_view_ids
            and configuration_id in (item.get("configuration_ids") or [])
        ]
        roots = [item for item in applicable_ebom if item.get("parent_id") is None]
        if candidate and len(roots) != 1:
            errors.append(
                f"configuration {configuration_id} requires exactly one applicable eBOM root"
            )
            continue
        total = Decimal("0")
        stack = [
            (root.get("id"), Decimal("1"))
            for root in roots
        ]
        visited = set()
        while stack:
            occurrence_id, parent_quantity = stack.pop()
            occurrence = occurrence_by_id.get(occurrence_id, {})
            if (
                occurrence_id in visited
                or occurrence.get("view_id") not in ebom_view_ids
                or configuration_id not in (occurrence.get("configuration_ids") or [])
            ):
                continue
            visited.add(occurrence_id)
            local_quantity = decimal_number(occurrence.get("quantity")) or Decimal("0")
            extended_quantity = parent_quantity * local_quantity
            key = (occurrence.get("part_number"), occurrence.get("revision"))
            total += cost_by_key.get(key, Decimal("0")) * extended_quantity
            for child_id in children.get(occurrence_id, []):
                stack.append((child_id, extended_quantity))
        configured_costs[configuration_id] = total

    serials = set()
    for index, unit in enumerate(built_units):
        require(
            unit,
            ("product_serial", "configuration_id", "bom_baseline", "work_order", "build_date", "site", "installed_items", "evidence"),
            f"as_built_units[{index}]",
            errors,
        )
        if unit.get("product_serial") in serials:
            errors.append("as-built product serials must be unique")
        serials.add(unit.get("product_serial"))
        if unit.get("configuration_id") not in config_set:
            errors.append(f"as_built_units[{index}] references unknown configuration")
        if present(unit.get("build_date")) and not valid_date(unit.get("build_date")):
            errors.append(f"as_built_units[{index}].build_date must be an ISO date")
        installed = unit.get("installed_items")
        if not isinstance(installed, list) or not installed:
            errors.append(f"as_built_units[{index}].installed_items must be non-empty")
        else:
            for item_index, item in enumerate(installed):
                if not isinstance(item, dict):
                    errors.append(f"as_built_units[{index}].installed_items[{item_index}] must be an object")
                    continue
                require(
                    item,
                    ("occurrence_id", "part_number", "revision", "quantity", "traceability_type", "evidence"),
                    f"as_built_units[{index}].installed_items[{item_index}]",
                    errors,
                )
                if item.get("occurrence_id") not in occurrence_set:
                    errors.append(f"as_built_units[{index}] installed item references unknown occurrence")
                if (item.get("part_number"), item.get("revision")) not in known_definitions:
                    errors.append(f"as_built_units[{index}] installed item references unknown definition")
                nominal_occurrence = occurrence_by_id.get(item.get("occurrence_id"), {})
                nominal_key = (nominal_occurrence.get("part_number"), nominal_occurrence.get("revision"))
                installed_key = (item.get("part_number"), item.get("revision"))
                if nominal_key in known_definitions and installed_key in known_definitions and installed_key != nominal_key:
                    covered_alternate = any(
                        (
                            alternate.get("primary_part", {}).get("part_number"),
                            alternate.get("primary_part", {}).get("revision"),
                        ) == nominal_key
                        and (
                            alternate.get("alternate_part", {}).get("part_number"),
                            alternate.get("alternate_part", {}).get("revision"),
                        ) == installed_key
                        and alternate.get("class") in {"equivalent", "conditional"}
                        and effectivity_applies(
                            alternate.get("effectivity"),
                            unit.get("configuration_id"),
                            unit.get("product_serial"),
                            unit.get("build_date"),
                            unit.get("site"),
                        )
                        for alternate in alternates
                    )
                    deviation = approved_deviations.get(item.get("deviation_id"))
                    covered_deviation = (
                        deviation is not None
                        and unit.get("product_serial") in deviation.get("product_serials", [])
                        and (
                            deviation.get("nominal_part", {}).get("part_number"),
                            deviation.get("nominal_part", {}).get("revision"),
                        ) == nominal_key
                        and (
                            deviation.get("substitute_part", {}).get("part_number"),
                            deviation.get("substitute_part", {}).get("revision"),
                        ) == installed_key
                    )
                    if not covered_alternate and not covered_deviation:
                        errors.append(
                            f"as_built_units[{index}] installed definition {installed_key} does not match "
                            f"nominal {nominal_key} and lacks an effective approved alternate or deviation"
                        )
                trace_type = item.get("traceability_type")
                if trace_type not in {"none", "lot", "serial", "lot_and_serial"}:
                    errors.append(f"as_built_units[{index}] installed item traceability_type is invalid")
                if trace_type in {"lot", "lot_and_serial"} and not present(item.get("lot")):
                    errors.append(f"as_built_units[{index}] lot-controlled item lacks lot")
                if trace_type in {"serial", "lot_and_serial"} and not present(item.get("serial")):
                    errors.append(f"as_built_units[{index}] serial-controlled item lacks serial")
                if definition_by_key.get((item.get("part_number"), item.get("revision")), {}).get("item_type") in {"software", "firmware"}:
                    require(item, ("version", "checksum", "target"), f"as_built_units[{index}].installed_items[{item_index}]", errors)

    event_ids = []
    for index, event in enumerate(maintenance):
        require(
            event,
            ("id", "product_serial", "date", "work_order", "action", "removed", "installed", "evidence", "release_role"),
            f"maintenance_events[{index}]",
            errors,
        )
        event_ids.append(event.get("id"))
        if event.get("product_serial") not in serials:
            errors.append(f"maintenance_events[{index}] references unknown product serial")
        if present(event.get("date")) and not valid_date(event.get("date")):
            errors.append(f"maintenance_events[{index}].date must be an ISO date")
    if len(event_ids) != len(set(event_ids)):
        errors.append("maintenance event IDs must be unique")

    reconciled_types = set()
    for index, reconciliation in enumerate(reconciliations):
        require(
            reconciliation,
            ("id", "type", "configuration_ids", "status", "differences", "artifact", "source_hash"),
            f"reconciliations[{index}]",
            errors,
        )
        if reconciliation.get("type") not in RECONCILIATION_TYPES:
            errors.append(f"reconciliations[{index}].type must be one of {sorted(RECONCILIATION_TYPES)}")
        if reconciliation.get("status") not in {"pass", "fail", "conditional"}:
            errors.append(f"reconciliations[{index}].status is invalid")
        elif reconciliation.get("status") == "pass":
            reconciled_types.add(reconciliation.get("type"))
        memberships = reconciliation.get("configuration_ids")
        if not isinstance(memberships, list) or not memberships or set(memberships) - config_set:
            errors.append(f"reconciliations[{index}].configuration_ids must be valid")
        if present(reconciliation.get("source_hash")) and not SHA256.fullmatch(
            str(reconciliation.get("source_hash"))
        ):
            errors.append(
                f"reconciliations[{index}].source_hash must be a controlled SHA-256"
            )
    if candidate and not {"cad_to_ebom", "ebom_to_mbom"}.issubset(reconciled_types):
        errors.append("production candidate requires passing CAD/eBOM and eBOM/mBOM reconciliations")

    for index, approval in enumerate(approvals):
        require(approval, ("approver", "role", "date", "scope", "configuration_ids", "decision"), f"approvals[{index}]", errors)
        if present(approval.get("date")) and not valid_date(approval.get("date")):
            errors.append(f"approvals[{index}].date must be an ISO date")
        if approval.get("decision") not in DECISIONS:
            errors.append(f"approvals[{index}].decision must be one of {sorted(DECISIONS)}")
        memberships = approval.get("configuration_ids")
        if not isinstance(memberships, list) or not memberships or set(memberships) - config_set:
            errors.append(f"approvals[{index}].configuration_ids must be valid")
    if candidate:
        authority_coverage = set()
        for approval in approvals:
            if (
                approval.get("decision") == "approved"
                and approval.get("role") == product.get("acceptance_authority_role")
                and isinstance(approval.get("configuration_ids"), list)
            ):
                authority_coverage.update(approval["configuration_ids"])
        missing_authority = config_set - authority_coverage
        if missing_authority:
            errors.append(
                "acceptance-authority approval does not cover configurations "
                f"{sorted(missing_authority)}"
            )
        if record_state != "controlled_evidence":
            warnings.append("template/fixture record cannot receive a production PASS")

    duplicate_change_ids = [key for key, count in Counter(item.get("id") for item in changes).items() if key and count > 1]
    if duplicate_change_ids:
        errors.append(f"duplicate change IDs: {duplicate_change_ids}")

    if errors:
        verdict = "FAIL"
    elif record_state != "controlled_evidence":
        verdict = "DRAFT"
    elif product.get("lifecycle_state") in {"concept", "prototype"}:
        verdict = "DRAFT"
    elif product.get("lifecycle_state") == "released":
        release = data.get("release")
        if not isinstance(release, dict):
            errors.append("released lifecycle requires release baseline metadata")
        else:
            for field in ("baseline_id", "effectivity", "release_authority_record"):
                if not present(release.get(field)):
                    errors.append(f"release.{field} is required for released lifecycle")
        verdict = "FAIL" if errors else "RELEASED"
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "definition_count": len(definitions),
            "occurrence_count": len(occurrences),
            "configuration_count": len(configs),
            "as_built_unit_count": len(built_units),
            "declared_unit_cost_sum": float(declared_cost_total),
            "configured_cost_by_configuration": {
                key: float(value) for key, value in sorted(configured_costs.items())
            },
            "currency": product.get("currency"),
        },
        "limitations": [
            "No FreeCAD, ERP, PLM, MES, supplier, certificate, or physical-unit data was inspected.",
            "Configured cost is a deterministic occurrence roll-up of declared records; "
            "it is not a supplier quote or ERP authorization.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.contract.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"verdict": "FAIL", "errors": [str(exc)]}, indent=2))
        return 2
    report = validate(data)
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.report:
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["verdict"] in {"PASS", "RELEASED"} else 1


if __name__ == "__main__":
    sys.exit(main())

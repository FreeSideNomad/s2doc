"""Mermaid UML diagram generation for aggregates"""

from typing import List
from .models import EntityResolver


class AggregateUMLGenerator:
    """Generate Mermaid UML class diagrams for aggregates"""

    def __init__(self, resolver: EntityResolver):
        self.resolver = resolver

    def generate_diagram(self, aggregate: dict) -> str:
        """Generate Mermaid classDiagram for aggregate"""
        lines = ["```mermaid", "classDiagram"]

        # Generate root entity class
        root_entity = self.resolver.get_entity(aggregate['root_ref'])
        if root_entity:
            lines.append(self._generate_entity_class(root_entity, is_root=True))

        # Generate value object classes (only for multi-attribute VOs)
        for vo_id in aggregate.get('value_objects', []):
            vo = self.resolver.get_value_object(vo_id)
            if vo and self._is_multi_attribute_vo(vo):
                lines.append(self._generate_value_object_class(vo))

        # Generate relationships (only to multi-attribute VOs)
        if root_entity:
            lines.extend(self._generate_relationships(root_entity, aggregate))

        lines.append("```")
        return "\n".join(lines)

    def _is_multi_attribute_vo(self, vo: dict) -> bool:
        """Check if value object has multiple attributes"""
        attributes = vo.get('attributes', [])
        return len(attributes) > 1

    def _generate_entity_class(self, entity: dict, is_root: bool = False) -> str:
        """Generate UML class for entity"""
        stereotype = "<<Entity Root>>" if is_root else "<<Entity>>"
        class_name = entity['name']

        lines = [f"    class {class_name} {{"]
        lines.append(f"        {stereotype}")

        # Attributes
        for attr in entity.get('attributes', []):
            attr_type = self._get_attribute_type_for_display(attr)
            attr_name = attr['name']
            lines.append(f"        +{attr_type} {attr_name}")

        lines.append("        --")

        # Methods
        for method in entity.get('business_methods', []):
            method_sig = self._generate_method_signature(method)
            lines.append(f"        +{method_sig}")

        lines.append("    }")
        return "\n".join(lines)

    def _generate_value_object_class(self, vo: dict) -> str:
        """Generate UML class for multi-attribute value object"""
        lines = [f"    class {vo['name']} {{"]
        lines.append("        <<Value Object>>")

        for attr in vo.get('attributes', []):
            lines.append(f"        +{attr['type']} {attr['name']}")

        lines.append("    }")
        return "\n".join(lines)

    def _generate_relationships(self, entity: dict, aggregate: dict) -> List[str]:
        """Generate relationships from entity to multi-attribute value objects"""
        lines = []
        entity_name = entity['name']

        for attr in entity.get('attributes', []):
            vo_id = attr.get('value_object_ref')
            if vo_id:
                vo = self.resolver.get_value_object(vo_id)
                # Only create relationship if it's a multi-attribute VO
                if vo and self._is_multi_attribute_vo(vo):
                    lines.append(f"    {entity_name} --> {vo['name']}")

        return lines

    def _get_attribute_type_for_display(self, attr: dict) -> str:
        """Get attribute type for display (simple type for single-attr VOs, VO name for multi-attr)"""
        vo_id = attr.get('value_object_ref')
        if vo_id:
            vo = self.resolver.get_value_object(vo_id)
            if vo:
                # For multi-attribute VOs, use VO name
                if self._is_multi_attribute_vo(vo):
                    return vo['name']
                # For single-attribute VOs, use the underlying type
                else:
                    vo_attrs = vo.get('attributes', [])
                    if vo_attrs:
                        return vo_attrs[0]['type']
        return attr['type']

    def _generate_method_signature(self, method: dict) -> str:
        """Generate method signature"""
        params = method.get('parameters', [])
        param_strs = [f"{p['name']}: {p['type']}" for p in params]
        param_list = ", ".join(param_strs)
        returns = method.get('returns', 'void')
        return f"{method['name']}({param_list}) {returns}"

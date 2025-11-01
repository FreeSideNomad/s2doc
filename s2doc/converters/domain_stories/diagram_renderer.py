"""
Diagram Renderer
Generates diagrams and renders them to PNG for DOCX embedding.
Uses custom PIL renderer for sequence diagrams and Graphviz for flow diagrams.
"""

import graphviz
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from .sequence_diagram import SequenceDiagramRenderer


class DiagramRenderer:
    """Renders domain story diagrams using custom PIL renderer and Graphviz."""

    def __init__(self, output_dir: Path):
        """
        Initialize diagram renderer.

        Args:
            output_dir: Directory where diagram images will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.diagram_count = 0
        self.seq_renderer = SequenceDiagramRenderer()

    @staticmethod
    def wrap_text(text: str, max_width: int = 20) -> str:
        """
        Wrap text into multiple lines at word boundaries.

        Args:
            text: Text to wrap
            max_width: Maximum characters per line

        Returns:
            Text with newlines inserted at word boundaries
        """
        if len(text) <= max_width:
            return text

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)
            # +1 for space
            if current_length + word_length + (1 if current_line else 0) <= max_width:
                current_line.append(word)
                current_length += word_length + (1 if len(current_line) > 1 else 0)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:
            lines.append(' '.join(current_line))

        return '\\n'.join(lines)

    def generate_sequence_diagram(
        self,
        story: Dict[str, Any],
        story_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a sequence diagram showing actor interactions with proper layout.

        Args:
            story: Story dictionary
            story_id: Story identifier

        Returns:
            Tuple of (description, image_path) or (None, None) if diagram not applicable
        """
        actors = story.get('actors', [])
        commands = story.get('commands', [])

        if not actors or not commands:
            return None, None

        try:
            # Render using custom PIL-based renderer
            self.diagram_count += 1
            output_filename = f'{story_id}_sequence.png'
            output_path = self.output_dir / output_filename

            success = self.seq_renderer.render(story, output_path)

            if success:
                # Return a description instead of source code
                description = f"Sequence Diagram: {story.get('title', '')}"
                return description, str(output_path)
            else:
                return None, None

        except Exception as e:
            print(f"Warning: Failed to generate sequence diagram for {story_id}: {e}")
            return None, None

    def generate_flow_diagram(
        self,
        story: Dict[str, Any],
        story_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a flowchart showing command-event-policy flow.

        Args:
            story: Story dictionary
            story_id: Story identifier

        Returns:
            Tuple of (dot_source, image_path) or (None, None) if diagram not applicable
        """
        commands = story.get('commands', [])
        events = story.get('events', [])
        policies = story.get('policies', [])

        if not commands and not events and not policies:
            return None, None

        try:
            # Create graph
            dot = graphviz.Digraph(
                name=f'flow_{story_id}',
                comment=f'Flow Diagram: {story.get("title", "")}',
                format='png'
            )

            # Graph attributes
            dot.attr(rankdir='LR', splines='ortho', nodesep='0.5', ranksep='1.0')
            dot.attr('node', style='filled')
            dot.attr('edge', color='black')

            # Limit to prevent diagram explosion
            max_nodes = 15
            node_count = 0

            for cmd in commands[:5]:
                if node_count >= max_nodes:
                    break

                cmd_id = cmd.get('command_id', '')
                cmd_name = cmd.get('name', cmd_id)
                wrapped_cmd_name = self.wrap_text(cmd_name, max_width=20)

                # Command node
                dot.node(cmd_id, label=wrapped_cmd_name, shape='box', fillcolor='lightblue')
                node_count += 1

                # Events emitted by command
                for evt_id in cmd.get('emits_events', [])[:2]:
                    if node_count >= max_nodes:
                        break

                    evt = next((e for e in events if e.get('event_id') == evt_id), None)
                    if evt:
                        evt_name = evt.get('name', evt_id)
                        wrapped_evt_name = self.wrap_text(evt_name, max_width=20)
                        dot.node(evt_id, label=wrapped_evt_name, shape='ellipse', fillcolor='lightgreen')
                        dot.edge(cmd_id, evt_id, label='emits')
                        node_count += 1

                        # Policies triggered by event
                        triggered_pols = evt.get('policies_triggered', [])
                        for pol_id in triggered_pols[:1]:
                            if node_count >= max_nodes:
                                break

                            pol = next((p for p in policies if p.get('policy_id') == pol_id), None)
                            if pol:
                                pol_name = pol.get('name', pol_id)
                                wrapped_pol_name = self.wrap_text(pol_name, max_width=18)
                                issues_cmd = pol.get('issues_command_id', '')

                                dot.node(pol_id, label=wrapped_pol_name, shape='diamond', fillcolor='lightyellow')
                                dot.edge(evt_id, pol_id, label='triggers')

                                if issues_cmd:
                                    dot.edge(pol_id, issues_cmd, label='issues')

                                node_count += 1

            if node_count == 0:
                # No content, skip diagram
                return None, None

            # Validate by attempting to get source
            dot_source = dot.source

            # Render to PNG
            self.diagram_count += 1
            output_filename = f'{story_id}_flow'
            output_path = self.output_dir / output_filename

            dot.render(output_filename, directory=str(self.output_dir), cleanup=True)

            image_path = str(output_path) + '.png'

            return dot_source, image_path

        except Exception as e:
            print(f"Warning: Failed to generate flow diagram for {story_id}: {e}")
            return None, None

    def validate_dot(self, dot_source: str) -> bool:
        """
        Validate Graphviz DOT syntax.

        Args:
            dot_source: DOT source code

        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to create a Source object (validates syntax)
            graphviz.Source(dot_source)
            return True
        except Exception:
            return False

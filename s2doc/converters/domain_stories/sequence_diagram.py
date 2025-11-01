"""
Custom Sequence Diagram Renderer
Generates proper sequence diagrams with horizontal actors and vertical lifelines.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import textwrap


class SequenceDiagramRenderer:
    """Renders UML-style sequence diagrams with actors and lifelines."""

    def __init__(self):
        """Initialize the sequence diagram renderer."""
        # High-resolution multiplier (4x for 400% resolution increase)
        self.scale = 4

        # Diagram dimensions and spacing (base sizes, will be multiplied by scale)
        self.actor_width = 140 * self.scale
        self.actor_height = 50 * self.scale
        self.actor_spacing = 80 * self.scale
        self.lifeline_spacing = 60 * self.scale
        self.message_spacing = 70 * self.scale
        self.margin = 40 * self.scale

        # Colors
        self.actor_bg = (144, 238, 144)  # lightgreen
        self.system_bg = (255, 255, 224)  # lightyellow
        self.actor_border = (0, 100, 0)  # darkgreen
        self.lifeline_color = (128, 128, 128)  # gray
        self.command_color = (0, 0, 255)  # blue
        self.event_color = (0, 128, 0)  # green
        self.text_color = (0, 0, 0)  # black

        # Try to load a font with scaled sizes, fall back to default if not available
        font_size = int(10 * self.scale)
        small_font_size = int(8 * self.scale)

        try:
            self.font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            self.small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", small_font_size)
        except:
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", small_font_size)
            except:
                self.font = ImageFont.load_default()
                self.small_font = ImageFont.load_default()

    def wrap_text(self, text: str, max_width: int = 20) -> List[str]:
        """Wrap text into multiple lines."""
        return textwrap.wrap(text, width=max_width, break_long_words=False)

    def draw_actor_box(self, draw: ImageDraw.ImageDraw, x: int, y: int,
                       label: str, bg_color: Tuple[int, int, int]) -> None:
        """Draw an actor box with rounded corners."""
        # Draw rounded rectangle (approximate with rectangle for simplicity)
        draw.rectangle(
            [x, y, x + self.actor_width, y + self.actor_height],
            fill=bg_color,
            outline=self.actor_border,
            width=2
        )

        # Draw label (center text)
        lines = self.wrap_text(label, max_width=15)
        line_height = int(12 * self.scale)  # Reduced from 14 to match smaller font
        total_height = len(lines) * line_height
        start_y = y + (self.actor_height - total_height) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=self.font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (self.actor_width - text_width) // 2
            text_y = start_y + i * line_height
            draw.text((text_x, text_y), line, fill=self.text_color, font=self.font)

    def draw_lifeline(self, draw: ImageDraw.ImageDraw, x: int, y_start: int,
                      y_end: int) -> None:
        """Draw a vertical dashed lifeline."""
        dash_length = int(8 * self.scale)
        gap_length = int(4 * self.scale)
        line_width = max(1, int(1 * self.scale))
        y = y_start

        while y < y_end:
            draw.line(
                [(x, y), (x, min(y + dash_length, y_end))],
                fill=self.lifeline_color,
                width=line_width
            )
            y += dash_length + gap_length

    def draw_message(self, draw: ImageDraw.ImageDraw, x_from: int, x_to: int,
                     y: int, label: str, is_return: bool = False) -> None:
        """Draw a message arrow between actors."""
        # Arrow color
        color = self.event_color if is_return else self.command_color

        # Scaled dimensions
        dash_length = int(8 * self.scale)
        gap_length = int(4 * self.scale)
        line_width = max(2, int(2 * self.scale))
        arrow_size = int(8 * self.scale)
        arrow_margin = int(10 * self.scale)

        # Line style
        if is_return:
            # Dashed line for return messages
            if x_from < x_to:
                x = x_from
                while x < x_to - arrow_margin:
                    draw.line([(x, y), (min(x + dash_length, x_to - arrow_margin), y)],
                             fill=color, width=line_width)
                    x += dash_length + gap_length
            else:
                x = x_from
                while x > x_to + arrow_margin:
                    draw.line([(x, y), (max(x - dash_length, x_to + arrow_margin), y)],
                             fill=color, width=line_width)
                    x -= dash_length + gap_length
        else:
            # Solid line for commands
            draw.line([(x_from, y), (x_to, y)], fill=color, width=line_width)

        # Draw arrowhead
        if x_from < x_to:
            # Right arrow
            draw.polygon(
                [(x_to, y), (x_to - arrow_size, y - arrow_size//2),
                 (x_to - arrow_size, y + arrow_size//2)],
                fill=color
            )
        else:
            # Left arrow
            draw.polygon(
                [(x_to, y), (x_to + arrow_size, y - arrow_size//2),
                 (x_to + arrow_size, y + arrow_size//2)],
                fill=color
            )

        # Draw label above the line
        lines = self.wrap_text(label, max_width=20)
        line_height = int(10 * self.scale)  # Reduced from 12 to match smaller font
        label_offset = int(5 * self.scale)
        label_y = y - len(lines) * line_height - label_offset

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=self.small_font)
            text_width = bbox[2] - bbox[0]
            # Center label on the line
            label_x = (x_from + x_to - text_width) // 2
            draw.text((label_x, label_y + i * line_height), line,
                     fill=self.text_color, font=self.small_font)

    def render(self, story: Dict[str, Any], output_path: Path) -> bool:
        """
        Render a sequence diagram for a domain story.

        Args:
            story: Story dictionary with actors, commands, events
            output_path: Path where to save the PNG image

        Returns:
            True if successful, False otherwise
        """
        actors = story.get('actors', [])
        commands = story.get('commands', [])
        events = story.get('events', [])

        if not actors or not commands:
            return False

        # Build actor list (including System)
        actor_list = []
        for actor in actors:
            actor_id = actor.get('actor_id', '').replace('act_', '')
            name = actor.get('name', actor_id)
            actor_list.append({
                'id': actor_id,
                'name': name,
                'color': self.actor_bg
            })

        # Add System if there are aggregates
        if story.get('aggregates'):
            actor_list.append({
                'id': 'system',
                'name': 'System',
                'color': self.system_bg
            })

        # Calculate actor positions
        actor_positions = {}
        total_width = len(actor_list) * (self.actor_width + self.actor_spacing) - self.actor_spacing

        for i, actor in enumerate(actor_list):
            x = self.margin + i * (self.actor_width + self.actor_spacing)
            actor_positions[actor['id']] = {
                'x': x,
                'center_x': x + self.actor_width // 2,
                'name': actor['name'],
                'color': actor['color']
            }

        # Calculate interactions (limit to 8)
        interactions = []
        for cmd in commands[:8]:
            cmd_actor_ids = cmd.get('actor_ids', [])
            cmd_name = cmd.get('name', '')

            if cmd_actor_ids:
                actor_short = cmd_actor_ids[0].replace('act_', '')

                # Command: Actor -> System
                interactions.append({
                    'from': actor_short,
                    'to': 'system',
                    'label': cmd_name,
                    'is_return': False
                })

                # Events: System -> Actor (return)
                emitted = cmd.get('emits_events', [])
                for evt_id in emitted[:1]:  # Limit to 1 event
                    evt = next((e for e in events if e.get('event_id') == evt_id), None)
                    if evt:
                        evt_name = evt.get('name', '')
                        interactions.append({
                            'from': 'system',
                            'to': actor_short,
                            'label': evt_name,
                            'is_return': True
                        })

        # Skip if no interactions
        if not interactions:
            return False

        # Calculate diagram height
        num_interactions = len(interactions)
        diagram_height = (self.margin * 2 + self.actor_height +
                         num_interactions * self.message_spacing + self.lifeline_spacing)
        diagram_width = total_width + self.margin * 2

        # Create image
        img = Image.new('RGB', (diagram_width, diagram_height), color='white')
        draw = ImageDraw.Draw(img)

        # Draw actors
        actor_y = self.margin
        for actor_id, pos in actor_positions.items():
            self.draw_actor_box(draw, pos['x'], actor_y, pos['name'], pos['color'])

        # Draw lifelines - start directly at bottom of actor boxes
        lifeline_start = actor_y + self.actor_height
        lifeline_end = diagram_height - self.margin

        for actor_id, pos in actor_positions.items():
            self.draw_lifeline(draw, pos['center_x'], lifeline_start, lifeline_end)

        # Draw interactions
        current_y = lifeline_start + int(20 * self.scale)
        for interaction in interactions:
            from_pos = actor_positions.get(interaction['from'])
            to_pos = actor_positions.get(interaction['to'])

            if from_pos and to_pos:
                self.draw_message(
                    draw,
                    from_pos['center_x'],
                    to_pos['center_x'],
                    current_y,
                    interaction['label'],
                    interaction['is_return']
                )
                current_y += self.message_spacing

        # Save image
        try:
            img.save(str(output_path), 'PNG')
            return True
        except Exception as e:
            print(f"Error saving sequence diagram: {e}")
            return False

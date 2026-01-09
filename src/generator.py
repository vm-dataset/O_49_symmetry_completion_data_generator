"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SYMMETRY COMPLETION TASK GENERATOR                         ║
║                                                                               ║
║  Generates grid-based patterns with vertical symmetry. The task is to      ║
║  complete the pattern by mirroring the left half to the right half.          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt

# Grid appearance constants
GRID_LINE_COLOR = "#cbd5e1"
GRID_LINE_WIDTH = 2
FILL_COLOR = "#1e293b"  # Dark color for filled cells
EMPTY_COLOR = "white"
BACKGROUND_COLOR = "#f8fafc"

# Pattern types - Focus on symmetry patterns
PATTERN_TYPES = [
    "vertical_symmetry",              # Left-right symmetry (main focus)
    "vertical_symmetry_checkerboard", # Checkerboard with vertical symmetry
    "vertical_symmetry_stripes",      # Stripes with vertical symmetry
    "vertical_symmetry_increment",    # Increment pattern with vertical symmetry
]

# Grid sizes - Must be even numbers for perfect left-right symmetry
GRID_SIZES = [4, 6, 8, 10, 12]


@dataclass
class PatternSpec:
    """Specification for a symmetry completion task."""
    pattern_type: str
    grid_size: int
    full_pattern: np.ndarray  # Complete pattern (0=empty, 1=filled)
    incomplete_pattern: np.ndarray  # Pattern with missing cells (-1=missing)
    missing_positions: List[Tuple[int, int]]  # List of (row, col) missing positions
    difficulty: str

    def get_signature(self) -> str:
        """Create a unique signature for this pattern."""
        missing_str = ",".join(f"{r},{c}" for r, c in sorted(self.missing_positions))
        pattern_str = "".join(str(self.full_pattern[i, j]) for i in range(self.grid_size) for j in range(self.grid_size))
        return f"{self.pattern_type}-{self.grid_size}-{missing_str}-{pattern_str}"


class SymmetryCompletionRenderer:
    """Renderer for symmetry completion frames using matplotlib."""

    def __init__(self, canvas: Tuple[int, int], dpi: int = 150):
        self.canvas = canvas
        self.dpi = dpi

    def render(self, pattern: PatternSpec, show_missing: bool) -> Image.Image:
        """Render pattern as PIL Image."""
        w, h = self.canvas
        fig, ax = plt.subplots(figsize=(w / self.dpi, h / self.dpi), dpi=self.dpi)
        ax.set_xlim(0, w)
        ax.set_ylim(0, h)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.invert_yaxis()
        
        # Draw background
        bg = Rectangle((0, 0), w, h, facecolor=BACKGROUND_COLOR, edgecolor="none")
        ax.add_patch(bg)
        
        # Draw grid
        self._draw_grid(ax, pattern, show_missing)
        
        # Save to temporary buffer and convert to PIL Image
        import io
        buf = io.BytesIO()
        fig.savefig(buf, dpi=self.dpi, bbox_inches="tight", pad_inches=0.01, format='png')
        buf.seek(0)
        img = Image.open(buf).convert('RGB')
        plt.close(fig)
        
        return img

    def _draw_grid(self, ax, pattern: PatternSpec, show_missing: bool) -> None:
        """Draw the grid with pattern."""
        w, h = self.canvas
        size = pattern.grid_size
        
        # Calculate cell size to fit in canvas
        max_cell_size = min(w, h) * 0.6 / size
        cell_size = max_cell_size
        
        # Center the grid
        grid_width = size * cell_size
        grid_height = size * cell_size
        start_x = (w - grid_width) / 2
        start_y = (h - grid_height) / 2
        
        # Draw cells
        pattern_to_show = pattern.incomplete_pattern if show_missing else pattern.full_pattern
        
        for i in range(size):
            for j in range(size):
                x = start_x + j * cell_size
                y = start_y + i * cell_size
                
                # Grid cell border
                cell = Rectangle((x, y), cell_size, cell_size,
                               facecolor=EMPTY_COLOR, edgecolor=GRID_LINE_COLOR, 
                               linewidth=GRID_LINE_WIDTH)
                ax.add_patch(cell)
                
                # Fill if pattern indicates (and not missing)
                if pattern_to_show[i, j] == 1:
                    fill = Rectangle((x + 2, y + 2), cell_size - 4, cell_size - 4,
                                    facecolor=FILL_COLOR, edgecolor="none")
                    ax.add_patch(fill)
                # Missing cells (only in first frame) are left empty


class TaskGenerator(BaseGenerator):
    """
    Symmetry completion task generator.
    
    Generates grid-based patterns with vertical symmetry. The left half is visible,
    and the right half needs to be completed by mirroring the left half.
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = SymmetryCompletionRenderer(
            canvas=config.image_size,
            dpi=config.render_dpi
        )
        
        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
        
        self._seen_signatures: set[str] = set()
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one symmetry completion task pair."""
        
        # Generate pattern
        pattern = self._create_pattern(self.config.difficulty or "medium")
        
        # Check uniqueness
        signature = pattern.get_signature()
        if signature in self._seen_signatures:
            # Try to generate a different pattern
            for _ in range(10):
                pattern = self._create_pattern(self.config.difficulty or "medium")
                signature = pattern.get_signature()
                if signature not in self._seen_signatures:
                    break
        self._seen_signatures.add(signature)
        
        # Render images
        first_image = self.renderer.render(pattern, show_missing=True)
        final_image = self.renderer.render(pattern, show_missing=False)
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, pattern)
        
        # Select prompt
        prompt = get_prompt(pattern.pattern_type)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    def _create_pattern(self, difficulty: str) -> PatternSpec:
        """Create a symmetry completion task pattern."""
        # Select grid size based on difficulty (must be even for symmetry)
        if difficulty == "easy":
            grid_size = random.choice([4, 6])
        elif difficulty == "hard":
            grid_size = random.choice([8, 10])
        else:  # medium
            grid_size = random.choice([6, 8])
        
        # Select pattern type
        pattern_type = random.choice(PATTERN_TYPES)
        
        # Generate full symmetric pattern
        full_pattern = self._generate_full_pattern(pattern_type, grid_size)
        
        # Calculate missing cells based on difficulty
        # We remove cells from the right half
        total_cells = grid_size * grid_size
        mid = grid_size // 2
        
        if difficulty == "easy":
            # Missing 30-40% of right half
            right_half_cells = grid_size * (grid_size - mid)
            missing_range = (int(right_half_cells * 0.3), int(right_half_cells * 0.4))
        elif difficulty == "hard":
            # Missing 70-80% of right half
            right_half_cells = grid_size * (grid_size - mid)
            missing_range = (int(right_half_cells * 0.7), int(right_half_cells * 0.8))
        else:  # medium
            # Missing 50-60% of right half
            right_half_cells = grid_size * (grid_size - mid)
            missing_range = (int(right_half_cells * 0.5), int(right_half_cells * 0.6))
        
        num_missing = random.randint(missing_range[0], missing_range[1])
        
        # Select missing positions from right half
        right_half_positions = [(i, j) for i in range(grid_size) for j in range(mid, grid_size)]
        num_missing = min(num_missing, len(right_half_positions))
        missing_positions = random.sample(right_half_positions, k=num_missing)
        
        # Create incomplete pattern
        incomplete_pattern = full_pattern.copy()
        for r, c in missing_positions:
            incomplete_pattern[r, c] = -1  # -1 means missing
        
        return PatternSpec(
            pattern_type=pattern_type,
            grid_size=grid_size,
            full_pattern=full_pattern,
            incomplete_pattern=incomplete_pattern,
            missing_positions=missing_positions,
            difficulty=difficulty,
        )
    
    def _generate_full_pattern(self, pattern_type: str, size: int) -> np.ndarray:
        """Generate a complete vertically symmetric pattern.
        
        Note: size must be even for perfect left-right symmetry.
        """
        assert size % 2 == 0, f"Grid size must be even for symmetry, got {size}"
        
        pattern = np.zeros((size, size), dtype=int)
        mid = size // 2  # For even sizes, this perfectly divides left and right
        
        # Generate left half pattern, then mirror to right half
        
        if pattern_type == "vertical_symmetry":
            # Simple vertical symmetry: random pattern on left, mirror to right
            for i in range(size):
                for j in range(mid):
                    pattern[i, j] = random.choice([0, 1])
            # Mirror to right half
            for i in range(size):
                for j in range(mid, size):
                    mirror_j = size - 1 - j
                    pattern[i, j] = pattern[i, mirror_j]
        
        elif pattern_type == "vertical_symmetry_checkerboard":
            # Checkerboard with vertical symmetry
            for i in range(size):
                for j in range(mid):
                    pattern[i, j] = (i + j) % 2
            # Mirror to right half
            for i in range(size):
                for j in range(mid, size):
                    mirror_j = size - 1 - j
                    pattern[i, j] = pattern[i, mirror_j]
        
        elif pattern_type == "vertical_symmetry_stripes":
            # Horizontal stripes with vertical symmetry
            for i in range(size):
                fill = i % 2
                for j in range(mid):
                    pattern[i, j] = fill
            # Mirror to right half
            for i in range(size):
                for j in range(mid, size):
                    mirror_j = size - 1 - j
                    pattern[i, j] = pattern[i, mirror_j]
        
        elif pattern_type == "vertical_symmetry_increment":
            # Row increment with vertical symmetry
            for i in range(size):
                num_filled = min(i + 1, mid)
                for j in range(num_filled):
                    pattern[i, j] = 1
            # Mirror to right half
            for i in range(size):
                for j in range(mid, size):
                    mirror_j = size - 1 - j
                    pattern[i, j] = pattern[i, mirror_j]
        
        # Verify symmetry (sanity check)
        for i in range(size):
            for j in range(mid):
                mirror_j = size - 1 - j
                assert pattern[i, j] == pattern[i, mirror_j], \
                    f"Symmetry violation at ({i}, {j}) vs ({i}, {mirror_j})"
        
        return pattern
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        pattern: PatternSpec
    ) -> Optional[str]:
        """Generate ground truth video showing cells filling in."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames showing cells filling in
        frames = self._create_filling_animation_frames(pattern)
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_filling_animation_frames(
        self,
        pattern: PatternSpec,
        hold_frames: int = 5,
        transition_frames: int = 25
    ) -> List[Image.Image]:
        """Create animation frames showing missing cells filling in."""
        frames = []
        
        # Hold initial position
        first_frame = self.renderer.render(pattern, show_missing=True)
        for _ in range(hold_frames):
            frames.append(first_frame)
        
        # Create intermediate frames showing gradual filling
        # For simplicity, we'll do a crossfade from first to final
        final_frame = self.renderer.render(pattern, show_missing=False)
        
        for i in range(transition_frames):
            progress = i / (transition_frames - 1) if transition_frames > 1 else 1.0
            
            # Simple crossfade
            if progress >= 1.0:
                frame = final_frame
            else:
                # Blend between first and final
                from PIL import Image
                frame = Image.blend(first_frame, final_frame, progress)
            
            frames.append(frame)
        
        # Hold final position
        for _ in range(hold_frames):
            frames.append(final_frame)
        
        return frames

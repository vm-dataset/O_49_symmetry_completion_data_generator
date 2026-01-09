"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SYMMETRY COMPLETION TASK CONFIGURATION                     ║
║                                                                               ║
║  Configuration for symmetry completion task generation.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Symmetry completion task configuration.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════
    
    domain: str = Field(default="symmetry_completion")
    image_size: tuple[int, int] = Field(default=(768, 512), description="Canvas size (width, height)")
    
    # ══════════════════════════════════════════════════════════════════════════
    #  RENDERING SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    render_dpi: int = Field(
        default=150,
        description="DPI for matplotlib rendering"
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )
    
    video_fps: int = Field(
        default=10,
        description="Video frame rate"
    )

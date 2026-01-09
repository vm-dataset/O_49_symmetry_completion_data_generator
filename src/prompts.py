"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SYMMETRY COMPLETION TASK PROMPTS                           ║
║                                                                               ║
║  Prompts for symmetry completion task.                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  PROMPT TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "Complete this pattern by filling in the missing grid cells on the right side. Observe the left half of the pattern and recognize that it should be mirrored to create a symmetric pattern. Fill in the right half by mirroring the left half across the vertical center line. Keep the camera view fixed in the top-down perspective and maintain all existing cells unchanged. Stop the video when the symmetric pattern is fully completed.",
        "Fill in the missing cells on the right side of the grid to complete the symmetric pattern. The left half shows the pattern that should be mirrored to the right. Mirror the left half across the vertical center line to complete the pattern. Maintain a fixed top-down camera view and keep all existing cells unchanged. Stop when the pattern is complete.",
        "Complete the symmetric pattern by mirroring the left half to the right. Observe the pattern in the left half and fill in the missing cells on the right side to create a vertically symmetric pattern. Keep the camera fixed in top-down view and preserve all existing cells. Stop the video when the symmetric pattern is fully completed.",
    ],
    
    "vertical_symmetry": [
        "Complete this pattern by filling in the missing grid cells on the right side. Observe the left half of the pattern and recognize that it should be mirrored to create a symmetric pattern. Fill in the right half by mirroring the left half across the vertical center line. Keep the camera view fixed in the top-down perspective and maintain all existing cells unchanged. Stop the video when the symmetric pattern is fully completed.",
    ],
    
    "vertical_symmetry_checkerboard": [
        "Complete the checkerboard pattern by filling in the missing cells on the right side. The left half shows a checkerboard pattern that should be mirrored to the right. Mirror the left half across the vertical center line to complete the symmetric checkerboard. Keep the camera fixed in top-down view and preserve all existing cells. Stop when the pattern is complete.",
    ],
    
    "vertical_symmetry_stripes": [
        "Complete the striped pattern by filling in the missing cells on the right side. The left half shows horizontal stripes that should be mirrored to the right. Mirror the left half across the vertical center line to complete the symmetric striped pattern. Keep the camera fixed in top-down view and preserve all existing cells. Stop when the pattern is complete.",
    ],
    
    "vertical_symmetry_increment": [
        "Complete the incrementing pattern by filling in the missing cells on the right side. The left half shows a pattern where each row has an incrementing number of filled cells. Mirror the left half across the vertical center line to complete the symmetric incrementing pattern. Keep the camera fixed in top-down view and preserve all existing cells. Stop when the pattern is complete.",
    ],
}


def get_prompt(pattern_type: str = "default") -> str:
    """
    Select a random prompt for the given pattern type.
    
    Args:
        pattern_type: Type of pattern (key in PROMPTS dict)
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(pattern_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(pattern_type: str = "default") -> list[str]:
    """Get all prompts for a given pattern type."""
    return PROMPTS.get(pattern_type, PROMPTS["default"])

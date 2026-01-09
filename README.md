# Symmetry Completion Task Data Generator 🎲

A data generator for creating symmetry completion reasoning tasks. This generator creates grid-based patterns with vertical symmetry, where the left half is visible and the right half needs to be completed by mirroring the left half.

This generator produces data in the VMEvalKit format for evaluating video generation models' reasoning capabilities.

Repository: [O_49_symmetry_completion_data_generator](https://github.com/vm-dataset/O_49_symmetry_completion_data_generator)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vm-dataset/O_49_symmetry_completion_data_generator.git
cd O_49_symmetry_completion_data_generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python3 examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
symmetry-completion-task-data-generator/
├── core/                    # ✅ Standard utilities
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image helpers
│   ├── video_utils.py      # Video generation
│   └── output_writer.py    # File output
├── src/                     # Symmetry completion task logic
│   ├── generator.py        # Pattern generator
│   ├── prompts.py          # Prompt templates
│   └── config.py           # Configuration
├── examples/
│   └── generate.py         # Entry point
└── data/questions/         # Generated output
```

---

## 📦 Output Format

Every generator produces data in VMEvalKit format:

```
data/questions/symmetry_completion_task/{task_id}/
├── first_frame.png          # Incomplete pattern (left half visible, right half missing)
├── final_frame.png          # Complete symmetric pattern
├── prompt.txt               # Instructions
└── ground_truth.mp4         # Solution video (optional)
```

---

## 🎯 Task Description

The symmetry completion task evaluates whether video generation models can complete visual patterns in grids by filling in missing cells based on symmetry rules.

### Pattern Types

1. **vertical_symmetry**: Simple vertical symmetry (random pattern on left, mirrored to right)
2. **vertical_symmetry_checkerboard**: Checkerboard pattern with vertical symmetry
3. **vertical_symmetry_stripes**: Horizontal stripes with vertical symmetry
4. **vertical_symmetry_increment**: Row increment pattern with vertical symmetry

### Grid Sizes

- Even numbers only (4×4, 6×6, 8×8, 10×10, 12×12) for perfect left-right symmetry

### Difficulty Levels

- **Easy**: 4×4 or 6×6 grids, 30-40% of right half missing
- **Medium**: 6×6 or 8×8 grids, 50-60% of right half missing
- **Hard**: 8×8 or 10×10 grids, 70-80% of right half missing

### Visual Structure

- Canvas: 768×512 pixels
- Background: Light gray (#f8fafc)
- Grid lines: Light blue-gray (#cbd5e1), 2px width
- Filled cells: Dark color (#1e293b)
- Empty cells: White

---

## 🎨 Configuration

### Basic Usage

```python
from src import TaskGenerator, TaskConfig
from pathlib import Path

config = TaskConfig(
    num_samples=100,
    domain="symmetry_completion",
    difficulty="medium",  # "easy", "medium", or "hard"
    random_seed=42,
    output_dir=Path("data/questions"),
    image_size=(768, 512),
    generate_videos=True,
    video_fps=10,
)

generator = TaskGenerator(config)
tasks = generator.generate_dataset()
```

### Command Line

```bash
# Generate 50 samples with default settings
python3 examples/generate.py --num-samples 50

# Generate with custom output directory and seed
python3 examples/generate.py --num-samples 100 --output data/my_output --seed 42

# Generate without videos
python3 examples/generate.py --num-samples 50 --no-videos
```

---

## 📝 Prompt Template

The default prompt instructs models to:

1. Observe the left half of the pattern
2. Recognize the symmetry rule
3. Fill in the right half by mirroring the left half
4. Maintain fixed top-down camera view
5. Keep all existing cells unchanged
6. Stop when the pattern is complete

Example prompt:
```
Complete this pattern by filling in the missing grid cells on the right side. 
Observe the left half of the pattern and recognize that it should be mirrored 
to create a symmetric pattern. Fill in the right half by mirroring the left 
half across the vertical center line. Keep the camera view fixed in the 
top-down perspective and maintain all existing cells unchanged. Stop the 
video when the symmetric pattern is fully completed.
```

---

## 🔧 Customization

### Modify Pattern Types

Edit `src/generator.py` to add new pattern types in the `_generate_full_pattern()` method.

### Modify Prompts

Edit `src/prompts.py` to customize prompts for different pattern types.

### Modify Configuration

Edit `src/config.py` to adjust grid sizes, difficulty levels, or visual appearance.

---

## 📊 Integration with VMEvalKit

The generated data follows the VMEvalKit format and can be directly used with the VMEvalKit evaluation framework:

1. Generate samples: `python3 examples/generate.py --num-samples 50`
2. Place data in `data/questions/symmetry_completion_task/`
3. Use with VMEvalKit runner for model evaluation

---

## 📄 License

See LICENSE file for details.

---

## 🙏 Acknowledgments

This generator is based on the symmetry completion task implementation in [VMEvalKit](https://github.com/Video-Reason/VMEvalKit).

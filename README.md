# Interactive Storytelling
This project allows the generation of procedural interactive stories using language models and Twine/Twee2. Based on GPT-2 and BERT and the huggingface transformer library, the tool can einer precalculate entire stories (maintwine.py) or play an interactively (mainqt.py).

## Installation
We recommend using conda to manage your python environments.

- Install conda
- Create an environment: create -n InteractiveStorytelling python=3.7
- Install all dependencies: pip install -r requirements.txt
- Start the generator/game: python maintwine.py / python mainqt.py

## Runtime
Here are some hints regaring the runtime:

- Generating a story can take a long time, so keep the number of actions small (1-3)
- Use a GPU for language model inference.

## Todo

### Generate more samples
- ..to get a better quality (more entities, rate rare entities)

### Evaluation
- Evaluation: What is quality? Dialog? Non-Dialog? Non dialog pushes story forward.

### Visual Support
- Add GANs to create images illustrating passages
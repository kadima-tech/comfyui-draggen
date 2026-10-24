# Draggen Extract Images

Collects the image elements on a moodboard so they can be processed one by one. Sizes can differ, so the result is a list of images rather than one stacked batch.

## Inputs

- **moodboard**: Output of Draggen Local Loader or Draggen Remote Loader.

## Output

- **IMAGE**: One image per image element. If the board has none, the node returns a blank 64×64 image.

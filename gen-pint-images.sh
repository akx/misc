#!/bin/bash

# Put images in `original/`, get resized and text-ified images in `texted/`.

set -xeuo pipefail

function overlay_text {
  local source_path="$1"
  local dest_path="$2"
  local text="$3"
  # Magic spell borrowed from https://www.imagemagick.org/discourse-server/viewtopic.php?p=142347#p142347
  convert "$source_path" \
    \( -background none -gravity center -font arial -pointsize 72 \
      -fill white label:"$text" -trim +repage \) \
    \( -clone 1 -background black -shadow 80x3+5+5 \) \
    \( -clone 1 -clone 2 +swap -background none -layers merge +repage \) \
    -delete 1,2 \
    -gravity center -compose over -composite \
    "$dest_path"
}

mkdir -p resized texted


for file in original/*.jpg; do
  resized_path="resized/${file##*/}"
  pint_path="texted/pint-${file##*/}"
  small_path="texted/small-${file##*/}"
  convert "$file" -resize 500x500^ -gravity center -extent 500x500 "$resized_path"
  overlay_text "$resized_path" "$pint_path" "Pint"
  overlay_text "$resized_path" "$small_path" "Small"
done

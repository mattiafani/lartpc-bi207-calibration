find . -type f \( -name "*.pdf" -o -name "*.gif" -o -name "*.png" \) | sort | while read -r f; do
  ext="${f##*.}"
  base="${f%.*}"
  png="${base}.png"

  # Convert PDF -> PNG if needed
  if [ "$ext" = "pdf" ]; then
    echo "Converting $f -> $png"
    convert -density 300 "$f" -quality 90 "$png"
    img="$png"
  else
    img="$f"
  fi

  # Generate alt text from filename
  name="$(basename "$base")"
  alt="$(echo "$name" | sed 's/^[0-9]\+_//; s/_/ /g')"

  # Print README line
  echo "<img src=\"${img#./}\" alt=\"${alt}\" width=\"500\"/>"
done

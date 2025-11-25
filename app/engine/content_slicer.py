from typing import List, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ContentSlicer:
    """
    Uses the JSON manifest describing boundaries to slice the raw input text into separate files.
    """

    def slice_content(self, raw_text: str, manifest: List[Dict]) -> Dict[str, str]:
        """
        Slice the raw text according to the markers in the manifest.

        Args:
            raw_text: The full raw input text string.
            manifest: List of dicts, each with 'filename', 'start_marker', 'end_marker'.

        Returns:
            Dict mapping filenames to their extracted content strings.
        """

        extracted_files = {}

        for item in manifest:
            filename = item.get("filename")
            start_marker = item.get("start_marker")
            end_marker = item.get("end_marker")

            if not (filename and start_marker and end_marker):
                logger.warning(f"Manifest entry missing required fields: {item}")
                continue

            try:
                start_idx = raw_text.index(start_marker) + len(start_marker)
                end_idx = raw_text.index(end_marker, start_idx)
                # Extract content between markers, stripping trailing whitespace
                content = raw_text[start_idx:end_idx].strip()
                extracted_files[filename] = content
            except ValueError as ve:
                logger.error(f"Marker not found in raw_text for {filename}: {ve}")

        logger.info(f"Sliced {len(extracted_files)} files from input text.")
        return extracted_files

import os
import sys
import asyncio
from app.config import settings
from app.engine.boundary_detector import BoundaryDetector
from app.engine.content_slicer import ContentSlicer
from app.utils.file_io import read_input_file, write_output_files
from app.utils.logger import get_logger
from app.utils.security import validate_path_safely

logger = get_logger(__name__)

async def process_file(input_filepath: str, output_dir: str):
    # Validate paths for security
    if not validate_path_safely(input_filepath) or not validate_path_safely(output_dir):
        logger.error(f"Invalid characters or path traversal detected in paths: {input_filepath}, {output_dir}")
        raise ValueError("Invalid paths provided.")

    # Read input raw text
    raw_text = await read_input_file(input_filepath)
    logger.info("Successfully read the input file.")

    # Step 1 & 2: Use LLM to generate JSON manifest of boundaries asynchronously
    boundary_detector = BoundaryDetector()
    json_manifest = await boundary_detector.detect_boundaries(raw_text)
    logger.info("Obtained JSON manifest with boundaries from LLM.")

    # Step 3 & 4: Slice content using Python engine
    content_slicer = ContentSlicer()
    files_content = content_slicer.slice_content(raw_text, json_manifest)

    # Write sliced content into files
    await write_output_files(files_content, output_dir)
    logger.info(f"Successfully wrote extracted files to: {output_dir}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Zero-Copy Slicer application for chaostocode")
    parser.add_argument("--input", type=str, default="input_data/dump.txt", help="Path to the raw input text file")
    parser.add_argument("--output", type=str, default="output_sliced_files/", help="Directory to output sliced files")

    args = parser.parse_args()

    try:
        asyncio.run(process_file(args.input, args.output))
    except Exception as ex:
        logger.error(f"Fatal error in processing file: {ex}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

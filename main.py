"""Main entry point for project file extractor."""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional
import time

from config import Config
from logger_config import setup_logger
from llm_client import OllamaClient
from file_extractor import FileExtractor
from file_creator import FileCreator

logger = setup_logger(__name__)


def validate_input_file(file_path: Path) -> bool:
    """Validate input file."""
    if not file_path.exists():
        logger.error(f"Input file does not exist: {file_path}")
        return False
    
    if not file_path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        return False
    
    # Check file extension
    if file_path.suffix not in Config.ALLOWED_FILE_EXTENSIONS:
        logger.error(f"Invalid file extension: {file_path.suffix}")
        logger.error(f"Allowed extensions: {Config.ALLOWED_FILE_EXTENSIONS}")
        return False
    
    # Check file size
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > Config.MAX_INPUT_FILE_SIZE_MB:
        logger.error(f"File too large: {file_size_mb:.2f}MB (max: {Config.MAX_INPUT_FILE_SIZE_MB}MB)")
        return False
    
    logger.info(f"Input file validated: {file_path} ({file_size_mb:.2f}MB)")
    return True


def read_input_file(file_path: Path) -> Optional[str]:
    """Read input file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Read input file: {len(content)} characters")
        return content
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        return None


def main(input_file: Path, output_dir: Optional[Path] = None) -> int:
    """
    Main execution function.
    
    Args:
        input_file: Path to input file
        output_dir: Optional output directory
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    start_time = time.time()
    
    logger.info("="*70)
    logger.info("PROJECT FILE EXTRACTOR STARTED")
    logger.info("="*70)
    
    # Validate input
    if not validate_input_file(input_file):
        return 1
    
    # Read input content
    content = read_input_file(input_file)
    if not content:
        return 1
    
    try:
        # Initialize LLM client
        logger.info("Initializing Ollama client...")
        with OllamaClient() as llm_client:
            # Check connection
            if not llm_client.check_connection():
                logger.error("Cannot connect to Ollama server. Is it running?")
                logger.error(f"Try: ollama serve")
                return 1
            
            # Check if model is available
            available_models = llm_client.list_models()
            if Config.OLLAMA_MODEL not in available_models:
                logger.error(f"Model not found: {Config.OLLAMA_MODEL}")
                logger.error(f"Available models: {available_models}")
                logger.error(f"Try: ollama pull {Config.OLLAMA_MODEL}")
                return 1
            
            # Initialize extractor
            extractor = FileExtractor(llm_client)
            
            # Step 1: Extract file structure
            logger.info("\nStep 1: Extracting file structure...")
            file_paths = extractor.extract_file_structure(content)
            
            if not file_paths:
                logger.error("No files extracted from content")
                return 1
            
            logger.info(f"Found {len(file_paths)} files")
            
            # Initialize file creator
            file_creator = FileCreator(output_dir)
            
            # Step 2: Create directory structure
            logger.info("\nStep 2: Creating directory structure...")
            file_creator.create_directory_structure(file_paths)
            
            # Step 3: Extract and write files
            logger.info(f"\nStep 3: Extracting and writing {len(file_paths)} files...")
            
            for idx, file_path in enumerate(file_paths, 1):
                logger.info(f"\nProcessing file {idx}/{len(file_paths)}: {file_path}")
                
                # Extract code for this file
                code = extractor.extract_code_for_file(content, file_path)
                
                if code:
                    # Write to file
                    success = file_creator.write_file(file_path, code)
                    if success:
                        logger.info(f"✓ Successfully created: {file_path}")
                    else:
                        logger.warning(f"✗ Failed to create: {file_path}")
                else:
                    logger.warning(f"✗ No code extracted for: {file_path}")
                    file_creator.failed_files.append({
                        'path': file_path,
                        'reason': 'Code extraction failed'
                    })
            
            # Print summary
            file_creator.print_summary()
            
            elapsed_time = time.time() - start_time
            logger.info(f"\nTotal execution time: {elapsed_time:.2f} seconds")
            logger.info("="*70)
            logger.info("PROJECT FILE EXTRACTOR COMPLETED")
            logger.info("="*70)
            
            # Return success if at least 50% of files were created
            success_rate = len(file_creator.created_files) / len(file_paths)
            if success_rate >= 0.5:
                return 0
            else:
                logger.error(f"Too many failures. Success rate: {success_rate:.1%}")
                return 1
            
    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


def cli():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract and create project files from a text document using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from projectTracker.txt to default output directory
  python main.py projectTracker.txt
  
  # Extract to specific output directory
  python main.py projectTracker.txt -o ./my_project
  
  # Use custom Ollama model
  OLLAMA_MODEL=codellama:latest python main.py input.txt
"""
    )
    
    parser.add_argument(
        'input_file',
        type=Path,
        help='Input file containing project structure and code'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='Output directory for created files (default: ./output)'
    )
    
    parser.add_argument(
        '-m', '--model',
        type=str,
        default=None,
        help=f'Ollama model to use (default: {Config.OLLAMA_MODEL})'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Override config if arguments provided
    if args.model:
        Config.OLLAMA_MODEL = args.model
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run main function
    exit_code = main(args.input_file, args.output)
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()

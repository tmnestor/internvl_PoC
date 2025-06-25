#!/usr/bin/env python3
"""
InternVL Single Image Information Extraction

This script processes a single image with InternVL and extracts structured information.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console

# Import from the internvl package
from internvl.config import load_config
from internvl.extraction.normalization import post_process_prediction
from internvl.model import load_model_and_tokenizer
from internvl.model.inference import get_raw_prediction
from internvl.utils.logging import get_logger, setup_logging


@dataclass
class RichConfig:
    """Configuration for rich console output."""

    console: Console = Console()
    success_style: str = "[bold green]✅[/bold green]"
    fail_style: str = "[bold red]❌[/bold red]"
    warning_style: str = "[bold yellow]⚠[/bold yellow]"
    info_style: str = "[bold blue]ℹ[/bold blue]"


rich_config = RichConfig()
app = typer.Typer(
    help="Process a single image with InternVL for information extraction."
)


@app.command()
def main(
    image_path: str = typer.Option(
        ..., "--image-path", "-i", help="Path to the image file to process"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output-file", "-o", help="Path to the output JSON file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """
    Process a single image with InternVL and extract structured information.
    """
    rich_config.console.print(
        f"{rich_config.info_style} Starting single image processing..."
    )
    rich_config.console.print(f"Image path: {image_path}")
    rich_config.console.print(f"Output file: {output_file or 'stdout'}")
    rich_config.console.print(f"Verbose: {verbose}")

    try:
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO

        # Create mock args for config loading (temporary compatibility)
        class MockArgs:
            def __init__(self):
                self.image_path = image_path
                self.output_file = output_file
                self.verbose = verbose

        args = MockArgs()
        config = load_config(args)
        transformers_log_level = config.get("transformers_log_level", "WARNING")

        setup_logging(log_level, transformers_log_level=transformers_log_level)
        logger = get_logger(__name__)

        # Resolve image path - use a clear, explicit approach
        image_path_obj = Path(image_path)

        # If path is not absolute and doesn't exist, try using project root only
        if not image_path_obj.is_absolute() and not image_path_obj.exists():
            # Try relative to project root only - the most common case for KFP

            project_root = Path(os.environ.get("INTERNVL_PROJECT_ROOT", ".")).absolute()
            alt_path = project_root / image_path_obj

            # Only update if the file exists at new path
            if alt_path.exists():
                image_path = str(alt_path)
                logger.info(f"Resolved relative path to project root: {image_path}")

        # Verify file exists before proceeding
        if not Path(image_path).exists():
            rich_config.console.print(
                f"{rich_config.fail_style} Image file not found: {image_path}"
            )
            raise typer.Exit(1)

        rich_config.console.print(
            f"{rich_config.info_style} Processing image: {image_path}"
        )

        # Get the prompt
        try:
            prompts_path = config.get("prompts_path")
            prompt_name = config.get("prompt_name")

            if prompts_path and Path(prompts_path).exists():
                with Path(prompts_path).open("r") as f:
                    prompts = yaml.safe_load(f)
                prompt = prompts.get(prompt_name, "")
                rich_config.console.print(
                    f"{rich_config.info_style} Using prompt '{prompt_name}' from {prompts_path}"
                )
            else:
                prompt = "<image>\nExtract information from this receipt and return it in JSON format."
                rich_config.console.print(
                    f"{rich_config.warning_style} Prompts file not found, using default prompt"
                )
        except Exception as e:
            rich_config.console.print(
                f"{rich_config.warning_style} Error loading prompt: {e}"
            )
            prompt = "<image>\nExtract information from this receipt and return it in JSON format."

        # Load model and tokenizer with auto-configuration
        rich_config.console.print(
            f"{rich_config.info_style} Loading model with auto-configuration..."
        )
        model, tokenizer = load_model_and_tokenizer(
            model_path=config["model_path"], auto_device_config=True
        )
        rich_config.console.print(
            f"{rich_config.success_style} Model loaded successfully!"
        )

        # Process image
        try:
            rich_config.console.print(f"{rich_config.info_style} Running inference...")
            raw_output = get_raw_prediction(
                image_path=image_path,
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                generation_config={
                    "max_new_tokens": config.get("max_tokens", 1024),
                    "do_sample": config.get("do_sample", False),
                },
                device="auto",
            )

            # Extract JSON and normalize
            processed_json = post_process_prediction(raw_output)

            # Save result
            if output_file:
                with Path(output_file).open("w") as f:
                    json.dump(processed_json, f, indent=2)
                rich_config.console.print(
                    f"{rich_config.success_style} Result saved to {output_file}"
                )
            else:
                # Print result to stdout
                rich_config.console.print("\n[bold]Result:[/bold]")
                rich_config.console.print(json.dumps(processed_json, indent=2))

        except Exception as e:
            rich_config.console.print(
                f"{rich_config.fail_style} Error processing image: {e}"
            )
            if verbose:
                import traceback

                rich_config.console.print(traceback.format_exc())
            raise typer.Exit(1) from e
        rich_config.console.print(
            f"{rich_config.success_style} Processing completed successfully!"
        )

    except Exception as e:
        rich_config.console.print(f"{rich_config.fail_style} Error: {e}")
        if verbose:
            import traceback

            rich_config.console.print(traceback.format_exc())
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()

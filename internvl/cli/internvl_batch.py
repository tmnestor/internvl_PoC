#!/usr/bin/env python3
"""
InternVL Batch Image Information Extraction

This script processes multiple images in parallel with InternVL and extracts structured information.
"""

import concurrent.futures as cf
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import typer
import yaml
from rich.console import Console
from rich.progress import Progress

# Import from the internvl package
from internvl.config import load_config
from internvl.extraction.normalization import post_process_prediction
from internvl.image.loader import get_image_filepaths
from internvl.model import load_model_and_tokenizer
from internvl.model.inference import get_raw_prediction
from internvl.utils.logging import get_logger, setup_logging
from internvl.utils.path import path_manager


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
    help="Process multiple images in parallel with InternVL for information extraction."
)


def process_image(
    image_path: str,
    model,
    tokenizer,
    prompt: str,
    generation_config: Dict[str, Any],
    device: str = "auto",
) -> Dict[str, Any]:
    """Process a single image and return extracted information."""
    start_time = time.time()
    image_id = Path(image_path).stem

    try:
        # Get raw prediction
        raw_output = get_raw_prediction(
            image_path=image_path,
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            generation_config=generation_config,
            device=device,
        )

        # Extract and normalize JSON
        processed_json = post_process_prediction(raw_output)

        # Add metadata
        result = {
            "image_id": image_id,
            "extracted_info": processed_json,
            "processing_time": time.time() - start_time,
        }

        return result

    except Exception as e:
        return {
            "image_id": image_id,
            "error": str(e),
            "processing_time": time.time() - start_time,
        }


def process_images_in_batch(
    image_paths: List[str],
    model,
    tokenizer,
    prompt: str,
    generation_config: Dict[str, Any],
    device: str = "auto",
    max_workers: int = 4,
) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """Process multiple images in parallel."""
    results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(
                process_image,
                image_path=image_path,
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                generation_config=generation_config,
                device=device,
            ): image_path
            for image_path in image_paths
        }

        # Process results as they complete with progress bar
        with Progress() as progress:
            task = progress.add_task("Processing images...", total=len(image_paths))

            for future in cf.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)

                    # Log progress
                    img_path = futures[future]
                    rich_config.console.print(
                        f"{rich_config.success_style} Processed: {Path(img_path).name}"
                    )
                    progress.advance(task)
                except Exception as e:
                    rich_config.console.print(
                        f"{rich_config.fail_style} Error processing image: {e}"
                    )
                    progress.advance(task)

    # Calculate statistics
    end_time = time.time()
    total_time = end_time - start_time
    processing_times = [r.get("processing_time", 0) for r in results]
    avg_time = sum(processing_times) / len(processing_times) if processing_times else 0

    stats = {
        "total_time": total_time,
        "avg_processing_time": avg_time,
        "num_images": len(results),
        "num_errors": sum(1 for r in results if "error" in r),
    }

    return results, stats


@app.command()
def main(
    image_folder_path: str = typer.Option(
        ...,
        "--image-folder-path",
        "-i",
        help="Path to the folder containing images to process",
    ),
    num_images: Optional[int] = typer.Option(
        None, "--num-images", "-n", help="Number of images to process (default: all)"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output-file", "-o", help="Path to the output CSV file"
    ),
    save_individual: bool = typer.Option(
        False,
        "--save-individual",
        "-s",
        help="Save individual JSON files for each image",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """
    Process multiple images in parallel with InternVL and extract structured information.
    """
    rich_config.console.print(
        f"{rich_config.info_style} Starting batch image processing..."
    )
    rich_config.console.print(f"Image folder: {image_folder_path}")
    rich_config.console.print(f"Output file: {output_file or 'none'}")
    rich_config.console.print(f"Save individual: {save_individual}")
    rich_config.console.print(f"Verbose: {verbose}")

    try:
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO

        # Create mock args for config loading (temporary compatibility)
        class MockArgs:
            def __init__(self):
                self.image_folder_path = image_folder_path
                self.num_images = num_images
                self.output_file = output_file
                self.save_individual = save_individual
                self.verbose = verbose

        args = MockArgs()
        config = load_config(args)
        transformers_log_level = config.get("transformers_log_level", "WARNING")

        setup_logging(log_level, transformers_log_level=transformers_log_level)
        get_logger(__name__)

        # Get image folder path
        image_folder_obj = Path(image_folder_path)
        if not image_folder_obj.exists():
            rich_config.console.print(
                f"{rich_config.fail_style} Image folder not found: {image_folder_path}"
            )
            raise typer.Exit(1)

        # Get image paths
        image_paths = get_image_filepaths(image_folder_obj)
        if not image_paths:
            rich_config.console.print(
                f"{rich_config.fail_style} No images found in {image_folder_path}"
            )
            raise typer.Exit(1)

        # Limit number of images if specified
        if num_images is not None and num_images > 0:
            image_paths = image_paths[:num_images]

        rich_config.console.print(
            f"{rich_config.info_style} Processing {len(image_paths)} images with {config['max_workers']} workers"
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

        # Process images with auto device detection
        generation_config = {
            "max_new_tokens": config.get("max_tokens", 1024),
            "do_sample": config.get("do_sample", False),
        }

        results, stats = process_images_in_batch(
            image_paths=image_paths,
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            generation_config=generation_config,
            device="auto",
            max_workers=config.get("max_workers", 8),
        )

        # Save results
        if output_file:
            # Create DataFrame
            df_data = []
            for result in results:
                item = {"image_id": result["image_id"]}
                if "error" in result:
                    item["error"] = result["error"]
                else:
                    for key, value in result["extracted_info"].items():
                        if isinstance(value, list):
                            item[key] = str(value)
                        else:
                            item[key] = value
                df_data.append(item)

            results_df = pd.DataFrame(df_data)
            results_df.to_csv(output_file, index=False)
            rich_config.console.print(
                f"{rich_config.success_style} Results saved to {output_file}"
            )

        # Save individual JSON files if requested
        if save_individual:
            output_dir = path_manager.get_output_path("predictions")
            output_dir.mkdir(parents=True, exist_ok=True)

            for result in results:
                if "error" not in result:
                    output_json_file = output_dir / f"{result['image_id']}.json"
                    with output_json_file.open("w") as f:
                        json.dump(result["extracted_info"], f, indent=2)

            rich_config.console.print(
                f"{rich_config.success_style} Individual JSON files saved to {output_dir}"
            )

        # Print statistics
        rich_config.console.print("\n[bold]Processing Statistics:[/bold]")
        rich_config.console.print(f"Total time: {stats['total_time']:.2f}s")
        rich_config.console.print(
            f"Average time per image: {stats['avg_processing_time']:.2f}s"
        )
        rich_config.console.print(f"Images processed: {stats['num_images']}")
        rich_config.console.print(f"Errors: {stats['num_errors']}")

        rich_config.console.print(
            f"{rich_config.success_style} Batch processing completed successfully!"
        )

    except Exception as e:
        rich_config.console.print(f"{rich_config.fail_style} Error: {e}")
        if verbose:
            import traceback

            rich_config.console.print(traceback.format_exc())
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()

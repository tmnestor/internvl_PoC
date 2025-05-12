# InternVL Evaluation Project

## Purpose & Overview

This project provides tools and infrastructure for extracting structured information from images using the InternVL2.5 multimodal model. It focuses primarily on receipt and invoice processing, converting unstructured visual data into structured JSON formats.

## Key Capabilities

- **Multimodal Understanding**: Uses InternVL2.5 to comprehend both visual and textual elements in documents
- **Structured Data Extraction**: Extracts key fields like dates, store names, taxes, totals, and itemized lists
- **Field Normalization**: Standardizes extracted date formats, currency values, and text elements
- **Dynamic Image Processing**: Employs adaptive tiling based on image aspect ratios for optimal processing
- **Batch Processing**: Supports parallel processing of multiple images with progress tracking
- **Comprehensive Evaluation**: Evaluates extraction accuracy against ground truth data

## Use Cases

This system is designed for scenarios where structured data needs to be extracted from receipt images:

- **Document Processing**: Automated extraction of information from receipts and invoices
- **Financial Record Keeping**: Digitizing receipt data for expense tracking and accounting
- **Data Extraction Evaluation**: Benchmarking and improving extraction accuracy
- **Research**: Testing and evaluating multimodal AI models on practical document understanding tasks

## Technical Architecture

The project follows a modular design with clear separation of concerns:

1. **Configuration Management**: Environment variables and YAML-based prompts
2. **Image Processing**: Preprocessing images for optimal model input
3. **Model Inference**: InternVL2.5 model loading and prompt-based extraction
4. **Data Extraction**: Standardized JSON output with field normalization
5. **Evaluation System**: Metrics for accuracy assessment

## Data Handling

The system works with both synthetic and real-world datasets:

- **SROIE Dataset**: Standard dataset of real-world receipts with ground truth annotations
- **Synthetic Data**: Generated receipt images with corresponding ground truth data
- **Custom Data**: Support for processing user-provided images

## Evaluation Criteria

The system evaluates extraction performance using several key metrics:

- **Field Accuracy**: Percentage of correctly extracted fields across all documents
- **Precision**: Ratio of correctly extracted fields to total extracted fields
- **Recall**: Ratio of correctly extracted fields to total fields in ground truth
- **F1 Score**: Harmonic mean of precision and recall, balancing both metrics
- **Field-Level Performance**: Separate evaluation for different field types (dates, prices, store names)
- **Normalization Impact**: Evaluation with and without field normalization to measure its effect

Evaluation results are stored in structured formats (JSON/CSV) and visualized with performance graphs.

## Project Status

This project serves as a proof-of-concept demonstrating the capabilities of InternVL2.5 for structured data extraction from images. It provides both research and practical application value for document understanding tasks.

---

*This document provides a high-level overview of the InternVL Evaluation Project. For detailed technical information and usage instructions, please refer to the README.md and documentation in the docs/ directory.*
# Synthetic Australian Receipt Generator

This directory contains scripts for generating synthetic Australian receipts for testing the InternVL model's information extraction capabilities.

## Available Scripts

- `simple_receipt_generator.py` - Basic script for generating simple Australian receipt images for testing
- `receipt_generator.py` - Advanced script for generating more realistic Australian receipts with various layouts and styles

## Usage Instructions

### Generating Simple Test Receipts

To generate basic synthetic receipts for testing:

```bash
# Activate the conda environment
conda activate internvl_env

# Use Python module execution
PYTHONPATH=$PWD python3 -m src.internvl.data.generators.simple_receipt_generator --num_receipts 20 --include_gst

# Or use the run.sh helper script (if implemented)
./run.sh generate-data --type simple --num_receipts 20 --include_gst
```

### Generating Advanced Test Receipts

To generate more visually diverse and realistic receipts:

```bash
# Activate the conda environment
conda activate internvl_env

# Use Python module execution
python -m src.internvl.data.generators.receipt_generator --num_receipts 20 --image_size 2048

# Or use the run.sh helper script (if implemented)
./run.sh generate-data --type advanced --num_receipts 20 --image_size 2048
```

### Parameters

#### Simple Receipt Generator Parameters:
- `--num_receipts`: Number of test receipts to generate (default: 20)
- `--include_gst`: Flag to include GST (Goods and Services Tax) on the receipts (recommended for Australian receipts)
- `--output_dir`: Output directory (overrides environment variable INTERNVL_SYNTHETIC_DATA_PATH)

#### Advanced Receipt Generator Parameters:
- `--num_receipts`: Number of receipts to generate (default: 20)
- `--image_size`: Size of output images (default: 2048)
- `--seed`: Random seed for reproducibility (default: 42)
- `--output_dir`: Output directory (overrides environment variable INTERNVL_SYNTHETIC_DATA_PATH)

### Generated Directory Structure

Both scripts will create the following directory structure for information extraction:

```
$INTERNVL_SYNTHETIC_DATA_PATH/
└── test/
    ├── images/
    │   ├── sample_receipt_001.jpg
    │   ├── sample_receipt_002.jpg
    │   └── ...
    └── ground_truth/
        ├── sample_receipt_001.json
        ├── sample_receipt_002.json
        └── ...
```

By default, `$INTERNVL_SYNTHETIC_DATA_PATH` is set to `$INTERNVL_DATA_PATH/synthetic`.

- `images/`: Contains the synthetic receipt images
- `ground_truth/`: Contains the ground truth data for information extraction evaluation

The advanced generator also creates a `metadata_summary.csv` file at the root of the output directory with summary information about the generated receipts.

### Receipt Features

Each generated receipt includes:
- Store name (randomly selected from common Australian retailers)
- Date (randomly generated within the last 30 days)
- Items (randomly selected from common grocery items)
- Quantities (random quantities between 1-3)
- Prices (random prices between $2.50-$25.00)
- GST amount (10% Australian tax)
- Total amount

The advanced generator adds:
- Multiple receipt layouts and styles (standard, detailed, minimal, fancy)
- More varied store names and items
- Randomized formatting and visual elements
- More realistic receipt dimensions and proportions

### Ground Truth Format

The ground truth JSON files have the following structure for information extraction:

```json
{
  "date_value": "01/05/2023",
  "store_name_value": "WOOLWORTHS",
  "tax_value": "1.45",
  "total_value": "15.95",
  "prod_item_value": ["Milk 2L", "Bread", "Eggs 12pk"],
  "prod_quantity_value": ["2", "1", "3"],
  "prod_price_value": ["4.50", "3.80", "7.65"]
}
```

This format matches the expected field names used by the InternVL model for Australian receipts. The field names align with:
1. date_value: The date of purchase
2. store_name_value: The name of the Australian store
3. tax_value: The GST (tax) amount
4. total_value: The total purchase amount
5. prod_item_value: List of product items purchased
6. prod_quantity_value: List of quantities for each product
7. prod_price_value: List of prices for each product

## Notes

- These scripts only generate test data since we're not performing fine-tuning
- The generators focus solely on information extraction (not question-answer pairs)
- All receipts follow Australian conventions, including GST (10% tax)
- The simple generator creates more basic receipts, while the advanced generator creates more visually diverse and realistic receipts
- Use the advanced generator when you need receipts with greater visual variety to test model robustness
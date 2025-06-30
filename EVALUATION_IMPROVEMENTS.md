# InternVL Evaluation System: Priority Improvements

## Executive Summary

The InternVL evaluation system has a solid foundation with modular architecture and comprehensive functionality. However, to meet ML/AI best practices for production systems, several critical improvements are needed. This document outlines priority enhancements organized by urgency and impact.

## Current State Assessment

### Strengths
- ✅ Modular architecture with clear separation of concerns
- ✅ Comprehensive error handling and detailed logging
- ✅ Flexible environment-based configuration management
- ✅ Multiple evaluation metrics (Precision, Recall, F1-score, BLEU)
- ✅ Domain-specific validation (GST calculation for Australian receipts)
- ✅ Robust data normalization pipeline

### Critical Gaps
- ❌ No structured testing framework
- ❌ Limited scalability (sequential processing only)
- ❌ Character-level metrics don't reflect semantic accuracy
- ❌ Missing data validation for ground truth consistency
- ❌ No experiment tracking or reproducibility controls
- ❌ Brittle schema detection logic

---

## HIGH PRIORITY IMPROVEMENTS

### 1. Implement Comprehensive Testing Framework

**Current State:** Ad-hoc test scripts without pytest integration

**Impact:** Critical for reliability, maintainability, and confidence in evaluation results

#### Implementation Plan

```bash
# Directory structure
tests/
├── unit/
│   ├── test_metrics.py
│   ├── test_schema_converter.py
│   ├── test_normalization.py
│   └── test_field_processing.py
├── integration/
│   ├── test_evaluation_pipeline.py
│   ├── test_prediction_generation.py
│   └── test_end_to_end.py
├── fixtures/
│   ├── sample_predictions.json
│   ├── sample_ground_truth.json
│   └── test_images/
└── conftest.py
```

#### Key Components

**Unit Tests Example:**
```python
# tests/unit/test_metrics.py
import pytest
from internvl.evaluation.metrics import calculate_metrics, normalize_field_values

class TestMetrics:
    def test_calculate_metrics_exact_match(self):
        """Test perfect match scenario."""
        actual = "WOOLWORTHS"
        predicted = "WOOLWORTHS"
        result = calculate_metrics(actual, predicted, "test_001")
        assert result['F1-score'] == 1.0
        assert result['precision'] == 1.0
        assert result['recall'] == 1.0
    
    def test_calculate_metrics_partial_match(self):
        """Test partial match scenario."""
        actual = "WOOLWORTHS SUPERMARKET"
        predicted = "WOOLWORTHS"
        result = calculate_metrics(actual, predicted, "test_002")
        assert 0 < result['F1-score'] < 1.0
    
    def test_normalize_field_values_date_formats(self):
        """Test date normalization with various formats."""
        test_cases = [
            {"date_value": "05/05/2025", "expected": "2025-05-05"},
            {"date_value": "5 May 2025", "expected": "2025-05-05"},
            {"date_value": "May 5, 2025", "expected": "2025-05-05"}
        ]
        for case in test_cases:
            normalized = normalize_field_values(case)
            assert normalized["date_value"] == case["expected"]
```

**Integration Tests Example:**
```python
# tests/integration/test_evaluation_pipeline.py
import pytest
from pathlib import Path
from internvl.evaluation.evaluate_extraction import main

class TestEvaluationPipeline:
    def test_full_evaluation_pipeline(self, tmp_path, sample_data):
        """Test complete evaluation pipeline."""
        # Setup test data
        pred_dir = tmp_path / "predictions"
        gt_dir = tmp_path / "ground_truth"
        output_dir = tmp_path / "output"
        
        # Create test files
        self._create_test_files(pred_dir, gt_dir, sample_data)
        
        # Run evaluation
        result = main(
            predictions_dir=pred_dir,
            ground_truth_dir=gt_dir,
            output_path=output_dir / "results.json"
        )
        
        # Verify results
        assert result["overall_accuracy"] > 0
        assert (output_dir / "results.json").exists()
```

**Configuration:**
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = --verbose --cov=internvl --cov-report=html --cov-report=term
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

**Estimated Effort:** 2-3 weeks
**Dependencies:** pytest, pytest-cov, pytest-mock

---

### 2. Enhanced Data Validation with Pydantic

**Current State:** Basic dictionary-based data handling without validation

**Impact:** Prevents silent failures and ensures data consistency

#### Implementation Plan

**Schema Definitions:**
```python
# internvl/schemas/receipt_schemas.py
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Union
from datetime import datetime
import re

class SROIESchema(BaseModel):
    """SROIE dataset schema with validation."""
    
    date_value: str = Field(..., description="Receipt date")
    store_name_value: str = Field(..., description="Store name")
    tax_value: str = Field(..., description="GST/Tax amount")
    total_value: str = Field(..., description="Total amount")
    prod_item_value: List[str] = Field(default_factory=list, description="Product items")
    prod_quantity_value: List[str] = Field(default_factory=list, description="Product quantities")
    prod_price_value: List[str] = Field(default_factory=list, description="Product prices")
    
    @validator('date_value')
    def validate_date(cls, v):
        """Validate date format."""
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{1,2}/\d{1,2}/\d{4}',  # D/M/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
        ]
        if not any(re.match(pattern, v) for pattern in date_patterns):
            raise ValueError(f"Invalid date format: {v}")
        return v
    
    @validator('tax_value', 'total_value')
    def validate_currency(cls, v):
        """Validate currency format."""
        # Remove currency symbols and commas
        clean_value = re.sub(r'[^\d.]', '', v)
        try:
            float(clean_value)
        except ValueError:
            raise ValueError(f"Invalid currency format: {v}")
        return v
    
    @validator('prod_quantity_value', 'prod_price_value')
    def validate_product_lists(cls, v, values):
        """Ensure product lists have consistent lengths."""
        if 'prod_item_value' in values:
            if len(v) != len(values['prod_item_value']):
                raise ValueError(
                    f"Product list length mismatch: items={len(values['prod_item_value'])}, "
                    f"current_field={len(v)}"
                )
        return v
    
    @validator('prod_quantity_value')
    def validate_quantities(cls, v):
        """Validate product quantities are numeric."""
        for qty in v:
            try:
                float(qty)
            except ValueError:
                raise ValueError(f"Invalid quantity: {qty}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "date_value": "05/05/2025",
                "store_name_value": "WOOLWORTHS",
                "tax_value": "$5.45",
                "total_value": "$65.00",
                "prod_item_value": ["MILK", "BREAD"],
                "prod_quantity_value": ["1", "2"],
                "prod_price_value": ["$4.50", "$3.00"]
            }
        }

class AustralianReceiptSchema(BaseModel):
    """Australian-specific receipt schema with GST validation."""
    
    date_value: str
    store_name_value: str
    abn_value: Optional[str] = None
    gst_value: str = Field(..., description="GST amount (10% in Australia)")
    total_value: str
    subtotal_value: Optional[str] = None
    prod_item_value: List[str] = Field(default_factory=list)
    prod_quantity_value: List[str] = Field(default_factory=list)
    prod_price_value: List[str] = Field(default_factory=list)
    
    @validator('abn_value')
    def validate_abn(cls, v):
        """Validate Australian Business Number format."""
        if v is None:
            return v
        # ABN is 11 digits, often formatted with spaces
        abn_digits = re.sub(r'\s+', '', v)
        if not re.match(r'^\d{11}$', abn_digits):
            raise ValueError(f"Invalid ABN format: {v}")
        return v
    
    @validator('gst_value')
    def validate_gst_calculation(cls, v, values):
        """Validate GST is approximately 10% of subtotal."""
        if 'subtotal_value' in values and values['subtotal_value']:
            try:
                gst_amount = float(re.sub(r'[^\d.]', '', v))
                subtotal = float(re.sub(r'[^\d.]', '', values['subtotal_value']))
                expected_gst = subtotal * 0.1
                
                # Allow 5% tolerance for rounding
                if abs(gst_amount - expected_gst) > expected_gst * 0.05:
                    raise ValueError(
                        f"GST calculation error: GST=${gst_amount:.2f}, "
                        f"expected ~${expected_gst:.2f} (10% of subtotal)"
                    )
            except ValueError as e:
                if "GST calculation error" in str(e):
                    raise
                # If parsing fails, let the currency validator handle it
        return v
```

**Data Validation Integration:**
```python
# internvl/evaluation/validation.py
from typing import Dict, List, Tuple, Any
from pathlib import Path
import json
from pydantic import ValidationError

from internvl.schemas.receipt_schemas import SROIESchema, AustralianReceiptSchema

class DataValidator:
    """Validate ground truth and prediction data."""
    
    def __init__(self, schema_type: str = "sroie"):
        self.schema_map = {
            "sroie": SROIESchema,
            "australian": AustralianReceiptSchema
        }
        self.schema = self.schema_map.get(schema_type, SROIESchema)
    
    def validate_ground_truth_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate a single ground truth file."""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate against schema
            self.schema(**data)
            return True, []
            
        except json.JSONDecodeError as e:
            errors.append(f"JSON parsing error: {e}")
        except ValidationError as e:
            errors.extend([f"Validation error: {error['msg']}" for error in e.errors()])
        except Exception as e:
            errors.append(f"Unexpected error: {e}")
        
        return False, errors
    
    def validate_ground_truth_directory(self, gt_dir: Path) -> Dict[str, Any]:
        """Validate all ground truth files in directory."""
        results = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "errors": {},
            "summary": {}
        }
        
        for file_path in gt_dir.glob("*.json"):
            results["total_files"] += 1
            
            is_valid, errors = self.validate_ground_truth_file(file_path)
            
            if is_valid:
                results["valid_files"] += 1
            else:
                results["invalid_files"] += 1
                results["errors"][str(file_path)] = errors
        
        results["summary"] = {
            "validation_rate": results["valid_files"] / results["total_files"] if results["total_files"] > 0 else 0,
            "error_rate": results["invalid_files"] / results["total_files"] if results["total_files"] > 0 else 0
        }
        
        return results
    
    def validate_predictions(self, predictions: List[Dict[str, Any]]) -> List[Tuple[int, bool, List[str]]]:
        """Validate prediction data."""
        results = []
        
        for i, pred in enumerate(predictions):
            try:
                self.schema(**pred)
                results.append((i, True, []))
            except ValidationError as e:
                errors = [f"Validation error: {error['msg']}" for error in e.errors()]
                results.append((i, False, errors))
        
        return results
```

**Estimated Effort:** 1-2 weeks
**Dependencies:** pydantic

---

### 3. Implement Semantic Similarity Metrics

**Current State:** Character-level comparison only

**Impact:** Better reflects actual extraction quality for human-readable content

#### Implementation Plan

**Enhanced Metrics Module:**
```python
# internvl/evaluation/semantic_metrics.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics import classification_report
import numpy as np
from typing import Dict, List, Union, Tuple
import editdistance
from difflib import SequenceMatcher
import re

class SemanticMetrics:
    """Advanced metrics incorporating semantic understanding."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.sentence_model = SentenceTransformer(model_name)
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between texts using sentence embeddings."""
        if not text1.strip() or not text2.strip():
            return 0.0
        
        embeddings = self.sentence_model.encode([text1, text2])
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)
    
    def normalized_edit_distance(self, text1: str, text2: str) -> float:
        """Calculate normalized edit distance (0 = identical, 1 = completely different)."""
        if not text1 and not text2:
            return 0.0
        
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 0.0
        
        edit_dist = editdistance.eval(text1, text2)
        return edit_dist / max_len
    
    def fuzzy_string_similarity(self, text1: str, text2: str) -> float:
        """Calculate fuzzy string similarity using SequenceMatcher."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def currency_accuracy(self, actual: str, predicted: str) -> Dict[str, float]:
        """Specialized accuracy for currency values."""
        def extract_amount(text):
            # Extract numeric value from currency string
            match = re.search(r'[\d,]+\.?\d*', text.replace('$', ''))
            return float(match.group().replace(',', '')) if match else 0.0
        
        try:
            actual_amount = extract_amount(actual)
            predicted_amount = extract_amount(predicted)
            
            if actual_amount == 0 and predicted_amount == 0:
                return {"exact_match": 1.0, "relative_error": 0.0}
            
            exact_match = 1.0 if actual_amount == predicted_amount else 0.0
            relative_error = abs(actual_amount - predicted_amount) / max(actual_amount, 0.01)
            
            return {
                "exact_match": exact_match,
                "relative_error": min(relative_error, 1.0),  # Cap at 1.0
                "absolute_error": abs(actual_amount - predicted_amount)
            }
        except (ValueError, AttributeError):
            return {"exact_match": 0.0, "relative_error": 1.0, "absolute_error": float('inf')}
    
    def date_accuracy(self, actual: str, predicted: str) -> Dict[str, float]:
        """Specialized accuracy for date values."""
        from datetime import datetime
        
        def parse_date(date_str):
            formats = ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue
            return None
        
        actual_date = parse_date(actual)
        predicted_date = parse_date(predicted)
        
        if actual_date is None or predicted_date is None:
            return {"exact_match": 0.0, "day_difference": float('inf')}
        
        exact_match = 1.0 if actual_date == predicted_date else 0.0
        day_difference = abs((actual_date - predicted_date).days)
        
        return {
            "exact_match": exact_match,
            "day_difference": day_difference,
            "within_week": 1.0 if day_difference <= 7 else 0.0
        }
    
    def comprehensive_field_metrics(self, actual: str, predicted: str, 
                                  field_type: str = "text") -> Dict[str, float]:
        """Calculate comprehensive metrics for a field."""
        base_metrics = {
            "exact_match": 1.0 if actual == predicted else 0.0,
            "semantic_similarity": self.semantic_similarity(actual, predicted),
            "fuzzy_similarity": self.fuzzy_string_similarity(actual, predicted),
            "normalized_edit_distance": self.normalized_edit_distance(actual, predicted)
        }
        
        # Add field-specific metrics
        if field_type == "currency":
            base_metrics.update(self.currency_accuracy(actual, predicted))
        elif field_type == "date":
            base_metrics.update(self.date_accuracy(actual, predicted))
        
        return base_metrics
    
    def calculate_aggregate_metrics(self, field_metrics: List[Dict[str, float]]) -> Dict[str, float]:
        """Aggregate metrics across multiple fields."""
        if not field_metrics:
            return {}
        
        # Calculate means for each metric
        all_keys = set()
        for metrics in field_metrics:
            all_keys.update(metrics.keys())
        
        aggregated = {}
        for key in all_keys:
            values = [m.get(key, 0.0) for m in field_metrics if key in m]
            if values:
                aggregated[f"mean_{key}"] = np.mean(values)
                aggregated[f"std_{key}"] = np.std(values)
                aggregated[f"min_{key}"] = np.min(values)
                aggregated[f"max_{key}"] = np.max(values)
        
        return aggregated
```

**Integration with Existing Evaluation:**
```python
# internvl/evaluation/enhanced_evaluate.py
from internvl.evaluation.semantic_metrics import SemanticMetrics
from internvl.evaluation.metrics import calculate_metrics

class EnhancedEvaluator:
    """Enhanced evaluator with semantic metrics."""
    
    def __init__(self):
        self.semantic_metrics = SemanticMetrics()
        self.field_types = {
            'date_value': 'date',
            'tax_value': 'currency',
            'total_value': 'currency',
            'prod_price_value': 'currency',
            'store_name_value': 'text',
            'prod_item_value': 'text'
        }
    
    def evaluate_field(self, field_name: str, actual: str, predicted: str) -> Dict[str, float]:
        """Evaluate a single field with appropriate metrics."""
        field_type = self.field_types.get(field_name, 'text')
        
        # Get legacy metrics for backward compatibility
        legacy_metrics = calculate_metrics(actual, predicted, field_name)
        
        # Get enhanced semantic metrics
        semantic_metrics = self.semantic_metrics.comprehensive_field_metrics(
            actual, predicted, field_type
        )
        
        # Combine metrics
        combined_metrics = {**legacy_metrics, **semantic_metrics}
        
        return combined_metrics
```

**Estimated Effort:** 2-3 weeks
**Dependencies:** sentence-transformers, scikit-learn, editdistance

---

## MEDIUM PRIORITY IMPROVEMENTS

### 4. Parallel Processing for Scalability

**Implementation:**
```python
# internvl/evaluation/parallel_evaluator.py
import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
from typing import List, Dict, Any
from pathlib import Path

class ParallelEvaluator:
    """Parallel evaluation for improved performance."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
    
    async def evaluate_batch_async(self, prediction_files: List[Path], 
                                 ground_truth_dir: Path) -> Dict[str, Any]:
        """Evaluate predictions in parallel using asyncio."""
        loop = asyncio.get_event_loop()
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = [
                loop.run_in_executor(
                    executor, 
                    partial(self._evaluate_single_file, pred_file, ground_truth_dir)
                )
                for pred_file in prediction_files
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions and aggregate results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        return {
            "successful_evaluations": len(successful_results),
            "failed_evaluations": len(failed_results),
            "results": successful_results,
            "errors": failed_results,
            "aggregated_metrics": self._aggregate_parallel_results(successful_results)
        }
```

**Estimated Effort:** 1-2 weeks

### 5. Experiment Tracking System

**Implementation:**
```python
# internvl/evaluation/experiment_tracking.py
import mlflow
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

@dataclass
class EvaluationConfig:
    """Configuration for evaluation experiments."""
    model_name: str
    prompt_name: str
    dataset_name: str
    evaluation_date: str
    normalization_enabled: bool
    semantic_metrics_enabled: bool
    validation_schema: str
    test_image_count: int
    
class ExperimentTracker:
    """MLflow-based experiment tracking."""
    
    def __init__(self, experiment_name: str = "internvl_evaluation"):
        mlflow.set_experiment(experiment_name)
        self.experiment_name = experiment_name
    
    def log_evaluation_run(self, 
                          config: EvaluationConfig,
                          metrics: Dict[str, float],
                          artifacts: Dict[str, Path],
                          tags: Optional[Dict[str, str]] = None):
        """Log complete evaluation run."""
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(asdict(config))
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log tags
            if tags:
                mlflow.set_tags(tags)
            
            # Log artifacts
            for artifact_name, path in artifacts.items():
                if path.exists():
                    mlflow.log_artifact(str(path), artifact_name)
            
            # Log system info
            mlflow.log_param("python_version", sys.version)
            mlflow.log_param("execution_time", datetime.now().isoformat())
            
            return mlflow.active_run().info.run_id
```

**Estimated Effort:** 1-2 weeks

---

## LOW PRIORITY IMPROVEMENTS

### 6. Advanced Visualization and Reporting

**Features:**
- Interactive evaluation dashboards
- Confusion matrices for classification tasks
- Performance trend analysis
- Field-level accuracy heatmaps

**Estimated Effort:** 2-3 weeks

### 7. Statistical Significance Testing

**Features:**
- Confidence intervals for metrics
- Statistical significance tests for model comparisons
- Bootstrap sampling for robust evaluation

**Estimated Effort:** 1-2 weeks

---

## Implementation Roadmap

### Phase 1: Foundation (4-6 weeks)
1. Implement comprehensive testing framework
2. Add Pydantic-based data validation
3. Create semantic similarity metrics

### Phase 2: Scalability (2-3 weeks)
1. Implement parallel processing
2. Add experiment tracking system

### Phase 3: Advanced Features (3-4 weeks)
1. Advanced visualization
2. Statistical significance testing
3. Automated reporting

## Success Metrics

- **Test Coverage:** >80% code coverage
- **Data Quality:** 100% validation pass rate for ground truth
- **Performance:** 5x speedup with parallel processing
- **Reliability:** Zero silent failures with comprehensive validation
- **Reproducibility:** All experiments tracked and reproducible

## Conclusion

These improvements will transform the InternVL evaluation system from a functional prototype into a production-ready ML evaluation framework. The prioritized approach ensures that critical reliability and accuracy improvements are implemented first, followed by performance and advanced features.

The investment in these improvements will pay dividends in:
- **Reduced debugging time** through comprehensive testing
- **Increased confidence** in evaluation results through validation
- **Better insights** through semantic metrics
- **Faster iteration** through parallel processing
- **Reproducible research** through experiment tracking
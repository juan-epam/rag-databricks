# RAG on Databricks

A comprehensive implementation of Retrieval Augmented Generation (RAG) applications on Databricks, featuring production-ready examples and quality iteration workflows.

## 🌟 Features

- **Production-Ready RAG Applications**: Complete examples of RAG implementations using Databricks
- **Quality Iteration Workflow**: Tools and notebooks for improving RAG application quality
- **Multiple Implementation Examples**:
  - Basic POC RAG Application
  - OpenAI SDK Integration
  - GenAI Cookbook Examples

## 📁 Repository Structure

```
.
├── rag_app_sample_code/           # Main RAG implementation examples
│   ├── A_POC_app/                # Proof of concept RAG application
│   │   ├── pdf_uc_volume/       # PDF document processing pipeline
│   │   ├── docx_uc_volume/      # Word document processing pipeline
│   │   ├── pptx_uc_volume/      # PowerPoint processing pipeline
│   │   ├── html_uc_volume/      # HTML document processing pipeline
│   │   └── databricks_docs_example/ # Example with Databricks documentation
│   ├── B_quality_iteration/      # Quality improvement workflows
│   │   ├── chain_code_fixes/    # Improvements for RAG chain code
│   │   ├── data_pipeline_fixes/ # Data processing pipeline improvements
│   │   ├── 01_root_cause_quality_issues.py # Quality analysis
│   │   └── 02_evaluate_fixes.py # Evaluation of improvements
│   ├── helpers/                  # Utility functions and helpers
│   └── resources/                # Additional resources and configs
├── openai_sdk_agent_app_sample_code/  # OpenAI SDK integration examples
├── genai_cookbook/               # General GenAI implementation examples
└── agent_app_sample_code/        # Agent-based application examples
```

## 🔍 RAG Application Details

### A. POC Application (`A_POC_app/`)

The Proof of Concept application demonstrates RAG implementation across different document types:

1. **Document Processing Pipelines**
   - PDF processing with advanced text extraction
   - Word document handling with structure preservation
   - PowerPoint slide processing with layout awareness
   - HTML document processing with semantic structure retention

2. **Utility Components**
   - `z_shared_utilities.py`: Common functions for document processing
   - `z_eval_set_utilities.py`: Evaluation set creation and management

### B. Quality Iteration (`B_quality_iteration/`)

A systematic approach to improving RAG application quality:

1. **Analysis Phase**
   - Root cause analysis of quality issues (`01_root_cause_quality_issues.py`)
   - Systematic evaluation of improvements (`02_evaluate_fixes.py`)

2. **Improvement Areas**
   - Chain code optimizations in `chain_code_fixes/`
   - Data pipeline enhancements in `data_pipeline_fixes/`

## 🚀 Getting Started

1. **Prerequisites**
   - Databricks workspace
   - Python 3.x
   - Required packages: databricks-agents, langchain, mlflow

2. **Configuration**
   - Copy `.env.example` to `.env` and fill in your credentials
   - Update `global_config.yaml` with your specific settings

3. **Running the RAG Application**
   - Start with the POC app in `rag_app_sample_code/A_POC_app/`
   - Process documents using appropriate pipeline (pdf, docx, pptx, or html)
   - Follow the numbered notebooks in sequence
   - Use quality iteration notebooks to measure and improve performance

## 📚 Key Components

- **Document Processing**: 
  - Multi-format support (PDF, DOCX, PPTX, HTML)
  - Intelligent chunking strategies
  - Advanced text extraction and structure preservation

- **Vector Store Integration**: 
  - Databricks Vector Search implementation
  - Optimized embedding generation
  - Efficient similarity search

- **Evaluation Framework**: 
  - Comprehensive testing setup
  - Performance metrics tracking
  - Quality assessment tools

- **Quality Improvement Pipeline**:
  - Systematic issue identification
  - Metric-driven improvements
  - A/B testing of enhancements

## 🛠️ Development Workflow

1. Initial Setup and POC
   - Configure environment
   - Process sample documents
   - Implement basic RAG chain

2. Quality Assessment
   - Run evaluation metrics
   - Identify performance bottlenecks
   - Document quality issues

3. Iteration and Improvement
   - Implement fixes in chain code
   - Enhance data processing pipeline
   - Validate improvements

4. Production Deployment
   - Scale testing
   - Performance optimization
   - Monitoring setup

## 📖 Documentation

For detailed documentation on each component:
- [Databricks Vector Search Documentation](https://docs.databricks.com/en/generative-ai/vector-search.html)
- [Databricks GenAI Development](https://docs.databricks.com/en/generative-ai/index.html)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any enhancements.

## 📄 License

This project is licensed under the terms specified in the LICENSE file. 
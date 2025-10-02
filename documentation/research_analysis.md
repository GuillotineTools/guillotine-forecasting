# Research Analysis: Approaching Human-Level Forecasting with Language Models

## Paper Overview
**Title**: Approaching Human-Level Forecasting with Language Models
**Authors**: Danny Halawi, Fred Zhang, Chen Yueh-Han, Jacob Steinhardt (UC Berkeley)
**Key Finding**: First automated system that nears human crowd performance in forecasting (Brier score 0.179 vs human crowd 0.149)

## Core Methodology

### System Architecture
1. **Retrieval System**: LM-generated search queries → news retrieval → relevance filtering → summarization
2. **Reasoning System**: Structured scratchpad prompting with 4-step reasoning
3. **Ensembling**: 6 forecasts aggregated using trimmed mean

### Key Innovation: 4-Step Reasoning Process
1. **Question Understanding**: Rephrase and expand the question with domain knowledge
2. **Dual Arguments**: Generate arguments for both YES and NO outcomes
3. **Weighted Aggregation**: Weight considerations by importance and aggregate
4. **Calibration**: Check for over/underconfidence and consider historical base rates

## Critical Findings

### 1. Base LMs Are Poor Forecasters
- Even GPT-4 achieves only Brier score 0.208 vs human crowd 0.149
- Most models perform at or worse than random guessing (0.25)
- **Implication**: Retrieval and structured reasoning are essential

### 2. Retrieval-Augmented Forecasting Works
- System performance improved from 0.208 to 0.179 with retrieval
- Query decomposition (breaking into sub-questions) improves coverage
- Relevance filtering prevents misleading information
- **Best Practices**: 15 relevant articles, ranked by relevance

### 3. Selective Forecasting Outperforms Humans
- System beats human crowd when:
  - Crowd uncertainty is high (predictions 0.3-0.7): Brier 0.238 vs 0.240
  - Early retrieval dates: Better relative performance
  - ≥5 relevant articles available
- **Implication**: Confidence thresholds can improve overall performance

### 4. Ensemble Methods Matter
- Trimmed mean outperforms simple averaging
- Multiple models (GPT-4 + fine-tuned variant) provide diversity
- Temperature sampling (T=0.5) increases prediction diversity

### 5. Natural Calibration Achieved
- System becomes well-calibrated without explicit calibration training
- Proper reasoning structure leads to better probability assessment
- Base rate consideration is crucial for calibration

## Domain-Specific Performance

| Domain | System Brier | Crowd Brier | Relative Performance |
|--------|--------------|--------------|---------------------|
| Healthcare & Biology | 0.074 | 0.063 | Close to human |
| Science & Tech | 0.143 | 0.114 | Close to human |
| Sports | 0.175 | 0.171 | Nearly matches |
| Economics & Business | 0.198 | 0.147 | Significant gap |
| Arts & Recreation | 0.221 | 0.146 | Largest gap |

## Practical Implications for Our Bot

### Immediate Improvements (No Fine-tuning Required)
1. **Enhanced 4-Step Reasoning Structure**
2. **Query Decomposition for Retrieval**
3. **Selective Forecasting with Confidence Thresholds**
4. **Trimmed Mean Ensemble Method**
5. **Relevance Filtering for Retrieved Articles**

### Advanced Improvements (Would Require Fine-tuning)
1. **Self-supervised fine-tuning on superior predictions**
2. **Domain-adaptive training for weaker domains**
3. **Iterative self-improvement loops**

### Human-AI Collaboration Insights
- Weighted average (4:1 crowd:system) improves overall performance
- System excels when humans are uncertain
- Can provide retrieval and reasoning assistance to human forecasters

## Implementation Priorities

### Phase 1: Enhanced Reasoning
- [ ] Implement 4-step reasoning structure in all forecasting prompts
- [ ] Add question rephrasing and expansion step
- [ ] Structure arguments for/against outcomes
- [ ] Include importance weighting and calibration steps

### Phase 2: Better Retrieval
- [ ] Implement query decomposition
- [ ] Add relevance scoring for articles
- [ ] Optimize number of articles (target ~15)
- [ ] Implement ranking by relevance and recency

### Phase 3: Selective Forecasting
- [ ] Add confidence assessment to reasoning process
- [ ] Implement selective forecasting based on uncertainty
- [ ] Track performance by domain and adjust strategies
- [ ] Add early retrieval date preference

### Phase 4: Ensemble Optimization
- [ ] Switch from simple average to trimmed mean
- [ ] Increase model diversity in ensemble
- [ ] Add temperature sampling for prediction diversity
- [ ] Implement dynamic weighting based on past performance

## Validation Metrics
- **Brier Score**: Primary metric (lower is better)
- **Accuracy**: Secondary metric for comparison
- **Calibration**: RMS calibration error
- **Coverage**: Percentage of questions where system provides forecasts
- **Relative Performance**: Comparison to human crowd aggregate

## References
- Paper: https://arxiv.org/abs/2402.18563
- Dataset: 5,516 binary questions from Metaculus, GJOpen, INFER, Polymarket, Manifold
- Test set: 914 questions from June 1, 2023 onwards (no knowledge leakage)
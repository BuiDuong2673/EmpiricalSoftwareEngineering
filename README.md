# EmpiricalSoftwareEngineering
Experimental Program for a Conference Paper Practicing Knowledge Learned in the Empirical Methods for Software Engineering Course.

## Description

## Result

### Accuracy Experiment (RQ1)
The LLM-based evaluator showed comparable performance to human evaluators. Here are the results:

```cmd
Human Evaluator 1 accuracy rate: 114 / 116 = 0.9828
Human Evaluator 2 accuracy rate: 114 / 116 = 0.9828
Accuracy of LLM: 112 / 116 = 0.9655
```

The accuracy of the LLM is 96.55%, which is high. It only produced two more incorrect cases compared to the humans.

We calculated the inter-rater consistency using Cohen’s Kappa metrics. Here are the results:

```cmd
Human vs Human inter-rater consistency - Cohen Kappa: 0.7327
Human 1 vs LLM inter-rater consistency - Cohen Kappa: 0.5991
Human 2 vs LLM inter-rater consistency - Cohen Kappa: 0.6485
```

This result shows that human evaluators were not always give correct evaluation. In this case, there are 4 cases that the evalutors give different assessments. In 2 of these cases, after discussion, it turns out that evaluator 1 is right. In 2 other cases, it turns out that evaluator 2 is correct.

### Prompt Attack Experiment (RQ2)

The overall accuracy of LLM, and the accuracies in different classes are:

```cmd
LLM attack assessment accuracy: 40 / 44 = 0.9091
LLM prompt injection attack assessment accuracy: 13 / 13 = 1.0000
LLM prompt leaking attack assessment accuracy: 8 / 10 = 0.8000
LLM jailbreaking attack assessment accuracy: 19 / 21 = 0.9048
```

The accuracy variances between different prompt attack techniques are:

```cmd
Standard deviation: 0.0817
Interquartile range: 0.1000
Mean: 0.9016
Median: 0.9048
```

Inter-rater consistency using Cohen's Kappa metrics between human evaluators and between human evaluators and LLM are:

```cmd
Human vs Human inter-rater consistency - Cohen Kappa: 0.8955
Human 1 vs LLM inter-rater consistency - Cohen Kappa: 0.7816
Human 2 vs LLM inter-rater consistency - Cohen Kappa: 0.7910
```

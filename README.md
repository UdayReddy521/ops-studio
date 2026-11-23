# Ops Studio

A collection of tools, workflows, and demos for engineering and business operations.

| Project | Start here | What to verify next |
| --- | --- | --- |
| GPU validation | [Python checker](gpu-validation/gpu_check.py) and [sample reports](gpu-validation/examples/) | Run the inventory check on a real NVIDIA node against agreed acceptance criteria. |
| Lead follow-up | [Importable n8n workflow](lead-followup/lead-followup.n8n.json) and [sample output](lead-followup/examples/lead-sample-output.json) | Connect an approved enquiry source and verify intake and reminder delivery end to end. |

## Quick start

From the repository root, run the GPU inventory checker with built-in sample data. It requires Python 3 and no GPU.

```bash
python3 gpu-validation/gpu_check.py --sample --expected-count 1 --expected-model 'NVIDIA H100 80GB HBM3' --expected-driver 570.133.20
```

For lead follow-up, import the workflow JSON into n8n and execute it manually. The output should flag only lead L101. The workflow uses fictional enquiries and creates a reminder item in its output.

See the [visual walkthrough](docs/open-the-demo.png) and [field guide](docs/field-guide.md) for the live GPU test commands, n8n integration steps, and pilot scoping questions. Store credentials in your deployment's credential store and keep real customer logs and contact details out of Git.

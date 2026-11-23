# Ops Studio

Python test automation for small engineering teams that want repeatable release checks and clear failure reports. This portfolio also includes a GPU infrastructure validation example.

| Project | Start here | What to verify next |
| --- | --- | --- |
| GPU validation | [Python checker](gpu-validation/gpu_check.py) and [sample reports](gpu-validation/examples/) | Run the inventory check on a real NVIDIA node against agreed acceptance criteria. |
| Release checks | [Lead follow-up API and test suite](lead-followup/release-checks/) | Verify enquiry intake, overdue reminders, and duplicate protection in [GitHub Actions](https://github.com/UdayReddy521/ops-studio/actions/workflows/release-checks.yml). |
| Lead follow-up | [Importable n8n workflow](lead-followup/lead-followup.n8n.json) and [sample output](lead-followup/examples/lead-sample-output.json) | Connect an approved enquiry source and verify intake and reminder delivery end to end. |

## Run the release checks

The staging example exercises the lead-follow-up flow through HTTP endpoints, with SQLite for enquiry storage and a simulated reminder inbox. The Python tests drive those endpoints and verify that the outcomes persist across a restart. The importable n8n workflow below remains available as a separate sample.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r lead-followup/release-checks/requirements.txt
python -m unittest discover -s lead-followup/release-checks -v
```

See the [release-check walkthrough](lead-followup/release-checks/README.md) to try the endpoints and read the expected results.

## GPU and n8n quick start

From the repository root, run the GPU inventory checker with built-in sample data. It requires Python 3 and no GPU.

```bash
python3 gpu-validation/gpu_check.py --sample --expected-count 1 --expected-model 'NVIDIA H100 80GB HBM3' --expected-driver 570.133.20
```

For lead follow-up, import the workflow JSON into n8n and execute it manually. The output should flag only lead L101. The workflow uses fictional enquiries and creates a reminder item in its output.

See the [visual walkthrough](docs/open-the-demo.png) and [field guide](docs/field-guide.md) for the live GPU test commands, n8n integration steps, and pilot scoping questions. Store credentials in your deployment's credential store and keep real customer logs and contact details out of Git.

# Two paid-pilot demos

Start with the visual walkthrough in [open-the-demo.png](open-the-demo.png). Both examples use fictional data. The GPU inventory tool also has a live mode. The n8n workflow is a manual demo with no credentials and sends no messages.

## A. GPU server handover

### Walk through the demo

Run the following from the gpu-validation folder with Python 3:

```bash
python3 gpu_check.py --sample --expected-count 1 --expected-model 'NVIDIA H100 80GB HBM3' --expected-driver 570.133.20
python3 gpu_check.py --sample --expected-count 2 --expected-model 'NVIDIA H100 80GB HBM3' --expected-driver 570.133.20
```

In the second command, the order calls for two GPUs, but the inventory sees one. Show the buyer the count mismatch. Exit 0 means inventory passed, 1 means criteria failed, and 2 means evidence was unavailable. Sample JSON reports are included.

### How an engineer tests a real node

1. Get the node model, exact GPU name as shown by NVIDIA tools, expected count, driver version, workload, test window, and agreed criteria. Confirm the shell or container can see the intended devices. Ask the buyer's engineer to run the checks if they prefer to keep access in-house.
2. On an approved Linux NVIDIA node, remove `--sample` and substitute the agreed values. Save stdout to a local per-node JSON file. Use `nvidia-smi topo -m` to inspect the GPU and NIC topology. Inventory and topology are evidence of visibility and configuration. They do not show throughput.
3. If the node has an approved CUDA environment, run a small PyTorch smoke test using its already installed CUDA-enabled PyTorch. The example below tests the default GPU and verifies a computation. For multiple GPUs, repeat per assigned device or use the node's approved validation suite.

```bash
python3 -c 'import torch; x = torch.arange(8, device="cuda"); assert (x * 2).sum().item() == 56; print(torch.cuda.get_device_name(), torch.version.cuda, "CUDA smoke PASS")'
```

4. On a supported data-center node with DCGM installed, agree on the diagnostic level and run `dcgmi diag -r 1` during the approved window. Record output, versions, and return status. Run active workload and communication tests only on reserved hardware or in the approved test window.
5. For an approved two-GPU single-node test with NVIDIA nccl-tests already built, run the command below. Check for successful completion, zero reported correctness errors, and compare out-of-place bus bandwidth at the same message size against an agreed baseline. Repeat on a like-for-like healthy node when investigating a gap. Treat unsupported or skipped checks as such. Multi-node testing needs a separate scope with matching ranks, allocation, topology, and transport settings.

```bash
./build/all_reduce_perf -b 128M -e 128M -g 2
```

6. Deliver a one-page summary with node aliases, environment versions, timestamps, test commands, agreed thresholds, results, and next action. Use PASS, FAIL, or INCONCLUSIVE per check. Keep raw customer logs private and ask the customer which fields can be shared. Report a low result as a symptom until the cause is verified. Agree on retest scope in advance.

References: [DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/dcgm-diagnostics.html) and [NVIDIA nccl-tests](https://github.com/NVIDIA/nccl-tests).

## B. Lead follow-up for an interior design business

In n8n, create a workflow, import lead-followup/lead-followup.n8n.json from file, then execute the workflow. Open the output of **Find overdue leads**. It should return only L101 for Priya. L102 is still within its deadline and L103 has already been contacted. The fixed clock is 12:00 IST in the example. The included output lets you show the flow without an n8n account.

For a customer pilot, use a test Google Sheet with columns lead_id, owner, status, due_at, and reminded_at. Start with one approved enquiry source. Append rows, then run a scheduled workflow that reads them and uses the current time. Route an overdue NEW lead to its assigned owner in a test channel. Use a stable reminder key per lead and due time, with a persistent delivery record and a way to reconcile uncertain sends. Test overdue, future, contacted, duplicate, invalid timestamp, missing owner, and failed delivery before turning on real reminders. Agree on elapsed time versus business hours and store explicit time offsets. This starter export contains the manual demo and filter. Live Google Sheets and message delivery require the buyer's approved accounts and setup.

## How to talk to buyers

**GPU delivery lead:** “Who signs off a new GPU node before handover? Which check takes your team the most time? Is there a rollout in the next 30 days where a second pair of hands would help?” Then show the mismatch report. Ask how many nodes, what topology, who runs the tests, and who approves the scope.

**Interior design owner:** “Where do your website and WhatsApp enquiries land? Who follows up, and how do you know if one was missed?” Then show L101. Ask for approximate enquiry volume, expected response time, and who owns follow-up. Agree on one intake channel and one internal reminder destination for a pilot.

**Close:** “Would you like a fixed-price pilot for one defined scope? If so, can we agree on a start date, a success criterion, and who can approve the quote?” A compliment is feedback. An agreed paid scope and start date are buying signals. Cash collected is the revenue you can count.

### What to learn, spend, and measure

| | GPU validation | Lead follow-up |
|---|---|---|
| Learn first | Turn hardware specs into pass criteria. Explain what device visibility, CUDA execution, and NCCL performance each prove. | Map the owner's current workflow. Learn Sheets credentials, timestamps, and duplicate-safe reminders. |
| Initial cash | ₹0. Use the included examples and buyer-provided hardware for paid work. | ₹0 for the demo on an existing n8n setup. Agree on recurring hosting or messaging costs before a live pilot. |
| Test quote | ₹25,000–₹40,000 for up to two nodes, a defined time window, and one report. | ₹8,000–₹15,000 for one enquiry source and one internal reminder flow. |
| Profit check | Track delivery hours, travel, tax and other direct costs before pricing additional deployments. | Track setup time, workflow support, hosting and messaging charges before offering monthly maintenance. |

These prices are hypotheses. Guaranteed revenue is ₹0. As an example, one ₹30,000 GPU pilot and one ₹10,000 n8n pilot would be ₹40,000 gross if both close and pay.

Show each demo to five relevant buyers. Track date, problem, decision-maker, deployment or start date, and quote response. Commit further time after a paid pilot or use the objections to improve the offer. Keep employer code and data out of the work and check your employment terms before accepting related paid work.

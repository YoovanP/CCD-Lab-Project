# Model provenance and operation

Model ID: sentiment.
Upstream trained model:
https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english
CPU runtime export:
https://huggingface.co/Xenova/distilbert-base-uncased-finetuned-sst-2-english

Pinned export revision: 0b6928efcb76139cae2c6881d49cda67fe119f42
Weights: onnx/model_quantized.onnx (67,581,197 bytes).
Tokenizer: tokenizer.json (711,396 bytes).
Configuration: config.json (735 bytes).
Total required asset size verified by actual download: 68,293,328 bytes.

The trained model's publisher identifies its license as Apache-2.0. The export
card links to the trained model; it does not declare a separate license in its
metadata. The release archive does not redistribute model weights. Retain
upstream attribution/license information if weights are bundled in Phase 2.
License reference: https://www.apache.org/licenses/LICENSE-2.0

The model is pretrained/fine-tuned for English SST-2 binary sentiment; we are
performing inference rather than training a model. Quantization reduces weight
storage versus full-precision weights. CPU inference was actually verified here.
RAM consumption has not been reliably measured in this execution environment;
record real process/container memory on your machine before choosing Pod limits.

Load once per process. Download only immutable allowlisted assets. ONNX Runtime
uses CPUExecutionProvider, with one native thread by default, without executing
client-selected remote model code. Readiness requires a successful warm-up.
Cached offline startup is supported after assets have been prepared.

Limitations: no neutral class, English focus, possible domain errors and biases,
softmax confidence is not calibrated correctness. Quantization may change outputs
slightly. Inputs are capped by characters and truncated by tokens.
Use synthetic sentences for demos and omit input text from logs.

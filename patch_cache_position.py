import os
import transformers

ved_path = os.path.join(
    os.path.dirname(transformers.__file__), 
    "models", 
    "vision_encoder_decoder", 
    "modeling_vision_encoder_decoder.py"
)

with open(ved_path, "r", encoding="utf-8") as f:
    content = f.read()

# Aggressive patch: Find the exact decoder call and inject the fix right above it
if "kwargs.pop('cache_position', None)" not in content:
    content = content.replace(
        "decoder_outputs = self.decoder(", 
        "kwargs.pop('cache_position', None)\n        decoder_outputs = self.decoder("
    )
    with open(ved_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Successfully patched transformers 4.50.0!")
else:
    print("✅ Already patched!")
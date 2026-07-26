import ollama

# Fetch all models currently active/loaded in memory
running_models = ollama.ps()

for model in running_models.models:

    print(model.name)
    print(model.context_length)
    print(model.size_vram)

    print(model.details.family)
    print(model.details.parameter_size)
    print(model.details.quantization_level)
    print(model.expires_at)